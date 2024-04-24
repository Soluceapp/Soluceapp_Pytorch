from django import forms
from charge.models import IAmodel, Indicator

class IAmodelform (forms.ModelForm):

    class Meta:
        model = IAmodel
        fields = ['iamodel_name','nbr_indicator']
        labels = {'iamodel_name':'Nom du modèle ','nbr_indicator':'Nombre d\'indicateurs '}
    def clean_nbr_indicator(self):
        nbr_indicator = self.cleaned_data['nbr_indicator']
        if nbr_indicator<=0:
            nbr_indicator=-nbr_indicator
        return nbr_indicator


class Chargemodel_form (IAmodelform):
    
    iamodel_name = forms.ModelChoiceField(queryset=IAmodel.objects.none(),label="Nom du modèle ",)  # Initial queryset is empty

    class Meta:
        model = IAmodel
        fields = ['iamodel_name']

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['iamodel_name'].queryset = IAmodel.objects.filter(user_id=user_id)


""" Voir à supprimer ou modifier """
class Indicatorform (forms.ModelForm):

    class Meta:
        model = Indicator
        fields = ['indicator_name','indicator_value']
        labels = {'indicator_name':'Nom de l\'indicateur ','indicator_value':'Valeur de l\'indicateur '}

"""
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
            messages.success(request,"Décrivez les indicateurs")
            return redirect("pytorch:confind")
        else:
            messages.success(request,"Modèle non conforme")
    else:    
        formcrea =IAmodelform()

    return render(request, 'pytorch/confmia_v.html', {"formcharg":formcharg,"formcrea":formcrea})
   

def confind_user(request):
     
    #indicator_instance =Indicator.objects.get(pk=1)
    IndicatorformSet = formset_factory(Indicatorform, extra=2)
    #formulaire des indicateurs
    if request.method == "POST":
        formset = IndicatorformSet(request.POST)
        if formset.is_valid():
            for form in formset: 
                print(form)           
            #formset.save()
            #modifmodel = Indicator.objects.all().order_by('id').latest('id')#erreur ici
            #modifmodel.iamodel_id=IAmodel.objects.get(pk=request.session['model_id'])#erreur ici
            #modifmodel.save()
            #miseensession(request, formind)
            #messages.success(request,"Indicateur sauvegardé et chargé")
                return redirect("pytorch:confind")
        #else:
            #messages.success(request,"Modèle non conforme")
    else:
        for form in formset: 
                print(form)    
        formset = IndicatorformSet()

    return render(request, 'pytorch/confind_v.html', {"formset":formset})


"""

