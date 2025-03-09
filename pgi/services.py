from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from django.shortcuts import get_object_or_404, redirect
from .forms import *
from django.contrib import messages
from cryptography.fernet import Fernet
from django.conf import settings
import re
from django.http import JsonResponse
from .models import Remise
from django.db.models import Count

##
# Fonctions sécurisant les sessions / Nettoyage
##
SECRET_KEY = settings.SECRET_KEY_ENCRYPTION
def encrypt_value(value):
    fernet = Fernet(SECRET_KEY)
    encrypted_value = fernet.encrypt(nettoyer(str(value)).encode())
    return encrypted_value.decode()
def decrypt_value(value):
    fernet = Fernet(SECRET_KEY)
    decrypted_value = fernet.decrypt(value.encode())
    return decrypted_value.decode()
def nettoyer(session_variable):
        symboles = r'[^a-zA-Z0-9_=+\-]'
        variable_nettoyee =re.sub(symboles,'',session_variable)
        return variable_nettoyee
def filter_int(value, default=None):
    try:
        return int(value)  
    except (ValueError, TypeError): 
        return default  # Retourne la valeur par défaut (None ou autre)

##
# Fonctions permettant de gérer une grande quantité de clients
##
class ClientService:

    @staticmethod
    def cherche_form(request):
        """ Recherche d'informations en tapant un mot."""
        cherche_form = ChercheClientForm(request.POST)
        form = None
        affiche_form = None
        clients_list=None

        if cherche_form.is_valid():
            search_query = cherche_form.cleaned_data['client_search']
            info_trouves = Client.objects.filter(nom__icontains=search_query)
            if info_trouves.exists():
                if info_trouves.count() == 1:
                    client = info_trouves.first()
                    affiche_form = EditClientForm(instance=client)
                    messages.success(request, "Il n'y a pas de doublon.")
                else:
                    clients_list = info_trouves
                    messages.warning(request, "Il existe plusieurs informations relatives.")
            else:
                messages.info(request, "Aucun client trouvé pour cette recherche.")  
        return form, affiche_form, clients_list

##
# Fonctions permettant de gérer une grande quantité de fournisseurs
##
class FournisseurService:

    @staticmethod
    def cherche_form(request):
        """ Recherche d'informations en tapant un mot."""
        cherche_form = ChercheFournisseurForm(request.POST)
        form = None
        affiche_form = None
        fournisseur_list=None

        if cherche_form.is_valid():
            search_query = cherche_form.cleaned_data['fournisseur_search']
            info_trouves = Fournisseur.objects.filter(nom__icontains=search_query)
            if info_trouves.exists():
                if info_trouves.count() == 1:
                    fournisseur = info_trouves.first()
                    affiche_form = EditFournisseurForm(instance=fournisseur)
                    messages.success(request, "Il n'y a pas de doublon.")
                else:
                    fournisseur_list = info_trouves
                    messages.warning(request, "Il existe plusieurs informations relatives.")
            else:
                messages.info(request, "Aucun fournisseur trouvé pour cette recherche.")  
        return form, affiche_form, fournisseur_list

##
# Fonctions permettant de gérer une grande quantité de produits
##
class ProduitService:

    @staticmethod
    def cherche_form(request):
        """ Recherche d'informations en tapant un mot."""
        cherche_form = ChercheProduitForm(request.POST)
        form = None
        affiche_form = None
        produit_list=None

        if cherche_form.is_valid():
            search_query = cherche_form.cleaned_data['produit_search']
            info_trouves = Produit.objects.filter(nom__icontains=search_query)
            if info_trouves.exists():
                if info_trouves.count() == 1:
                    produit = info_trouves.first()
                    affiche_form = EditProduitForm(instance=produit)
                    messages.success(request, "Il n'y a pas de doublon.")
                else:
                    produit_list = info_trouves
                    messages.warning(request, "Il existe plusieurs informations relatives.")
            else:
                messages.info(request, "Aucun produit trouvé pour cette recherche.")  
        return form, affiche_form, produit_list

##
#API permettant de récupérer le prix unitaire (utilise une urls.py)
##
from django.http import JsonResponse
from .models import Produit

def get_prix_unitaire(request):
    produit_id = request.GET.get('produit_id')
    if produit_id:
        try:
            produit = Produit.objects.get(id_produit=produit_id)
            return JsonResponse({'prix_unitaire': str(produit.prix_unitaire)})
        except Produit.DoesNotExist:
            return JsonResponse({'error': 'Produit non trouvé'}, status=404)
    return JsonResponse({'error': 'ID produit non fourni'}, status=400)

##
#Permet de récupérer dans custom.js la remise car c'est une foreignkey (utilise une urls.py).
##
def get_taux_remise(request):
    remise_id = request.GET.get('remise_id') 
    try:
        remise = Remise.objects.get(id_remise=remise_id)
        return JsonResponse({'taux': remise.taux})
    except Remise.DoesNotExist:
        return JsonResponse({'error': 'Remise non trouvée'}, status=404)

##
#Permet de récupérer dans custom.js la tva car c'est une foreignkey (utilise une urls.py).
##
def get_taux_tva(request):
    tva_id = request.GET.get('tva_id')  
    try:
        tva = Tva.objects.get(id_tva=tva_id)
        return JsonResponse({'taux': tva.taux})
    except Tva.DoesNotExist:
        return JsonResponse({'error': 'Tva non trouvée'}, status=404)

##
#Permet de supprimer les commandes sans lignes de commande et bon de livraison (qui sont vides).
##
def supprimer_commandes_sans_lignes():
    commandes_sans_lignes = Commande.objects.annotate(nb_lignes=Count('lignecommande')).filter(nb_lignes=0)
    commandes_sans_lignes.delete()
    commandes_sans_lignes = Achat.objects.annotate(nb_lignes=Count('ligneachat')).filter(nb_lignes=0)
    commandes_sans_lignes.delete()
    commandes_sans_lignes = BonLivraison.objects.annotate(nb_lignes=Count('lignebonlivraison')).filter(nb_lignes=0)
    commandes_sans_lignes.delete()

##
#Permet de supprimer les factures et écritures sans lignes de facture (qui sont vides).
##
def supprimer_factures_sans_lignes():
    factures_sans_lignes = FactureVente.objects.annotate(nb_lignes=Count('lignefacturevente')).filter(nb_lignes=0)
    factures_sans_lignes.delete()
    factures_sans_lignes = FactureAchat.objects.annotate(nb_lignes=Count('lignefactureachat')).filter(nb_lignes=0)
    factures_sans_lignes.delete()
    ecritures_sans_lignes = EcritureComptable.objects.annotate(nb_lignes=Count('ligneecriturecomptable')).filter(nb_lignes=0)
    ecritures_sans_lignes.delete()


