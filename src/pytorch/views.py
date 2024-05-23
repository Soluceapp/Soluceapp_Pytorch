from django.shortcuts import render, redirect
from .forms import Equationform
from django.contrib.auth.decorators import login_required
from .nettoyage import Nettoyage
from .manage_session import Manage_session

@login_required        
def confsys_user(request):
    #try:
        context = ""
        if request.method == "POST":
            ## Bouton permettant d'insérer une équation en session
            form = Equationform(request.POST)
            action = request.POST.get('action') 
            if form.is_valid() and "=" in str(form.cleaned_data['equation']):
                if action == 'add_form':
                    if request.session['compte_equation'] == "" : request.session['compte_equation'] = 0  # compteur passant par session pour ajouter visuellement des équations.
                    else : request.session['compte_equation'] +=1
                    Manage_session.equa_session(request, form)
                    context = request.session['dico_equation']
                    form=Equationform() # reset case html
                    form.reset()
                else :
                    Nettoyage.escape_nettoyage(request)          
            ## Bouton permettant de supprimer dernière equation 
            elif action == 'supprime':
                if request.session['dico_equation']:
                    request.session['dico_equation'].popitem()
                    context = request.session['dico_equation']
                    request.session['compte_equation'] = len(request.session['dico_equation'])
            ### Bouton permettant de supprimer toutes les équations   
            elif action == 'efface': 
                Nettoyage.escape_nettoyage(request)
            ### Crée un bouton permettant de trouver la solution 
            elif action == 'solution':
                Manage_session.soluce_session(request)
                context = request.session['dico_solution'] 
                Nettoyage.escape_nettoyage(request)
                return render(request, 'pytorch/sol_v.html',{"context":context} ) 
                   
            
        else: form = Equationform()
    #except: Nettoyage.escape_nettoyage(request)
     
        return render(request, 'pytorch/confsys_v.html',{"form":form,"context":context} ) # Ne pas oublier d'utiliser "safe" en html  
   
@login_required
def solution_user(request):
    context=""
    return render(request, 'pytorch/sol_v.html',{"context":context} )

@login_required
def prevision_user(request):
      
    return render(request, 'pytorch/prev_v.html')





