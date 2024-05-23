from django import forms

class Equationform (forms.Form):
    equation = forms.CharField(max_length=100, required=False, label ='Equations ')

    def reset(self):
            self.fields['equation'].initial = None

