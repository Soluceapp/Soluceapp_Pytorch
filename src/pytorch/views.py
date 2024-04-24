from django.shortcuts import render, redirect
from .forms import Equationform
from django.contrib.auth.decorators import login_required
from .system import System

@login_required        
def confsys_user(request):
    try:
        context = ""
        if request.method == "POST":
            ### Crée formulaire de récupération d'équation.
            form = Equationform(request.POST) 
            if form.is_valid() and "=" in str(form.cleaned_data['equation']):
                if request.session['compte_equation'] == "" : request.session['compte_equation'] = 0  # compteur passant par session pour ajouter visuellement des équations.
                else : request.session['compte_equation'] +=1
                miseensession(request, form)
                context = request.session['dico_equation']
            else :
                request.session['equations']= ""
                request.session['compte_equation'] = 0
            
            action = request.POST.get('action')
            ## Bouton permettant de supprimer dernière equation 
            if action == 'supprime':
                if request.session['dico_equation']:
                    request.session['dico_equation'].popitem()
                    request.session['dico_equation'].popitem()
                    request.session['compte_equation'] = len(request.session['dico_equation'])
            ### Bouton permettant de supprimer les équations   
            elif action == 'efface': 
                request.session['dico_equation'].clear()
                request.session['compte_equation'] = 0 
            ### Crée un bouton permettant de supprimer les équations   
            elif action == 'solution': 
                print("jdefefh") 
        
            
        else: form = Equationform()
    except: print("exception") #redirect('/confsys/')
        
           
    return render(request, 'pytorch/confsys_v.html',{"form":form,"context":context} )
   
@login_required
def solution_user(request):
      

    return render(request, 'pytorch/sol_v.html')

@login_required
def prevision_user(request):
      

    return render(request, 'pytorch/prev_v.html')

def miseensession(request,form):
    ### Mise en session des équations et nettoyage
    equation_nette= str(form.cleaned_data['equation'])
    symboles =["<",">","(",")","#","{","}","&","_","@","]","[",">","&","/",";","*","$","€","|",":","\"","\'","\""]
    for i in symboles: equation_nette = equation_nette.replace(i,"")  
    request.session['equations']= equation_nette.replace(" ","")
    request.session.set_expiry(3000)
    # Création d'une variable dictionnaire des équations {compte_equation:equation_nette}
    session_data = request.session.get('dico_equation', {})
    prochaine_cle = len(session_data) + 1
    session_data[prochaine_cle] = equation_nette
    request.session['dico_equation'] = session_data 
    request.session.save()
    System.creamatrice(request)


