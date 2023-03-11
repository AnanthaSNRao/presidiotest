from django.shortcuts import render
from django.http import HttpResponse
import boto3
from botocore.exceptions import ClientError
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
    
def get(request):
    print('myview-------')
    if request.method == 'POST':
        f = request.FILES['my_file']
        name = f.name
        # file_contents = f.read().decode('utf-8')
        # file_name = 'my_file'
        object_name = None

        print(request.FILES)
        fs = FileSystemStorage()
        file_name = fs.save('static/'+ name, f)
        name = name.split('/')[-1]
        uploaded_file_url = fs.url(name)
        print(uploaded_file_url, file_name)
        # Do something with the file contents
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
        return HttpResponse('File uploaded successfully.')
    else:
        return render(request, 'form.html')

