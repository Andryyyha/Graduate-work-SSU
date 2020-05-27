import argparse
import os
import boto3


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_path', help='where to place data in local server', dest='local_path')
    parser.add_argument('--bucket_name', help='S3 bucket name to copy data', dest='bucket_name')
    return parser.parse_args()


def load_to_s3(local_path, bucket_name):
    s3_client = boto3.client('s3')
    files = os.listdir(local_path)
    for file in files:
        print(local_path + '/' + file)
        s3_client.upload_file(local_path + '/' + file, bucket_name, 'data/{}'.format(file))


def main():
    args = parse()
    local_path = args.local_path
    bucket_name = args.bucket_name
    load_to_s3(local_path, bucket_name)


if __name__ == '__main__':
    main()