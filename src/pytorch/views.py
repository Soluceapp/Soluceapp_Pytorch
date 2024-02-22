from django.shortcuts import render, redirect
from .forms import IAmodelform,Chargemodel_form,Indicatorform
from charge.models import IAmodel, Indicator
from django.contrib.auth.models import User
from django.contrib import messages

def miseensession(request,form):
            ### Mise en session de model_name
            request.session['model_name'] = str(form.cleaned_data['iamodel_name'])
            request.session.set_expiry(3000)
            context = request.session['model_name']
            ### Mise en session de model_id
            request.session['model_id'] = str(IAmodel.objects.all().filter(iamodel_name=context)) #erreur ici
            request.session.set_expiry(3000)
            ### Récupération des indicateurs et mise en session
            print(request.session['model_id'])#à faire
            ###

def confmia_user(request):

    #formulaire de chargement
    user_id = request.user.id ### Correction de dépendance de user.id
    if request.method == "POST":
        formcharg = Chargemodel_form(user_id,request.POST)
        if formcharg.is_valid():
            miseensession(request, formcharg)
            messages.success(request,"Modèle chargé")
            return redirect("pytorch:prevision")
    else:    
        formcharg =Chargemodel_form(user_id=user_id)

    #formulaire de création
    if request.method == "POST":
        formcrea = IAmodelform(request.POST)
        if formcrea.is_valid():
            #form.save()
            modifmodel = IAmodel.objects.all().order_by('id').latest('id')
            modifmodel.user_id=User.objects.get(pk=request.user.id) #corrige l'id du propriétaire en interne
            #modifmodel.save()
            miseensession(request, formcrea)
            messages.success(request,"Modèle sauvegardé et chargé")
            return redirect("pytorch:confind")
        else:
            messages.success(request,"Modèle non conforme")
    else:    
        formcrea =IAmodelform()

    return render(request, 'pytorch/confmia_v.html', {"formcharg":formcharg,"formcrea":formcrea})
   

def confind_user(request):
     
    #formulaire des indicateurs
    if request.method == "POST":
        formind = Indicator(request.POST)
        if formind.is_valid():
            #form.save()
            modifmodel = Indicator.objects.all().order_by('id').latest('id')#erreur ici
            modifmodel.iamodel_id=IAmodel.objects.get(pk=request.session['model_id'])#erreur ici
            #modifmodel.save()
            miseensession(request, formind)
            messages.success(request,"Indicateur sauvegardé et chargé")
            return redirect("pytorch:confind")
        else:
            messages.success(request,"Modèle non conforme")
    else:   
        formind = Indicatorform()

    return render(request, 'pytorch/confind_v.html', {"formind":formind})



def prevision_user(request):
      

    return render(request, 'pytorch/prev_v.html')