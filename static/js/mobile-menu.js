class MobileMenu {
    constructor() {
        this.menu = document.getElementById('mobileMenu');
        this.toggleButton = document.getElementById('mobileMenuToggle');
        this.closeButton = document.getElementById('mobileMenuClose');
        this.isOpen = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        this.toggleButton.addEventListener('click', () => {
            this.toggleMenu();
        });

        this.closeButton.addEventListener('click', () => {
            this.closeMenu();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });
    }

    toggleMenu() {
        if (this.isOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }

    openMenu() {
        this.menu.classList.add('open');
        this.isOpen = true;
        document.body.style.overflow = 'hidden';
    }

    closeMenu() {
        this.menu.classList.remove('open');
        this.isOpen = false;
        document.body.style.overflow = '';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new MobileMenu();
});