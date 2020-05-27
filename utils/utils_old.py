import subprocess
import argparse
import os
import boto3
import configparser


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', help='which command to execute', dest='command')
    parser.add_argument('--username', dest='username')
    parser.add_argument('--hostname', dest='hostname')
    parser.add_argument('--path_to_key', help='path to ssh .pem file', dest='path_to_key')
    parser.add_argument('--remote_path', help='path to directory with data on remote server', dest='remote_path')
    parser.add_argument('--recursive', help='flag for single file of whole directory', default='yes')
    parser.add_argument('--local_path', help='where to place data in local server', dest='local_path')
    parser.add_argument('--bucket_name', help='S3 bucket name to copy data', dest='bucket_name')
    parser.add_argument('--date', help='date for pick the folder (date format is YYYYMMDD)', dest='date')
    parser.add_argument('--hour', help='batch hour for creating mask for find missing files', dest='hour')
    return parser.parse_args()


def init():
    configs = configparser.ConfigParser()
    configs.read('prod.conf')
    os.environ['AIRFLOW_VAR_REDSHIFT_URL'] = configs['redshift']['url']
    os.environ['AIRFLOW_VAR_SSH_KEY_PATH'] = configs['credentials']['path_to_key']
    os.environ['AIRFLOW_VAR_USERNAME'] = configs['credentials']['username']
    os.environ['AIRFLOW_VAR_HOSTNAME'] = configs['credentials']['hostname']
    os.environ['AIRFLOW_VAR_BUCKET_NAME'] = configs['s3']['bucket_name']


def exists_remote(username, hostname, path_to_key, path):
    status = subprocess.call(
        ['ssh', '-i', path_to_key, '-o', 'StrictHostKeyChecking=no', '{}@{}'.format(username, hostname), 'test -f {}'.format(path)])
    if status == 0:
        return True
    if status == 1:
        return False
    raise Exception('SSH failed')


def copy_to_local(username, hostname, path_to_key, remote_path, recursive, local_path):
    if exists_remote(username, hostname, path_to_key, remote_path):
        if recursive == 'yes':
            subprocess.run(['scp', '-r', '-i', path_to_key, '-o', 'StrictHostKeyChecking=no', '{}@{}:{}'
                           .format(username, hostname, remote_path), local_path])
        else:
            subprocess.run(['scp', '-i', path_to_key, '-o', 'StrictHostKeyChecking=no', '{}@{}:{}'
                           .format(username, hostname, remote_path), local_path])
    else:
        print("Not all files present on a remote host. Wait when all files will be loaded and try again")


def validate(path, date, hour, username, hostname, path_to_key, remote_path):
    files = os.listdir(path)
    missing_files = list()
    if len(files) != 6:
        print("Files missing, checking...")
        for i in range(6):
            if not os.path.exists('{}/stations{}{}{}'.format(path, date, hour, i * 10)):
                missing_files.append('stations{}{}{}'.format(date, hour, i * 10))
        for file in missing_files:
            copy_to_local(username, hostname, path_to_key, '{}/{}'.format(remote_path, file), recursive='no', local_path=path)
    else:
        print("All files collected")


def load_to_s3(local_path, bucket_name):
    s3_client = boto3.client('s3')
    files = os.listdir(local_path)
    for file in files:
        print(local_path + '/' + file)
        s3_client.upload_file(local_path + '/' + file, bucket_name, 'data/{}'.format(file))


def get_cluster_id():
    emr_client = boto3.client('emr')
    running_cluster = emr_client.list_clusters(ClusterStates=['WAITING'])
    cluster_id = running_cluster['Clusters'][0]['Id']
    return cluster_id


def main():
    args = parse()
    command = args.command
    username = args.username
    hostname = args.hostname
    path_to_key = args.path_to_key
    remote_path = args.remote_path
    local_path = args.local_path
    if command == 'init':
        init()
    elif command == 'copy':
        recursive = args.recursive
        copy_to_local(username, hostname, path_to_key, remote_path, recursive, local_path)
    elif command == 'validate':
        date = args.date
        hour = args.hour
        validate(local_path, date, hour, username, hostname, path_to_key, remote_path)
    elif command == 'load':
        local_path = args.local_path
        bucket_name = args.bucket_name
        date = args.date
        load_to_s3(local_path, bucket_name)
    elif command == "get_cluster_id":
        get_cluster_id()


if __name__ == '__main__':
    main()