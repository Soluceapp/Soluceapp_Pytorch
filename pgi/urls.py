from django.urls import path,include
from . import views
from .services import get_prix_unitaire, get_taux_remise, get_taux_tva

app_name="pgi"

urlpatterns = [
    path('pgi/',views.home_pgi,name="home_pgi"),
    path('pgi/detail_achat/',views.detail_achat_pgi,name="detail_achat_pgi"),
    path('pgi/vente/',views.vente_pgi,name="vente_pgi"),
    path('pgi/comptabilité',views.compta_pgi,name="compta_pgi"),
    path('pgi/admin/',views.param_pgi,name="param_pgi"),
    path('pgi/creation_bon_commande/',views.bon_commande_pgi_create,name="bon_commande_pgi_create"),
    path('pgi/bon_commande/',views.bon_commande_pgi,name="bon_commande_pgi"),
    path('pgi/creation_facture_vente/',views.facture_vente_pgi_create,name="facture_vente_pgi_create"),
    path('pgi/facture_vente/',views.facture_vente_pgi,name="facture_vente_pgi"),
    path('pgi/creation_bon_livraison/',views.bon_livraison_pgi_create,name="bon_livraison_pgi_create"),
    path('pgi/bon_livraison/',views.bon_livraison_pgi,name="bon_livraison_pgi"),
    path('pgi/bon_achat/',views.achat_pgi,name="bon_achat_pgi"),
    path('pgi/creation_bon_achat/',views.bon_achat_pgi_create,name="bon_achat_pgi_create"),
    path('pgi/creation_facture_achat/',views.facture_achat_pgi_create,name="facture_achat_pgi_create"),
    path('pgi/facture_achat/',views.facture_achat_pgi,name="facture_achat_pgi"),
    path('pgi/client/', views.client_pgi, name='client_pgi'),
    path('pgi/produit/',views.gestion_stock_pgi,name="gestion_stock_pgi"),
    path('pgi/stock/',views.produit_pgi,name="produit_pgi"),
    path('pgi/fournisseur/',views.fournisseur_pgi,name="fournisseur_pgi"),
    path('pgi/compte_résultat/',views.compte_resultat_pgi,name="compte_resultat_pgi"),
    path('pgi/grand_livre/',views.grand_livre_pgi,name="grand_livre_pgi"),
    path('pgi/bilan/',views.bilan_pgi,name="bilan_pgi"),
    path('pgi/identite/',views.identite_pgi,name="identite_pgi"),
    path('pgi/periode/',views.periode_pgi,name="periode_pgi"),
    path('pgi/stock_securite/',views.stock_securite_pgi,name="stock_securite_pgi"),
    path('pgi/tva/',views.tva_pgi,name="tva_pgi"),
    path('pgi/remise/',views.remise_pgi,name="remise_pgi"),
    path('pgi/plan_comptable/',views.plan_comptable_pgi,name="plan_comptable_pgi"),
    path('pgi/ecriture_comptable/',views.ecriture_comptable_pgi,name="ecriture_comptable_pgi"),
    path('pgi/ecriture_comptable_creation/',views.ecriture_comptable_pgi_create,name="ecriture_comptable_pgi_create"),
    path('api/get_prix_unitaire/', get_prix_unitaire, name='get_prix_unitaire'), # utilise un service.py
    path('api/get_taux_remise/', get_taux_remise, name='get_taux_remise'),
    path('api/get_taux_tva/', get_taux_tva, name='get_taux_tva'),
]