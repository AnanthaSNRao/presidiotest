import boto3
from botocore.exceptions import ClientError
import os
from django.core.files.storage import FileSystemStorage
from decouple import config
import csv
import logging
from datetime import datetime

logger = logging.getLogger("presidiotest")
S3_client = boto3.client('s3',  aws_access_key_id= config('AWS_ACCESS_KEY_ID'),
         aws_secret_access_key= config('AWS_SECRET_ACCESS_KEY'))
dynamodb_client = boto3.resource('dynamodb',  aws_access_key_id= config('AWS_ACCESS_KEY_ID'),
         aws_secret_access_key= config('AWS_SECRET_ACCESS_KEY'), region_name= config('AWS_REGION_NAME'))
tmpfilename = 'lts-Presidio' + str(datetime.now()) +'.csv' 


def handler():
    table = dynamodb_client.Table(config('TABLE_NAME') )
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
    S3_client.upload_file((tmpfilename), config('OUTPUT_BUCKET') ,config('OUTPUT_KEY'))
    location = config('AWS_REGION_NAME')
    os.remove(tmpfilename)
    if(config('EMPTY_DB_WHILE_BACK_UP')== 'Yes'):
        empty_dynamodb()
    url = "https://s3-%s.amazonaws.com/%s/%s" % (location, config('OUTPUT_BUCKET'), config('OUTPUT_KEY'))
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

# def get_S3_object_list(name):
#     response = S3_client.list_objects_v2(Bucket= name)
#     objects = response['Contents']
#     return objects

def empty_dynamodb():
    table = dynamodb_client.Table(config('TABLE_NAME'))
    response = table.scan()

    with table.batch_writer() as batch:
        print(response['Items'])
        for id in response['Items']['id']:
            batch.delete_item(Key=id)

def upload(file):
    if not file:
        return False
    name = file.name
    object_name = None
    fs = FileSystemStorage()
    file_name = fs.save('static/'+ name, file)
    name = name.split('/')[-1]
    uploaded_file_url = fs.url(name)
    print(uploaded_file_url, file_name)
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = S3_client.upload_file(file_name, config('INITIAL_S3_BUCKET_NAME'), object_name)
    except ClientError as e:
        logger.exception(e)
        raise e
    
    os.remove(file_name)
    return True
