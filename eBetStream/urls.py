from django.urls import path, include

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('core.urls')),
    path('betting/', include('betting.urls')),
] 