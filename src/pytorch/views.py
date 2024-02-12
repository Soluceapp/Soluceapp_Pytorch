from django.shortcuts import render, redirect
from .forms import IAmodelform
# Create your views here.

def confmia_user(request):

        if request.method == "POST":
            form = IAmodelform(request.POST)
            if form.is_valid():
                #user_id=username
                form.save()
                return redirect("connexion:dashboard")

        else:
            form =IAmodelform()

        return render(request, 'pytorch/confmia_v.html', {"form":form})

def prevision_user(request):

        
    return render(request, 'pytorch/prev_v.html')