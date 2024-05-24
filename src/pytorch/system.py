import torch
import re
from .nettoyage import Nettoyage

class System:

    def __init__(self, partie_gauche, partie_droite):
        
        self._partie_gauche = partie_gauche
        self._partie_droite  = partie_droite

    # 
    # Sépare en deux dico_equation puis transforme en matrice la session (qui a été sécurisée)
    # @ param request : session dico_equation : dictionnaire
    # @ session partie_gauche,partie_droite : matrice
    #
    def decompose_equation(request):
        # sépare en deux dico_equation
        dictionnaire = Nettoyage.nettoyer_dictionnaire(request.session['dico_equation'])
        partie_gauche = {}
        partie_droite = {}   
        for cle, valeur in dictionnaire.items():
            elements = valeur.split('=')  # Sépare la valeur en deux parties en fonction du signe '='
            partie_gauche[cle] = elements[0].strip()  # Ajoute la partie de gauche dans le premier dictionnaire
            partie_droite[cle] = elements[1].strip()  # Ajoute la partie de droite dans le deuxième dictionnaire
            try:
                partie_droite[cle] = float(elements[1]) # Vérifie partie de droite sous la forme ... = 10
            except:
                request.session['dico_equation'].clear()
                request.session['compte_equation'] = 0    
        # Traitement de l'absence de coefficient pour "-"
        for key, value in partie_gauche.items():
            updated_value = ''
            for i in range(len(value)):
                if value[i] == '-' and i < len(value) - 1 and value[i + 1].isalpha():
                    updated_value += '-1'
                    continue  # Passe au caractère suivant sans ajouter le "-"
                updated_value += value[i]
            partie_gauche[key] = updated_value
        # Création de la matrice à partir de la partie gauche
        matrices = {}
        for key, value in partie_gauche.items():
            matrix = []
            # Utilisation d'une expression régulière pour capturer les coefficients
            coefficients = re.findall(r'(-?\d+)?([a-zA-Z])', value)
            for coeff, var in coefficients: 
                if coeff:
                    # Si un coefficient est trouvé mit en entier
                    matrix.append(int(coeff))
                else:    
                    matrix.append(1)
            matrices[key] = matrix 
        list_system =[]
        for key, value in matrices.items():
            list_system.append(value) 
        partie_gauche=list_system # Récupération du terme partie gauche pour plus de lisibilité
        partie_droite=[[value] for value in partie_droite.values()] # Transforme en matrice colonne de float la partie de droite
        request.session['partie_gauche']=partie_gauche
        request.session['partie_droite']=partie_droite
        print(request.session['partie_gauche'])
        print(request.session['partie_droite']) 
    
    
    # Appelle la création de matrice et résout par tenseurs pytorch le système et mise en session
    # @ param session : matrice
    # @return solution_arrondie : list
    #
    def resolv(request):
        try:
            partie_gauche = request.session['partie_gauche']
            partie_droite = request.session['partie_droite']
            #partie_gauche = [[[4, 5, -0.5, 8],[3, 2, 7, 3], [-1, -4, 4, -3], [1, 7, 3, 2]]]
            #partie_droite = [[2], [1], [3], [1]]
            solution_arrondie = []
            partie_gauche = torch.tensor(partie_gauche, dtype=torch.float)
            partie_droite = torch.tensor(partie_droite, dtype=torch.float)
            solution_système = torch.linalg.solve(torch.tensor(partie_gauche), torch.tensor(partie_droite)) 
            solution_arrondie = torch.round(solution_système * 100) / 100  # Arrondi à 2 décimales
            solution_arrondie = solution_arrondie.tolist()
            print(solution_arrondie)
        except: 
            solution_arrondie = request.session['partie_gauche']
        return solution_arrondie
    


"""



"""
