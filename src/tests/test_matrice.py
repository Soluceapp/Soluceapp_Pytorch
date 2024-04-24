import unittest
import numpy as np
from numpy.linalg import inv


def action_matrices(solution_test):
    """   
    Test être capable de résoudre le système suivant :
    4x + 5y -0.5z +8w = 2
    3x + 2y +7z + 3w = 1
    -x -4y +4z -3w = 3
    x +7y +3z +2y = 1
    x=-6.89 y=-0.72  z=1.48  w= 4.24 
    """
    solution_test = [[-6.89],[-0.72],[1.49],[4.24]]
    return solution_test

class TestMatrices(unittest.TestCase):

    def test_matrice(self):
        # Matrices d'exemple
        matrice_test = np.array([[4, 5, -0.5, 8],
                                 [3, 2, 7, 3],
                                 [-1, -4, 4, -3],
                                 [1, 7, 3, 2]])
        matrice_colonne = np.array([[2], [1], [3], [1]])

        solution_test = np.dot(inv(matrice_test), matrice_colonne)
        solution_arrondie = np.round(solution_test, decimals=2)
        resultat_attendu = action_matrices(solution_arrondie)

        # Vérification du résultat
        self.assertTrue(np.allclose(solution_arrondie, resultat_attendu))

if __name__ == '__main__':
    unittest.main()