import torch
import re

class System:

    def __init__(self, list_system, list_total):
        self._list_system = torch.tensor(list_system, dtype=torch.float)  # Convertir en tenseur PyTorch
        self._list_total = torch.tensor(list_total, dtype=torch.float)  # Convertir en tenseur PyTorch

    def resolv(self):
        solution_test = torch.linalg.solve(self._list_system, self._list_total)  # Utiliser la fonction de résolution de PyTorch
        solution_arrondie = torch.round(solution_test * 100) / 100  # Arrondir à 2 décimales
        return solution_arrondie
    
    def creamatrice(request):# sépare en deux dico_equation puis transforme en matrice
        # sépare en deux dico_equation
        dictionnaire = request.session['dico_equation']
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
        print(list_system)
        print(partie_droite)

system1 = System([[4, 5, -0.5, 8], [3, 2, 7, 3], [-1, -4, 4, -3], [1, 7, 3, 2]],
                 [[2], [1], [3], [1]])
solution = system1.resolv()
print(solution)


 
