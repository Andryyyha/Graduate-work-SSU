import argparse
import csv
import boto3
import json


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stream_name', help='name of Kinesis stream', dest='stream_name', default='stations')
    parser.add_argument('--shard_count', help='count of shards for stream', dest='shard_count', default=1, type=int)
    parser.add_argument('--num_of_retries', help='num of retries to send the same file', dest='num_of_retries',
                        default=5, type=int)
    parser.add_argument('--filename', help='file name with data to send', dest='filename', default='./stations.csv')
    return parser.parse_args()


def send_data_to_stream(kinesis_client, stream_name, shard_count, num_of_retries, filename):
    for i in range(num_of_retries):
        with open(filename) as data:
            print("Iteration {}".format(i))
            reader = csv.reader(data)
            next(reader)
            for line in reader:
                line[1] = '"' + line[1] + '"'
                line[2] = '"' + line[2] + '"'
                record = {
                    'id': line[0],
                    'name': line[1],
                    'address': line[2],
                    'lon': line[3],
                    'lat': line[4],
                    'elevation': line[5]
                }
                # print(record)
                response = kinesis_client.put_record(
                    StreamName=stream_name,
                    Data=json.dumps(record),
                    PartitionKey=str(shard_count)
                )
                print(response)
                record = dict()
        data.close()


def main():
    args = parse()
    stream_name = args.stream_name
    shard_count = args.shard_count
    num_of_retries = args.num_of_retries
    filename = args.filename
    kinesis_client = boto3.client('kinesis', 'us-east-2')
    send_data_to_stream(kinesis_client, stream_name, shard_count, num_of_retries, filename)


if __name__ == "__main__":
    main()
