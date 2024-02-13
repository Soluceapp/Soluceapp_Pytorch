from django.shortcuts import render, redirect
from .forms import IAmodelform
#from .forms import Indicatorform
#from .forms import Previsionsform
from django.contrib import messages

def confmia_user(request):
                   
        return render(request, 'pytorch/confmia_v.html')

def prevision_user(request):
      
    return render(request, 'pytorch/prev_v.html')

def creamia_user(request):

    if request.method == "POST":
        form = IAmodelform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Modèle sauvegardé")
            return redirect("pytorch:prevision")
        else:
            messages.success(request,"Modèle non conforme")
    else:    
        form =IAmodelform()
        #form =IAmodelform(user=request.user)

    return render(request, 'pytorch/creamia_v.html', {"form":form})

def chargemia_user(request):

    if request.method == "POST":
        form = IAmodelform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Modèle sauvegardé")
            return redirect("pytorch:prevision")
        else:
            messages.success(request,"Modèle non conforme")
    else:    
        form =IAmodelform()
        #form =IAmodelform(user=request.user)

    return render(request, 'pytorch/chargemia_v.html', {"form":form})
   