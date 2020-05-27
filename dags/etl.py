from datetime import timedelta

from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from airflow.models import Variable
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago
import datetime


DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(3),
    'email': ['adrianvalir@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

# 1 check if data exists
# 2 trigger python script at remote server
# 3.1 run job for metrics
# 3.2 run job for conversion
# 4.1 wait for 3.1 execution
# 4 wait for 3.2 execution
# 5 send email about completion

configs = Variable.get('configs', deserialize_json=True)
redshift_url = configs['redshift_url']
aws_access_key_id = configs['aws_access_key_id']
aws_secret_key = configs['aws_secret_key']

SPARK_STEPS = [
    {
        'Name': 'Metrics',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['spark-submit', '--deploy-mode', 'client', '--jars',
                     's3://prod-data-and-other/dependencies/RedshiftJDBC41-1.2.12.1017.jar', '--packages',
                     'org.apache.spark:spark-streaming-kinesis-asl_2.11:2.4.0,com.databricks:spark-redshift_2.11:2.0.0,'
                     'com.google.protobuf:protobuf-java:2.6.1,org.apache.spark:spark-avro_2.11:2.4.5,'
                     'org.apache.avro:avro-mapred:1.8.1,com.eclipsesource.minimal-json:minimal-json:0.9.5',
                     '--conf', 'spark.streaming.receiver.writeAheadLog.enable=true',
                     's3://prod-data-and-other/application/metrics.py', '--redshift_url',
                     redshift_url, '--access_key_id', aws_access_key_id,
                     '--secret_key', aws_secret_key]
        }
    }
]

CONVERTER = [
    {
        'Name': 'CSV_Parquet_Converter',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['spark-submit', '--deploy-mode', 'client',
                     '--conf', 'spark.streaming.receiver.writeAheadLog.enable=true',
                     's3://prod-data-and-other/application/csv_parquet_converter.py',
                     '--access_key_id', aws_access_key_id,
                     '--secret_key', aws_secret_key]
        }
    }
]

dag = DAG(dag_id='run_batch_etl',
          default_args=DEFAULT_ARGS,
          dagrun_timeout=timedelta(hours=1),
          schedule_interval=None
          )

ssh_hook = SSHHook(ssh_conn_id='prod_server')

t1 = SSHOperator(
    task_id='check_if_data_exists',
    ssh_hook=ssh_hook,
    command="""
            if [[ -d "/home/ec2-user/data/csv" ]]; then
                echo "Files exists"
            else
                echo "Files does not exists!"
                exit 1
            fi
              """,
    retries=0,
    dag=dag
)

t2 = SSHOperator(
    task_id='trigger_remote_script',
    ssh_hook=ssh_hook,
    command='python3 /home/ec2-user/scripts/utils.py --command load --local_path /home/ec2-user/data/csv '
            '--bucket_name prod-data-and-other',
    retries=0,
    dag=dag
)

t3a = EmrAddStepsOperator(
    task_id='calc_metrics',
    job_flow_id=Variable.get("cluster_id"),
    aws_conn_id='prod_aws',
    steps=SPARK_STEPS,
    retries=0,
    dag=dag
)

t4a = EmrAddStepsOperator(
    task_id='convert_csv',
    job_flow_id=Variable.get("cluster_id"),
    aws_conn_id='prod_aws',
    steps=CONVERTER,
    retries=0,
    dag=dag
)

t3b = EmrStepSensor(
    task_id='wait_for_execution',
    job_flow_id=Variable.get("cluster_id"),
    step_id="{{ task_instance.xcom_pull(task_ids='calc_metrics', key='return_value')[0] }}",
    aws_conn_id='prod_aws',
    dag=dag
)

t4b = EmrStepSensor(
    task_id='wait_for_convert_completion',
    job_flow_id=Variable.get("cluster_id"),
    step_id="{{ task_instance.xcom_pull(task_ids='convert_csv', key='return_value')[0] }}",
    aws_conn_id='prod_aws',
    dag=dag
)

t5 = EmailOperator(
    task_id='etl_pipeline_complete',
    to='adrianvalir@gmail.com',
    subject='ETL pipeline for {} complete!'.format(datetime.datetime.now().strftime('%Y%m%d')),
    html_content='',
    mime_charset='utf-8',
    dag=dag
)
t3a >> t3b
t4a >> t4b
t3b >> t5
t4b >> t5
t1 >> t2 >> [t3a, t4a]

