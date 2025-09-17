/**
 * eBetStream Theme Manager
 * Ultra-Modern Theme Switching System (Light, Dark, System)
 * Cyber-Futuristic Implementation with Local Storage Persistence
 */

class ThemeManager {
    constructor() {
        this.themes = ['light', 'dark', 'system'];
        this.currentTheme = this.getStoredTheme();
        this.systemTheme = this.getSystemTheme();
        
        // Initialize theme on load
        this.init();
        
        // Listen for system theme changes
        this.watchSystemTheme();
    }
    
    /**
     * Initialize theme system
     */
    init() {
        this.applyTheme(this.currentTheme);
        this.updateThemeSelector();
        this.createThemeTransition();
    }
    
    /**
     * Get stored theme from localStorage
     */
    getStoredTheme() {
        const stored = localStorage.getItem('ebetstream-theme');
        return this.themes.includes(stored) ? stored : 'system';
    }
    
    /**
     * Get system/OS preferred theme
     */
    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    /**
     * Apply theme to document
     */
    applyTheme(theme) {
        const effectiveTheme = theme === 'system' ? this.systemTheme : theme;
        
        // Apply theme attribute to document
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(effectiveTheme);
        
        // Store current theme
        this.currentTheme = theme;
        localStorage.setItem('ebetstream-theme', theme);
        
        // Dispatch theme change event
        this.dispatchThemeChangeEvent(effectiveTheme);
    }
    
    /**
     * Update meta theme-color for mobile browsers
     */
    updateMetaThemeColor(theme) {
        let themeColor = '#000008'; // Dark theme default
        
        if (theme === 'light') {
            themeColor = '#ffffff';
        }
        
        // Update existing meta tag or create new one
        let metaTheme = document.querySelector('meta[name="theme-color"]');
        if (!metaTheme) {
            metaTheme = document.createElement('meta');
            metaTheme.name = 'theme-color';
            document.head.appendChild(metaTheme);
        }
        metaTheme.content = themeColor;
    }
    
    /**
     * Watch for system theme changes
     */
    watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        mediaQuery.addEventListener('change', (e) => {
            this.systemTheme = e.matches ? 'dark' : 'light';
            
            // If user has system theme selected, update accordingly
            if (this.currentTheme === 'system') {
                this.applyTheme('system');
            }
        });
    }
    
    /**
     * Switch to next theme in cycle
     */
    switchTheme() {
        const currentIndex = this.themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % this.themes.length;
        const nextTheme = this.themes[nextIndex];
        
        this.applyTheme(nextTheme);
        this.updateThemeSelector();
        
        // Add visual feedback
        this.showThemeChangeNotification(nextTheme);
    }
    
    /**
     * Set specific theme
     */
    setTheme(theme) {
        if (this.themes.includes(theme)) {
            this.applyTheme(theme);
            this.updateThemeSelector();
            this.showThemeChangeNotification(theme);
        }
    }
    
    /**
     * Update theme selector UI
     */
    updateThemeSelector() {
        const selector = document.getElementById('theme-selector');
        if (selector) {
            selector.setAttribute('data-current-theme', this.currentTheme);
            
            // Update button text and icon
            const button = selector.querySelector('.theme-btn');
            if (button) {
                this.updateThemeButton(button);
            }
        }
    }
    
    /**
     * Update theme button appearance
     */
    updateThemeButton(button) {
        const icons = {
            light: 'bi-sun-fill',
            dark: 'bi-moon-fill', 
            system: 'bi-circle-half'
        };
        
        // Get localized labels from template data attributes
        const selector = document.getElementById('theme-selector');
        const labels = {
            light: selector?.dataset.labelLight || 'Light',
            dark: selector?.dataset.labelDark || 'Dark',
            system: selector?.dataset.labelSystem || 'System'
        };
        
        // Update icon
        const icon = button.querySelector('i');
        if (icon) {
            icon.className = `bi ${icons[this.currentTheme]}`;
        }
        
        // Update label
        const label = button.querySelector('.theme-label');
        if (label) {
            label.textContent = labels[this.currentTheme];
        }
        
        // Update tooltip with localized text
        const currentLabel = labels[this.currentTheme];
        button.title = `${button.title.split(':')[0]}: ${currentLabel}`;
    }
    
    /**
     * Show theme change notification
     */
    showThemeChangeNotification(theme) {
        // Get localized notification texts from template data attributes
        const selector = document.getElementById('theme-selector');
        const labels = {
            light: selector?.dataset.notificationLight || 'Light Theme Activated',
            dark: selector?.dataset.notificationDark || 'Dark Theme Activated',
            system: selector?.dataset.notificationSystem || 'System Theme Activated'
        };
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.innerHTML = `
            <i class="bi bi-check-circle-fill"></i>
            <span>${labels[theme]}</span>
        `;
        
        // Add to document
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 2000);
    }
    
    /**
     * Create smooth transition effect during theme change
     */
    createThemeTransition() {
        if (!document.querySelector('#theme-transition-style')) {
            const style = document.createElement('style');
            style.id = 'theme-transition-style';
            style.textContent = `
                * {
                    transition: background-color 0.3s ease, 
                               color 0.3s ease, 
                               border-color 0.3s ease,
                               box-shadow 0.3s ease !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    /**
     * Dispatch custom theme change event
     */
    dispatchThemeChangeEvent(effectiveTheme) {
        const event = new CustomEvent('themechange', {
            detail: {
                theme: this.currentTheme,
                effectiveTheme: effectiveTheme,
                systemTheme: this.systemTheme
            }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Get current theme info
     */
    getThemeInfo() {
        return {
            current: this.currentTheme,
            effective: this.currentTheme === 'system' ? this.systemTheme : this.currentTheme,
            system: this.systemTheme,
            available: this.themes
        };
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create global theme manager instance
    window.themeManager = new ThemeManager();
    
    // Add event listeners for theme selector
    const themeSelector = document.getElementById('theme-selector');
    if (themeSelector) {
        const themeBtn = themeSelector.querySelector('.theme-btn');
        if (themeBtn) {
            themeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                window.themeManager.switchTheme();
            });
        }
    }
    
    // Add keyboard shortcut (Ctrl/Cmd + Shift + T)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            window.themeManager.switchTheme();
        }
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}