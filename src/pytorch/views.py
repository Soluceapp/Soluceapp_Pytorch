from django.shortcuts import render, redirect
from .forms import IAmodelform
from charge.models import IAmodel
from django.contrib.auth import get_user
from django.contrib.auth.models import User
#from .forms import Indicatorform
#from .forms import Previsionsform
from django.contrib import messages


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
   
def confmia_user(request):
                   
    return render(request, 'pytorch/confmia_v.html')

def creamia_user(request):
    if request.method == "POST":
        form = IAmodelform(request.POST)
        if form.is_valid():
            form.save()
            modifmodel = IAmodel.objects.all().order_by('id').latest('id')
            modifmodel.user_id=User.objects.get(pk=request.user.id)
            modifmodel.save()
            messages.success(request,"Modèle sauvegardé")
            return redirect("pytorch:prevision")
        else:
            messages.success(request,"Modèle non conforme")
    else:    
        form =IAmodelform()
    return render(request, 'pytorch/creamia_v.html', {"form":form})

def prevision_user(request):
      
    return render(request, 'pytorch/prev_v.html')