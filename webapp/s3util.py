import boto3


def write_file_data(bucket, filename, contents):
    s3 = boto3.resource('s3')
    object = s3.Object(bucket, filename)
    object.put(Body=contents)


def read_file_data(bucket, filename):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, filename)
    contents = obj.get()['Body'].read().decode('utf-8')
    return contents


