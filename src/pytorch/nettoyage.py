import re
from django.shortcuts import render

class Nettoyage:

    def __init__(self, nettoyage):      
        self._nettoyage = nettoyage

    def nettoyer_symboles(session_variable):
        symboles = r'[^a-zA-Z0-9_=+\-]'
        variable_nettoyee =re.sub(symboles,'',session_variable)
        return variable_nettoyee

    def nettoyer_array(session_array):
        return [Nettoyage.nettoyer_symboles(item) for item in session_array]
    
    def nettoyer_dictionnaire(session_dict):
        return {key: Nettoyage.nettoyer_symboles(value) for key, value in session_dict.items()} 

    # supprime les lettres misent en trop et échappe si pas de lettre après chiffre
    def nettoyage_profondeur(chaine):
        if not chaine: return ""
        resultat = []
        i = 0
        # déplace le curseur i et j et saute des lettres si besoin
        while i < len(chaine):
            resultat.append(chaine[i])
            j = i + 1
            # compare la nature du caractère (ici 2 lettres de suite)
            while j < len(chaine) and chaine[j].isalpha() and chaine[i].isalpha():
                j += 1
            i = j
        variable_nette_profondeur = ''.join(resultat)
        if variable_nette_profondeur == " ":Nettoyage.escape_nettoyage()
        print(variable_nette_profondeur)
        return variable_nette_profondeur
    
    # Permet d'échapper les cas non prévus en cas d'échec de nettoyage
    def escape_nettoyage(request):
        request.session['dico_equation'].clear()
        request.session['compte_equation']=""
        request.session['equations']=""
        context = ""
        return render(request, 'pytorch/confsys_v.html',{"context":context} )  
    
    # permet de passer un chiffre de l'équation de l'autre côté
    def equilibre_equa(chaine):
        equilibre_equa=chaine
        return  equilibre_equa
  
