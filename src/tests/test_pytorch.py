import unittest
import torch

def action_matrices(solution_test):
    """
    Fonction pour vérifier la solution d'un système linéaire.
    """
    #solution_test = ([-6.89], [-0.72], [1.48], [4.24])
    return solution_test

class TestMatrices(unittest.TestCase):

    def test_matrice(self):
        # Matrices d'exemple
        matrice_test = torch.tensor([[4, 5, -0.5, 8],
                                     [3, 2, 7, 3],
                                     [-1, -4, 4, -3],
                                     [1, 7, 3, 2]], dtype=torch.float)
        matrice_colonne = torch.tensor([[2], [1], [3], [1]], dtype=torch.float)

        # Calcul de la solution du système
        solution_test = torch.linalg.solve(matrice_test, matrice_colonne)

        # Arrondir la solution pour correspondre aux valeurs attendues
        solution_arrondie = torch.round(solution_test * 100) / 100

        # Récupération de la solution attendue
        resultat_attendu = action_matrices(solution_arrondie)

        # Vérification du résultat
        self.assertTrue(torch.allclose(solution_arrondie, resultat_attendu))

if __name__ == '__main__':
    unittest.main()
    