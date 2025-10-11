class ThemeManager {
    constructor() {
        this.currentTheme = this.getPreferredTheme();
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.bindEvents();
        this.setupThemeDetection();
    }

    bindEvents() {
        const themeToggle = document.getElementById('themeToggle');
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!this.isThemeManuallySet()) {
                this.currentTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(this.currentTheme);
            }
        });
    }

    getPreferredTheme() {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) {
            return storedTheme;
        }

        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    isThemeManuallySet() {
        return localStorage.getItem('theme') !== null;
    }

    applyTheme(theme) {
        const html = document.documentElement;
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle?.querySelector('i');

        // Remove existing theme classes
        html.removeAttribute('data-bs-theme');
        document.body.classList.remove('theme-light', 'theme-dark');

        // Apply new theme
        html.setAttribute('data-bs-theme', theme);
        document.body.classList.add(`theme-${theme}`);

        // Update toggle button
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'bi bi-sun-fill';
                themeToggle?.setAttribute('aria-label', 'Переключить на светлую тему');
            } else {
                icon.className = 'bi bi-moon-fill';
                themeToggle?.setAttribute('aria-label', 'Переключить на темную тему');
            }
        }

        // Fix contrast issues
        this.fixContrastIssues(theme);

        // Save preference
        localStorage.setItem('theme', theme);
        this.currentTheme = theme;

        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChange', { detail: theme }));
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

   fixContrastIssues(theme) {
    // Исправляем контраст для всех текстовых элементов
    const textElements = document.querySelectorAll('body *');
    textElements.forEach(el => {
        if (theme === 'dark') {
            // Убеждаемся, что текст видим в темной теме
            const computedStyle = window.getComputedStyle(el);
            const color = computedStyle.color;
            
            // Если цвет слишком светлый для темной темы, исправляем
            if (color.includes('255, 255, 255') || color === 'rgb(255, 255, 255)') {
                el.style.color = 'var(--gray-900)';
            }
        }
    });

    // Исправляем карточки
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        if (theme === 'dark') {
            card.style.color = 'var(--gray-900)';
            card.style.backgroundColor = 'var(--gray-800)';
        }
    });

    // Исправляем кнопки
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        if (theme === 'dark' && btn.classList.contains('btn-outline')) {
            btn.style.borderColor = 'var(--gray-400)';
            btn.style.color = 'var(--gray-900)';
        }
    });


        // Fix navbar brand text color
        const brandTitle = document.querySelector('.brand-title');
        if (brandTitle) {
            if (theme === 'dark') {
                brandTitle.classList.add('text-light');
                brandTitle.classList.remove('text-dark');
            } else {
                brandTitle.classList.add('text-dark');
                brandTitle.classList.remove('text-light');
            }
        }
    }

    setupThemeDetection() {
        // Add theme detection for dynamic content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    this.fixContrastIssues(this.currentTheme);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Public method to get current theme
    getCurrentTheme() {
        return this.currentTheme;
    }

    // Public method to set theme programmatically
    setTheme(theme) {
        if (['light', 'dark'].includes(theme)) {
            this.applyTheme(theme);
        }
    }
}

// Initialize theme manager
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}