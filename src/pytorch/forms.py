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
        self.fields['iamodel_name'].queryset = IAmodel.objects.filter(user_id_id=user_id)


class Indicatorform (forms.ModelForm):

    class Meta:
        model = Indicator
        fields = ['indicator_name','indicator_value']
        labels = {'indicator_name':'Nom de l\'indicateur ','indicator_value':'Valeur de l\'indicateur '}

