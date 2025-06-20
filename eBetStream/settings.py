LANGUAGE_CODE = 'fr'
USE_I18N = True
LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('es', 'Español'),
]
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    // ... existing code ...
]
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'ebetsiream.com', 'www.ebetsiream.com']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000', 'https://ebetsiream.com', 'https://www.ebetsiream.com'] 