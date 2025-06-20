from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Categorie, Sujet, Message
from .forms import SujetForm, MessageForm, CategorieForm

def liste_categories(request):
    categories = Categorie.objects.filter(est_active=True).annotate(
        nombre_sujets=Count('sujets')
    )
    return render(request, 'forum/liste_categories.html', {
        'categories': categories
    })

def liste_sujets(request, categorie_slug):
    categorie = get_object_or_404(Categorie, slug=categorie_slug, est_active=True)
    sujets = categorie.sujets.all()
    return render(request, 'forum/liste_sujets.html', {
        'categorie': categorie,
        'sujets': sujets
    })

def detail_sujet(request, categorie_slug, sujet_slug):
    sujet = get_object_or_404(Sujet, slug=sujet_slug, categorie__slug=categorie_slug)
    sujet.nombre_vues += 1
    sujet.save()
    
    if request.method == 'POST' and not sujet.est_verrouille:
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sujet = sujet
            message.auteur = request.user
            message.save()
            messages.success(request, 'Votre message a été publié avec succès.')
            return redirect('forum:detail_sujet', categorie_slug=categorie_slug, sujet_slug=sujet_slug)
    else:
        form = MessageForm()
    
    return render(request, 'forum/detail_sujet.html', {
        'sujet': sujet,
        'messages_forum': sujet.messages.all(),
        'form': form
    })

@login_required
def creer_sujet(request, categorie_slug):
    categorie = get_object_or_404(Categorie, slug=categorie_slug, est_active=True)
    
    if request.method == 'POST':
        form = SujetForm(request.POST)
        if form.is_valid():
            sujet = form.save(commit=False)
            sujet.categorie = categorie
            sujet.auteur = request.user
            sujet.save()
            messages.success(request, 'Votre sujet a été créé avec succès.')
            return redirect('forum:detail_sujet', categorie_slug=categorie_slug, sujet_slug=sujet.slug)
    else:
        form = SujetForm(initial={'categorie': categorie})
    
    return render(request, 'forum/creer_sujet.html', {
        'form': form,
        'categorie': categorie
    })

@login_required
def modifier_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, auteur=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            message = form.save(commit=False)
            message.est_modifie = True
            message.save()
            messages.success(request, 'Votre message a été modifié avec succès.')
            return redirect('forum:detail_sujet', 
                          categorie_slug=message.sujet.categorie.slug,
                          sujet_slug=message.sujet.slug)
    else:
        form = MessageForm(instance=message)
    
    return render(request, 'forum/modifier_message.html', {
        'form': form,
        'message': message
    })

@login_required
def supprimer_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, auteur=request.user)
    sujet = message.sujet
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Votre message a été supprimé avec succès.')
        return redirect('forum:detail_sujet', 
                       categorie_slug=sujet.categorie.slug,
                       sujet_slug=sujet.slug)
    
    return render(request, 'forum/supprimer_message.html', {
        'message': message
    })
