import argparse

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import min, max, avg
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType


class Metrics:

    def __init__(self, elevation_column, session: SparkSession, args) -> None:
        self.elevation_column = elevation_column
        self.spark_session = session
        self.args = args
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

    def process_from_s3(self):
        print("Processing from S3 started")
        df = self.spark_session.read.option("header", "true") \
            .csv("s3n://prod-data-and-other/data/*.csv", schema=self.schema)
        df.show(50)
        self.write_to_table(self.min_max_lvl(df), self.args.min_max_table)
        self.write_to_table(self.avg_lvl(df), self.args.avg_table)

    def start_metrics(self):
        print("Processing started")
        self.process_from_s3()


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--redshift_url', help='URL of redshift DB', dest='redshift_url')
    parser.add_argument('--min_max_table', help='table name for min and max values', dest='min_max_table',
                        default='min_max')
    parser.add_argument('--avg_table', help='table name for average values', dest='avg_table', default='average')
    parser.add_argument('--s3_tem_dir', help='temp directory in s3 bucket', dest='s3_tem_dir',
                        default='s3n://prod-data-and-other/tmp')
    parser.add_argument('--access_key_id', help='AWS_ACCESS_KEY_ID', dest='access_key_id')
    parser.add_argument('--secret_key', help='AWS_SECRET_KEY', dest='secret_key')
    return parser.parse_args()


def main():
    args = parse()
    access_key_id = args.access_key_id
    secret_key = args.secret_key

    appName = "Metrics"

    conf = SparkConf()
    conf.set("spark.streaming.receiver.writeAheadLog.enable", "true")
    print("Conf has been set")

    sc = SparkContext(
        appName=appName,
        conf=conf
    )
    print("Context been set")
    sc._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId", access_key_id)
    sc._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey", secret_key)

    session = SparkSession.builder.appName(appName)\
        .config(conf=conf).getOrCreate()
    print("Session has been created")

    metrics = Metrics("elevation", session, args)
    metrics.start_metrics()


if __name__ == '__main__':
    main()
