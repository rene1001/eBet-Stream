/**
 * Theme Toggle System - UX Optimized
 * Système de changement de thème ergonomique et performant
 * 
 * Fonctionnalités:
 * - Changement instantané sans rechargement
 * - Persistence via cookie sécurisé
 * - Mise à jour meta theme-color
 * - Transitions fluides
 * - < 1KB optimisé
 */

class ThemeManager {
    constructor() {
        this.themes = ['cyber', 'dim', 'contrast'];
        this.currentTheme = document.documentElement.getAttribute('data-theme') || 'cyber';
        this.themeColors = {
            cyber: '#FF9500',
            dim: '#6B7280', 
            contrast: '#FFFFFF'
        };
        
        this.init();
    }
    
    init() {
        // Écouter les changements de thème (gestion correcte des clics)
        document.addEventListener('click', (e) => {
            const themeButton = e.target.closest('[data-theme-toggle]');
            if (themeButton) {
                e.preventDefault();
                const newTheme = themeButton.getAttribute('data-theme-toggle');
                this.setTheme(newTheme);
            }
        });
        
        // Support prefers-reduced-motion pour l'accessibilité
        this.handleReducedMotion();
    }
    
    setTheme(theme) {
        if (!this.themes.includes(theme)) return;
        
        // Mise à jour immédiate de l'interface
        document.documentElement.setAttribute('data-theme', theme);
        this.updateThemeColor(theme);
        
        // Persistence cookie (30 jours)
        document.cookie = `ebetstream_theme=${theme}; path=/; max-age=2592000; SameSite=Lax`;
        
        // Mise à jour état actuel
        this.currentTheme = theme;
        
        // Mise à jour UI en temps réel
        this.updateUIState(theme);
        
        // Notification UX accessible
        this.announceThemeChange(theme);
    }
    
    updateThemeColor(theme) {
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', this.themeColors[theme]);
        }
    }
    
    updateUIState(theme) {
        // Mettre à jour l'icône et le texte du bouton principal (sécurisé)
        const triggerButton = document.querySelector('#theme-trigger');
        if (triggerButton) {
            const icon = triggerButton.querySelector('i');
            const text = triggerButton.querySelector('span');
            
            const themeIcons = {
                cyber: 'bi-lightning-charge-fill',
                dim: 'bi-moon-stars-fill',
                contrast: 'bi-circle-half'
            };
            
            const themeNames = {
                cyber: 'Cyber',
                dim: 'Dim', 
                contrast: 'Contraste'
            };
            
            if (icon) {
                icon.className = themeIcons[theme];
            }
            if (text) {
                text.textContent = themeNames[theme];
            }
        }
        
        // Mettre à jour les états actifs dans le dropdown
        document.querySelectorAll('[data-theme-toggle]').forEach(item => {
            const isActive = item.getAttribute('data-theme-toggle') === theme;
            item.classList.toggle('active', isActive);
            item.setAttribute('aria-checked', isActive.toString());
            
            // Mettre à jour les checkmarks (amélioré)
            const checkmark = item.querySelector('.theme-checkmark');
            if (checkmark) {
                checkmark.style.display = isActive ? 'inline' : 'none';
            }
        });
    }
    
    announceThemeChange(theme) {
        // Annonce accessible pour les lecteurs d'écran
        const themeNames = {
            cyber: 'Cyber Gaming',
            dim: 'Mode Confort',
            contrast: 'Contraste Élevé'
        };
        
        // Créer un annonce ARIA live
        let announcer = document.getElementById('theme-announcer');
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'theme-announcer';
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.style.cssText = 'position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden';
            document.body.appendChild(announcer);
        }
        
        announcer.textContent = `Thème activé: ${themeNames[theme]}`;
    }
    
    handleReducedMotion() {
        // Support prefers-reduced-motion (sécurisé)
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.style.setProperty('--anim-intensity', '0.1'); // Évite divide-by-zero
            document.documentElement.style.setProperty('--bg-animation-opacity', '0.1');
            // Optionnel: ajouter attribut pour désactiver complètement
            document.documentElement.setAttribute('data-reduced-motion', 'true');
        }
    }
    
    // API publique
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    getAvailableThemes() {
        return this.themes;
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Export pour utilisation externe si nécessaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}