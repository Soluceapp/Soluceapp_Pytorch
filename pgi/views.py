from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import *
from .forms import *
from django.forms import inlineformset_factory, modelformset_factory
from .models import Produit
from django.db.models import Q
from decimal import Decimal
from django.db.models import Sum


##
#View dirigeant urls.py home_pgi
##
@login_required 
def home_pgi(request):
    return render(request, 'pgi/index_pgi.html')

##
#View dirigeant urls.py achat_pgi
##
@login_required 
def detail_achat_pgi(request):
    # Récupération de la période :
    identite = get_object_or_404(Identite, pk=1)
    periode = identite.periode

    # Récupération du montant total des factures pour l'année spécifiée
    total_achat = FactureAchat.objects.filter(date_facture__year=periode).aggregate(Sum('montant_total'))['montant_total__sum'] or 0

    # Calcul de l'évolution par rapport à l'année précédente
    periodep = int((identite.periode)-1)
    total_achatp = FactureAchat.objects.filter(date_facture__year=periodep).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    evol = round(((total_achat - total_achatp)/ total_achat) *100,2)

    return render(request, 'pgi/detail_achat_pgi.html',{'periode' : periode, 'total_achat':total_achat, 'evol':evol})

##
#View dirigeant urls.py vente_pgi
##
@login_required 
def vente_pgi(request):

    # Récupération de la période :
    identite = get_object_or_404(Identite, pk=1)
    periode = identite.periode

    # Récupération du montant total des factures pour l'année spécifiée
    chiffre_affaires = FactureVente.objects.filter(date_facture__year=periode).aggregate(Sum('montant_total'))['montant_total__sum'] or 0

    # Calcul de l'évolution par rapport à l'année précédente
    periodep = int((identite.periode)-1)
    chiffre_affairesp = FactureVente.objects.filter(date_facture__year=periodep).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    evol = round(((chiffre_affaires - chiffre_affairesp)/ chiffre_affaires) *100,2)

    return render(request, 'pgi/vente_pgi.html',{'periode' : periode, 'chiffre_affaires':chiffre_affaires, 'evol':evol})

##
#View dirigeant urls.py compta_pgi
##
@login_required 
def compta_pgi(request):
    return render(request, 'pgi/compta_pgi.html')

##
#View dirigeant urls.py param_pgi
##
@login_required 
def param_pgi(request):
    return render(request, 'pgi/param_pgi.html')

##
#View dirigeant urls.py modification de client
##
@login_required 
def client_pgi(request):
    cherche_form = None
    create_form = None
    modify_form = None
    affiche_form = None
    edit_form = None
    clients_list = None # utile à ClientService à des fins experimentales
    form = SelectClientForm(request.POST or None) 
    compte = None

    if request.method == "POST" :
        if 'cherche_form' in request.POST:
            form, affiche_form, clients_list = ClientService.cherche_form(request)
        if 'create_form' in request.POST: # pas elif du fait du template
            form = '' 
            create_form = CreateClientForm()
        elif 'modif_form' in request.POST:
            form = SelectClientForm(request.POST)
            if form.is_valid():
                selected_client = form.cleaned_data['client']
                request.session['selected_client_id'] = encrypt_value(selected_client.id_client)
                modify_form = EditClientForm(instance=selected_client)
                compte=selected_client.plan_comptable
        elif 'affiche_form' in request.POST:
            form = SelectClientForm(request.POST)
            if form.is_valid():
                selected_client = form.cleaned_data['client'] 
                affiche_form = EditClientForm(instance=selected_client)
                compte=selected_client.plan_comptable
        elif 'create_info' in request.POST:
            create_form = CreateClientForm(request.POST)
            if create_form.is_valid():
                client = create_form.save()
                numero_plan_comptable = 411000 + client.id_client

                # Création du plan comptable client
                plan_comptable = PlanComptable.objects.create(
                    numero=numero_plan_comptable,
                    nom=f"Client {client.nom}",
                    valeur=0)

                # Lier le plan comptable au client
                client.plan_comptable = plan_comptable
                client.save()

                messages.info(request, "Création effectuée.")
                return redirect('pgi:client_pgi')
        elif 'delete_info' in request.POST:
            id_client = request.POST.get('client')
            if id_client:  
                info_to_delete = get_object_or_404(Client, id_client=id_client)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:client_pgi')
            else:
                form.add_error('client', 'Information non trouvée') 
        elif 'modif_info' in request.POST:
            selected_client_id = request.session.get('selected_client_id')
            if not selected_client_id:
                messages.warning(request, "Modification non effectuée.")
                return redirect('pgi:client_pgi')
            id_client = decrypt_value(selected_client_id)
            if id_client:
                info_to_modif = get_object_or_404(Client, id_client=id_client)
                edit_form = EditClientForm(request.POST, instance=info_to_modif)
                if edit_form.is_valid():
                    edit_form.save()
                    del request.session['selected_client_id']
                    edit_form = None
                    form = None
                    messages.info(request, "La modification est effectuée.")
                    return redirect('pgi:client_pgi')
                else:
                    form = edit_form
                    form.add_error('client', 'Indiquez l\'information recherchée')
            else:
                form = EditClientForm(request.POST)
                form.add_error('nom', 'Information non trouvée')           
            if redirect_response:
                return redirect_response
        elif 'retour' in request.POST:
                return redirect("pgi:client_pgi")
        else:
            cherche_form = ChercheClientForm()
    return render(request, 'pgi/client_pgi.html', {'compte': compte,'form': form, 'create_form': create_form,  'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'clients_list': clients_list})

##
#View dirigeant urls.py modification de fournisseur
##
@login_required 
def fournisseur_pgi(request):
    create_form = None
    modify_form = None
    edit_form = None
    affiche_form = None
    cherche_form = None
    fournisseur_list = None
    compte = None
    form = SelectFournisseurForm(request.POST or None) 

    if request.method == "POST":
        if 'cherche_form' in request.POST:
            form, affiche_form, fournisseur_list = FournisseurService.cherche_form(request)
        if 'create_form' in request.POST: # ne pas mettre elif
            form = '' 
            create_form = CreateFournisseurForm()
        elif 'modif_form' in request.POST:
            form = SelectFournisseurForm(request.POST)
            if form.is_valid():
                selected_fournisseur = form.cleaned_data['fournisseur']  
                request.session['selected_fournisseur_id'] = encrypt_value(selected_fournisseur.id_fournisseur)  
                modify_form = EditFournisseurForm(instance=selected_fournisseur)
            compte=selected_fournisseur.plan_comptable
        elif 'affiche_form' in request.POST:
            form = SelectFournisseurForm(request.POST)
            if form.is_valid():
                selected_fournisseur = form.cleaned_data['fournisseur']  
                affiche_form = EditFournisseurForm(instance=selected_fournisseur)
            compte=selected_fournisseur.plan_comptable
        elif 'create_info' in request.POST:
            create_form = CreateFournisseurForm(request.POST)
            if create_form.is_valid():
                fournisseur = create_form.save()
                numero_plan_comptable = 401000 + fournisseur.id_fournisseur

                # Création du plan comptable client
                plan_comptable = PlanComptable.objects.create(
                    numero=numero_plan_comptable,
                    nom=f"Fournisseur {fournisseur.nom}",
                    valeur=0)

                # Lier le plan comptable au client
                fournisseur.plan_comptable = plan_comptable
                fournisseur.save()
                messages.info(request,("Création effectuée."))
                return redirect('pgi:fournisseur_pgi')
        elif 'delete_info' in request.POST:
            id_fournisseur = request.POST.get('fournisseur')
            if id_fournisseur:  
                info_to_delete = get_object_or_404(Fournisseur, id_fournisseur=id_fournisseur)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:fournisseur_pgi')
            else:
                form.add_error('fournisseur', 'Information non trouvée') 
        elif 'modif_info' in request.POST:
            selected_fournisseur_id = request.session.get('selected_fournisseur_id')
            if not selected_fournisseur_id:
                messages.warning(request, "Modification non effectuée.")
                return redirect('pgi:fournisseur_pgi')
            id_fournisseur = decrypt_value(selected_fournisseur_id) 
            if id_fournisseur:
                info_to_modif = get_object_or_404(Fournisseur, id_fournisseur=id_fournisseur)
                edit_form = EditFournisseurForm(request.POST, instance=info_to_modif)
                if edit_form.is_valid():
                    edit_form.save()
                    del request.session['selected_fournisseur_id']
                    edit_form = None
                    form = None
                    messages.info(request, "La modification est effectuée.")
                    return redirect('pgi:fournisseur_pgi')
                else:
                    form = edit_form
                    form.add_error('fournisseur', 'Indiquez l\'information recherchée')
            else:
                form = EditFournisseurForm(request.POST)
                form.add_error('nom', 'Information non trouvée')           
            if redirect_response:
                return redirect_response
        elif 'retour' in request.POST:
                return redirect("pgi:fournisseur_pgi")
        else:
            cherche_form = ChercheFournisseurForm()
    return render(request, 'pgi/fournisseur_pgi.html', {'compte': compte,'form': form, 'create_form': create_form,  'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'fournisseur_list': fournisseur_list})


##
#View dirigeant urls.py modification de produit
##
@login_required 
def produit_pgi(request):
    create_form = None
    modify_form = None
    edit_form = None
    affiche_form = None
    cherche_form = None
    produit_list = None
    form = SelectProduitForm(request.POST or None) 

    if request.method == "POST":
        if 'cherche_form' in request.POST:
            form, affiche_form, produit_list = ProduitService.cherche_form(request)
        if 'create_form' in request.POST: # ne pas mettre elif
            form = '' 
            create_form = CreateProduitForm()
        elif 'modif_form' in request.POST:
            form = SelectProduitForm(request.POST)
            if form.is_valid():
                selected_produit = form.cleaned_data['produit']  
                request.session['selected_produit_id'] = encrypt_value(selected_produit.id_produit)  
                modify_form = EditProduitForm(instance=selected_produit)
        elif 'affiche_form' in request.POST:
            form = SelectProduitForm(request.POST)
            if form.is_valid():
                selected_produit = form.cleaned_data['produit']  
                affiche_form = EditProduitForm(instance=selected_produit)
        elif 'create_info' in request.POST:
            create_form = CreateProduitForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                messages.info(request,("Création effectuée."))
                return redirect('pgi:produit_pgi')
        elif 'delete_info' in request.POST:
            id_produit = request.POST.get('produit')
            if id_produit:  
                info_to_delete = get_object_or_404(Produit, id_produit=id_produit)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:produit_pgi')
            else:
                form.add_error('produit', 'Information non trouvée') 
        elif 'modif_info' in request.POST:
            selected_produit_id = request.session.get('selected_produit_id')
            if not selected_produit_id:
                messages.warning(request, "Modification non effectuée.")
                return redirect('pgi:produit_pgi')
            id_produit = decrypt_value(selected_produit_id)
            if id_produit:
                info_to_modif = get_object_or_404(Produit, id_produit=id_produit)
                edit_form = EditProduitForm(request.POST, instance=info_to_modif)
                if edit_form.is_valid():
                    edit_form.save()
                    del request.session['selected_produit_id']
                    edit_form = None
                    form = None
                    messages.info(request, "La modification est effectuée.")
                    return redirect('pgi:produit_pgi')
                else:
                    form = edit_form
                    form.add_error('produit', 'Indiquez l\'information recherchée')
            else:
                form = EditProduitForm(request.POST)
                form.add_error('nom', 'Information non trouvée')           
            if redirect_response:
                return redirect_response
        elif 'retour' in request.POST:
                return redirect("pgi:produit_pgi")
        else:
            cherche_form = ChercheProduitForm()
    return render(request, 'pgi/produit_pgi.html', {'form': form, 'create_form': create_form,  'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'produit_list': produit_list})

##
#View dirigeant urls.py modification de bon de commande
##
@login_required 
def bon_commande_pgi(request):
    form = SelectCommandeForm(request.POST or None)
    affiche_form = None
    modify_form = None
    edit_form = None
    cherche_form = None
    bon_commande_list = None 
    if request.method == "POST":
        if 'affiche_form' in request.POST:
            if form.is_valid():
                selected_commande = form.cleaned_data['commande']    
                detail_commande = Commande.objects.filter(id_commande=selected_commande.id_commande) # id de selected_commande
                detail_identite = Identite.objects.filter(id_identite=1)
                detail_client = Client.objects.filter(id_client=selected_commande.client.id_client)
                lignes_commande = LigneCommande.objects.filter(commande_id=selected_commande.id_commande)
                for ligne in lignes_commande:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_commande)
                affiche_form = EditCommandeForm(instance=selected_commande)
                return render(request, 'pgi/bon_commande_pgi.html', {
                    'form': form,  # navbar 
                    'affiche_form': affiche_form,
                    'lignes_commande': lignes_commande,
                    'detail_commande': detail_commande,
                    'detail_identite': detail_identite,
                    'detail_client': detail_client,  
                    'total_general': total_general 
                })
        elif 'choix_modif' in request.POST:
            form = SelectCommandeForm(request.POST)
            if form.is_valid():
                # Récupérer les lignes de commande
                selected_commande = form.cleaned_data['commande']
                lignes_commande = LigneCommande.objects.filter(commande_id=selected_commande.id_commande)
                
                # Calcul des totaux des lignes
                for ligne in lignes_commande:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_commande)

                # Créer les formulaires
                edit_form = EditCommandeForm(instance=selected_commande)  # Pas besoin de POST ici, juste une instance pour l'édition
                LigneCommandeFormSet = modelformset_factory(LigneCommande, form=LigneCommandeForm, extra=0)
                ligne_formset = LigneCommandeFormSet(queryset=LigneCommande.objects.filter(commande=selected_commande))

                # Mise en session de l'id de la commande
                request.session['selected_commande_id'] = encrypt_value(selected_commande.id_commande)

                return render(request, 'pgi/bon_commande_pgi.html', {
                    'selected_commande': selected_commande,
                    'form': form,
                    'lignes_commande': lignes_commande,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_commande_data': zip(ligne_formset, lignes_commande),
                    'produits': Produit.objects.all(),
                })

        elif 'modification' in request.POST:
            # Vérifier que l'ID de la commande est dans la session
            selected_commande_id_encrypted = request.session.get('selected_commande_id')
            if selected_commande_id_encrypted is None:
                messages.error(request, "Aucune commande sélectionnée. Veuillez en sélectionner une.")
                return redirect('pgi:selection_commande') 
            
            # Déchiffrer l'ID de la commande depuis la session
            id_commande = decrypt_value(selected_commande_id_encrypted)
            selected_commande = get_object_or_404(Commande, id_commande=id_commande)
            
            # Créer les formulaires avec les données de la commande
            edit_form = EditCommandeForm(request.POST, instance=selected_commande)
            LigneCommandeFormSet = modelformset_factory(LigneCommande, form=LigneCommandeForm, extra=0)
            ligne_formset = LigneCommandeFormSet(request.POST, queryset=LigneCommande.objects.filter(commande=selected_commande))
            
            if edit_form.is_valid() and ligne_formset.is_valid():
                # Sauvegarder la commande et les lignes de commande modifiées
                edit_form.save()
                for form in ligne_formset:
                    if form.instance.produit:
                        form.instance.prix_unitaire = form.instance.produit.prix_unitaire
                    form.save()
                
                # Recalculer les totaux après avoir enregistré
                lignes_commande = LigneCommande.objects.filter(commande_id=id_commande)
                for ligne in lignes_commande:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_commande)
                
                # Laisser l'ID de la commande dans la session pour le réutiliser lors des prochaines actions
                
                messages.info(request, "La modification est effectuée.")
                return render(request, 'pgi/bon_commande_pgi.html', {
                    'selected_commande': selected_commande,
                    'lignes_commande': lignes_commande,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_commande_data': zip(ligne_formset, lignes_commande),
                    'produits': Produit.objects.all(),
                })
            else:
                # Gérer les erreurs de validation (pour archive et développement)
                if not edit_form.is_valid():
                    for field, errors in edit_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Formulaire à compléter")
                            #messages.error(request, f"{field}: {error}")
                if not ligne_formset.is_valid():
                    for form in ligne_formset:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"Formulaire à compléter")
                
                # Renvoyer la vue avec les données précédentes et le total recalculé
                lignes_commande = LigneCommande.objects.filter(commande_id=id_commande)
                for ligne in lignes_commande:
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_commande)
                
                return render(request, 'pgi/bon_commande_pgi.html', {
                    'selected_commande': selected_commande,
                    'form': None,  # Pas besoin du formulaire de sélection de commande ici
                    'lignes_commande': lignes_commande,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_commande_data': zip(ligne_formset, lignes_commande),
                    'produits': Produit.objects.all(),
                })

        elif 'transfert' in request.POST:
            # Vérifier que l'ID de la commande est dans la session
            selected_commande_id_encrypted = request.session.get('selected_commande_id')
            if selected_commande_id_encrypted is None:
                messages.error(request, "Aucune commande sélectionnée. Veuillez en sélectionner une.")
                return redirect('pgi:selection_commande') 
            
            # Déchiffrer l'ID de la commande depuis la session
            id_commande = decrypt_value(selected_commande_id_encrypted)
            selected_commande = get_object_or_404(Commande, id_commande=id_commande)
            
            # Créer les formulaires avec les données de la commande
            edit_form = EditCommandeForm(request.POST, instance=selected_commande)
            LigneCommandeFormSet = modelformset_factory(LigneCommande, form=LigneCommandeForm, extra=0)
            ligne_formset = LigneCommandeFormSet(request.POST, queryset=LigneCommande.objects.filter(commande=selected_commande))
            
            if edit_form.is_valid() and ligne_formset.is_valid():
                # Sauvegarder la commande
                commande = edit_form.save()

                # Si la commande n'a pas encore de facture, créer la facture
                if not commande.facture:
                    facture_vente = FactureVente.objects.create(
                        client=commande.client,
                        commande=commande,
                        date_facture=commande.date_commande, 
                        statut="Non payée",  
                    )
                    commande.facture = facture_vente 
                    commande.save()

                # Sauvegarder les lignes de commande
                for form in ligne_formset:
                    if form.instance.produit:
                        form.instance.prix_unitaire = form.instance.produit.prix_unitaire
                    ligne_commande = form.save(commit=False)
                    ligne_commande.commande = commande  
                    ligne_commande.save()

                    # Sauvegarder une ligne de facture associée à la ligne de commande
                    facture_ligne = LigneFactureVente.objects.create(
                        produit=ligne_commande.produit,
                        quantite=ligne_commande.quantite,
                        prix_unitaire=ligne_commande.prix_unitaire,
                        remise=ligne_commande.remise,
                        tva=ligne_commande.produit.tva,  
                        montant_ligne=ligne_commande.quantite * ligne_commande.prix_unitaire,
                        facture_vente=commande.facture,  
                    )

                # Mettre à jour le montant total de la facture
                montant_total = sum(ligne.montant_ligne for ligne in commande.facture.lignefacturevente_set.all())
                commande.facture.montant_total = montant_total
                commande.facture.save()
                
                # Recalculer les totaux après avoir enregistré
                lignes_commande = LigneCommande.objects.filter(commande_id=id_commande)
                for ligne in lignes_commande:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_commande)
                
                # Laisser l'ID de la commande dans la session pour le réutiliser lors des prochaines actions
                
                messages.info(request, "Le transfert est effectué.")
                return render(request, 'pgi/bon_commande_pgi.html', {
                    'selected_commande': selected_commande,
                    'lignes_commande': lignes_commande,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_commande_data': zip(ligne_formset, lignes_commande),
                    'produits': Produit.objects.all(),
                })
            else:
                # Renvoyer la vue avec les données précédentes et le total recalculé
                lignes_commande = LigneCommande.objects.filter(commande_id=id_commande)
                for ligne in lignes_commande:
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_commande)
                
                return render(request, 'pgi/bon_commande_pgi.html', {
                    'selected_commande': selected_commande,
                    'form': None,  # Pas besoin du formulaire de sélection de commande ici
                    'lignes_commande': lignes_commande,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_commande_data': zip(ligne_formset, lignes_commande),
                    'produits': Produit.objects.all(),
                })

        elif 'delete_info' in request.POST:
            id_commande = request.POST.get('commande')
            if id_commande:  
                info_to_delete = get_object_or_404(Commande, id_commande=id_commande)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:bon_commande_pgi')
            else:
                form.add_error('commande', 'Information non trouvée')
        elif 'create_form' in request.POST: 
            return redirect("pgi:bon_commande_pgi_create")
        elif 'cherche_form' in request.POST:
            cherche_form = ChercheCommandeForm(request.POST)
            if cherche_form.is_valid():
                id_commande = cherche_form.cleaned_data['commande_search']
                try:
                    affiche_form = Commande.objects.get(id_commande=id_commande)
                    detail_commande = [affiche_form]
                    lignes_commande = LigneCommande.objects.filter(commande=affiche_form)
                    total_general = sum(ligne.prix_unitaire * ligne.quantite for ligne in lignes_commande)
                except Commande.DoesNotExist:
                    detail_commande = []
                    lignes_commande = []
                    total_general = 0
                return render(request, 'pgi/bon_commande_pgi.html', {
                    'form': form, 
                    'edit_form': edit_form, 
                    'affiche_form': affiche_form,
                    'cherche_form': cherche_form,
                    'bon_commande_list': bon_commande_list,
                    'lignes_commande': lignes_commande,
                    'detail_commande': detail_commande,  
                    'total_general': total_general 
                })
        elif 'retour' in request.POST:
                return redirect("pgi:bon_commande_pgi")
        else:
            cherche_form = ChercheCommandeForm()
    return render(request, 'pgi/bon_commande_pgi.html', {'form': form, 'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'bon_commande_list': bon_commande_list})

##
#View permettant de créer la commande
##
@login_required 
def bon_commande_pgi_create(request):
    LigneCommandeFormSetC = inlineformset_factory(Commande, LigneCommande, form=LigneCommandeFormC, extra=request.session.get('nb_ligne', 1), can_delete=True)

    if request.method == 'POST':
        form_commande = CommandeForm(request.POST)
        
        if form_commande.is_valid(): 
            commande = form_commande.save(commit=False)  # Crée la commande sans la sauvegarder pour l'instant
            commande.save() 
            formset_lignes = LigneCommandeFormSetC(request.POST, instance=commande)  
            supprimer_commandes_sans_lignes()

            if 'ajout_ligne' in request.POST:
                request.session['nb_ligne'] += 1
                formset_lignes = LigneCommandeFormSetC(instance=commande)  # Actualise le formset avec la nouvelle commande
                return render(request, 'pgi/bon_commande_pgi_create.html', {
                    'form_commande': form_commande,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'suppr_ligne' in request.POST:
                request.session['nb_ligne'] -= 1
                formset_lignes = LigneCommandeFormSetC(instance=commande) 
                return render(request, 'pgi/bon_commande_pgi_create.html', {
                    'form_commande': form_commande,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'confirme' in request.POST:
                if form_commande.is_valid() and formset_lignes.is_valid():
                    commande.save()
                    lignes = formset_lignes.save(commit=False)
                    for ligne in lignes:
                        if ligne not in formset_lignes.deleted_objects:
                            produit_id = ligne.produit_id
                            if produit_id:
                                produit = Produit.objects.get(id_produit=produit_id)
                                ligne.prix_unitaire = produit.prix_unitaire
                                ligne.commande = commande
                                ligne.save()
                    formset_lignes.save()
                    supprimer_commandes_sans_lignes()
                    messages.success(request, "La création a été effectuée.")
                    request.session['nb_ligne'] = 1
                    return redirect('pgi:bon_commande_pgi')
                else:
                    for form in formset_lignes:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"Erreur dans le champ {field} : {error}")
        else:
            messages.error(request, "Modifiez le haut de la commande (ex: la date JJ-MM-AAAA)")
            request.session['nb_ligne'] = 1
            formset_lignes = LigneCommandeFormSetC()
        
    else:
        request.session['nb_ligne'] = 1
        form_commande = CommandeForm()
        formset_lignes = LigneCommandeFormSetC()

    return render(request, 'pgi/bon_commande_pgi_create.html', {
        'form_commande': form_commande,
        'formset_lignes': formset_lignes,
        'produits': Produit.objects.all(),
    })

##
#View dirigeant urls.py modification de la facture de vente
##
@login_required 
def facture_vente_pgi(request):
    form = SelectFactureVenteForm(request.POST or None)
    affiche_form = None
    modify_form = None
    edit_form = None
    cherche_form = None
    facture_vente_list = None 
    if request.method == "POST":
        if 'affiche_form' in request.POST:
            if form.is_valid():
                selected_facture_vente = form.cleaned_data['facture_vente']    
                detail_facture_vente = FactureVente.objects.filter(id_facture_vente=selected_facture_vente.id_facture_vente)
                detail_identite = Identite.objects.filter(id_identite=1)
                detail_client = Client.objects.filter(id_client=selected_facture_vente.client.id_client)
                lignes_facture_vente = LigneFactureVente.objects.filter(facture_vente_id=selected_facture_vente.id_facture_vente)
                for ligne in lignes_facture_vente:
                    if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))* (1 - (ligne.remise.taux / 100))
                    elif ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    elif ligne.tva and ligne.tva.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))
                    else:ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_facture_vente)
                affiche_form = EditFactureVenteForm(instance=selected_facture_vente)
                return render(request, 'pgi/facture_vente_pgi.html', {
                    'form': form,  # navbar 
                    'affiche_form': affiche_form,
                    'lignes_facture_vente': lignes_facture_vente,
                    'detail_facture_vente': detail_facture_vente,
                    'detail_identite': detail_identite,
                    'detail_client': detail_client,  
                    'total_general': total_general 
                })
        elif 'choix_modif' in request.POST:
            form = SelectFactureVenteForm(request.POST)
            if form.is_valid():
                selected_facture_vente = form.cleaned_data['facture_vente']

                # Créer les formulaires pour l'affichage de la modification en fonction de selected_facture_vente
                edit_form = EditFactureVenteForm(instance=selected_facture_vente) 
                LigneFactureVenteFormSet = modelformset_factory(LigneFactureVente, form=LigneFactureVenteForm, extra=0)
                ligne_formset = LigneFactureVenteFormSet(queryset=LigneFactureVente.objects.filter(facture_vente=selected_facture_vente.id_facture_vente))

                # Récupérer les totaux
                lignes_facture_vente = LigneFactureVente.objects.filter(facture_vente_id=selected_facture_vente.id_facture_vente)
                for ligne in lignes_facture_vente:
                    if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))* (1 - (ligne.remise.taux / 100))
                    elif ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    elif ligne.tva and ligne.tva.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))
                    else:ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_facture_vente)

                # Mise en session de l'id de la facture de vente
                request.session['selected_facture_vente_id'] = encrypt_value(selected_facture_vente.id_facture_vente)

                return render(request, 'pgi/facture_vente_pgi.html', {
                    'selected_facture_vente': selected_facture_vente,
                    'form': form, # Navbar principale
                    'lignes_facture_vente': lignes_facture_vente,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_facture_vente_data': zip(ligne_formset, lignes_facture_vente),
                })

        elif 'modification' in request.POST:
            # Vérifier que l'ID de la facture de vente est dans la session
            selected_facture_vente_id_encrypted = request.session.get('selected_facture_vente_id')
            if selected_facture_vente_id_encrypted is None:
                messages.error(request, "Aucune commande sélectionnée. Veuillez en sélectionner une.")
                return redirect('pgi:selection_facture_vente')
            
            # Déchiffrer l'ID de la facture depuis la session
            id_facture_vente = decrypt_value(selected_facture_vente_id_encrypted)
            selected_facture_vente = get_object_or_404(FactureVente, id_facture_vente=id_facture_vente)
            
            # Créer les formulaires avec les données de la facture de vente
            edit_form = EditFactureVenteForm(request.POST, instance=selected_facture_vente)
            LigneFactureVenteFormSet = modelformset_factory(LigneFactureVente, form=LigneFactureVenteForm, extra=0)
            ligne_formset = LigneFactureVenteFormSet(request.POST, queryset=LigneFactureVente.objects.filter(facture_vente=selected_facture_vente))
            
            if edit_form.is_valid() and ligne_formset.is_valid():
                facture = edit_form.save()

                # Sauvegarder les lignes de facture modifiées
                for ligne in ligne_formset:
                    if ligne.instance.produit:
                        ligne.instance.prix_unitaire = ligne.instance.produit.prix_unitaire
                    
                    # Récupération de l'ancien stock et de l'ancienne quantité
                    ligne_facture_vente = LigneFactureVente.objects.get(id_ligne_facture_vente=ligne.instance.id_ligne_facture_vente)
                    produit_ancien = ligne_facture_vente.produit 
                    ancien_stock = produit_ancien.stock
                    ancienne_quantite_facture = ligne_facture_vente.quantite  
                    ligne.save()

                    # Récupération de la nouvelle quantité et modification du stock
                    nouvelle_quantite_facture = ligne.instance.quantite  
                    produit_modifie = Produit.objects.get(id_produit=ligne.instance.produit.id_produit)
                    produit_modifie.stock = ancien_stock + (ancienne_quantite_facture - nouvelle_quantite_facture)
                    identite = get_object_or_404(Identite, pk=1)
                    if identite.stock_securite is not None:
                        if produit_modifie.stock < identite.stock_securite:
                            messages.warning(request, "Attention : Stock de sécurité dépassé !")
                    else:
                            messages.warning(request, "Aucun stock de sécurité défini pour ce produit.")
                    produit_modifie.save()

                    # Recalculer les totaux après avoir sauvegardé toutes les lignes
                    lignes_facture_vente = LigneFactureVente.objects.filter(facture_vente_id=id_facture_vente)
                    total_general = 0  
                    for ligne in lignes_facture_vente:
                        if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100)) * (1 - (ligne.remise.taux / 100))
                        elif ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                        elif ligne.tva and ligne.tva.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))
                        else:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                        ligne.montant_ligne = ligne.total_ligne
                        ligne.save() 
                        total_general += ligne.total_ligne

                    # Sauvegarde du total général dans la facture
                    facture.montant_total = total_general
                    facture.save()
                
                # Ne pas supprimer l'ID de la facture de vente dans la session
                messages.info(request, "La modification est effectuée.")
                return render(request, 'pgi/facture_vente_pgi.html', {
                    'selected_facture_vente': selected_facture_vente,
                    'lignes_facture_vente': lignes_facture_vente,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_facture_vente_data': zip(ligne_formset, lignes_facture_vente),
                    'produits': Produit.objects.all(),
                })
            else:
                # Si erreur recopier pour vérif comme commande     
                # Renvoyer la vue avec les données précédentes et le total recalculé
                lignes_facture_vente = LigneFactureVente.objects.filter(facture_vente_id=id_facture_vente)
                for ligne in lignes_facture_vente:
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_facture_vente)
                
                return render(request, 'pgi/facture_vente_pgi.html', {
                    'selected_facture_vente': selected_facture_vente,
                    'form': None,  # Pas besoin du formulaire de sélection de commande ici
                    'lignes_facture_vente': lignes_facture_vente,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_facture_vente_data': zip(ligne_formset, lignes_facture_vente),
                    'produits': Produit.objects.all(),
                })

        elif 'delete_info' in request.POST:
            id_facture_vente = request.POST.get('facture_vente')
            if id_facture_vente:  
                info_to_delete = get_object_or_404(FactureVente, id_facture_vente=id_facture_vente)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:facture_vente_pgi')
            else:
                form.add_error('facture_vente', 'Information non trouvée')
        elif 'create_form' in request.POST: 
            return redirect("pgi:facture_vente_pgi_create")
        elif 'cherche_form' in request.POST:
            cherche_form = ChercheFactureVenteForm(request.POST)
            if cherche_form.is_valid():
                id_facture_vente = cherche_form.cleaned_data['facture_vente_search']
                try:
                    affiche_form = FactureVente.objects.get(id_facture_vente=id_facture_vente)
                    detail_facture_vente = [affiche_form]
                    lignes_facture_vente = LigneFactureVente.objects.filter(facture_vente=affiche_form)
                    total_general = sum(ligne.prix_unitaire * ligne.quantite for ligne in lignes_facture_vente)
                except FactureVente.DoesNotExist:
                    detail_facture_vente = []
                    lignes_facture_vente = []
                    total_general = 0
                return render(request, 'pgi/facture_vente_pgi.html', {
                    'form': form, 
                    'edit_form': edit_form, 
                    'affiche_form': affiche_form,
                    'cherche_form': cherche_form,
                    'facture_vente_list': facture_vente_list,
                    'lignes_facture_vente': lignes_facture_vente,
                    'detail_facture_vente': detail_facture_vente,  
                    'total_general': total_general 
                })
        elif 'retour' in request.POST:
                return redirect("pgi:facture_vente_pgi")
        else:
            cherche_form = ChercheFactureVenteForm()
    return render(request, 'pgi/facture_vente_pgi.html', {'form': form, 'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'facture_vente_list': facture_vente_list})

##
#View permettant de créer la facture de vente
##
@login_required 
def facture_vente_pgi_create(request):
    LigneFactureVenteFormSetC = inlineformset_factory(FactureVente, LigneFactureVente, form=LigneFactureVenteFormC, extra=request.session.get('nb_ligne', 1), can_delete=True)

    if request.method == 'POST':
        form_facture_vente = FactureVenteForm(request.POST)
        
        if form_facture_vente.is_valid():  
            facture_vente = form_facture_vente.save(commit=False)  # Crée la facture sans la sauvegarder pour l'instant
            facture_vente.save()  
            formset_lignes = LigneFactureVenteFormSetC(request.POST, instance=facture_vente)  # Associe la facture validée aux lignes
            supprimer_factures_sans_lignes()

            if 'ajout_ligne' in request.POST:
                request.session['nb_ligne'] += 1
                formset_lignes = LigneFactureVenteFormSetC(instance=facture_vente)  # Actualise le formset avec la nouvelle facture
                return render(request, 'pgi/facture_vente_pgi_create.html', {
                    'form_facture_vente': form_facture_vente,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'suppr_ligne' in request.POST:
                request.session['nb_ligne'] -= 1
                formset_lignes = LigneFactureVenteFormSetC(instance=facture_vente)
                return render(request, 'pgi/facture_vente_pgi_create.html', {
                    'form_facture_vente': form_facture_vente,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'confirme' in request.POST:
                if form_facture_vente.is_valid() and formset_lignes.is_valid():
                    facture_vente.save()
                    lignes = formset_lignes.save(commit=False)
                    total_general = 0  # Initialisation du total général

                    for ligne in lignes:
                        if ligne not in formset_lignes.deleted_objects:
                            produit_id = ligne.produit_id
                            if produit_id:
                                produit = Produit.objects.get(id_produit=produit_id)
                                ligne.prix_unitaire = produit.prix_unitaire
                                ligne.facture_vente = facture_vente
                                ligne.save()
                                # Diminution du stock et avertissement si nécessaire.
                                produit.stock -= ligne.quantite
                                identite = get_object_or_404(Identite, pk=1)
                                if produit.stock<identite.stock_securite:
                                    messages.warning(request, "Attention : Stock de sécurité dépassé !")
                                produit.save()

                        # Calcul des totaux pour chaque ligne
                        if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100)) * (1 - (ligne.remise.taux / 100))
                        elif ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                        elif ligne.tva and ligne.tva.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))                        
                        else:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                        ligne.montant_ligne = ligne.total_ligne
                        ligne.save()
                        
                        # Ajouter le total de chaque ligne à total_general
                        total_general += ligne.total_ligne if ligne.total_ligne else 0

                    # Enregistrement du total_general dans la facture, par exemple
                    facture_vente.montant_total = total_general
                    facture_vente.save()

                    formset_lignes.save()
                    supprimer_factures_sans_lignes()
                    messages.success(request, "La création a été effectuée.")
                    request.session['nb_ligne'] = 1
                    return redirect('pgi:facture_vente_pgi')
                else:
                    for form in formset_lignes:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"Erreur dans un champ")
        else:
            messages.error(request, "Modifiez le haut de la facture (ex: la date JJ/MM/AAAA)")
            request.session['nb_ligne'] = 1
            formset_lignes = LigneFactureVenteFormSetC()
        
    else:
        request.session['nb_ligne'] = 1
        form_facture_vente = FactureVenteForm()
        formset_lignes = LigneFactureVenteFormSetC()

    return render(request, 'pgi/facture_vente_pgi_create.html', {
        'form_facture_vente': form_facture_vente,
        'formset_lignes': formset_lignes,
        'produits': Produit.objects.all(),
    })

##
#View dirigeant urls.py modification bon de livraison
##
@login_required 
def bon_livraison_pgi(request):
    form = SelectLivraisonForm(request.POST or None)
    affiche_form = None
    modify_form = None
    edit_form = None
    cherche_form = None
    bon_livraison_list = None 
    if request.method == "POST":
        if 'affiche_form' in request.POST:
            if form.is_valid():
                selected_livraison = form.cleaned_data['livraison']    
                detail_livraison = BonLivraison.objects.filter(id_bon_livraison=selected_livraison.id_bon_livraison)
                detail_identite = Identite.objects.filter(id_identite=1)
                detail_client = Client.objects.filter(id_client=selected_livraison.client.id_client)
                lignes_livraison = LigneBonLivraison.objects.filter(bon_livraison_id=selected_livraison.id_bon_livraison)
                for ligne in lignes_livraison:
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_livraison)
                affiche_form = EditLivraisonForm(instance=selected_livraison)
                return render(request, 'pgi/bon_livraison_pgi.html', {
                    'form': form,  # navbar 
                    'affiche_form': affiche_form,
                    'lignes_livraison': lignes_livraison,
                    'detail_livraison': detail_livraison,
                    'detail_identite': detail_identite,
                    'detail_client': detail_client,   
                    'total_general': total_general 
                })
        elif 'choix_modif' in request.POST:
            form = SelectLivraisonForm(request.POST)
            if form.is_valid():
                selected_livraison = form.cleaned_data['livraison']
                # Récupérer les lignes de commande
                lignes_bon_livraison = LigneBonLivraison.objects.filter(bon_livraison_id=selected_livraison.id_bon_livraison)
                
                # Calcul des totaux des lignes
                for ligne in lignes_bon_livraison:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_bon_livraison)

                # Créer les formulaires
                edit_form = EditLivraisonForm(instance=selected_livraison)  # Pas besoin de POST ici, juste une instance pour l'édition
                LigneLivraisonFormSet = modelformset_factory(LigneBonLivraison, form=LigneLivraisonForm, extra=0)
                ligne_formset = LigneLivraisonFormSet(queryset=LigneBonLivraison.objects.filter(bon_livraison=selected_livraison))

                # Mise en session de l'id de la commande
                request.session['selected_livraison_id'] = encrypt_value(selected_livraison.id_bon_livraison)

                # Renvoyer la page avec les informations
                return render(request, 'pgi/bon_livraison_pgi.html', {
                    'selected_livraison': selected_livraison,
                    'form': form,
                    'lignes_livraison': lignes_bon_livraison,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_livraison_data': zip(ligne_formset, lignes_bon_livraison),
                    'produits': Produit.objects.all(),
                })

        elif 'modification' in request.POST:
            # Vérifier que l'ID de la livraison est dans la session
            selected_livraison_id_encrypted = request.session.get('selected_livraison_id')
            if selected_livraison_id_encrypted is None:
                messages.error(request, "Aucune livraison sélectionnée. Veuillez en sélectionner une.")
                return redirect('pgi:selection_livraison') 
            
            # Déchiffrer l'ID de la livraison depuis la session
            id_bon_livraison = decrypt_value(selected_livraison_id_encrypted)
            selected_livraison = get_object_or_404(BonLivraison, id_bon_livraison=id_bon_livraison)
            
            # Créer les formulaires avec les données de la livraison
            edit_form = EditLivraisonForm(request.POST, instance=selected_livraison)
            LigneLivraisonFormSet = modelformset_factory(LigneBonLivraison, form=LigneLivraisonForm, extra=0)
            ligne_formset = LigneLivraisonFormSet(request.POST, queryset=LigneBonLivraison.objects.filter(bon_livraison=selected_livraison))
            if edit_form.is_valid() and ligne_formset.is_valid():
                # Sauvegarder la livraison et les lignes de livraison modifiées
                edit_form.save()
                for form in ligne_formset:
                    if form.instance.produit:
                        form.instance.prix_unitaire = form.instance.produit.prix_unitaire
                    form.save()
                
                # Recalculer les totaux après avoir enregistré
                lignes_livraison = LigneBonLivraison.objects.filter(bon_livraison_id=id_bon_livraison)
                for ligne in lignes_livraison:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_livraison)
                
                # Laisser l'ID de la livraison dans la session pour le réutiliser lors des prochaines actions
                
                messages.info(request, "La modification est effectuée.")
                return render(request, 'pgi/bon_livraison_pgi.html', {
                    'selected_livraison': selected_livraison,
                    'lignes_livraison': lignes_livraison,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_livraison_data': zip(ligne_formset, lignes_livraison),
                    'produits': Produit.objects.all(),
                })
            else:
                # Gérer les erreurs de validation (à supprimer)
                if not edit_form.is_valid():
                    for field, errors in edit_form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                if not ligne_formset.is_valid():
                    for form in ligne_formset:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"ligne:{field}: {error}")
                # Renvoyer la vue avec les données précédentes et le total recalculé
                lignes_livraison = LigneBonLivraison.objects.filter(bon_livraison_id=id_bon_livraison)
                for ligne in lignes_livraison:
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_livraison)
                
                return render(request, 'pgi/bon_livraison_pgi.html', {
                    'selected_livraison': selected_livraison,
                    'form': None,  # Pas besoin du formulaire de sélection de livraison ici
                    'lignes_livraison': lignes_livraison,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_livraison_data': zip(ligne_formset, lignes_livraison),
                    'produits': Produit.objects.all(),
                })

        elif 'delete_info' in request.POST:
            id_livraison = request.POST.get('livraison')
            if id_livraison:  
                info_to_delete = get_object_or_404(Livraison, id_livraison=id_livraison)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:bon_livraison_pgi')
            else:
                form.add_error('livraison', 'Information non trouvée')
        elif 'create_form' in request.POST: 
            return redirect("pgi:bon_livraison_pgi_create")
        elif 'cherche_form' in request.POST:
            cherche_form = ChercheLivraisonForm(request.POST)
            if cherche_form.is_valid():
                id_livraison = cherche_form.cleaned_data['livraison_search']
                try:
                    affiche_form = BonLivraison.objects.get(id_bon_livraison=id_livraison)
                    detail_livraison = [affiche_form]
                    lignes_livraison = LigneBonLivraison.objects.filter(bon_livraison=affiche_form)
                    total_general = sum(ligne.prix_unitaire * ligne.quantite for ligne in lignes_livraison)
                except BonLivraison.DoesNotExist:
                    detail_livraison = []
                    lignes_livraison = []
                    total_general = 0
                return render(request, 'pgi/bon_livraison_pgi.html', {
                    'form': form, 
                    'edit_form': edit_form, 
                    'affiche_form': affiche_form,
                    'cherche_form': cherche_form,
                    'bon_livraison_list': bon_livraison_list,
                    'lignes_livraison': lignes_livraison,
                    'detail_livraison': detail_livraison,  
                    'total_general': total_general 
                })
        elif 'retour' in request.POST:
                return redirect("pgi:bon_livraison_pgi")
        else:
            cherche_form = ChercheLivraisonForm()
    return render(request, 'pgi/bon_livraison_pgi.html', {'form': form, 'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'bon_livraison_list': bon_livraison_list})

##
#View permettant de créer la livraison
##
@login_required 
def bon_livraison_pgi_create(request):
    LigneLivraisonFormSetC = inlineformset_factory(BonLivraison, LigneBonLivraison, form=LigneLivraisonFormC, extra=request.session.get('nb_ligne', 1), can_delete=True)

    if request.method == 'POST':
        form_livraison = LivraisonForm(request.POST)
        
        if form_livraison.is_valid():  
            livraison = form_livraison.save(commit=False)  # Crée la livraison sans la sauvegarder pour l'instant
            livraison.save()  
            formset_lignes = LigneLivraisonFormSetC(request.POST, instance=livraison)  # Associe la commande validée aux lignes
            supprimer_commandes_sans_lignes()

            if 'ajout_ligne' in request.POST:
                # Ajout de ligne sans validation de livraison
                request.session['nb_ligne'] += 1
                formset_lignes = LigneLivraisonFormSetC(instance=livraison)  
                return render(request, 'pgi/bon_livraison_pgi_create.html', {
                    'form_livraison': form_livraison,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'suppr_ligne' in request.POST:
                request.session['nb_ligne'] -= 1
                formset_lignes = LigneLivraisonFormSetC(instance=livraison) 
                return render(request, 'pgi/bon_livraison_pgi_create.html', {
                    'form_livraison': form_livraison,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'confirme' in request.POST:
                if form_livraison.is_valid() and formset_lignes.is_valid():
                    livraison.save()
                    lignes = formset_lignes.save(commit=False)
                    for ligne in lignes:
                        if ligne not in formset_lignes.deleted_objects:
                            produit_id = ligne.produit_id
                            if produit_id:
                                produit = Produit.objects.get(id_produit=produit_id)
                                ligne.prix_unitaire = produit.prix_unitaire
                                ligne.livraison = livraison
                                ligne.save()
                    formset_lignes.save()
                    supprimer_commandes_sans_lignes()
                    messages.success(request, "La création a été effectuée.")
                    request.session['nb_ligne'] = 1
                    return redirect('pgi:bon_livraison_pgi')
                else:
                    for form in formset_lignes:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"Erreur dans le champ {field} : {error}")
        else:
            messages.error(request, "Modifiez le haut de la livraison (ex: la date JJ-MM-AAAA)")
            request.session['nb_ligne'] = 1
            formset_lignes = LigneLivraisonFormSetC()
        
    else:
        request.session['nb_ligne'] = 1
        form_livraison = LivraisonForm()
        formset_lignes = LigneLivraisonFormSetC()

    return render(request, 'pgi/bon_livraison_pgi_create.html', {
        'form_livraison': form_livraison,
        'formset_lignes': formset_lignes,
        'produits': Produit.objects.all(),
    })

##
#View dirigeant urls.py modification de bon d'achat
##
@login_required 
def achat_pgi(request):
    form = SelectAchatForm(request.POST or None)
    affiche_form = None
    modify_form = None
    edit_form = None
    cherche_form = None
    bon_achat_list = None 
    if request.method == "POST":
        if 'affiche_form' in request.POST:
            if form.is_valid():
                selected_achat = form.cleaned_data['achat']    
                detail_achat = Achat.objects.filter(id_achat=selected_achat.id_achat) # id de selected_achat
                detail_identite = Identite.objects.filter(id_identite=1)
                detail_fournisseur = Fournisseur.objects.filter(id_fournisseur=selected_achat.fournisseur.id_fournisseur)
                lignes_achat = LigneAchat.objects.filter(achat_id=selected_achat.id_achat)
                for ligne in lignes_achat:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_achat)
                affiche_form = EditAchatForm(instance=selected_achat)
                return render(request, 'pgi/bon_achat_pgi.html', {
                    'form': form,  # navbar 
                    'affiche_form': affiche_form,
                    'lignes_achat': lignes_achat,
                    'detail_achat': detail_achat,
                    'detail_identite': detail_identite,
                    'detail_fournisseur': detail_fournisseur,   
                    'total_general': total_general 
                })
        elif 'choix_modif' in request.POST:
            form = SelectAchatForm(request.POST)
            if form.is_valid():
                selected_achat = form.cleaned_data['achat']
                # Récupérer les lignes de bon d'achat
                lignes_achat = LigneAchat.objects.filter(achat_id=selected_achat.id_achat)
                
                # Calcul des totaux des lignes
                for ligne in lignes_achat:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_achat)

                # Créer les formulaires
                edit_form = EditAchatForm(instance=selected_achat)  # Pas besoin de POST ici, juste une instance pour l'édition
                LigneAchatFormSet = modelformset_factory(LigneAchat, form=LigneAchatForm, extra=0)
                ligne_formset = LigneAchatFormSet(queryset=LigneAchat.objects.filter(achat=selected_achat))

                # Mise en session de l'id du bon d'achat
                request.session['selected_achat_id'] = encrypt_value(selected_achat.id_achat)

                # Renvoyer la page avec les informations
                return render(request, 'pgi/bon_achat_pgi.html', {
                    'selected_achat': selected_achat,
                    'form': form,
                    'lignes_achat': lignes_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_achat_data': zip(ligne_formset, lignes_achat),
                    'produits': Produit.objects.all(),
                })

        elif 'modification' in request.POST:
            # Vérifier que l'ID du bon d'achat est dans la session
            selected_achat_id_encrypted = request.session.get('selected_achat_id')
            if selected_achat_id_encrypted is None:
                # Si l'ID du bon d'achat n'est pas dans la session, rediriger vers la page de sélection du bon d'achat
                messages.error(request, "Aucun achat sélectionné. Veuillez en sélectionner un.")
                return redirect('pgi:selection_achat')  
            
            # Déchiffrer l'ID de la commande depuis la session
            id_achat = decrypt_value(selected_achat_id_encrypted)
            selected_achat = get_object_or_404(Achat, id_achat=id_achat)
            
            # Créer les formulaires avec les données du bon d'achat
            edit_form = EditAchatForm(request.POST, instance=selected_achat)
            LigneAchatFormSet = modelformset_factory(LigneAchat, form=LigneAchatForm, extra=0)
            ligne_formset = LigneAchatFormSet(request.POST, queryset=LigneAchat.objects.filter(achat=selected_achat))
            
            if edit_form.is_valid() and ligne_formset.is_valid():
                edit_form.save()
                for form in ligne_formset:
                    if form.instance.produit:
                        form.instance.prix_unitaire = form.instance.produit.prix_unitaire
                    form.save()
                
                # Recalculer les totaux après avoir enregistré
                lignes_achat = LigneAchat.objects.filter(achat_id=id_achat)
                for ligne in lignes_achat:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_achat)
                
                # Laisser l'ID de la commande dans la session pour le réutiliser lors des prochaines actions
                
                messages.info(request, "La modification est effectuée.")
                return render(request, 'pgi/bon_achat_pgi.html', {
                    'selected_achat': selected_achat,
                    'lignes_achat': lignes_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_achat_data': zip(ligne_formset, lignes_achat),
                    'produits': Produit.objects.all(),
                })
            else:
                # Si erreur voir commande pour code de gestion d'erreur
                # Renvoyer la vue avec les données précédentes et le total recalculé
                lignes_achat = LigneAchat.objects.filter(achat_id=id_achat)
                for ligne in lignes_achat:
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_achat)
                
                return render(request, 'pgi/bon_achat_pgi.html', {
                    'selected_achat': selected_achat,
                    'form': None,  # Pas besoin du formulaire de sélection de l'achat ici
                    'lignes_achat': lignes_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_achat_data': zip(ligne_formset, lignes_achat),
                })

        elif 'transfert' in request.POST:
            # Vérifier que l'ID du bon d'achat est dans la session
            selected_achat_id_encrypted = request.session.get('selected_achat_id')
            if selected_achat_id_encrypted is None:
                # Si l'ID du bon d'achat n'est pas dans la session, rediriger vers la page de sélection du bon d'achat
                messages.error(request, "Aucun achat sélectionné. Veuillez en sélectionner un.")
                return redirect('pgi:selection_achat')  
            
            # Déchiffrer l'ID de la commande depuis la session
            id_achat = decrypt_value(selected_achat_id_encrypted)
            selected_achat = get_object_or_404(Achat, id_achat=id_achat)
            
            # Créer les formulaires avec les données du bon d'achat
            edit_form = EditAchatForm(request.POST, instance=selected_achat)
            LigneAchatFormSet = modelformset_factory(LigneAchat, form=LigneAchatForm, extra=0)
            ligne_formset = LigneAchatFormSet(request.POST, queryset=LigneAchat.objects.filter(achat=selected_achat))
            
            if edit_form.is_valid() and ligne_formset.is_valid():
                # Sauvegarder la commande
                achat = edit_form.save()

                # Si le bon d'achat n'a pas encore de facture, créer la facture
                if not achat.facture:
                    facture_achat = FactureAchat.objects.create(
                        fournisseur=achat.fournisseur,
                        achat=achat,
                        date_facture=achat.date_achat, 
                        statut="Non payée",  
                    )
                    achat.facture = facture_achat  
                    achat.save()

                # Sauvegarder les lignes de bon d'achat
                for form in ligne_formset:
                    if form.instance.produit:
                        form.instance.prix_unitaire = form.instance.produit.prix_unitaire
                    ligne_achat = form.save(commit=False)
                    ligne_achat.achat = achat  
                    ligne_achat.save()

                    # Sauvegarder une ligne de facture associée à la ligne d'achat
                    facture_ligne = LigneFactureAchat.objects.create(
                        produit=ligne_achat.produit,
                        quantite=ligne_achat.quantite,
                        prix_unitaire=ligne_achat.prix_unitaire,
                        remise=ligne_achat.remise,
                        tva=ligne_achat.produit.tva,  
                        montant_ligne=ligne_achat.quantite * ligne_achat.prix_unitaire,
                        facture_achat=achat.facture,  
                    )

                # Mettre à jour le montant total de la facture
                montant_total = sum(ligne.montant_ligne for ligne in achat.facture.lignefactureachat_set.all())
                achat.facture.montant_total = montant_total
                achat.facture.save()
                
                # Recalculer les totaux après avoir enregistré
                lignes_achat = LigneAchat.objects.filter(achat_id=id_achat)
                for ligne in lignes_achat:
                    if ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    else:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_achat)
                
                # Laisser l'ID de la commande dans la session pour le réutiliser lors des prochaines actions
                
                messages.info(request, "Le transfert est effectué.")
                return render(request, 'pgi/bon_achat_pgi.html', {
                    'selected_achat': selected_achat,
                    'lignes_achat': lignes_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_achat_data': zip(ligne_formset, lignes_achat),
                    'produits': Produit.objects.all(),
                })
            else:
                # Si erreur voir commande pour code de gestion d'erreur
                # Renvoyer la vue avec les données précédentes et le total recalculé
                lignes_achat = LigneAchat.objects.filter(achat_id=id_achat)
                for ligne in lignes_achat:
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_achat)
                
                return render(request, 'pgi/bon_achat_pgi.html', {
                    'selected_achat': selected_achat,
                    'form': None,  # Pas besoin du formulaire de sélection de l'achat ici
                    'lignes_achat': lignes_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_achat_data': zip(ligne_formset, lignes_achat),
                    'produits': Produit.objects.all(),
                })

        elif 'delete_info' in request.POST:
            id_achat = request.POST.get('achat')
            if id_achat:  
                info_to_delete = get_object_or_404(Achat, id_achat=id_achat)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:bon_achat_pgi')
            else:
                form.add_error('achat', 'Information non trouvée')
        elif 'create_form' in request.POST: 
            return redirect("pgi:bon_achat_pgi_create")
        elif 'cherche_form' in request.POST:
            cherche_form = ChercheAchatForm(request.POST)
            if cherche_form.is_valid():
                id_achat = cherche_form.cleaned_data['achat_search']
                try:
                    affiche_form = Achat.objects.get(id_achat=id_achat)
                    detail_achat = [affiche_form]
                    lignes_achat = LigneAchat.objects.filter(achat=affiche_form)
                    total_general = sum(ligne.prix_unitaire * ligne.quantite for ligne in lignes_achat)
                except Achat.DoesNotExist:
                    detail_achat = []
                    lignes_achat = []
                    total_general = 0
                return render(request, 'pgi/bon_achat_pgi.html', {
                    'form': form, 
                    'edit_form': edit_form, 
                    'affiche_form': affiche_form,
                    'cherche_form': cherche_form,
                    'bon_achat_list': bon_achat_list,
                    'lignes_achat': lignes_achat,
                    'detail_achat': detail_achat,  
                    'total_general': total_general 
                })
        elif 'retour' in request.POST:
                return redirect("pgi:bon_achat_pgi")
        else:
            cherche_form = ChercheAchatForm()
    return render(request, 'pgi/bon_achat_pgi.html', {'form': form, 'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'bon_achat_list': bon_achat_list})

##
#View permettant de créer le bon d'achat
##
@login_required 
def bon_achat_pgi_create(request):
    LigneAchatFormSetC = inlineformset_factory(Achat, LigneAchat, form=LigneAchatFormC, extra=request.session.get('nb_ligne', 1), can_delete=True)

    if request.method == 'POST':
        form_achat = AchatForm(request.POST)
        
        if form_achat.is_valid():  
            achat = form_achat.save(commit=False)  # Crée le bon d'achat sans la sauvegarder pour l'instant
            achat.save()  
            formset_lignes = LigneAchatFormSetC(request.POST, instance=achat)  
            supprimer_commandes_sans_lignes()

            if 'ajout_ligne' in request.POST:
                request.session['nb_ligne'] += 1
                formset_lignes = LigneAchatFormSetC(instance=achat)
                return render(request, 'pgi/bon_achat_pgi_create.html', {
                    'form_achat': form_achat,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'suppr_ligne' in request.POST:
                request.session['nb_ligne'] -= 1
                formset_lignes = LigneAchatFormSetC(instance=achat) 
                return render(request, 'pgi/bon_achat_pgi_create.html', {
                    'form_achat': form_achat,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'confirme' in request.POST:
                if form_achat.is_valid() and formset_lignes.is_valid():
                    achat.save()
                    lignes = formset_lignes.save(commit=False)
                    for ligne in lignes:
                        if ligne not in formset_lignes.deleted_objects:
                            produit_id = ligne.produit_id
                            if produit_id:
                                produit = Produit.objects.get(id_produit=produit_id)
                                ligne.prix_unitaire = produit.prix_unitaire
                                ligne.achat = achat
                                ligne.save()
                    formset_lignes.save()
                    supprimer_commandes_sans_lignes()
                    messages.success(request, "La création a été effectuée.")
                    request.session['nb_ligne'] = 1
                    return redirect('pgi:bon_achat_pgi')
                else:
                    for form in formset_lignes:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"Erreur dans un champ")
        else:
            messages.error(request, "Modifiez le haut de l'achat (ex: la date JJ-MM-AAAA)")
            request.session['nb_ligne'] = 1
            formset_lignes = LigneAchatFormSetC()
    else:
        request.session['nb_ligne'] = 1
        form_achat = AchatForm()
        formset_lignes = LigneAchatFormSetC()

    return render(request, 'pgi/bon_achat_pgi_create.html', {
        'form_achat': form_achat,
        'formset_lignes': formset_lignes,
        'produits': Produit.objects.all(),
    })

##
#View dirigeant urls.py modification de la facture d'achat
##
@login_required 
def facture_achat_pgi(request):
    form = SelectFactureAchatForm(request.POST or None)
    affiche_form = None
    modify_form = None
    edit_form = None
    cherche_form = None
    facture_achat_list = None 
    if request.method == "POST":
        if 'affiche_form' in request.POST:
            if form.is_valid():
                selected_facture_achat = form.cleaned_data['facture_achat']    
                detail_facture_achat = FactureAchat.objects.filter(id_facture_achat=selected_facture_achat.id_facture_achat)
                detail_identite = Identite.objects.filter(id_identite=1)
                detail_fournisseur = Fournisseur.objects.filter(id_fournisseur=selected_facture_achat.fournisseur.id_fournisseur)
                lignes_facture_achat = LigneFactureAchat.objects.filter(facture_achat_id=selected_facture_achat.id_facture_achat)
                for ligne in lignes_facture_achat:
                    if ligne.remise and ligne.remise.taux:
                        if ligne.tva and ligne.tva.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100)) * (1 - (ligne.remise.taux / 100))
                        else:ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    elif ligne.tva and ligne.tva.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))
                    else:ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_facture_achat)
                affiche_form = EditFactureAchatForm(instance=selected_facture_achat)
                return render(request, 'pgi/facture_achat_pgi.html', {
                    'form': form,  # navbar 
                    'affiche_form': affiche_form,
                    'lignes_facture_achat': lignes_facture_achat,
                    'detail_facture_achat': detail_facture_achat,
                    'detail_identite': detail_identite,
                    'detail_fournisseur': detail_fournisseur,  
                    'total_general': total_general 
                })
        elif 'choix_modif' in request.POST:
            form = SelectFactureAchatForm(request.POST)
            if form.is_valid():
                selected_facture_achat = form.cleaned_data['facture_achat']

                # Créer les formulaires pour l'affichage de la modification en fonction de selected_facture_achat
                edit_form = EditFactureAchatForm(instance=selected_facture_achat) 
                LigneFactureAchatFormSet = modelformset_factory(LigneFactureAchat, form=LigneFactureAchatForm, extra=0)
                ligne_formset = LigneFactureAchatFormSet(queryset=LigneFactureAchat.objects.filter(facture_achat=selected_facture_achat.id_facture_achat))

                # Récupérer les totaux
                lignes_facture_achat = LigneFactureAchat.objects.filter(facture_achat_id=selected_facture_achat.id_facture_achat)
                for ligne in lignes_facture_achat:
                    if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))* (1 - (ligne.remise.taux / 100))
                    elif ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    elif ligne.tva and ligne.tva.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))
                    else:ligne.total_ligne = ligne.quantite * ligne.prix_unitaire 
                total_general = sum(ligne.total_ligne for ligne in lignes_facture_achat)

                # Mise en session de l'id de la facture de vente
                request.session['selected_facture_achat_id'] = encrypt_value(selected_facture_achat.id_facture_achat)

                return render(request, 'pgi/facture_achat_pgi.html', {
                    'selected_facture_achat': selected_facture_achat,
                    'form': form, # Navbar principale
                    'lignes_facture_achat': lignes_facture_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_facture_achat_data': zip(ligne_formset, lignes_facture_achat),
                })

        elif 'modification' in request.POST:
            # Vérifier que l'ID de la facture d'achat est dans la session
            selected_facture_achat_id_encrypted = request.session.get('selected_facture_achat_id')
            if selected_facture_achat_id_encrypted is None:
                # Si l'ID de la facture d'achat n'est pas dans la session, rediriger vers la page de sélection de facture d'achat
                messages.error(request, "Aucune commande sélectionnée. Veuillez en sélectionner une.")
                return redirect('pgi:selection_commande') 
            
            # Déchiffrer l'ID de la facture depuis la session
            id_facture_achat = decrypt_value(selected_facture_achat_id_encrypted)
            selected_facture_achat = get_object_or_404(FactureAchat, id_facture_achat=id_facture_achat)
            
            # Créer les formulaires avec les données de la facture d'achat
            edit_form = EditFactureAchatForm(request.POST, instance=selected_facture_achat)
            LigneFactureAchatFormSet = modelformset_factory(LigneFactureAchat, form=LigneFactureAchatForm, extra=0)
            ligne_formset = LigneFactureAchatFormSet(request.POST, queryset=LigneFactureAchat.objects.filter(facture_achat=selected_facture_achat))
            
            if edit_form.is_valid() and ligne_formset.is_valid():
                facture = edit_form.save()

                # Sauvegarder les lignes de facture modifiées
                for ligne in ligne_formset:
                    if ligne.instance.produit:
                        ligne.instance.prix_unitaire = ligne.instance.produit.prix_unitaire
                    
                    # Récupération de l'ancien stock et de l'ancienne quantité
                    ligne_facture_achat = LigneFactureAchat.objects.get(id_ligne_facture_achat=ligne.instance.id_ligne_facture_achat)
                    produit_ancien = ligne_facture_achat.produit 
                    ancien_stock = produit_ancien.stock
                    ancienne_quantite_facture = ligne_facture_achat.quantite  
                    ligne.save()

                    # Récupération de la nouvelle quantité et modification du stock
                    nouvelle_quantite_facture = ligne.instance.quantite  
                    produit_modifie = Produit.objects.get(id_produit=ligne.instance.produit.id_produit)
                    produit_modifie.stock = ancien_stock - (ancienne_quantite_facture - nouvelle_quantite_facture)
                    identite = get_object_or_404(Identite, pk=1)
                    if identite.stock_securite is not None:
                        if produit_modifie.stock < identite.stock_securite:
                            messages.warning(request, "Attention : Stock de sécurité dépassé !")
                    else:
                            messages.warning(request, "Aucun stock de sécurité défini pour ce produit.")
                    produit_modifie.save()

                    # Recalculer les totaux après avoir sauvegardé toutes les lignes
                    lignes_facture_achat = LigneFactureAchat.objects.filter(facture_achat_id=id_facture_achat)
                    total_general = 0 

                    for ligne in lignes_facture_achat:
                        if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100)) * (1 - (ligne.remise.taux / 100))
                        elif ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                        elif ligne.tva and ligne.tva.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))
                        else:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                        ligne.montant_ligne = ligne.total_ligne
                        ligne.save()  # Sauvegarder chaque ligne après mise à jour du total

                        # Ajouter le total de chaque ligne à total_general
                        total_general += ligne.total_ligne

                    # Sauvegarde du total général dans la facture
                    facture.montant_total = total_general
                    facture.save()

                    # Ne pas supprimer l'ID de la facture d'achat dans la session
                    messages.info(request, "La modification est effectuée.")
                return render(request, 'pgi/facture_achat_pgi.html', {
                    'selected_facture_achat': selected_facture_achat,
                    'lignes_facture_achat': lignes_facture_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_facture_achat_data': zip(ligne_formset, lignes_facture_achat),
                })
            else:
                # Si erreur voir commande pour code de gestion d'erreur
                # Renvoyer la vue avec les données précédentes et le total recalculé
                lignes_facture_achat = LigneFactureAchat.objects.filter(facture_achat_id=id_facture_achat)
                for ligne in lignes_facture_achat:
                    if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))* (1 - (ligne.remise.taux / 100))
                    elif ligne.remise and ligne.remise.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                    elif ligne.tva and ligne.tva.taux:
                        ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))
                    else:ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                total_general = sum(ligne.total_ligne for ligne in lignes_facture_achat)
                
                return render(request, 'pgi/facture_achat_pgi.html', {
                    'selected_facture_achat': selected_facture_achat,
                    'form': None,  # Pas besoin du formulaire de sélection de la facture ici
                    'lignes_facture_achat': lignes_facture_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'total_general': total_general,
                    'lignes_facture_achat_data': zip(ligne_formset, lignes_facture_achat),
                    'produits': Produit.objects.all(),
                })

        elif 'delete_info' in request.POST:
            id_facture_achat = request.POST.get('facture_achat')
            if id_facture_achat:  
                info_to_delete = get_object_or_404(FactureAchat, id_facture_achat=id_facture_achat)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:facture_achat_pgi')
            else:
                form.add_error('facture_achat', 'Information non trouvée')
        elif 'create_form' in request.POST: 
            return redirect("pgi:facture_achat_pgi_create")
        elif 'cherche_form' in request.POST:
            cherche_form = ChercheFactureAchatForm(request.POST)
            if cherche_form.is_valid():
                id_facture_achat = cherche_form.cleaned_data['facture_achat_search']
                try:
                    affiche_form = FactureAchat.objects.get(id_facture_achat=id_facture_achat)
                    detail_facture_achat = [affiche_form]
                    lignes_facture_achat = LigneFactureAchat.objects.filter(facture_achat=affiche_form)
                    total_general = sum(ligne.prix_unitaire * ligne.quantite for ligne in lignes_facture_achat)
                except FactureAchat.DoesNotExist:
                    detail_facture_achat = []
                    lignes_facture_achat = []
                    total_general = 0
                return render(request, 'pgi/facture_achat_pgi.html', {
                    'form': form, 
                    'edit_form': edit_form, 
                    'affiche_form': affiche_form,
                    'cherche_form': cherche_form,
                    'facture_achat_list': facture_achat_list,
                    'lignes_facture_achat': lignes_facture_achat,
                    'detail_facture_achat': detail_facture_achat,  
                    'total_general': total_general 
                })
        elif 'retour' in request.POST:
                return redirect("pgi:facture_achat_pgi")
        else:
            cherche_form = ChercheFactureAchatForm()
    return render(request, 'pgi/facture_achat_pgi.html', {'form': form, 'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'facture_achat_list': facture_achat_list})

##
#View permettant de créer la facture d'achat
##
@login_required 
def facture_achat_pgi_create(request):
    LigneFactureAchatFormSetC = inlineformset_factory(FactureAchat, LigneFactureAchat, form=LigneFactureAchatFormC, extra=request.session.get('nb_ligne', 1), can_delete=True)

    if request.method == 'POST':
        form_facture_achat = FactureAchatForm(request.POST)
        
        if form_facture_achat.is_valid():  
            facture_achat = form_facture_achat.save(commit=False)  # Crée la facture sans la sauvegarder pour l'instant
            facture_achat.save()  
            formset_lignes = LigneFactureAchatFormSetC(request.POST, instance=facture_achat)  # Associe la facture validée aux lignes
            supprimer_factures_sans_lignes()

            if 'ajout_ligne' in request.POST:
                # Ajout de ligne sans validation de la facture
                request.session['nb_ligne'] += 1
                formset_lignes = LigneFactureAchatFormSetC(instance=facture_achat)  # Actualise le formset avec la nouvelle facture
                return render(request, 'pgi/facture_achat_pgi_create.html', {
                    'form_facture_achat': form_facture_achat,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'suppr_ligne' in request.POST:
                request.session['nb_ligne'] -= 1
                formset_lignes = LigneFactureAchatFormSetC(instance=facture_achat)
                return render(request, 'pgi/facture_achat_pgi_create.html', {
                    'form_facture_achat': form_facture_achat,
                    'formset_lignes': formset_lignes,
                    'produits': Produit.objects.all(),
                })
            elif 'transfert' in request.POST:
                1==1
            elif 'confirme' in request.POST:
                if form_facture_achat.is_valid() and formset_lignes.is_valid():
                    facture_achat.save()
                    lignes = formset_lignes.save(commit=False)
                    total_general = 0  # Initialisation du total général

                    for ligne in lignes:
                        if ligne not in formset_lignes.deleted_objects:
                            produit_id = ligne.produit_id
                            if produit_id:
                                produit = Produit.objects.get(id_produit=produit_id)
                                ligne.prix_unitaire = produit.prix_unitaire
                                ligne.facture_achat = facture_achat
                                ligne.save()
                                # Diminution du stock et avertissement si nécessaire.
                                produit.stock += ligne.quantite
                                identite = get_object_or_404(Identite, pk=1)
                                if produit.stock<identite.stock_securite:
                                    messages.warning(request, "Attention : Stock de sécurité dépassé !")
                                produit.save()

                        # Calcul des totaux pour chaque ligne
                        if ligne.tva and ligne.tva.taux and ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100)) * (1 - (ligne.remise.taux / 100))
                        elif ligne.remise and ligne.remise.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 - (ligne.remise.taux / 100))
                        elif ligne.tva and ligne.tva.taux:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire * (1 + (ligne.tva.taux / 100))                        
                        else:
                            ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                        ligne.montant_ligne = ligne.total_ligne
                        ligne.save()
                        
                        # Ajouter le total de chaque ligne à total_general
                        total_general += ligne.total_ligne if ligne.total_ligne else 0

                    # Enregistrement du total_general dans la facture
                    facture_achat.montant_total = total_general
                    facture_achat.save()
                    formset_lignes.save()
                    supprimer_factures_sans_lignes()
                    messages.success(request, "La création a été effectuée.")
                    request.session['nb_ligne'] = 1
                    return redirect('pgi:facture_achat_pgi')
                else:
                    for form in formset_lignes:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"Erreur dans le champ {field} : {error}")
        else:
            messages.error(request, "Modifiez le haut de la facture (ex: la date JJ-MM-AAAA)")
            request.session['nb_ligne'] = 1
            formset_lignes = LigneFactureAchatFormSetC()
        
    else:
        request.session['nb_ligne'] = 1
        form_facture_achat = FactureAchatForm()
        formset_lignes = LigneFactureAchatFormSetC()

    return render(request, 'pgi/facture_achat_pgi_create.html', {
        'form_facture_achat': form_facture_achat,
        'formset_lignes': formset_lignes,
        'produits': Produit.objects.all(),
    })


##
#View dirigeant l'identité de l'entreprise
##
@login_required 
def identite_pgi(request):
    try:
        identite = Identite.objects.get()
    except Identite.DoesNotExist:
        identite = None
    if request.method == "POST":
        if identite:
            identite_form = ChangeIdentiteForm(request.POST, instance=identite)
            if identite_form.is_valid():
                identite_form.save()
                messages.info(request, ("Modification effectuée."))
                return redirect('pgi:identite_pgi')
        else:
            identite_form = ChangeIdentiteForm(request.POST)
            if identite_form.is_valid():
                identite_form.save()
                messages.info(request, ("Création effectuée."))
                return redirect('pgi:identite_pgi')
    else:
        if identite:
            identite_form = ChangeIdentiteForm(instance=identite)
        else:
            identite_form = ChangeIdentiteForm()
    return render(request, 'pgi/identite_pgi.html', {
        'identite_form': identite_form,
        'identite_existe': bool(identite)
    })

##
#View dirigeant urls.py périodes du pgi
##
@login_required 
def periode_pgi(request):
    identite = get_object_or_404(Identite, pk=1)
    if request.method == 'POST':
        form = ChangePeriodeForm(request.POST, instance=identite)
        if form.is_valid():
            form.save()  
            messages.success(request, "La période comptable est modifiée.")
            return redirect('pgi:periode_pgi') 
    else:
        form = ChangePeriodeForm(instance=identite)
    
    return render(request, 'pgi/periode_pgi.html',{'form': form, 'identite': identite})

##
#View dirigeant urls.py le stock de sécurité du pgi
##
@login_required 
def stock_securite_pgi(request):
    identite = get_object_or_404(Identite, pk=1)
    if request.method == 'POST':
        form = ChangeStockSecuriteForm(request.POST, instance=identite)
        if form.is_valid():
            form.save()  
            messages.success(request, "Le stock de sécurité est modifié.")
            return redirect('pgi:stock_securite_pgi') 
    else:
        form = ChangeStockSecuriteForm(instance=identite)
    
    return render(request, 'pgi/stock_securite_pgi.html',{'form': form, 'identite': identite})

##
#View dirigeant urls.py modification de la TVA
##
@login_required 
def tva_pgi(request):
    create_form = None
    modify_form = None
    edit_form = None
    form = SelectTvaForm(request.POST or None) 

    if request.method == "POST" :
        if 'create_form' in request.POST: 
            form = '' 
            create_form = CreateTvaForm()
        elif 'modif_form' in request.POST:
            form = SelectTvaForm(request.POST)
            if form.is_valid():
                selected_tva = form.cleaned_data['tva']
                request.session['selected_tva_id'] = encrypt_value(selected_tva.id_tva)
                modify_form = EditTvaForm(instance=selected_tva)
        elif 'create_info' in request.POST:
            create_form = CreateTvaForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                messages.info(request,("Création effectuée."))
                return redirect('pgi:tva_pgi')
        elif 'delete_info' in request.POST:
            id_tva = request.POST.get('tva')
            if id_tva:  
                info_to_delete = get_object_or_404(Tva, id_tva=id_tva)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:tva_pgi')
            else:
                form.add_error('tva', 'Information non trouvée') 
        elif 'modif_info' in request.POST:
            selected_tva_id = request.session.get('selected_tva_id')
            if not selected_tva_id:
                return redirect('pgi:tva_pgi')
            id_tva = decrypt_value(selected_tva_id)
            selected_info = get_object_or_404(Tva, id_tva=id_tva)
            edit_form = EditTvaForm(request.POST, instance=selected_info)    
            if edit_form.is_valid():
                edit_form.save()
                messages.info(request, "La modification est effectuée.")
                return redirect('pgi:tva_pgi')
            else:
                del request.session['selected_tva_id']
                messages.info(request, "Les informations ne sont pas valides.")
                return redirect("pgi:tva_pgi")
        elif 'retour' in request.POST:
                return redirect("pgi:tva_pgi")
        else:
            return redirect("pgi:tva_pgi")
    return render(request, 'pgi/tva_pgi.html', {'form': form, 'create_form': create_form,  'modify_form': modify_form, 'edit_form': edit_form})

##
#View dirigeant urls.py modification des remises et escomptes
##
@login_required 
def remise_pgi(request):
    create_form = None
    modify_form = None
    edit_form = None
    form = SelectRemiseForm(request.POST or None) 

    if request.method == "POST" :
        if 'create_form' in request.POST: 
            form = '' 
            create_form = CreateRemiseForm()
        elif 'modif_form' in request.POST:
            form = SelectRemiseForm(request.POST)
            if form.is_valid():
                selected_remise = form.cleaned_data['remise']
                request.session['selected_remise_id'] = encrypt_value(selected_remise.id_remise)
                modify_form = EditRemiseForm(instance=selected_remise)
        elif 'create_info' in request.POST:
            create_form = CreateRemiseForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                messages.info(request,("Création effectuée."))
                return redirect('pgi:remise_pgi')
        elif 'delete_info' in request.POST:
            id_tva = request.POST.get('remise')
            if id_remise:  
                info_to_delete = get_object_or_404(Remise, id_remise=id_remise)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:remise_pgi')
            else:
                form.add_error('remise', 'Information non trouvée') 
        elif 'modif_info' in request.POST:
            selected_remise_id = request.session.get('selected_remise_id')
            if not selected_remise_id:
                return redirect('pgi:remise_pgi')
            id_remise = decrypt_value(selected_remise_id)
            selected_info = get_object_or_404(Remise, id_remise=id_remise)
            edit_form = EditRemiseForm(request.POST, instance=selected_info)    
            if edit_form.is_valid():
                edit_form.save()
                messages.info(request, "La modification est effectuée.")
                return redirect('pgi:remise_pgi')
            else:
                del request.session['selected_remise_id']
                messages.info(request, "Les informations ne sont pas valides.")
                return redirect("pgi:remise_pgi")
        elif 'retour' in request.POST:
                return redirect("pgi:remise_pgi")
        else:
            return redirect("pgi:remise_pgi")
    return render(request, 'pgi/remise_pgi.html', {'form': form, 'create_form': create_form,  'modify_form': modify_form, 'edit_form': edit_form})

##
#View dirigeant urls.py gestion des stocks
##
@login_required 
def gestion_stock_pgi(request):
    # Récupération du stock de sécurité et du formulaire :
    identite = get_object_or_404(Identite, pk=1)
    stock_securite = identite.stock_securite
    type_stock_form = ChoixTypeStockForm(request.POST or None) 
    produits_undersec = [] 

    if request.method == "POST":

        if type_stock_form.is_valid():
            type_stock = type_stock_form.cleaned_data['type_stock']
            #messages.info(request, f"Analyse du type de stock: {type_stock}")

            # Vérification que stock_securite est défini et valide
            if stock_securite is not None:
                # Récupération des produits dont le stock est inférieur au stock de sécurité
                produits_undersec = Produit.objects.filter(
                    type_stock=type_stock,  
                    stock__lt=stock_securite  # Filtre par stock et stock de sécurité
                )
            else:
                messages.warning(request, "Le stock de sécurité n'est pas défini.")

            return render(request, 'pgi/gestion_stock_pgi.html', {
                'stock_securite': stock_securite,
                'type_stock': type_stock,
                'produits_undersec': produits_undersec, 
                'type_stock_form': type_stock_form
            })
        else:
            messages.error(request, "Formulaire non valide.")
            messages.error(request, type_stock_form.errors)
            
    return render(request, 'pgi/gestion_stock_pgi.html', {
        'type_stock_form': type_stock_form,
    })

##
#View dirigeant urls.py modification du plan comptable
##
@login_required 
def plan_comptable_pgi(request):
    create_form = None
    modify_form = None
    edit_form = None
    form = SelectPlanComptableForm(request.POST or None) 

    if request.method == "POST" :
        if 'create_form' in request.POST: 
            form = '' 
            create_form = CreatePlanComptableForm()
        elif 'modif_form' in request.POST:
            form = SelectPlanComptableForm(request.POST)
            identite = Identite.objects.first()
            if form.is_valid():
                selected_plan_comptable = form.cleaned_data['plan_comptable']
                request.session['selected_plan_comptable_id'] = encrypt_value(selected_plan_comptable.id_plan_comptable)
                modify_form = EditPlanComptableForm(instance=selected_plan_comptable)
        elif 'create_info' in request.POST:
            create_form = CreatePlanComptableForm(request.POST)
            identite = Identite.objects.first()
            if create_form.is_valid():
                create_form.save()
                messages.info(request,("Création effectuée."))
                return redirect('pgi:plan_comptable_pgi')
        elif 'delete_info' in request.POST:
            id_plan_comptable = request.POST.get('plan_comptable')
            if id_plan_comptable:  
                info_to_delete = get_object_or_404(PlanComptable, id_plan_comptable=id_plan_comptable)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:plan_comptable_pgi')
            else:
                form.add_error('plan_comptable', 'Information non trouvée') 
        elif 'modif_info' in request.POST:
            # Modification par formulaire avec l'id de session
            id_plan_comptable = decrypt_value(request.session.get('selected_plan_comptable_id')) if request.session.get('selected_plan_comptable_id') else redirect('pgi:plan_comptable_pgi')
            selected_info = get_object_or_404(PlanComptable, id_plan_comptable=id_plan_comptable)
            edit_form = EditPlanComptableForm(request.POST, instance=selected_info)    
            if edit_form.is_valid():
                edit_form.save()
                del request.session['selected_plan_comptable_id']
                messages.info(request, "La modification est effectuée.")
                return redirect('pgi:plan_comptable_pgi')
            else:
                del request.session['selected_plan_comptable_id']
                messages.info(request, "Les informations ne sont pas valides.")
                return redirect("pgi:plan_comptable_pgi")
        elif 'retour' in request.POST:
                return redirect("pgi:plan_comptable_pgi")
        else:
            return redirect("pgi:plan_comptable_pgi")
    return render(request, 'pgi/plan_comptable_pgi.html', {'form': form, 'create_form': create_form,  'modify_form': modify_form, 'edit_form': edit_form})

##
#View dirigeant urls.py grand livre
##
@login_required 
def grand_livre_pgi(request):

    # Récupération de la période :
    identite = get_object_or_404(Identite, pk=1)
    periode = identite.periode

    # Récupération des totaux débits crédits:
    plan_comptable = PlanComptable.objects.filter(numero__gte=1, numero__lte=799999).order_by('numero')
    total_debit = plan_comptable.aggregate(total=Sum('debit'))['total']
    total_credit = plan_comptable.aggregate(total=Sum('credit'))['total']

    # Calcul du résultat
    plan_comptable = PlanComptable.objects.filter(numero__gte=1, numero__lte=799999).order_by('numero')
    plan_comptable = plan_comptable.filter(Q(numero__startswith='6')|Q(numero__startswith='7')).order_by('numero')
    total_debitr = plan_comptable.aggregate(total=Sum('debit'))['total']
    total_creditr = plan_comptable.aggregate(total=Sum('credit'))['total']
    benefice = 0
    perte = total_debitr - total_creditr
    total_cumul = total_debit
    if perte < 0:
        benefice = total_creditr - total_debitr
        perte = 0
        total_cumul = total_credit

    plan_comptable = PlanComptable.objects.filter(numero__gte=1, numero__lte=799999).order_by('numero')

    return render(request, 'pgi/grand_livre_pgi.html',{
    'periode': periode,
    'plan_comptable':plan_comptable,
    'total_debit':total_debit,
    'total_credit':total_credit,
    'benefice':benefice,
    'perte':perte,
    'total_cumul':total_cumul
    })

##
#View dirigeant urls.py bilan
##
@login_required 
def compte_resultat_pgi(request):

    # Récupération de la période :
    identite = get_object_or_404(Identite, pk=1)
    periode = identite.periode

    # Récupération des totaux débits crédits:
    plan_comptable = PlanComptable.objects.filter(numero__gte=1, numero__lte=799999).order_by('numero')
    plan_comptable = plan_comptable.filter(Q(numero__startswith='6')|Q(numero__startswith='7')).order_by('numero')
    total_debit = plan_comptable.aggregate(total=Sum('debit'))['total']
    total_credit = plan_comptable.aggregate(total=Sum('credit'))['total']

    # Calcul des achat 60
    plan_comptable60 = plan_comptable.filter(Q(numero__startswith='60')).order_by('numero')
    charge60 = plan_comptable60.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des services extérieurs 6162
    plan_comptable6162 = plan_comptable.filter(Q(numero__startswith='61')|Q(numero__startswith='62')).order_by('numero')
    charge6162 = plan_comptable6162.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des impôts et taxes 63
    plan_comptable63 = plan_comptable.filter(Q(numero__startswith='63')).order_by('numero')
    charge63 = plan_comptable63.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des charges de personnel 64
    plan_comptable64 = plan_comptable.filter(Q(numero__startswith='64')).order_by('numero')
    charge64 = plan_comptable64.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des charges financières et autres 65666769
    plan_comptable65666769 = plan_comptable.filter(Q(numero__startswith='65')|Q(numero__startswith='66')|Q(numero__startswith='67')|Q(numero__startswith='69')).order_by('numero')
    charge65666769 = plan_comptable65666769.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des dotations 68
    plan_comptable68 = plan_comptable.filter(Q(numero__startswith='68')).order_by('numero')
    charge68 = plan_comptable68.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des ventes de produits 70
    plan_comptable70 = plan_comptable.filter(Q(numero__startswith='70')).order_by('numero')
    produit70 = plan_comptable70.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul des productions stockées et immobilisées 7172
    plan_comptable7172 = plan_comptable.filter(Q(numero__startswith='71')|Q(numero__startswith='72')).order_by('numero')
    produit7172 = plan_comptable7172.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul des Autres productions 737475
    plan_comptable737475 = plan_comptable.filter(Q(numero__startswith='73')|Q(numero__startswith='74')|Q(numero__startswith='75')).order_by('numero')
    produit737475 = plan_comptable737475.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul des ventes de produits financiers 76
    plan_comptable76 = plan_comptable.filter(Q(numero__startswith='76')).order_by('numero')
    produit76 = plan_comptable76.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul des Autres productions 777879
    plan_comptable777879 = plan_comptable.filter(Q(numero__startswith='77')|Q(numero__startswith='78')|Q(numero__startswith='79')).order_by('numero')
    produit777879 = plan_comptable777879.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul du résultat
    benefice = 0
    perte = total_debit - total_credit
    total_cumul = total_debit
    if perte < 0:
        benefice = total_credit - total_debit
        perte = 0
        total_cumul = total_credit

    return render(request, 'pgi/compte_resultat_pgi.html',{
    'periode': periode,
    'benefice':benefice,
    'perte':perte,
    'total_cumul':total_cumul,
    'charge60':charge60,
    'charge6162':charge6162,
    'charge63':charge63,
    'charge64':charge64,
    'charge65666769':charge65666769,
    'charge68':charge68,
    'produit70':produit70,
    'produit7172':produit7172,
    'produit737475':produit737475,
    'produit76':produit76,
    'produit777879':produit777879,
    })

##
#View dirigeant urls.py bilan
##
@login_required 
def bilan_pgi(request):

    # Récupération de la période :
    identite = get_object_or_404(Identite, pk=1)
    periode = identite.periode

    # Récupération des totaux débits crédits:
    plan_comptable = PlanComptable.objects.filter(numero__gte=1, numero__lte=599999).order_by('numero')
    total_debit = plan_comptable.aggregate(total=Sum('debit'))['total']
    total_credit = plan_comptable.aggregate(total=Sum('credit'))['total']

    # Calcul des immobilisations
    plan_comptable = PlanComptable.objects.filter(numero__gte=1, numero__lte=599999).order_by('numero')
    plan_comptable2 = plan_comptable.filter(Q(numero__startswith='2')).order_by('numero')
    immobilisation = plan_comptable2.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des stocks
    plan_comptable3 = plan_comptable.filter(Q(numero__startswith='3')).order_by('numero')
    stock = plan_comptable3.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des Emprunts
    plan_comptable16 = plan_comptable.filter(Q(numero__startswith='16')).order_by('numero')
    emprunt = plan_comptable16.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul du capital
    plan_comptable1 = plan_comptable.filter(Q(numero__startswith='1')).order_by('numero')
    plan_comptable1 = plan_comptable1.exclude(numero__startswith='16')
    capital = plan_comptable1.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul des créances clients
    plan_comptable41 = plan_comptable.filter(Q(numero__startswith='4')).order_by('numero')
    creance = plan_comptable41.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des dettes fournisseurs
    plan_comptable40 = plan_comptable.filter(Q(numero__startswith='4')).order_by('numero')
    dette = plan_comptable40.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul des banques débiteur
    plan_comptable5d = plan_comptable.filter(Q(numero__startswith='5')).order_by('numero')
    banqued = plan_comptable5d.aggregate(total=Sum('debit'))['total'] or 0

    # Calcul des banques créditeur
    plan_comptable5c = plan_comptable.filter(Q(numero__startswith='5')).order_by('numero')
    banquec = plan_comptable5c.aggregate(total=Sum('credit'))['total'] or 0

    # Calcul du résultat
    plan_comptable = PlanComptable.objects.filter(numero__gte=1, numero__lte=799999).order_by('numero')
    plan_comptable = plan_comptable.filter(Q(numero__startswith='6')|Q(numero__startswith='7')).order_by('numero')
    total_debitr = plan_comptable.aggregate(total=Sum('debit'))['total']
    total_creditr = plan_comptable.aggregate(total=Sum('credit'))['total']
    perte = 0
    benefice = total_creditr - total_debitr
    total_cumulc = total_credit + benefice
    total_cumuld = total_debit
    if benefice < 0:
        perte = total_debitr - total_creditr
        benefice = 0
        total_cumuld = total_debit + perte
        total_cumulc = total_credit

    return render(request, 'pgi/bilan_pgi.html',{
    'periode': periode,
    'benefice':benefice,
    'perte':perte,
    'total_cumuld':total_cumuld,
    'total_cumulc':total_cumulc,
    'capital':capital,
    'immobilisation':immobilisation,
    'stock':stock,
    'emprunt':emprunt,
    'creance':creance,
    'dette':dette,
    'banqued':banqued,
    'banquec':banquec,
    })

##
#View dirigeant urls.py modification des enregistrements comptables
##
@login_required 
def ecriture_comptable_pgi(request):
    form = SelectEcritureComptableForm(request.POST or None)
    affiche_form = None
    modify_form = None
    edit_form = None
    cherche_form = None
    ecriture_comptable_list = None 
    if request.method == "POST":
        if 'affiche_form' in request.POST:
            if form.is_valid():
                selected_ecriture_comptable = form.cleaned_data['ecriture_comptable']    
                detail_ecriture_comptable = EcritureComptable.objects.filter(id_ecriture_comptable=selected_ecriture_comptable.id_ecriture_comptable)
                detail_identite = Identite.objects.filter(id_identite=1)
                lignes_ecriture_comptable = LigneEcritureComptable.objects.filter(ecriture_comptable_id=selected_ecriture_comptable.id_ecriture_comptable)
                affiche_form = EditEcritureComptableForm(instance=selected_ecriture_comptable)
                return render(request, 'pgi/ecriture_comptable_pgi.html', {
                    'form': form,  # navbar 
                    'affiche_form': affiche_form,
                    'lignes_ecriture_comptable': lignes_ecriture_comptable,
                    'detail_ecriture_comptable': detail_ecriture_comptable,
                    'detail_identite': detail_identite,
                })
        elif 'choix_modif' in request.POST:
            form = SelectEcritureComptableForm(request.POST)
            if form.is_valid():
                selected_ecriture_comptable = form.cleaned_data['ecriture_comptable']
                # Récupérer les lignes des écritures comptables
                lignes_ecriture_comptable = LigneEcritureComptable.objects.filter(ecriture_comptable_id=selected_ecriture_comptable.id_ecriture_comptable)
                
                # Créer les formulaires
                edit_form = EditEcritureComptableForm(instance=selected_ecriture_comptable)  # Pas besoin de POST ici, juste une instance pour l'édition
                LigneEcritureComptableFormSet = modelformset_factory(LigneEcritureComptable, form=LigneEcritureComptableForm, extra=0)
                ligne_formset = LigneEcritureComptableFormSet(queryset=LigneEcritureComptable.objects.filter(ecriture_comptable=selected_ecriture_comptable))

                # Récupération des anciens montant debit/credit associés à un numero de plan comptable de l'écriture et mise en session.
                initial_values = {}
                for ligne in ligne_formset:
                    plan_comptable = ligne.instance.plan_comptable  
                    debit = ligne.instance.debit
                    credit = ligne.instance.credit
                    initial_values[str(plan_comptable.numero)] = {'debit': float(debit) if debit is not None else 0.0,'credit': float(credit) if credit is not None else 0.0}
                request.session['initial_values'] = initial_values
                
                # Mise en session de l'id de l'écriture comptable
                request.session['selected_ecriture_comptable_id'] = encrypt_value(selected_ecriture_comptable.id_ecriture_comptable)

                return render(request, 'pgi/ecriture_comptable_pgi.html', {
                    'selected_ecriture_comptable': selected_ecriture_comptable,
                    'form': form,
                    'lignes_ecriture_comptable': lignes_ecriture_comptable,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'lignes_ecriture_comptable_data': zip(ligne_formset, lignes_ecriture_comptable),
                })
        elif 'modification' in request.POST:

            # Récupération des valeurs initiales en session.
            initial_values = request.session.get('initial_values')

            # Vérifier que l'ID de l'écriture comptable est dans la session
            selected_ecriture_comptable_id_encrypted = request.session.get('selected_ecriture_comptable_id')
            if selected_ecriture_comptable_id_encrypted is None:
                messages.error(request, "Aucune écriture comptable sélectionnée. Veuillez en sélectionner une.")
                return redirect('pgi:ecriture_comptable') 
            
            # Déchiffrer l'ID de l'écriture comptable depuis la session
            id_ecriture_comptable = decrypt_value(selected_ecriture_comptable_id_encrypted)
            selected_ecriture_comptable = get_object_or_404(EcritureComptable, id_ecriture_comptable=id_ecriture_comptable)
            
            # Créer les formulaires avec les données des écritures comptables
            edit_form = EditEcritureComptableForm(request.POST, instance=selected_ecriture_comptable)
            LigneEcritureComptableFormSet = modelformset_factory(LigneEcritureComptable, form=LigneEcritureComptableForm, extra=0)
            ligne_formset = LigneEcritureComptableFormSet(request.POST, queryset=LigneEcritureComptable.objects.filter(ecriture_comptable=selected_ecriture_comptable))

            # Sauvegarder les lignes d'écriture comptable modifiées
            if edit_form.is_valid() and ligne_formset.is_valid():
                ecriture_comptable = edit_form.save()
                lignes_ecriture_comptable = LigneEcritureComptable.objects.filter(ecriture_comptable_id=ecriture_comptable.id_ecriture_comptable)
                
                # Enregistrer les nouvelles lignes du formset
                for ligne in ligne_formset:
                    if ligne.is_valid():
                        ligne.save()

                # Initialisation des totaux pour vérification de l'équilibrage des écritures.
                total_debit = 0
                total_credit = 0
                ecart_debit = 0
                ecart_credit = 0

                # Transfert au plan comptable (totaux du grand livre)
                for ligne in lignes_ecriture_comptable:
                    plan_comptable = ligne.plan_comptable
                    # S'assurer que les montants existants dans le PlanComptable ne sont pas None
                    montant_initial_debit = plan_comptable.debit if plan_comptable.debit is not None else 0
                    montant_initial_credit = plan_comptable.credit if plan_comptable.credit is not None else 0

                    # Calcul des écart entre les écritures
                    plan_comptable_numero = ligne.plan_comptable.numero
                    if str(plan_comptable_numero) in initial_values:
                        anciens_debits = initial_values[str(plan_comptable_numero)]['debit']
                        anciens_credits = initial_values[str(plan_comptable_numero)]['credit']
                        ecart_debit = Decimal(ligne.debit or 0) - Decimal(anciens_debits or 0)
                        ecart_credit = Decimal(ligne.credit or 0) - Decimal(anciens_credits or 0)

                        # Ajouter les écarts au montant existant du grand livre avant sauvegarde
                        plan_comptable.debit = Decimal(montant_initial_debit) + Decimal(ecart_debit or 0)
                        plan_comptable.credit = Decimal(montant_initial_credit) + Decimal(ecart_credit or 0)

                        # Accumuler les totaux pour vérifier l'équilibre ensuite
                        total_debit += ligne.debit or 0
                        total_credit += ligne.credit or 0
                        
                        # Sauvegarder le grand livre mis à jour
                    plan_comptable.save()

                # Vérification de l'équilibre des écritures comptables
                if total_debit != total_credit:
                        messages.warning(request, "Ecriture non équilibrée !")

                # Ne pas supprimer l'ID de la facture d'achat dans la session
                messages.info(request, "La modification est effectuée.")
                return render(request, 'pgi/ecriture_comptable_pgi.html', {
                    'selected_ecriture_comptable': selected_ecriture_comptable,
                    'lignes_ecriture_comptable': lignes_ecriture_comptable,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'lignes_ecriture_comptable_data': zip(ligne_formset, lignes_ecriture_comptable),
                })
            else:
                # Si erreur voir commande pour code de gestion d'erreur
                lignes_ecriture_comptable = LigneEcritureComptable.objects.filter(ecritude_comptable_id=id_ecriture_comptable)
                
                return render(request, 'pgi/ecriture_comptable_pgi.html', {
                    'selected_facture_achat': selected_facture_achat,
                    'form': None,  # Pas besoin du formulaire de sélection de la facture ici
                    'lignes_facture_achat': lignes_facture_achat,
                    'ligne_formset': ligne_formset,
                    'edit_form': edit_form,
                    'lignes_facture_achat_data': zip(ligne_formset, lignes_facture_achat),
                })

        elif 'delete_info' in request.POST:
            id_ecriture_comptable = request.POST.get('ecriture_comptable')
            if id_ecriture_comptable:  
                info_to_delete = get_object_or_404(EcritureComptable, id_ecriture_comptable=id_ecriture_comptable)
                info_to_delete.delete()
                messages.info(request,("La suppression est effectuée."))
                return redirect('pgi:ecriture_comptable_pgi')
            else:
                form.add_error('ecriture_comptable', 'Information non trouvée')
        elif 'create_form' in request.POST: 
            return redirect("pgi:ecriture_comptable_pgi_create")
        elif 'cherche_form' in request.POST:
            cherche_form = ChercheEcritureComptableForm(request.POST)
            if cherche_form.is_valid():
                id_ecriture_comptable = cherche_form.cleaned_data['ecriture_comptable_search']
                try:
                    affiche_form = EcritureComptable.objects.get(id_ecriture_comptable=id_ecriture_comptable)
                    detail_ecriture_comptable = [affiche_form]
                    lignes_ecriture_comptable = LigneEcritureComptable.objects.filter(ecriture_comptable=affiche_form)
                except EcritureComptable.DoesNotExist:
                    detail_ecriture_comptable = []
                    lignes_ecriture_comptable = []
                return render(request, 'pgi/ecriture_comptable_pgi.html', {
                    'form': form, 
                    'edit_form': edit_form, 
                    'affiche_form': affiche_form,
                    'cherche_form': cherche_form,
                    'ecriture_comptable_list': ecriture_comptable_list,
                    'lignes_ecriture_comptable': lignes_ecriture_comptable,
                    'detail_ecriture_comptable': detail_ecriture_comptable,
                })
        elif 'retour' in request.POST:
                return redirect("pgi:ecriture_comptable_pgi")
        else:
            cherche_form = ChercheEcritureComptableForm()
    return render(request, 'pgi/ecriture_comptable_pgi.html', {'form': form, 'modify_form': modify_form, 'edit_form': edit_form, 'affiche_form': affiche_form,'cherche_form': cherche_form ,'ecriture_comptable_list': ecriture_comptable_list})

##
#View permettant de créer l'écriture comptable
##
@login_required 
def ecriture_comptable_pgi_create(request):
    LigneEcritureComptableFormSetC = inlineformset_factory(EcritureComptable, LigneEcritureComptable, form=LigneEcritureComptableFormC, extra=request.session.get('nb_ligne', 1), can_delete=True)
    form_ecriture_comptable = EcritureComptableForm(request.POST or None)

    if request.method == 'POST':
        form_ecriture_comptable = EcritureComptableForm(request.POST)
        
        if form_ecriture_comptable.is_valid():  
            ecriture_comptable = form_ecriture_comptable.save(commit=False)  # Crée l'écriture sans la sauvegarder pour l'instant
            ecriture_comptable.save()  
            formset_lignes = LigneEcritureComptableFormSetC(request.POST, instance=ecriture_comptable)  # Associe l'écriture validée aux lignes
            supprimer_factures_sans_lignes() # agit aussi sur écritures.

            if 'ajout_ligne' in request.POST:
                # Ajout de ligne sans validation de l'écriture
                request.session['nb_ligne'] += 1
                formset_lignes = LigneEcritureComptableFormSetC(instance=ecriture_comptable)  # Actualise le formset 
                return render(request, 'pgi/ecriture_comptable_pgi_create.html', {
                    'form_ecriture_comptable': form_ecriture_comptable,
                    'formset_lignes': formset_lignes,
                })
            elif 'suppr_ligne' in request.POST:
                request.session['nb_ligne'] -= 1
                formset_lignes = LigneEcritureComptableFormSetC(instance=ecriture_comptable)
                return render(request, 'pgi/ecriture_comptable_pgi_create.html', {
                    'form_ecriture_comptable': form_ecriture_comptable,
                    'formset_lignes': formset_lignes,
                })
            elif 'confirme' in request.POST:
                if form_ecriture_comptable.is_valid() and formset_lignes.is_valid():

                    ecriture_comptable.save()
                    lignes = formset_lignes.save(commit=False)
                    for ligne in lignes:
                        if ligne not in formset_lignes.deleted_objects:
                                ligne.save()
                    ecriture_comptable.save()
                    formset_lignes.save()

                    # Transfert au plan comptable
                    lignes_ecriture_comptable = LigneEcritureComptable.objects.filter(ecriture_comptable_id=ecriture_comptable.id_ecriture_comptable)
                    for ligne in lignes_ecriture_comptable:
                        # Récupérer le PlanComptable associé à la ligne d'écriture
                        plan_comptable = ligne.plan_comptable                        
                        # S'assurer que les montants existants dans le PlanComptable ne sont pas None
                        montant_initial_debit = plan_comptable.debit if plan_comptable.debit is not None else 0
                        montant_initial_credit = plan_comptable.credit if plan_comptable.credit is not None else 0
                        # Ajouter les montants actuels des lignes au montant existant
                        plan_comptable.debit = montant_initial_debit + (ligne.debit or 0)
                        plan_comptable.credit = montant_initial_credit + (ligne.credit or 0)
                        # Sauvegarder le PlanComptable mis à jour
                        plan_comptable.save()

                    supprimer_factures_sans_lignes()
                    messages.success(request, "La création a été effectuée.")
                    request.session['nb_ligne'] = 1
                    return redirect('pgi:ecriture_comptable_pgi')
                else:
                    for form in formset_lignes:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"Erreur dans le champ {field} : {error}")
        else:
            messages.error(request, "Modifiez le haut de l'écriture (ex: la date JJ-MM-AAAA)")
            request.session['nb_ligne'] = 1
            formset_lignes = LigneEcritureComptableFormSetC()
        
    else:
        request.session['nb_ligne'] = 1
        form_facture_achat = EcritureComptableForm()
        formset_lignes = LigneEcritureComptableFormSetC()

    return render(request, 'pgi/ecriture_comptable_pgi_create.html', {
        'form_ecriture_comptable': form_ecriture_comptable,
        'formset_lignes': formset_lignes,
    })
