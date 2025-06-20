from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Categorie, Article, Commentaire
from .forms import ArticleForm, CommentaireForm

def liste_articles(request):
    articles = Article.objects.filter(statut='publie').order_by('-date_publication')
    categories = Categorie.objects.filter(est_active=True)
    return render(request, 'blog/liste_articles.html', {
        'articles': articles,
        'categories': categories
    })

def detail_article(request, slug):
    article = get_object_or_404(Article, slug=slug, statut='publie')
    article.nombre_vues += 1
    article.save()
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.auteur = request.user
            commentaire.save()
            messages.success(request, 'Votre commentaire a été publié avec succès.')
            return redirect('blog:detail_article', slug=slug)
    else:
        form = CommentaireForm()
    
    return render(request, 'blog/detail_article.html', {
        'article': article,
        'commentaires': article.commentaires.filter(parent=None),
        'form': form
    })

@login_required
def creer_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            if article.statut == 'publie':
                article.date_publication = timezone.now()
            article.save()
            messages.success(request, 'Votre article a été créé avec succès.')
            return redirect('blog:detail_article', slug=article.slug)
    else:
        form = ArticleForm()
    
    return render(request, 'blog/creer_article.html', {
        'form': form
    })

@login_required
def modifier_article(request, slug):
    article = get_object_or_404(Article, slug=slug, auteur=request.user)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if article.statut == 'publie' and not article.date_publication:
                article.date_publication = timezone.now()
            article.save()
            messages.success(request, 'Votre article a été modifié avec succès.')
            return redirect('blog:detail_article', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'blog/modifier_article.html', {
        'form': form,
        'article': article
    })

@login_required
def supprimer_article(request, slug):
    article = get_object_or_404(Article, slug=slug, auteur=request.user)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Votre article a été supprimé avec succès.')
        return redirect('blog:liste_articles')
    
    return render(request, 'blog/supprimer_article.html', {
        'article': article
    })

@login_required
def modifier_commentaire(request, commentaire_id):
    commentaire = get_object_or_404(Commentaire, id=commentaire_id, auteur=request.user)
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST, instance=commentaire)
        if form.is_valid():
            commentaire = form.save()
            messages.success(request, 'Votre commentaire a été modifié avec succès.')
            return redirect('blog:detail_article', slug=commentaire.article.slug)
    else:
        form = CommentaireForm(instance=commentaire)
    
    return render(request, 'blog/modifier_commentaire.html', {
        'form': form,
        'commentaire': commentaire
    })

@login_required
def supprimer_commentaire(request, commentaire_id):
    commentaire = get_object_or_404(Commentaire, id=commentaire_id, auteur=request.user)
    
    if request.method == 'POST':
        commentaire.delete()
        messages.success(request, 'Votre commentaire a été supprimé avec succès.')
        return redirect('blog:detail_article', slug=commentaire.article.slug)
    
    return render(request, 'blog/supprimer_commentaire.html', {
        'commentaire': commentaire
    })
