"""from django.test import TestCase
from charge.models import IAmodel

class Formtests(TestCase):
    def setUp(self):
        self.iamodel = IAmodel.objects.create(iamodel_name ="Test IAmodel")

    def test_is_correct_instance(self):
        self.assertIsInstance(self.iamodel, IAmodel)

    def test_exists(self):
        iamodel = IAmodel.objects.get(pk=1)
        self.assertTrue(iamodel)
        """