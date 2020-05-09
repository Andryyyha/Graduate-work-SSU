import argparse
import csv
import boto3
import json
import time
import datetime


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', help='where to upload data: kinesis or s3', dest='mode', default='kinesis')
    parser.add_argument('--stream_name', help='name of Kinesis stream', dest='stream_name', default='stations')
    parser.add_argument('--shard_count', help='count of shards for stream', dest='shard_count', default=1, type=int)
    parser.add_argument('--num_of_retries', help='num of retries to send the same file', dest='num_of_retries',
                        default=5, type=int)
    parser.add_argument('--filename', help='file name with data to send', dest='filename', default='./stations.csv')
    parser.add_argument('--bucket_name', help='bucket name', dest='bucket_name', default='prod-data-and-other')
    return parser.parse_args()


def send_data_to_stream(kinesis_client, stream_name, shard_count, num_of_retries, filename):
    for i in range(200):
        with open(filename) as data:
            print("Iteration {}".format(i))
            reader = csv.reader(data)
            next(reader)
            for line in reader:
                line[1] = '"' + line[1] + '"'
                line[2] = '"' + line[2] + '"'
                record = {
                    'id': int(line[0]),
                    'name': line[1],
                    'address': line[2],
                    'lon': float(line[3]),
                    'lat': float(line[4]),
                    'elevation': int(line[5])
                }
                # print(record)
                response = kinesis_client.put_record(
                    StreamName=stream_name,
                    Data=json.dumps(record),
                    PartitionKey=str(shard_count)
                )
                print(response)
                record = dict()
                print("Sleeping 1s")
                time.sleep(1)
        data.close()


def upload_json_data_to_s3(num_of_retries, bucket_name, filename):
    s3_client = boto3.client('s3')
    for i in range(num_of_retries):
        with open(filename) as data:
            print("Iteration {}".format(i))
            reader = csv.reader(data)
            next(reader)
            for line in reader:
                line[1] = '"' + line[1] + '"'
                line[2] = '"' + line[2] + '"'
                record = {
                    'id': int(line[0]),
                    'name': line[1],
                    'address': line[2],
                    'lon': float(line[3]),
                    'lat': float(line[4]),
                    'elevation': int(line[5])
                }
                # print(record)
                s3_client.put_object(Body=json.dumps(record),
                                     Bucket=bucket_name,
                                     Key='data/dummy_data_{}.json'
                                     .format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
                record = dict()
                print("Sleeping 1s")
                time.sleep(1)
        data.close()


def upload_csv_to_s3(num_of_retries, bucket_name, filename):
    s3_clinet = boto3.client('s3')
    for i in range(num_of_retries):
        print("Iteration {}".format(i))
        response = s3_clinet.upload_file(filename, bucket_name, 'data/stations{}.csv'
                                         .format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        print("Sleeping 1s")
        time.sleep(1)


def main():
    args = parse()
    mode = args.mode
    if mode == 'kinesis':
        stream_name = args.stream_name
        shard_count = args.shard_count
        num_of_retries = args.num_of_retries
        filename = args.filename
        kinesis_client = boto3.client('kinesis', 'us-east-2')
        send_data_to_stream(kinesis_client, stream_name, shard_count, num_of_retries, filename)
    elif mode == 's3':
        num_of_retries = args.num_of_retries
        filename = args.filename
        bucket_name = args.bucket_name
        upload_csv_to_s3(num_of_retries, bucket_name, filename)
        # upload_json_data_to_s3(num_of_retries, bucket_name, filename)


if __name__ == "__main__":
    main()
