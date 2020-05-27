import argparse

import boto3
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, IntegerType, StructField, StringType, DoubleType


class Converter:
    def __init__(self, session: SparkSession, args):
        self.session = session
        self.args = args
        self.schema = StructType([
            StructField('id', IntegerType(), nullable=False),
            StructField('name', StringType(), nullable=False),
            StructField('address', StringType(), nullable=False),
            StructField('lon', DoubleType(), nullable=False),
            StructField('lat', DoubleType(), nullable=False),
            StructField('elevation', IntegerType(), nullable=False)
        ])

    def process(self):
        s3_client = boto3.client('s3',
                                 aws_access_key_id=self.args.access_key_id,
                                 aws_secret_access_key=self.args.secret_key)
        files = s3_client.list_objects_v2(
            Bucket='prod-data-and-other',
            Prefix='data/'
        )
        file_names = list()
        for file in files['Contents']:
            file_names.append(file['Key'])
        for name in file_names:
            df = self.session.read.csv('s3n://prod-data-and-other//{}'.format(name), schema=self.schema)
            df.write.parquet('s3n://{}/{}{}'.format(self.args.result_bucket, self.args.prefix, name.split('/')[1]),
                             compression='gzip', mode='overwrite')


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result_bucket', help='Bucket name to place parquet files. Default is prod-data-and-other',
                        dest='result_bucket', default='prod-data-and-other')
    parser.add_argument('--prefix', help='Key prefix for s3 bucket. Default is parquet/',
                        dest='prefix', default='parquet/')
    parser.add_argument('--access_key_id', help='AWS_ACCESS_KEY_ID', dest='access_key_id')
    parser.add_argument('--secret_key', help='AWS_SECRET_KEY', dest='secret_key')
    return parser.parse_args()


def main():
    args = parse()
    access_key_id = args.access_key_id
    secret_key = args.secret_key

    appName = "CSV_Parquet_converter"

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

    session = SparkSession.builder.appName(appName).config(conf=conf).getOrCreate()
    print("Session has been created")

    converter = Converter(session, args)
    converter.process()


if __name__ == '__main__':
    main()
