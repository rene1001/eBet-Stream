// mobile-interactions.js - Amélioration des interactions tactiles

document.addEventListener('DOMContentLoaded', function() {
    // Détection du type d'appareil
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // Désactiver le zoom sur les champs de formulaire sur mobile
    if (isMobile) {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                document.body.style.zoom = '100%';
                window.scrollTo(0, 0);
            });
        });
        
        // Empêcher le zoom sur le double-tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }
    
    // Amélioration des menus déroulants pour le tactile
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        // Ajouter un gestionnaire pour les écrans tactiles
        dropdown.addEventListener('touchstart', function(e) {
            // Si le menu est déjà ouvert, on le ferme au prochain clic
            if (this.classList.contains('show')) {
                return;
            }
            // Sinon, on ouvre le menu
            e.preventDefault();
            const dropdownMenu = this.querySelector('.dropdown-menu');
            if (dropdownMenu) {
                dropdownMenu.classList.add('show');
                this.classList.add('show');
            }
        });
    });
    
    // Fermer les menus déroulants quand on clique ailleurs
    document.addEventListener('touchstart', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
                menu.closest('.dropdown').classList.remove('show');
            });
        }
    });
    
    // Amélioration de l'accessibilité pour les éléments cliquables
    const clickableElements = document.querySelectorAll('button, a, [role="button"], [tabindex="0"]');
    clickableElements.forEach(element => {
        element.style.cursor = 'pointer';
        element.setAttribute('aria-label', element.textContent || element.getAttribute('aria-label') || 'Bouton');
    });
    
    // Détection de l'orientation de l'écran
    function handleOrientationChange() {
        if (window.matchMedia('(orientation: portrait)').matches) {
            document.body.classList.add('portrait');
            document.body.classList.remove('landscape');
        } else {
            document.body.classList.add('landscape');
            document.body.classList.remove('portrait');
        }
    }
    
    // Écouter les changements d'orientation
    window.addEventListener('orientationchange', handleOrientationChange);
    handleOrientationChange(); // Appel initial
    
    // Optimisation du défilement fluide
    if ('scrollBehavior' in document.documentElement.style) {
        const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
        smoothScrollLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId !== '#') {
                    e.preventDefault();
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }
});

// Gestion du viewport pour iOS
(function() {
    // Prévenir le zoom sur iOS
    document.addEventListener('touchmove', function(e) {
        if (e.scale !== 1) { 
            e.preventDefault();
        }
    }, { passive: false });
    
    // Détection de la taille de l'écran
    function updateViewport() {
        const viewport = document.querySelector('meta[name=viewport]');
        if (window.innerWidth <= 480) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0');
        } else {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0');
        }
    }
    
    window.addEventListener('resize', updateViewport);
    updateViewport();
})();
