# core/context_processors.py

def theme_context(request):
    """
    Context processor pour gérer les thèmes de manière ergonomique
    
    Thèmes disponibles:
    - cyber: Expérience eBetStream complète (défaut)
    - dim: Intensité réduite pour sessions longues
    - contrast: Accessibilité WCAG AA
    """
    theme = request.COOKIES.get('ebetstream_theme', 'cyber')
    
    # Validation des thèmes disponibles
    valid_themes = ['cyber', 'dim', 'contrast']
    if theme not in valid_themes:
        theme = 'cyber'
    
    # Métadonnées pour l'interface utilisateur
    theme_data = {
        'cyber': {
            'name': 'Cyber',
            'description': 'Gaming complet',
            'icon': '⚡',
            'color': '#FF9500'
        },
        'dim': {
            'name': 'Dim',
            'description': 'Confort visuel',
            'icon': '🌙',
            'color': '#6B7280'
        },
        'contrast': {
            'name': 'Contraste',
            'description': 'Accessibilité',
            'icon': '🔍',
            'color': '#FFFFFF'
        }
    }
    
    return {
        'current_theme': theme,
        'theme_info': theme_data.get(theme, theme_data['cyber']),
        'available_themes': theme_data
    }