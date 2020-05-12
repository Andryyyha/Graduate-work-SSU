import pipes
import subprocess
import argparse
import os

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', help='which command to execute', dest='command')
    parser.add_argument('--username', dest='username')
    parser.add_argument('--hostname', dest='hostname')
    parser.add_argument('--path_to_key', help='path to ssh .pem file', dest='path_to_key')
    parser.add_argument('--remote_path', help='path to directory with data on remote server', dest='remote_path')
    parser.add_argument('--recursive', help='flag for single file of whole directory', default='yes')
    parser.add_argument('--local_path', help='where to place data in local server', dest='path')
    parser.add_argument('--bucket_name', help='S3 bucket name to copy data', dest='bucket_name')
    parser.add_argument('--object_name', help='object name for S3', dest='object_name')
    parser.add_argument('--date', help='date for creting mask for find missing files', dest='date')
    parser.add_argument('--hour', help='batch hour for creating mask for find missing files', dest='hour')
    return parser.parse_args()


def exists_remote(host, path):
    """Test if a file exists at path on a host accessible with SSH."""
    status = subprocess.call(
        ['ssh', host, 'test -f {}'.format(pipes.quote(path))])
    if status == 0:
        return True
    if status == 1:
        return False
    raise Exception('SSH failed')


def copy_to_local(username, hostname, path_to_key, remote_path, recursive, local_path):
    if recursive == 'yes':
        subprocess.run(['scp', '-r', '-i', path_to_key, '-o', 'StrictHostKeyChecking=no', '{}@{}:{}'
                       .format(username, hostname, remote_path), local_path])
    else:
        subprocess.run(['scp', '-i', path_to_key, '-o', 'StrictHostKeyChecking=no', '{}@{}:{}'
                       .format(username, hostname, remote_path), local_path])


def validate(path, date, hour, username, hostname, path_to_key, remote_path, local_path):
    files = os.listdir(path)
    missing_files = list()
    if len(files) != 6:
        for i in range(6):
            if not os.path.exists('{}/stations{}{}{}'.format(path, date, hour, i * 10)):
                missing_files.append('stations{}{}{}'.format(date, hour, i * 10))
        for file in missing_files:
            copy_to_local(username, hostname, path_to_key, '{}/{}'.format(remote_path, file), recursive='no', local_path=local_path)


def load_to_s3(local_path, bucket_name, object_name):
    pass


def main():
    args = parse()
    command = args.command
    username = args.username
    hostname = args.hostname
    path_to_key = args.path_to_key
    remote_path = args.remote_path
    local_path = args.local_path
    if command == 'copy':
        recursive = args.recursive
        copy_to_local(username, hostname, path_to_key, remote_path, recursive, local_path)
    elif command == 'validate':
        date = args.date
        hour = args.hour
        validate(local_path, date, hour)
    elif command == 'load':
        local_path = args.local_path
        bucket_name = args.bucket_name
        object_name = args.object_name
        load_to_s3(local_path, bucket_name, object_name)


if __name__ == '__main__':
    main()