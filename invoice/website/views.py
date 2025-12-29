from django.shortcuts import render

def home(request):
    return render(request, 'webiste/index.html')

def about(request):
    return render(request, 'webiste/menu.html')
