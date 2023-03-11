import boto3
from botocore.exceptions import ClientError
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import csv

S3_client = boto3.client('s3',  aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
         aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)
dynamodb_client = boto3.resource('dynamodb',  aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
         aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY, region_name= settings.AWS_REGION_NAME)
tmpfilename = 'lts-Presidio.csv'


def handler():
    table = dynamodb_client.Table(settings.TABLE_NAME )
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
    S3_client.upload_file(tmpfilename, settings.OUTPUT_BUCKET ,settings.OUTPUT_KEY)
    location = settings.AWS_REGION_NAME
    os.remove(tmpfilename)
    url = "https://s3-%s.amazonaws.com/%s/%s" % (location, settings.OUTPUT_BUCKET, settings.OUTPUT_KEY)
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
    if not f:
        return False
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
    try:
        response = S3_client.upload_file(file_name, "presidio-test", object_name)
    except ClientError as e:
        print(e)
    
    os.remove(file_name)
    return True
