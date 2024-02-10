from django.shortcuts import render

# Create your views here.

def confmia_user(request):

        
    return render(request, 'pytorch/confmia_v.html')

def prevision_user(request):

        
    return render(request, 'pytorch/prev_v.html')