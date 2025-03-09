from django.db import models

# Modèle pour les Clients
class Client(models.Model):
    id_client = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    plan_comptable = models.ForeignKey('PlanComptable', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nom


# Modèle pour les Fournisseurs
class Fournisseur(models.Model):
    id_fournisseur = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    plan_comptable = models.ForeignKey('PlanComptable', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nom

# Modèle de liste des taux de TVA
class Tva(models.Model):
    id_tva = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    taux = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.nom} ({self.taux}%)"

# Modèle pour les Produits
class Produit(models.Model):
    MARCHANDISES = 'Marchandises'
    CONSOMMABLES = 'Consommables'
    IMMOBILISATIONS = 'Immobilisations'

    TYPE_STOCK_CHOICES = [
        (MARCHANDISES, 'Marchandises'),
        (CONSOMMABLES, 'Consommables'),
        (IMMOBILISATIONS, 'Immobilisations'),
    ]

    id_produit = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    tva = models.ForeignKey(Tva, to_field='id_tva', on_delete=models.CASCADE, null=True)
    type_stock = models.CharField(max_length=50, null=True, blank=True, choices=TYPE_STOCK_CHOICES)

    def __str__(self):
        return self.nom

# Modèle pour les commandes
class Commande(models.Model):
    id_commande = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, to_field='id_client', on_delete=models.CASCADE)
    date_commande = models.DateField()
    statut = models.CharField(max_length=50, null=True)
    facture = models.ForeignKey('FactureVente', to_field='id_facture_vente', on_delete=models.SET_NULL, null=True, blank=True, related_name='commande_facture')  # related_name ici
    
    def __str__(self):
        return f"Ref : {self.id_commande} pour {self.client.nom}"

# Modèle pour les Lignes de Commande
class LigneCommande(models.Model):
    id_ligne_commande = models.AutoField(primary_key=True)
    commande = models.ForeignKey(Commande, to_field='id_commande', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, to_field='id_produit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.ForeignKey('Remise', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} pour Commande {self.commande.id_commande}"

# Modèle pour les Factures de vente
class FactureVente(models.Model):
    id_facture_vente = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, to_field='id_client', on_delete=models.CASCADE, null=True, blank=True)
    commande = models.ForeignKey('Commande', to_field='id_commande', on_delete=models.CASCADE, null=True, blank=True, related_name='facture_commande')  # related_name ici
    statut = models.CharField(max_length=50, null=True)
    date_facture = models.DateField()
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Facture {self.id_facture_vente} pour {self.client.nom}"


# Modèle pour les Lignes de Facture de vente
class LigneFactureVente(models.Model):
    id_ligne_facture_vente = models.AutoField(primary_key=True)
    facture_vente = models.ForeignKey(FactureVente, to_field='id_facture_vente', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, to_field='id_produit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.ForeignKey('Remise', on_delete=models.SET_NULL, null=True, blank=True)
    tva = models.ForeignKey('Tva', on_delete=models.SET_NULL, null=True, blank=True)
    montant_ligne = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} pour Facture {self.facture_vente.id_facture_vente}"

# Modèle pour les Bons de Livraison
class BonLivraison(models.Model):
    id_bon_livraison = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, to_field='id_client', on_delete=models.CASCADE, null=True, blank=True)
    commande = models.ForeignKey(Commande, to_field='id_commande', on_delete=models.CASCADE, null=True, blank=True)
    date_livraison = models.DateField()
    adresse_livraison = models.CharField(max_length=255)
    statut = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"Bon de Livraison {self.id_bon_livraison} pour Client {self.client.nom}"

# Modèle pour les Lignes de Bon de Livraison
class LigneBonLivraison(models.Model):
    id_ligne_bon_livraison = models.AutoField(primary_key=True)
    bon_livraison = models.ForeignKey(BonLivraison, to_field='id_bon_livraison', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, to_field='id_produit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} pour Bon de Livraison {self.bon_livraison.id_bon_livraison}"

# Modèle pour les Achats
class Achat(models.Model):
    id_achat = models.AutoField(primary_key=True)
    fournisseur = models.ForeignKey(Fournisseur, to_field='id_fournisseur', on_delete=models.CASCADE)
    facture = models.ForeignKey('FactureAchat', to_field='id_facture_achat', on_delete=models.SET_NULL, null=True, blank=True, related_name='achat_facture')  
    date_achat = models.DateField()
    statut = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"Ref : {self.id_achat} de {self.fournisseur.nom}"

# Modèle pour les Lignes d'Achat
class LigneAchat(models.Model):
    id_ligne_achat = models.AutoField(primary_key=True)
    achat = models.ForeignKey(Achat, to_field='id_achat', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, to_field='id_produit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.ForeignKey('Remise', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} pour Achat {self.achat.id_achat}"

# Modèle pour les Factures d'Achat
class FactureAchat(models.Model):
    id_facture_achat = models.AutoField(primary_key=True)
    fournisseur = models.ForeignKey(Fournisseur, to_field='id_fournisseur', on_delete=models.CASCADE, null=True, blank=True)
    achat = models.ForeignKey(Achat, to_field='id_achat', on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, null=True)
    date_facture = models.DateField()
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        if self.achat:
            return f"Facture Achat {self.id_facture_achat} de {self.fournisseur.nom}"
        else:
            return f"Facture Achat {self.id_facture_achat} (sans commande)"

# Modèle pour les Lignes de Facture d'Achat
class LigneFactureAchat(models.Model):
    id_ligne_facture_achat = models.AutoField(primary_key=True)
    facture_achat = models.ForeignKey(FactureAchat, to_field='id_facture_achat', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, to_field='id_produit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.ForeignKey('Remise', on_delete=models.SET_NULL, null=True, blank=True)
    tva = models.ForeignKey('Tva', on_delete=models.SET_NULL, null=True, blank=True)
    montant_ligne = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} pour Facture Achat {self.facture_achat.id_facture_achat}"

# Modèle pour l'identité de l'entreprise du PGI
class Identite(models.Model):
    id_identite = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    siret = models.CharField(max_length=14)
    num_tva = models.CharField(max_length=11)
    periode = models.IntegerField(null=True, blank=True)
    stock_securite = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nom

# Modèle de liste des remise, rabais, escompte et ristourne
class Remise(models.Model):
    id_remise = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    taux = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.nom} ({self.taux}%)"

# Modèle de plan comptable
class PlanComptable(models.Model):
    id_plan_comptable = models.AutoField(primary_key=True)
    numero = models.IntegerField()
    nom = models.CharField(max_length=50)
    periode = models.ForeignKey(Identite,on_delete=models.CASCADE, null=True, blank=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    @property
    def periode_valeur(self):
        return self.periode.periode if self.periode else ''

    def __str__(self):
        return f"{self.numero} ({self.nom})"

# Modèle des écritures comptables 
class EcritureComptable(models.Model):
    id_ecriture_comptable = models.AutoField(primary_key=True)
    date_ecriture_comptable = models.DateField()
    statut = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"Ecriture n° {self.id_ecriture_comptable} ({self.date_ecriture_comptable})"

# Modèle des lignes des écritures comptables
class LigneEcritureComptable(models.Model):
    id_ligne_ecriture_comptable = models.AutoField(primary_key=True)
    ecriture_comptable = models.ForeignKey(EcritureComptable, to_field='id_ecriture_comptable', on_delete=models.CASCADE)
    plan_comptable = models.ForeignKey(PlanComptable, to_field='id_plan_comptable', on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Ecriture n°{self.ecriture_comptable.id_ecriture_comptable} ({self.plan_comptable.numero})"

