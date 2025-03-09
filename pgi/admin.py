from django.contrib import admin

from .models import Client, Fournisseur, Produit, Commande, LigneCommande, FactureVente, LigneFactureVente, BonLivraison, LigneBonLivraison, Achat, LigneAchat, FactureAchat, LigneFactureAchat, PlanComptable 

admin.site.register(Client)
admin.site.register(Fournisseur)
admin.site.register(Produit)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(FactureVente)
admin.site.register(LigneFactureVente)
admin.site.register(BonLivraison)
admin.site.register(LigneBonLivraison)
admin.site.register(Achat)
admin.site.register(LigneAchat)
admin.site.register(FactureAchat)
admin.site.register(LigneFactureAchat)
admin.site.register(PlanComptable)
