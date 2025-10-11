class AccessibilityManager {
    constructor() {
        this.panel = document.getElementById('accessibilityPanel');
        this.toggleButton = document.getElementById('accessibilityToggle');
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupAccessibility();
        this.loadSavedSettings();
    }

    setupAccessibility() {
        this.addSkipLink();
        this.setupKeyboardNavigation();
    }

    addSkipLink() {
        // Проверяем, не добавлена ли уже ссылка
        if (document.querySelector('.skip-link')) return;

        const skipLink = document.createElement('a');
        skipLink.href = '#mainContent';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #7cb342;
            color: white;
            padding: 8px 12px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
            font-weight: 600;
            transition: top 0.2s ease;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });

        document.body.prepend(skipLink);
    }

    setupKeyboardNavigation() {
        // Навигация с клавиатуры
        document.addEventListener('keydown', (e) => {
            // Tab показывает focus styles
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
            
            // Escape закрывает панель доступности
            if (e.key === 'Escape' && this.panel.classList.contains('show')) {
                this.hideAccessibilityPanel();
            }
        });

        // Убираем класс при клике мышью
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // Улучшенные focus styles для элементов
        this.enhanceFocusStyles();
    }

    enhanceFocusStyles() {
        // Добавляем улучшенные стили для фокуса
        const focusStyles = `
            .keyboard-navigation *:focus {
                outline: 3px solid #7cb342 !important;
                outline-offset: 2px !important;
            }
            
            .keyboard-navigation .btn:focus,
            .keyboard-navigation .btn-action:focus,
            .keyboard-navigation .nav-link:focus {
                box-shadow: 0 0 0 3px rgba(124, 179, 66, 0.3) !important;
            }
            
            .skip-link:focus {
                top: 6px !important;
                outline: 3px solid white !important;
                outline-offset: 2px !important;
            }
        `;

        // Проверяем, не добавлены ли уже стили
        if (!document.getElementById('accessibility-focus-styles')) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'accessibility-focus-styles';
            styleSheet.textContent = focusStyles;
            document.head.appendChild(styleSheet);
        }
    }

    bindEvents() {
        // Toggle accessibility panel
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => {
                this.toggleAccessibilityPanel();
            });
        }

        // Font size controls
        const increaseFont = document.getElementById('increaseFont');
        const decreaseFont = document.getElementById('decreaseFont');
        const normalFont = document.getElementById('normalFont');

        if (increaseFont) {
            increaseFont.addEventListener('click', () => {
                this.changeFontSize(1);
            });
        }

        if (decreaseFont) {
            decreaseFont.addEventListener('click', () => {
                this.changeFontSize(-1);
            });
        }

        if (normalFont) {
            normalFont.addEventListener('click', () => {
                this.resetFontSize();
            });
        }

        // High contrast
        const highContrast = document.getElementById('highContrast');
        if (highContrast) {
            highContrast.addEventListener('click', (e) => {
                this.toggleHighContrast(e.target);
            });
        }

        // Grayscale
        const grayscale = document.getElementById('grayscale');
        if (grayscale) {
            grayscale.addEventListener('click', (e) => {
                this.toggleGrayscale(e.target);
            });
        }

        // Close panel
        const closeAccessibility = document.getElementById('closeAccessibility');
        if (closeAccessibility) {
            closeAccessibility.addEventListener('click', () => {
                this.hideAccessibilityPanel();
            });
        }

        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (this.panel && this.panel.classList.contains('show') && 
                !this.panel.contains(e.target) && 
                !this.toggleButton.contains(e.target)) {
                this.hideAccessibilityPanel();
            }
        });
    }

    toggleAccessibilityPanel() {
        if (!this.panel) return;
        
        this.panel.classList.toggle('show');
        const isVisible = this.panel.classList.contains('show');
        
        if (isVisible) {
            this.toggleButton.setAttribute('aria-expanded', 'true');
            this.focusFirstControl();
        } else {
            this.toggleButton.setAttribute('aria-expanded', 'false');
            this.toggleButton.focus();
        }
    }

    hideAccessibilityPanel() {
        if (!this.panel) return;
        
        this.panel.classList.remove('show');
        if (this.toggleButton) {
            this.toggleButton.setAttribute('aria-expanded', 'false');
            this.toggleButton.focus();
        }
    }

    focusFirstControl() {
        if (!this.panel) return;
        
        const firstControl = this.panel.querySelector('button');
        if (firstControl) {
            setTimeout(() => {
                firstControl.focus();
            }, 100);
        }
    }

    changeFontSize(direction) {
        const html = document.documentElement;
        const currentSize = parseFloat(getComputedStyle(html).fontSize);
        const newSize = currentSize + (direction * 2);
        
        // Limit font size between 14px and 22px
        if (newSize >= 14 && newSize <= 22) {
            html.style.fontSize = `${newSize}px`;
            this.saveSetting('fontSize', newSize);
            this.updateFontSizeButtons();
        }
    }

    resetFontSize() {
        document.documentElement.style.fontSize = '';
        this.saveSetting('fontSize', null);
        this.updateFontSizeButtons();
    }

    updateFontSizeButtons() {
        const html = document.documentElement;
        const currentSize = parseFloat(getComputedStyle(html).fontSize);
        const normalSize = 16; // Базовый размер шрифта
        
        const increaseBtn = document.getElementById('increaseFont');
        const decreaseBtn = document.getElementById('decreaseFont');
        const normalBtn = document.getElementById('normalFont');

        if (increaseBtn) {
            increaseBtn.setAttribute('aria-pressed', currentSize > normalSize);
        }
        if (decreaseBtn) {
            decreaseBtn.setAttribute('aria-pressed', currentSize < normalSize);
        }
        if (normalBtn) {
            normalBtn.setAttribute('aria-pressed', currentSize === normalSize);
        }
    }

    toggleHighContrast(button) {
        document.body.classList.toggle('high-contrast');
        const isActive = document.body.classList.contains('high-contrast');
        
        if (button) {
            button.setAttribute('aria-pressed', isActive);
        }
        
        this.saveSetting('highContrast', isActive);
        
        // Отключаем grayscale при включении high contrast
        if (isActive) {
            document.body.classList.remove('grayscale');
            const grayscaleBtn = document.getElementById('grayscale');
            if (grayscaleBtn) {
                grayscaleBtn.setAttribute('aria-pressed', 'false');
            }
        }
    }

    toggleGrayscale(button) {
        document.body.classList.toggle('grayscale');
        const isActive = document.body.classList.contains('grayscale');
        
        if (button) {
            button.setAttribute('aria-pressed', isActive);
        }
        
        this.saveSetting('grayscale', isActive);
        
        // Отключаем high contrast при включении grayscale
        if (isActive) {
            document.body.classList.remove('high-contrast');
            const highContrastBtn = document.getElementById('highContrast');
            if (highContrastBtn) {
                highContrastBtn.setAttribute('aria-pressed', 'false');
            }
        }
    }

    saveSetting(key, value) {
        try {
            const settings = this.getSavedSettings();
            settings[key] = value;
            localStorage.setItem('accessibilitySettings', JSON.stringify(settings));
        } catch (error) {
            console.warn('Не удалось сохранить настройки доступности:', error);
        }
    }

    getSavedSettings() {
        try {
            return JSON.parse(localStorage.getItem('accessibilitySettings') || '{}');
        } catch (error) {
            console.warn('Не удалось загрузить настройки доступности:', error);
            return {};
        }
    }

    loadSavedSettings() {
        const settings = this.getSavedSettings();
        
        // Font size
        if (settings.fontSize) {
            document.documentElement.style.fontSize = `${settings.fontSize}px`;
        }
        
        // High contrast
        if (settings.highContrast) {
            document.body.classList.add('high-contrast');
            const highContrastBtn = document.getElementById('highContrast');
            if (highContrastBtn) {
                highContrastBtn.setAttribute('aria-pressed', 'true');
            }
        }
        
        // Grayscale
        if (settings.grayscale) {
            document.body.classList.add('grayscale');
            const grayscaleBtn = document.getElementById('grayscale');
            if (grayscaleBtn) {
                grayscaleBtn.setAttribute('aria-pressed', 'true');
            }
        }
        
        // Update font size buttons state
        this.updateFontSizeButtons();
    }

    // Public methods for external use
    enableHighContrast() {
        this.toggleHighContrast(document.getElementById('highContrast'));
    }

    enableGrayscale() {
        this.toggleGrayscale(document.getElementById('grayscale'));
    }

    resetAllSettings() {
        this.resetFontSize();
        document.body.classList.remove('high-contrast', 'grayscale');
        
        // Сбрасываем все кнопки
        const buttons = document.querySelectorAll('.btn-accessibility');
        buttons.forEach(btn => {
            btn.setAttribute('aria-pressed', 'false');
        });
        
        // Сбрасываем normal font button
        const normalBtn = document.getElementById('normalFont');
        if (normalBtn) {
            normalBtn.setAttribute('aria-pressed', 'true');
        }
        
        // Очищаем настройки
        localStorage.removeItem('accessibilitySettings');
    }
}

// Initialize accessibility manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, что необходимые элементы существуют
    const accessibilityPanel = document.getElementById('accessibilityPanel');
    const accessibilityToggle = document.getElementById('accessibilityToggle');
    
    if (accessibilityPanel || accessibilityToggle) {
        window.accessibilityManager = new AccessibilityManager();
    } else {
        console.warn('Элементы доступности не найдены на странице');
    }
});

// Добавляем глобальные стили для режимов доступности
document.addEventListener('DOMContentLoaded', function() {
    const accessibilityStyles = `
        /* High Contrast Mode */
        .high-contrast {
            --primary-green: #00ff00 !important;
            --primary-green-light: #00ff00 !important;
            --primary-green-dark: #00ff00 !important;
            --white: #000000 !important;
            --gray-50: #000000 !important;
            --gray-100: #000000 !important;
            --gray-200: #ffffff !important;
            --gray-300: #ffffff !important;
            --gray-400: #ffffff !important;
            --gray-500: #ffffff !important;
            --gray-600: #ffffff !important;
            --gray-700: #ffffff !important;
            --gray-800: #ffffff !important;
            --gray-900: #ffffff !important;
        }

        .high-contrast body {
            background: #000000 !important;
            color: #ffffff !important;
        }

        .high-contrast .header {
            background: #000000 !important;
            border-bottom: 2px solid #ffffff !important;
        }

        .high-contrast .feature-card,
        .high-contrast .service-card,
        .high-contrast .glass {
            background: #000000 !important;
            border: 2px solid #ffffff !important;
            color: #ffffff !important;
        }

        .high-contrast .btn {
            border: 2px solid #ffffff !important;
        }

        .high-contrast .btn-primary {
            background: #000000 !important;
            color: #00ff00 !important;
            border-color: #00ff00 !important;
        }

        .high-contrast .btn-outline-primary {
            background: transparent !important;
            color: #00ff00 !important;
            border-color: #00ff00 !important;
        }

        /* Grayscale Mode */
        .grayscale {
            filter: grayscale(100%) !important;
        }

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        }

        /* Focus styles for accessibility */
        .accessibility-focus *:focus {
            outline: 3px solid #7cb342 !important;
            outline-offset: 2px !important;
        }

        /* Print styles for accessibility */
        @media print {
            .accessibility-panel,
            .accessibility-toggle,
            .navbar-toggler,
            .back-to-top {
                display: none !important;
            }
            
            body {
                font-size: 12pt !important;
                line-height: 1.6 !important;
            }
            
            a::after {
                content: " (" attr(href) ")";
            }
        }
    `;

    // Добавляем стили только если они еще не добавлены
    if (!document.getElementById('global-accessibility-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'global-accessibility-styles';
        styleSheet.textContent = accessibilityStyles;
        document.head.appendChild(styleSheet);
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityManager;
}