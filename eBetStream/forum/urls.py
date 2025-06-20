from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.liste_categories, name='liste_categories'),
    path('categorie/<slug:categorie_slug>/', views.liste_sujets, name='liste_sujets'),
    path('categorie/<slug:categorie_slug>/sujet/<slug:sujet_slug>/', views.detail_sujet, name='detail_sujet'),
    path('categorie/<slug:categorie_slug>/nouveau-sujet/', views.creer_sujet, name='creer_sujet'),
    path('message/<int:message_id>/modifier/', views.modifier_message, name='modifier_message'),
    path('message/<int:message_id>/supprimer/', views.supprimer_message, name='supprimer_message'),
] 