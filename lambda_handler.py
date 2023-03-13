import json
import urllib.parse
import boto3
import csv
import codecs


print('Loading function')

s3 = boto3.client('s3')
dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    table = dynamodb.Table("presidio-test-db")
    header = True
    header_items = []
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        for row in csv.reader(codecs.getreader("utf-8")(response["Body"]), delimiter='\t'):
            if header:
                header_items = row
                header = False
                continue
            d = {}
            for i,h in enumerate(header_items):
                if i ==0:
                    d[h] = int(row[i])
                else:
                    d[h] = row[i]
                    
            table.put_item(Item = d)
            print(d)
    except Exception as e:
        print(e)
        raise e
              