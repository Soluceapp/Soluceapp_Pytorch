from django import forms
from .models import *
from django.forms import inlineformset_factory
from django.forms import modelformset_factory

##
# Clients
##

class SelectClientForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all().order_by('nom'),label="")

class ChercheClientForm(forms.Form):
    client_search = forms.CharField(
        label="Recherche doublon de client ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le nom du client...', 'id': 'client-search-input'}))

class CreateClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['id_client','nom', 'adresse', 'telephone', 'email']  
        labels = {
            'nom': 'Nom  ',
            'adresse': 'Adresse ',
            'telephone': 'Téléphone ',
            'email': 'Email ', 
        }
    def reset(self):
            self.initial = None

class EditClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['id_client','nom', 'adresse', 'telephone', 'email']

##
# Fournisseurs
##
class SelectFournisseurForm(forms.Form):
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all().order_by('nom'),label="")

class ChercheFournisseurForm(forms.Form):
    fournisseur_search = forms.CharField(
        label="Recherche doublon de fournisseurs ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le nom du fournisseur...', 'id': 'fournisseur-search-input'}))

class CreateFournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'adresse', 'telephone', 'email'] 
        labels = {'nom':' '}
        labels = {'adresse':' '}
        labels = {'telephone':' '}
        labels = {'email':' email'}

    def reset(self):
            self.initial = None

class EditFournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['id_fournisseur','nom', 'adresse', 'telephone', 'email']

##
# Produits
##
class SelectProduitForm(forms.Form):
    produit = forms.ModelChoiceField(queryset=Produit.objects.all().order_by('id_produit'),label="Trie par référence")

class ChercheProduitForm(forms.Form):
    produit_search = forms.CharField(
        label="Recherche doublon de produits ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le nom du produit...', 'id': 'produit-search-input'}))

class CreateProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'description', 'prix_unitaire', 'stock','tva','type_stock'] 
        labels = {'tva':'Taux de TVA ','stock':'Montant du stock ','prix_unitaire':'Prix unitaire ',
        'description':'Description du produit ','nom':'Nom du produit ','type_stock':'Type de stock '}

    def reset(self):
            self.initial = None

class EditProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['id_produit','nom', 'description', 'prix_unitaire', 'stock','tva','type_stock']
        labels = {'tva':'Taux de TVA ','stock':'Montant du stock ','prix_unitaire':'Prix unitaire ',
        'description':'Description du produit ','nom':'Nom du produit ','type_stock':'Type de stock '}

class ChoixTypeStockForm(forms.Form):
    TYPE_STOCK_CHOICES = [
        ('Immobilisations', 'Immobilisations'),
        ('Marchandises', 'Marchandises'),
        ('Consommables', 'Consommables'),
        
    ]
    type_stock = forms.ChoiceField(
        choices=TYPE_STOCK_CHOICES, 
        required=True, 
        label="Choisir le type de stock à analyser",
        #widget=forms.Select(attrs={'class': 'form-control'})  # Ajout d'un style pour plus de lisibilité
    )

# Identité de l'entreprise et periode
##
class ChangeIdentiteForm(forms.ModelForm):
    class Meta:
        model = Identite
        fields = ['nom', 'adresse', 'telephone', 'email', 'siret', 'num_tva']
        labels = {
            'nom': 'Dénomination sociale ',
            'adresse': 'Adresse de l\'entreprise ',
            'telephone': 'Téléphone ',
            'email': 'Email ',
            'siret': 'Numéro RCS ',
            'num_tva': 'Numéro de TVA intracommunautaire ',
        }
class ChangePeriodeForm(forms.ModelForm):
    class Meta:
        model = Identite
        fields = ['periode']
        labels = {
            'periode': 'Période comptable '
       }
class ChangeStockSecuriteForm(forms.ModelForm):
    class Meta:
        model = Identite
        fields = ['stock_securite']
        labels = {
            'stock_securite': 'stock de sécurite '
       }

##
# Commandes de vente (bond de commande)
##
class SelectCommandeForm(forms.Form):
    commande = forms.ModelChoiceField(queryset=Commande.objects.all().order_by('-id_commande'),label="")

# Utilisé lors de la création du haut de commande
class CommandeForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un client",
        label="Client",)
    statut = forms.CharField(
        required=False,  # rendre le champ non requis
        widget=forms.TextInput(attrs={'placeholder': ''}),  # facultatif, pour un indice visuel
        label="Conditions",)
    class Meta:
        model = Commande
        fields = ['client', 'date_commande', 'statut']
        labels = {'statut': 'Conditions'}
    date_commande = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),
        input_formats=['%d-%m-%Y','%d/%m/%Y'],
        label='Date (JJ-MM-AAAA ou JJ/MM/AAAA)',
        error_messages={
            'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
            'required': "Veuillez indiquer une date de commande.",})
    def clean_date_commande(self):
        date_commande = self.cleaned_data.get('date_commande')
        return date_commande

# Utilisé à la création pour les lignes de commande
class LigneCommandeFormC(forms.ModelForm):
    class Meta:
        model = LigneCommande
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prix_unitaire'].required = False
        # Ne marche pas avec Javascript (utilisation d'une case hidden)
        self.fields['remise'] = forms.ModelChoiceField(
            queryset=Remise.objects.all().order_by('nom'), 
            empty_label="Sélectionnez une remise",  
            label="Taux de remise")
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite

# Utilisé lors de la modification partielle du haut de commande
class EditCommandeForm(forms.ModelForm): 
    class Meta:
        model = Commande
        fields = ['id_commande', 'client', 'date_commande', 'statut']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].disabled = False
        self.fields['statut'].required = False
    date_commande = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),  
        input_formats=['%d-%m-%Y','%d/%m/%Y'], 
        label='Date (JJ-MM-AAAA)',
        error_messages={'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
        'required': "Veuillez indiquer une date de commande.",})
    client = forms.ModelChoiceField(
        queryset=Client.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un client",
        label="Client",)

# Utilisé lors de la modification partielle des lignes de commandes
class LigneCommandeForm(forms.ModelForm):
    class Meta:
        model = LigneCommande
        fields = ['id_ligne_commande', 'produit', 'quantite', 'prix_unitaire', 'remise']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remise'].queryset = Remise.objects.all().order_by('nom')
        # On rend le champ prix_unitaire disabled mais pas nécessairement obligatoire
        self.fields['prix_unitaire'].disabled = True
        self.fields['prix_unitaire'].required = False
        # Remplir automatiquement le prix_unitaire en fonction du produit
        if self.instance and self.instance.produit:
            self.fields['prix_unitaire'].initial = self.instance.produit.prix_unitaire
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all().order_by('nom'),
        widget=forms.Select,
        label="Produit",)

# Utilisé lors de la recherche par id        
class ChercheCommandeForm(forms.Form): 
    commande_search = forms.IntegerField(
        label="Recherche par numéro de commande ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le numéro de commande...', 'id': 'commande-search-input'}))

##
# Facture de vente
##

class SelectFactureVenteForm(forms.Form):
    facture_vente = forms.ModelChoiceField(queryset=FactureVente.objects.all().order_by('-id_facture_vente'),label="")

# Utilisé lors de la création du haut de la facture de vente
class FactureVenteForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un client",
        label="Client",)
    commande = forms.ModelChoiceField(
        queryset=Commande.objects.all().order_by('-id_commande'),
        required=False,
        widget=forms.Select,
        label="Commande",)
    statut = forms.CharField(
        required=False,  # rendre le champ non requis
        widget=forms.TextInput(attrs={'placeholder': ''}),  # facultatif, pour un indice visuel
        label="Conditions",)
    class Meta:
        model = FactureVente
        fields = ['client', 'commande', 'statut', 'date_facture', 'montant_total']
        labels = {'statut': 'Conditions'}
    date_facture = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),
        input_formats=['%d-%m-%Y','%d/%m/%Y'],
        label='Date (JJ-MM-AAAA ou JJ/MM/AAAA)',
        error_messages={
            'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
            'required': "Veuillez indiquer une date de facture.",})
    def clean_date_facture(self):
        date_facture = self.cleaned_data.get('date_facture')
        return date_facture
    

# Utilisé à la création pour les lignes de facture de vente
class LigneFactureVenteFormC(forms.ModelForm):
    class Meta:
        model = LigneFactureVente
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise', 'tva', 'montant_ligne']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prix_unitaire'].required = False
        # Ne marche pas avec Javascript (utilisation d'une case hidden)
        self.fields['remise'] = forms.ModelChoiceField(
            queryset=Remise.objects.all().order_by('nom'), 
            #empty_label="Sélectionnez une remise",  
            label="Taux de remise")
        self.fields['tva'] = forms.ModelChoiceField(
            queryset=Tva.objects.all().order_by('nom'),
            label="Taux de tva")
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite

# Utilisé lors de la modification partielle du haut de facture de vente
class EditFactureVenteForm(forms.ModelForm): 
    class Meta:
        model = FactureVente
        fields = ['id_facture_vente', 'client', 'commande', 'statut', 'date_facture', 'montant_total']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].disabled = False
        self.fields['statut'].required = False
    date_facture = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),  
        input_formats=['%d-%m-%Y','%d/%m/%Y'], 
        label='Date (JJ-MM-AAAA)',
        error_messages={'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
        'required': "Veuillez indiquer une date de facture.",})

# Utilisé lors de la modification partielle des lignes de facture de vente
class LigneFactureVenteForm(forms.ModelForm):
    class Meta:
        model = LigneFactureVente
        fields = ['id_ligne_facture_vente', 'produit', 'quantite', 'prix_unitaire', 'remise', 'tva', 'montant_ligne']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remise'].queryset = Remise.objects.all()
        self.fields['tva'].queryset = Tva.objects.all()
        # On rend le champ prix_unitaire disabled mais pas nécessairement obligatoire
        self.fields['prix_unitaire'].disabled = True
        self.fields['prix_unitaire'].required = False
        # Remplir automatiquement le prix_unitaire en fonction du produit
        if self.instance and self.instance.produit:
            self.fields['prix_unitaire'].initial = self.instance.produit.prix_unitaire
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite

# Utilisé lors de la recherche par id        
class ChercheFactureVenteForm(forms.Form): 
    facture_vente_search = forms.IntegerField(
        label="Recherche par numéro de facture de vente ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le numéro de la facture...', 'id': 'facture-search-input'}))

##
# Bon de livraison après vente
##
class SelectLivraisonForm(forms.Form):
    livraison = forms.ModelChoiceField(queryset=BonLivraison.objects.all().order_by('-id_bon_livraison'),label="")

# Utilisé lors de la création du haut de commande
class LivraisonForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un client",
        label="Client",)
    commande = forms.ModelChoiceField(
        queryset=Commande.objects.all().order_by('-id_commande'),
        required=False,
        widget=forms.Select,
        label="Commande",)
    statut = forms.CharField(
        required=False,  
        widget=forms.TextInput(attrs={'placeholder': ''}),  
        label="Conditions",)
    adresse_livraison = forms.CharField(
        required=False,  
        widget=forms.TextInput(attrs={
            'placeholder': ''
        }),
        label="Adresse_livraison",),
    class Meta:
        model = BonLivraison
        fields = ['client', 'commande', 'date_livraison', 'statut','adresse_livraison']
        labels = {'statut': 'Conditions'}
    date_livraison = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),
        input_formats=['%d-%m-%Y','%d/%m/%Y'],
        label='Date (JJ-MM-AAAA ou JJ/MM/AAAA)',
        error_messages={
            'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
            'required': "Veuillez indiquer une date de livraison.",})
    def clean_date_livraison(self):
        date_livraison = self.cleaned_data.get('date_livraison')
        return date_livraison

# Utilisé à la création pour les lignes de livraison
class LigneLivraisonFormC(forms.ModelForm):
    class Meta:
        model = LigneBonLivraison
        fields = ['produit', 'quantite', 'prix_unitaire']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prix_unitaire'].required = False
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite

# Utilisé lors de la modification partielle du haut de livraison
class EditLivraisonForm(forms.ModelForm): 
    class Meta:
        model = BonLivraison
        fields = ['id_bon_livraison', 'client', 'commande', 'date_livraison', 'statut','adresse_livraison']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].disabled = False
        self.fields['adresse_livraison'].required = False
        self.fields['statut'].required = False
    date_livraison = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),  
        input_formats=['%d-%m-%Y','%d/%m/%Y'], 
        label='Date (JJ-MM-AAAA)',
        error_messages={'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
        'required': "Veuillez indiquer une date de livraison.",})
    client = forms.ModelChoiceField(
        queryset=Client.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un client",
        label="Client",)
    commande = forms.ModelChoiceField(
        queryset=Commande.objects.all().order_by('-id_commande'),
        required=False,
        widget=forms.Select,
        label="Commande",)

# Utilisé lors de la modification partielle des lignes de livraison
class LigneLivraisonForm(forms.ModelForm):
    class Meta:
        model = LigneBonLivraison
        fields = ['id_ligne_bon_livraison','produit', 'quantite', 'prix_unitaire']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On rend le champ prix_unitaire disabled mais pas nécessairement obligatoire
        self.fields['prix_unitaire'].disabled = True
        self.fields['prix_unitaire'].required = False
        
        # Remplir automatiquement le prix_unitaire en fonction du produit, si le produit est présent
        if self.instance and hasattr(self.instance, 'produit') and self.instance.produit:
            self.fields['prix_unitaire'].initial = self.instance.produit.prix_unitaire

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite


# Utilisé lors de la recherche par id        
class ChercheLivraisonForm(forms.Form): 
    livraison_search = forms.IntegerField(
        label="Recherche par numéro de livraison ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le numéro de livraison...', 'id': 'livraison-search-input'}))

##
# Commandes d'achat (bond d'achat)
##
class SelectAchatForm(forms.Form):
    achat = forms.ModelChoiceField(queryset=Achat.objects.all().order_by('-id_achat'),label="")

# Utilisé lors de la création du haut de commande d'achat
class AchatForm(forms.ModelForm):
    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un fournisseur",
        label="Fournisseur",)
    statut = forms.CharField(
        required=False,  # rendre le champ non requis
        widget=forms.TextInput(attrs={'placeholder': ''}),  # facultatif, pour un indice visuel
        label="Conditions",)
    class Meta:
        model = Achat
        fields = ['fournisseur', 'date_achat', 'statut']
        labels = {'statut': 'Conditions'}
    date_achat = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),
        input_formats=['%d-%m-%Y','%d/%m/%Y'],
        label='Date (JJ-MM-AAAA ou JJ/MM/AAAA)',
        error_messages={
            'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
            'required': "Veuillez indiquer une date de commande.",})
    def clean_date_achat(self):
        date_achat = self.cleaned_data.get('date_achat')
        return date_achat

# Utilisé à la création pour les lignes de commande
class LigneAchatFormC(forms.ModelForm):
    class Meta:
        model = LigneAchat
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prix_unitaire'].required = False
        # Ne marche pas avec Javascript (utilisation d'une case hidden)
        self.fields['remise'] = forms.ModelChoiceField(
            queryset=Remise.objects.all().order_by('nom'), 
            empty_label="Sélectionnez une remise",  
            label="Taux de remise")
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite

# Utilisé lors de la modification partielle du haut de commande
class EditAchatForm(forms.ModelForm): 
    class Meta:
        model = Achat
        fields = ['id_achat', 'fournisseur', 'date_achat', 'statut']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fournisseur'].disabled = False
        self.fields['statut'].required = False
    date_achat = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),  
        input_formats=['%d-%m-%Y','%d/%m/%Y'], 
        label='Date (JJ-MM-AAAA)',
        error_messages={'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
        'required': "Veuillez indiquer une date de commande.",})
    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un fournisseur",
        label="Fournisseur",)

# Utilisé lors de la modification partielle des lignes de commandes d'achat
class LigneAchatForm(forms.ModelForm):
    class Meta:
        model = LigneAchat
        fields = ['id_ligne_achat', 'produit', 'quantite', 'prix_unitaire', 'remise']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remise'].queryset = Remise.objects.all().order_by('nom')
        # On rend le champ prix_unitaire disabled mais pas nécessairement obligatoire
        self.fields['prix_unitaire'].disabled = True
        self.fields['prix_unitaire'].required = False
        # Remplir automatiquement le prix_unitaire en fonction du produit
        if self.instance and self.instance.produit:
            self.fields['prix_unitaire'].initial = self.instance.produit.prix_unitaire
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all().order_by('nom'),
        widget=forms.Select,
        label="Produit",)

# Utilisé lors de la recherche par id        
class ChercheAchatForm(forms.Form): 
    achat_search = forms.IntegerField(
        label="Recherche par numéro d'achat ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le numéro de commande...', 'id': 'commande-search-input'}))

##
# Facture d'achat
##

class SelectFactureAchatForm(forms.Form):
    facture_achat = forms.ModelChoiceField(queryset=FactureAchat.objects.all().order_by('-id_facture_achat'),label="")

# Utilisé lors de la création du haut de la facture d'achat
class FactureAchatForm(forms.ModelForm):
    class Meta:
        model = FactureAchat
        fields = ['fournisseur', 'achat', 'statut', 'date_facture', 'montant_total']
        labels = {'statut': 'Conditions'}
    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.all().order_by('nom'),
        widget=forms.Select,
        empty_label="Sélectionnez un fournisseur",
        label="Fournisseur",)
    achat = forms.ModelChoiceField(
        queryset=Achat.objects.all().order_by('-id_achat'),
        widget=forms.Select,
        label="Achat",)
    statut = forms.CharField(
        required=False,  
        widget=forms.TextInput(attrs={'placeholder': ''}),  # facultatif, pour un indice visuel
        label="Conditions",)
    date_facture = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),
        input_formats=['%d-%m-%Y','%d/%m/%Y'],
        label='Date (JJ-MM-AAAA ou JJ/MM/AAAA)',
        error_messages={
            'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
            'required': "Veuillez indiquer une date de facture.",})
    def clean_date_facture(self):
        date_facture = self.cleaned_data.get('date_facture')
        return date_facture

# Utilisé à la création pour les lignes de facture d'achat'
class LigneFactureAchatFormC(forms.ModelForm):
    class Meta:
        model = LigneFactureAchat
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise', 'tva', 'montant_ligne']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prix_unitaire'].required = False
        # Ne marche pas avec Javascript (utilisation d'une case hidden)
        self.fields['remise'] = forms.ModelChoiceField(
            queryset=Remise.objects.all().order_by('nom'), 
            #empty_label="Sélectionnez une remise",  
            label="Taux de remise")
        self.fields['tva'] = forms.ModelChoiceField(
            queryset=Tva.objects.all().order_by('nom'),
            label="Taux de tva")
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite

# Utilisé lors de la modification partielle du haut de facture de vente
class EditFactureAchatForm(forms.ModelForm): 
    class Meta:
        model = FactureAchat
        fields = ['id_facture_achat', 'fournisseur', 'achat', 'statut', 'date_facture', 'montant_total']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fournisseur'].disabled = False
        self.fields['statut'].required = False
    date_facture = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),  
        input_formats=['%d-%m-%Y','%d/%m/%Y'], 
        label='Date (JJ-MM-AAAA)',
        error_messages={'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
        'required': "Veuillez indiquer une date de facture.",})

# Utilisé lors de la modification partielle des lignes de facture de vente
class LigneFactureAchatForm(forms.ModelForm):
    class Meta:
        model = LigneFactureAchat
        fields = ['id_ligne_facture_achat', 'produit', 'quantite', 'prix_unitaire', 'remise', 'tva', 'montant_ligne']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remise'].queryset = Remise.objects.all()
        self.fields['tva'].queryset = Tva.objects.all()
        # On rend le champ prix_unitaire disabled mais pas nécessairement obligatoire
        self.fields['prix_unitaire'].disabled = True
        self.fields['prix_unitaire'].required = False
        # Remplir automatiquement le prix_unitaire en fonction du produit
        if self.instance and self.instance.produit:
            self.fields['prix_unitaire'].initial = self.instance.produit.prix_unitaire
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité ne peut pas être négative ou nulle.")
        return quantite

# Utilisé lors de la recherche par id        
class ChercheFactureAchatForm(forms.Form): 
    facture_achat_search = forms.IntegerField(
        label="Recherche par numéro de facture d'achat ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le numéro de la facture...', 'id': 'facture-search-input'}))

##
# TVA
##

class SelectTvaForm(forms.Form):
    tva = forms.ModelChoiceField(queryset=Tva.objects.all().order_by('nom'),label="")

class CreateTvaForm(forms.ModelForm):
    class Meta:
        model = Tva
        fields = ['nom', 'taux'] 
        labels = {'nom':'Désignation du taux '}
        labels = {'taux':'Taux (en %) '}

    def reset(self):
            self.initial = None

class EditTvaForm(forms.ModelForm):
    taux = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )    
    class Meta:
        model = Tva
        fields = ['id_tva','nom', 'taux']

##
# Remises, rabais, escompte et ristournes
##

class SelectRemiseForm(forms.Form):
    remise = forms.ModelChoiceField(queryset=Remise.objects.all().order_by('-id_remise'),label="")

class CreateRemiseForm(forms.ModelForm):
    class Meta:
        model = Remise
        fields = ['nom', 'taux'] 
        labels = {'nom':'Nom de la réduction '}
        labels = {'taux':'Taux (un nombre) '}

    def reset(self):
            self.initial = None

class EditRemiseForm(forms.ModelForm):
    taux = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = Remise
        fields = ['id_remise', 'nom', 'taux']

##
# Plan comptable
##

class SelectPlanComptableForm(forms.Form):
    plan_comptable = forms.ModelChoiceField(queryset=PlanComptable.objects.all().order_by('numero'),label="")

class CreatePlanComptableForm(forms.ModelForm):
    class Meta:
        model = PlanComptable
        fields = ['numero', 'nom', 'debit', 'credit', 'periode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le champ 'periode' caché
        self.fields['periode'].widget = forms.HiddenInput()

        # Récupérer la première instance Identite
        identite = Identite.objects.first()

        # Assigner l'ID de l'Identite comme valeur initiale pour le champ 'periode'
        if identite:
            self.fields['periode'].initial = identite.id_identite

class EditPlanComptableForm(forms.ModelForm):
    class Meta:
        model = PlanComptable
        fields = ['id_plan_comptable','numero', 'nom']

##
# Ecriture comptable 
##

class SelectEcritureComptableForm(forms.Form):
    ecriture_comptable = forms.ModelChoiceField(queryset=EcritureComptable.objects.all().order_by('-id_ecriture_comptable'),label="")

# Utilisé lors de la création du haut de l'écriture comptable
class EcritureComptableForm(forms.ModelForm):
    class Meta:
        model = EcritureComptable
        fields = ['date_ecriture_comptable', 'statut']
        labels = {'statut': 'Conditions '}
    statut = forms.CharField(
        required=False,  
        widget=forms.TextInput(attrs={'placeholder': ''}),  # facultatif, pour un indice visuel
        label="Conditions",)
    date_ecriture_comptable = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),
        input_formats=['%d-%m-%Y','%d/%m/%Y'],
        label='Date (JJ-MM-AAAA ou JJ/MM/AAAA)',
        error_messages={
            'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
            'required': "Veuillez indiquer une date de l'écriture comptable.",})
    def clean_date_ecriture_comptable(self):
        date_ecriture_comptable = self.cleaned_data.get('date_ecriture_comptable')
        return date_ecriture_comptable

# Utilisé à la création pour les lignes de l'écriture comptable
class LigneEcritureComptableFormC(forms.ModelForm):
    class Meta:
        model = LigneEcritureComptable
        fields = ['plan_comptable', 'debit', 'credit']
    def clean_quantite(self):
        debit = self.cleaned_data.get('debit')
        credit = self.cleaned_data.get('credit')
        if valeur is None or valeur < 0:
            raise forms.ValidationError("La valeur ne peut pas être négative.")
        return valeur

# Utilisé lors de la modification partielle du haut de l'écriture comptable
class EditEcritureComptableForm(forms.ModelForm): 
    class Meta:
        model = EcritureComptable
        fields = ['id_ecriture_comptable', 'date_ecriture_comptable', 'statut']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['statut'].required = False
    date_ecriture_comptable = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y'),  
        input_formats=['%d-%m-%Y','%d/%m/%Y'], 
        label='Date (JJ-MM-AAAA)',
        error_messages={'invalid': "La date doit être au format JJ-MM-AAAA ou JJ/MM/AAAA.",
        'required': "Veuillez indiquer une date de facture.",})

# Utilisé lors de la modification partielle des lignes de l'écriture comptable
class LigneEcritureComptableForm(forms.ModelForm):
    class Meta:
        model = LigneEcritureComptable
        fields = ['id_ligne_ecriture_comptable', 'plan_comptable', 'debit', 'credit']
    def clean_quantite(self):
        debit = self.cleaned_data.get('debit')
        credit = self.cleaned_data.get('credit')
        if valeur is None or valeur < 0:
            raise forms.ValidationError("La valeur ne peut pas être négative.")
        return valeur

# Utilisé lors de la recherche par id        
class ChercheEcritureComptableForm(forms.Form): 
    ecriture_comptable_search = forms.IntegerField(
        label="Recherche par numéro d'écriture comptable ", 
        widget=forms.TextInput(attrs={'placeholder': 'Tapez le numéro de l\'écriture...', 'id': 'ecriture_comptable-search-input'}))



