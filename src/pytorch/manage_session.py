from .system import System
from .nettoyage import Nettoyage

# Cette classe regroupe des méthodes permettant de gérer les données sessions

class Manage_session:
    def __init__(self,request):
        self.session =request.session

    # Mise en session des équations et nettoyage
    # @ Param request, form
    # @ return request.session['dico_equation'] : Dictionnaire
    def equa_session(request,form):
        equation_brute= Nettoyage.nettoyage_profondeur(Nettoyage.nettoyer_symboles(str(form.cleaned_data['equation']))) 
        Manage_session.session_equations_brutes(request,equation_brute) 
        request.session.set_expiry(3000)  
        System.decompose_equation(request)

    # Mise en session de la solution du système
    # @ Param request
    # @ return request.session['dico_solution']
    def soluce_session(request):
        request.session['dico_solution']=System.resolv(request)

    # Mise en session d'equations_brutes
    # @ Param request, equation_brute : string
    # @ return request.session['dico_equation']  : Dictionnaire
    def session_equations_brutes(request,equation_brute):
        session_data = Nettoyage.nettoyer_dictionnaire(request.session.get('dico_equation', {}))
        prochaine_cle = len(session_data) + 1
        session_data[prochaine_cle] = equation_brute
        request.session['dico_equation'] = session_data 
        request.session.save()
        print(request.session['dico_equation'])