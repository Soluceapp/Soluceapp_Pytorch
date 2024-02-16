from django.test import TestCase

# Create your tests here.
class MyTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testpass(self):
        print("Le test a fonctionné")
        self.assertFalse(False)
        
   # def testfail(self):
    #    print("Le test a échoué")
     #   self.assertTrue(False)

    def testfail(self):
        print("Le test a fonctionné")
        self.assertEqual(1+1,2)