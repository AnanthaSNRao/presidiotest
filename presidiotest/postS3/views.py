from django.shortcuts import render
from django.http import HttpResponse
from . import stoage_db
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger("presidiotest")

@csrf_exempt
def get(request):
    try:
        if request.method == 'POST':
            f = request.FILES.get('my_file', None)
            if not f:
                logger.warning("No file selected")
                return HttpResponse('Please select a file.', status=400)
            elif f.content_type != 'text/plain':
                logger.info("Invalid file type.", f.content_type)
                return HttpResponse('Invalid file type.', status=400)
            else:
                res = stoage_db.upload(f)
                return HttpResponse('File uploaded successfully.') if res else HttpResponse('File upload was not successful.')
        else:
            return render(request, 'form.html')
    except Exception as e:
        logger.error(e)
        return HttpResponse("Internal Server Error", status=500)
    
@csrf_exempt
def download(request):
    try:
        url = stoage_db.handler()
        if url is None or not url:
            return HttpResponse('No file available for download.', status=404)
        
        return HttpResponse(url) 
    except Exception as e:
        logger.error(e)
        return HttpResponse("Internal Server Error", status=500)


# def get_list(request):
#     l = stoage_db.get_list
#     return render(request, 'form.html', {'list': l})

