from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from . import stoage_db

def get(request):
    if request.method == 'POST':
        f = request.FILES.get('my_file', None)
        if not f:
            return HttpResponse('Please select a file.', status=400)
        elif f.content_type != 'text/plain':
            return HttpResponse('Invalid file type.', status=400)
        else:
            res = stoage_db.upload(f)
            return HttpResponse('File uploaded successfully.') if res else HttpResponse('File upload was not successful.')
    else:
        return render(request, 'form.html')
    

def download(request):
    url = stoage_db.handler()
    if url is None or not url:
        return HttpResponse('No file available for download.', status=404)
    
    return render(request, 'form.html', {'url': url})


# def get_list(request):
#     l = stoage_db.get_list
#     return render(request, 'form.html', {'list': l})

