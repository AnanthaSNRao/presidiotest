from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# def my_view(request):
#     print('myview-------')
#     if request.method == 'POST':
#         my_file = request.FILES['my_file']
#         file_contents = my_file.read().decode('utf-8')
#         # Do something with the file contents
#         return HttpResponse('File uploaded successfully.')
#     else:
#         return render(request, 'form.html')
    
def get(request):
    print('myview-------')
    if request.method == 'POST':
        my_file = request.FILES['my_file']
        file_contents = my_file.read().decode('utf-8')
        # Do something with the file contents
        return HttpResponse('File uploaded successfully.')
    else:
        return render(request, 'form.html')

