from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.liste_articles, name='liste_articles'),
    path('article/<slug:slug>/', views.detail_article, name='detail_article'),
    path('nouvel-article/', views.creer_article, name='creer_article'),
    path('article/<slug:slug>/modifier/', views.modifier_article, name='modifier_article'),
    path('article/<slug:slug>/supprimer/', views.supprimer_article, name='supprimer_article'),
    path('commentaire/<int:commentaire_id>/modifier/', views.modifier_commentaire, name='modifier_commentaire'),
    path('commentaire/<int:commentaire_id>/supprimer/', views.supprimer_commentaire, name='supprimer_commentaire'),
] 