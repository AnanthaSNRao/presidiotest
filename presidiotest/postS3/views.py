from django.shortcuts import render
from django.http import HttpResponse
from . import stoage_db

def get(request):
    print('myview-------')
    if request.method == 'POST':
        f = request.FILES['my_file']
        stoage_db.upload(f)
        return HttpResponse('File uploaded successfully.')
    else:
        return render(request, 'form.html')
    

def download(request, name):
    url = stoage_db.handler(name)
    return render(request, 'form.html', {'url': url})

def get_list(request):
    l = stoage_db.get_list
    return render(request, 'form.html', {'list': l})

