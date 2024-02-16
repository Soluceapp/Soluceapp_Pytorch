from django import forms
from charge.models import IAmodel


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
'''
    def __init__(self, user, *args, **kwargs):
        super(IAmodelform, self).__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        instance = super(IAmodelform, self).save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
'''
    