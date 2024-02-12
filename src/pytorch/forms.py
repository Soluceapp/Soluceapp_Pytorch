from django import forms
from charge.models import IAmodel


class IAmodelform (forms.ModelForm):
   # iamodel_name = forms.ModelChoiceField(queryset=iamodel_name.objects.All(),label ="Nom du modèle d'IA")
    class Meta:
        model = IAmodel
        fields = ['iamodel_name','user','nbr_indicator']
        labels = {'iamodel_name':'Nom du modèle d\'IA ','user':'Propriétaire ','nbr_indicator':'Nombre d\'indicateurs '}