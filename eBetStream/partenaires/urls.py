from django.urls import path
from . import views

app_name = 'partenaires'

urlpatterns = [
    path('', views.liste_partenaires, name='liste_partenaires'),
    path('<int:partenaire_id>/', views.detail_partenaire, name='detail_partenaire'),
] 