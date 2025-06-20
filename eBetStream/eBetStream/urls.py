"""
URL configuration for eBetStream project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),  # Page d'accueil et routes principales
    path("betting/", include("betting.urls")),  # Routes pour les paris
    path("streaming/", include("streaming.urls")),  # Routes pour le streaming
    path("users/", include("users.urls")),  # Routes pour les utilisateurs
    path("gameurs/", include("gameurs.urls")),  # Routes pour les gameurs
    path("clans/", include("clans_gaming.urls")),  # Routes pour les clans
    path("evenements/", include("evenements.urls")),  # Routes pour les événements
    path("partenaires/", include("partenaires.urls")),  # Routes pour les partenaires
    path("forum/", include("forum.urls")),  # Routes pour le forum
    path("blog/", include("blog.urls")),  # Routes pour le blog
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
