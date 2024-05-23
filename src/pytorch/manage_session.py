from .system import System
from .nettoyage import Nettoyage

# Cette classe regroupe des méthodes permettant de gérer les données sessions

class Manage_session:
    def __init__(self,request):
        self.session =request.session

    # Mise en session des équations et nettoyage
    # @ Param request, form
    # @ return request.session['dico_equation']
    def equa_session(request,form):
        equation_nette= Nettoyage.nettoyage_profondeur(Nettoyage.nettoyer_symboles(str(form.cleaned_data['equation'])))
        request.session.set_expiry(3000)
        # Création d'une variable dictionnaire des équations {compte_equation:equation_nette}
        session_data = Nettoyage.nettoyer_dictionnaire(request.session.get('dico_equation', {}))
        prochaine_cle = len(session_data) + 1
        session_data[prochaine_cle] = equation_nette
        request.session['dico_equation'] = session_data 
        request.session.save()
        System.decompose_equation(request)

    # Mise en session de la solution du système
    # @ Param request, ?
    # @ return request.session['dico_solution']
    def soluce_session(request):
        request.session['dico_solution']=System.resolv(request)
      
    