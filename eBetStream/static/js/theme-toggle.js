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
        // Binding direct sur les boutons de thème (fix Bootstrap dropdown propagation)
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const newTheme = btn.getAttribute('data-theme-toggle');
                // Theme change triggered
                this.setTheme(newTheme);
            });
        });
        
        // Support prefers-reduced-motion pour l'accessibilité
        this.handleReducedMotion();
        
        // Debug: vérifier l'état initial
        // ThemeManager initialized successfully
    }
    
    setTheme(theme) {
        if (!this.themes.includes(theme)) {
            // Invalid theme
            return;
        }
        
        // Setting theme
        
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
        
        // Theme change completed
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
                icon.className = `bi ${themeIcons[theme]}`;
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
        // Notification toast + ARIA pour lecteurs d'écran
        const themeNames = {
            cyber: 'Cyber Gaming',
            dim: 'Mode Confort',
            contrast: 'Contraste Élevé'
        };
        
        const themeIcons = {
            cyber: '⚡',
            dim: '🌙',
            contrast: '🔍'
        };
        
        // Afficher toast notification
        this.showToast({
            icon: themeIcons[theme],
            title: 'Thème modifié',
            message: `${themeNames[theme]} activé`,
            type: 'info',
            duration: 3000
        });
        
        // Créer un annonce ARIA live pour accessibilité
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
    
    // Système de notifications toast
    showToast({ icon = 'ℹ️', title, message, type = 'info', duration = 4000 }) {
        // Créer le container s'il n'existe pas
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        // Créer le toast
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast toast-ebetstream toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="toast-header">
                <span class="me-2">${icon}</span>
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fermer"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        // Ajouter au container
        container.appendChild(toast);
        
        // Afficher avec animation
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
        
        // Auto-dismiss après duration
        setTimeout(() => {
            this.hideToast(toastId);
        }, duration);
        
        // Event listener pour fermeture manuelle
        toast.querySelector('.btn-close').addEventListener('click', () => {
            this.hideToast(toastId);
        });
    }
    
    hideToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }
    
    // API publique
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    getAvailableThemes() {
        return this.themes;
    }
    
    // API publique pour toasts
    toast(options) {
        this.showToast(options);
    }
}

// Gestionnaire de raccourcis clavier gaming
class KeyboardManager {
    constructor() {
        this.shortcuts = {
            'KeyH': () => window.location.href = '/',
            'KeyG': () => window.location.href = '/games/',
            'KeyB': () => window.location.href = '/betting/',
            'KeyT': () => this.toggleThemeSelector(),
            'KeyL': () => this.toggleLanguageSelector(),
            'Escape': () => this.hideShortcuts(),
            'F1': (e) => { e.preventDefault(); this.showShortcuts(); }
        };
        
        this.shortcutsVisible = false;
        this.init();
    }
    
    init() {
        document.addEventListener('keydown', (e) => {
            // Ignorer si l'utilisateur tape dans un input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            const shortcut = this.shortcuts[e.code];
            if (shortcut) {
                shortcut(e);
                this.animateKeyPress(e.code);
            }
        });
        
        // Afficher les raccourcis au premier chargement (3 secondes)
        setTimeout(() => {
            this.showShortcuts();
            setTimeout(() => this.hideShortcuts(), 4000);
        }, 2000);
    }
    
    toggleThemeSelector() {
        const themeButton = document.getElementById('theme-trigger');
        if (themeButton) {
            themeButton.click();
        }
    }
    
    toggleLanguageSelector() {
        const langSelect = document.querySelector('select[name="language"]');
        if (langSelect) {
            langSelect.focus();
        }
    }
    
    showShortcuts() {
        let shortcutsDiv = document.getElementById('keyboard-shortcuts');
        if (!shortcutsDiv) {
            shortcutsDiv = document.createElement('div');
            shortcutsDiv.id = 'keyboard-shortcuts';
            shortcutsDiv.className = 'keyboard-shortcuts';
            shortcutsDiv.innerHTML = `
                <div class="shortcut-title">⚡ Raccourcis Gaming</div>
                <div class="shortcut-item">
                    <span class="shortcut-desc">Accueil</span>
                    <kbd class="shortcut-key">H</kbd>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-desc">Jeux</span>
                    <kbd class="shortcut-key">G</kbd>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-desc">Paris</span>
                    <kbd class="shortcut-key">B</kbd>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-desc">Thème</span>
                    <kbd class="shortcut-key">T</kbd>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-desc">Aide</span>
                    <kbd class="shortcut-key">F1</kbd>
                </div>
            `;
            document.body.appendChild(shortcutsDiv);
        }
        
        shortcutsDiv.classList.add('show');
        this.shortcutsVisible = true;
    }
    
    hideShortcuts() {
        const shortcutsDiv = document.getElementById('keyboard-shortcuts');
        if (shortcutsDiv) {
            shortcutsDiv.classList.remove('show');
            this.shortcutsVisible = false;
        }
    }
    
    animateKeyPress(keyCode) {
        const body = document.body;
        body.classList.add('key-pressed');
        setTimeout(() => body.classList.remove('key-pressed'), 200);
    }
}

// Gestionnaire de chargement
class LoadingManager {
    static show() {
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-cyber"></div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.classList.add('show');
    }
    
    static hide() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }
}

// Initialisation automatique - Une seule fois
if (!window.themeManager) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            // DOM loaded - initializing managers
            window.themeManager = new ThemeManager();
            window.keyboardManager = new KeyboardManager();
            window.LoadingManager = LoadingManager;
        });
    } else {
        // Document ready - initializing managers
        window.themeManager = new ThemeManager();
        window.keyboardManager = new KeyboardManager();
        window.LoadingManager = LoadingManager;
    }
}

// Export pour utilisation externe si nécessaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}