import boto3
from botocore.exceptions import ClientError
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import csv
import json

TABLE_NAME_PREFIX = 'presidio-test-db'
OUTPUT_BUCKET = 'long-term-storage-presidio'
tmpfilename_PREFIX = 'lts-Presidio'
OUTPUT_KEY_PREFIX = 'lts-Presidio'

S3_client = boto3.client('s3',  aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
         aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)
dynamodb_client = boto3.resource('dynamodb',  aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
         aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY, region_name='us-west-1')



def handler(name):
    table = dynamodb_client.Table(TABLE_NAME_PREFIX + '-' +name)
    tmpfilename = tmpfilename_PREFIX + name
    with open(tmpfilename, 'w') as output_file:
        writer = csv.writer(output_file)
        header = True
        first_page = True

        # Paginate results
        while True:
            if first_page:
                response = table.scan()
                first_page = False
            else:
                response = table.scan(ExclusiveStartKey = response['LastEvaluatedKey'])

            for item in response['Items']:

                # Write header row?
                if header:
                    writer.writerow(item.keys())
                    header = False

                writer.writerow(item.values())

            # Last page?
            if 'LastEvaluatedKey' not in response:
                break

    # Upload temp file to S3
    S3_client.upload_file(tmpfilename, OUTPUT_BUCKET ,OUTPUT_KEY_PREFIX + '-'+ name)
    location = 'us-west-1'
    url = "https://s3-%s.amazonaws.com/%s%s" % (location, OUTPUT_BUCKET, tmpfilename)
    return url

def get_list():
    table_names = []
    response = dynamodb_client.list_tables()

    while True:
        table_names.extend(response['TableNames'])
        if 'LastEvaluatedTableName' not in response:
            break
        response = dynamodb_client.list_tables(ExclusiveStartTableName=response['LastEvaluatedTableName'])

    return table_names



def upload(f):
    name = f.name
    object_name = None
    fs = FileSystemStorage()
    file_name = fs.save('static/'+ name, f)
    name = name.split('/')[-1]
    uploaded_file_url = fs.url(name)
    print(uploaded_file_url, file_name)
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file

    s3_client = boto3.client('s3',  aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)
    try:
        response = s3_client.upload_file(file_name, "presidio-test", object_name)
    except ClientError as e:
        print(e)
    
    os.remove(file_name)
    return True
