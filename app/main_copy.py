from pyspark import SparkConf, SparkContext, StorageLevel
from pyspark.streaming import StreamingContext
from pyspark.streaming.kinesis import KinesisUtils, InitialPositionInStream
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType
from pyspark.streaming import DStream
from pyspark.sql.functions import min, max, avg

import argparse


class Metrics:

    def __init__(self, elevation_column, session: SparkSession, args, kinesis_stream: DStream, window_interval,
                 sliding_interval) -> None:
        self.elevation_column = elevation_column
        self.spark_session = session
        self.args = args
        self.kinesis_stream = kinesis_stream
        self.window_interval = window_interval
        self.sliding_interval = sliding_interval
        self.schema = StructType([
            StructField('id', IntegerType(), nullable=False),
            StructField('name', StringType(), nullable=False),
            StructField('address', StringType(), nullable=False),
            StructField('lon', DoubleType(), nullable=False),
            StructField('lat', DoubleType(), nullable=False),
            StructField('elevation', IntegerType(), nullable=False)
        ])

    def write_to_table(self, df: DataFrame, table_name):
        print("Writing to table {}".format(table_name))
        df.write \
            .format("com.databricks.spark.redshift") \
            .option("url", "jdbc:redshift://{}".format(self.args.redshift_url)) \
            .option("dbtable", table_name) \
            .option("tempdir", 's3n://prod-data-and-other/tmp') \
            .mode("append") \
            .save()

    def min_max_lvl(self, df: DataFrame):
        return df.agg(min(self.elevation_column).alias("min_elevation"),
                      max(self.elevation_column).alias("max_elevation"))

    def avg_lvl(self, df: DataFrame):
        return df.agg(avg(self.elevation_column).alias("average_elevation"))

    def create_df(self, rdd, spark: SparkSession):
        print("Creating DF")
        return spark.createDataFrame(rdd, self.schema)

    def process(self, rdd):
        print("Creating DF")
        df = self.create_df(rdd, self.spark_session)
        print("Print DF")
        df.show(50)
        print("Calculate min_max and write to Redshift")
        # self.write_to_table(self.min_max_lvl(df), self.args.min_max_table)
        print("Calculate avg and write to Redshift")
        # self.write_to_table(self.avg_lvl(df), self.args.avg_table)

    def process_from_s3(self):
        print("Processing from S3 started")
        # Working thing
        df = self.spark_session.read.option("header", "true").csv("s3n://prod-data-and-other/data/*.csv",
                                                                  schema=self.schema)
        df.show(50)
        self.write_to_table(self.min_max_lvl(df), self.args.min_max_table)
        self.write_to_table(self.avg_lvl(df), self.args.avg_table)

    def start_metrics(self):
        print("Processing started")
        self.process_from_s3()
        # rdd_from_stream = self.kinesis_stream.map(lambda x: json.loads(x))
        # self.kinesis_stream.pprint()
        # rdd_from_stream.foreachRDD(lambda rdd: self.process(rdd))


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint_url', help='url to kinesis stream', dest='endpoint_url',
                        default='https://kinesis.us-east-2.amazonaws.com')
    parser.add_argument('--aws_region', help='aws region for stream', dest='aws_region', default='us-east-2')
    parser.add_argument('--kinesis_checkpoint_interval', help='kinesis checkpoint interval, recommended to set the '
                                                              'same as batch interval of application', default=10)
    parser.add_argument('--total_running_time', help='total running time of application', dest='total_running_time',
                        default=60, type=int)
    parser.add_argument('--window_interval', help='window length for computation', dest='window_interval', default=180,
                        type=int)
    parser.add_argument('--sliding_interval', help='length of interval for sliding through window',
                        dest='sliding_interval', default=30, type=int)
    parser.add_argument('--redshift_url', help='URL of redshift DB', dest='redshift_url')
    parser.add_argument('--min_max_table', help='table name for min and max values', dest='min_max_table',
                        default='min_max')
    parser.add_argument('--avg_table', help='table name for average values', dest='avg_table', default='average')
    parser.add_argument('--s3_tem_dir', help='temp directory in s3 bucket', dest='s3_tem_dir',
                        default='s3n://prod-data-and-other/tmp')
    parser.add_argument('--access_key_id', help='AWS_ACCESS_KEY_ID', dest='access_key_id')
    parser.add_argument('--secret_key', help='AWS_SECRET_KEY', dest='secret_key')
    parser.add_argument('--date')
    return parser.parse_args()


def main():
    args = parse()
    endpoint_url = args.endpoint_url
    aws_region = args.aws_region
    kinesis_checkpoint_interval = args.kinesis_checkpoint_interval
    total_running_time = args.total_running_time
    window_interval = args.window_interval
    sliding_interval = args.sliding_interval
    access_key_id = args.access_key_id
    secret_key = args.secret_key
    appName = "ETL"

    conf = SparkConf()
    conf.set("spark.streaming.receiver.writeAheadLog.enable", "true")
    print("Conf has been set")

    sc = SparkContext(
        appName=appName,
        conf=conf
    )
    print("Context been set")
    sc._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId",  access_key_id)
    sc._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey", secret_key)
    ssc = StreamingContext(sc, 10)

    print("Streaming context has been sent")

    session = SparkSession.builder.appName(appName).config(conf=conf).getOrCreate()
    print("Session has been created")

    kinesis_stream = KinesisUtils.createStream(ssc, appName, "stations", endpoint_url, aws_region,
                                               InitialPositionInStream.LATEST, kinesis_checkpoint_interval,
                                               StorageLevel.MEMORY_AND_DISK_2, awsAccessKeyId=access_key_id,
                                               awsSecretKey=secret_key)

    print("Kinesis client has been initialized")
    metrics = Metrics("elevation", session, args, kinesis_stream, window_interval, sliding_interval)
    metrics.start_metrics()

    print("Computation started")
    # ssc.start()
    # ssc.awaitTermination(total_running_time)
    # ssc.stop()


if __name__ == '__main__':
    main()