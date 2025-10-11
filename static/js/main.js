class MainApp {
    constructor() {
        this.searchManager = null;
        this.notificationManager = null;
        this.init();
    }

    init() {
        this.setupBackToTop();
        this.setupThemeToggle();
        this.setupSmoothScrolling();
        this.setupHeaderBehavior();
        this.setupAnimations();
        this.setupPerformance();
        
        this.setupSearch();
        this.setupNotifications();
    }

    setupSearch() {
        this.searchManager = new SearchManager();
    }

    setupNotifications() {
        this.notificationManager = new NotificationManager();
        window.notificationManager = this.notificationManager;
    }

    setupBackToTop() {
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            const checkScroll = () => {
                if (window.pageYOffset > 300) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
            };

            window.addEventListener('scroll', checkScroll, { passive: true });
            checkScroll();

            backToTop.addEventListener('click', (e) => {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const savedTheme = localStorage.getItem('theme') || 'light';
            this.applyTheme(savedTheme, themeToggle);

            themeToggle.addEventListener('click', () => {
                const html = document.documentElement;
                const currentTheme = html.getAttribute('data-bs-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.applyTheme(newTheme, themeToggle);
                localStorage.setItem('theme', newTheme);
            });
        }
    }

    applyTheme(theme, toggleButton) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        if (toggleButton) {
            toggleButton.innerHTML = theme === 'dark' ? 
                '<i class="bi bi-sun-fill"></i>' : 
                '<i class="bi bi-moon-fill"></i>';
            toggleButton.setAttribute('aria-label', 
                theme === 'dark' ? 'Переключить на светлую тему' : 'Переключить на темную тему');
        }
    }

    setupSmoothScrolling() {
        document.addEventListener('click', (e) => {
            const target = e.target;
            const link = target.closest('a[href^="#"]');
            
            if (link && link.getAttribute('href') !== '#') {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    this.scrollToElement(targetElement);
                }
            }
        });
    }

    scrollToElement(element, offset = 80) {
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    setupHeaderBehavior() {
        const header = document.querySelector('.header');
        if (!header) return;

        let lastScrollY = window.scrollY;
        let ticking = false;

        const updateHeader = () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                header.style.transform = 'translateY(-100%)';
            } else {
                header.style.transform = 'translateY(0)';
            }

            if (currentScrollY > 10) {
                header.style.boxShadow = 'var(--shadow-md)';
            } else {
                header.style.boxShadow = 'var(--shadow-sm)';
            }

            lastScrollY = currentScrollY;
            ticking = false;
        };

        const onScroll = () => {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        };

        window.addEventListener('scroll', onScroll, { passive: true });
        
        header.addEventListener('mouseenter', () => {
            header.style.transform = 'translateY(0)';
        });
    }

    setupAnimations() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            const animateElements = document.querySelectorAll('.feature-card, .service-card, .hero-content');
            animateElements.forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(el);
            });
        }

        this.animateStats();
    }

    animateStats() {
        const statElements = document.querySelectorAll('.stat-number');
        if (statElements.length === 0) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        statElements.forEach(stat => observer.observe(stat));
    }

    animateCounter(element) {
        const target = parseInt(element.textContent) || 0;
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    setupPerformance() {
        this.lazyLoadImages();
        this.optimizeResize();
        this.setupErrorHandling();
    }

    lazyLoadImages() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                        }
                        if (img.dataset.srcset) {
                            img.srcset = img.dataset.srcset;
                        }
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    optimizeResize() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.updateLayout();
            }, 250);
        });
    }

    updateLayout() {
        const header = document.querySelector('.header');
        const mainContent = document.querySelector('.main-content');
        
        if (header && mainContent) {
            const headerHeight = header.offsetHeight;
            mainContent.style.paddingTop = headerHeight + 'px';
        }
    }

    setupErrorHandling() {
        window.addEventListener('error', (e) => {
            console.error('Ошибка:', e.error);
        });

        window.addEventListener('unhandledrejection', (e) => {
            console.error('Необработанный Promise:', e.reason);
            e.preventDefault();
        });
    }

    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.mainApp = new MainApp();
    
    const notificationStyles = `
        .notification-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 0.75rem;
            border-bottom: 1px solid var(--gray-200);
            transition: background-color 0.2s ease;
        }
        
        .notification-item:last-child {
            border-bottom: none;
        }
        
        .notification-item:hover {
            background: var(--gray-50);
        }
        
        .notification-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .notification-icon.info {
            background: var(--info);
            color: white;
        }
        
        .notification-icon.warning {
            background: var(--warning);
            color: white;
        }
        
        .notification-icon.success {
            background: var(--success);
            color: white;
        }
        
        .notification-icon.error {
            background: var(--error);
            color: white;
        }
        
        .notification-content {
            flex: 1;
            min-width: 0;
        }
        
        .notification-title {
            font-weight: 600;
            font-size: 0.875rem;
            margin-bottom: 0.25rem;
            color: var(--gray-800);
        }
        
        .notification-text {
            font-size: 0.8125rem;
            color: var(--gray-600);
            margin-bottom: 0.25rem;
            line-height: 1.4;
        }
        
        .notification-time {
            font-size: 0.75rem;
            color: var(--gray-500);
        }
        
        .notification-close {
            background: none;
            border: none;
            color: var(--gray-500);
            cursor: pointer;
            padding: 0.25rem;
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
            flex-shrink: 0;
        }
        
        .notification-close:hover {
            background: var(--gray-200);
            color: var(--gray-700);
        }
        
        .notification-empty {
            text-align: center;
            padding: 2rem 1rem;
            color: var(--gray-500);
        }
        
        .notification-empty i {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            display: block;
        }
    `;

    const styleSheet = document.createElement('style');
    styleSheet.textContent = notificationStyles;
    document.head.appendChild(styleSheet);
});

window.utils = {
    formatNumber: (number) => {
        return new Intl.NumberFormat('ru-RU').format(number);
    },
    
    formatDate: (date) => {
        return new Intl.DateTimeFormat('ru-RU').format(new Date(date));
    },
    
    truncateText: (text, maxLength) => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },
    
    isMobile: () => {
        return window.innerWidth < 768;
    },
    
    isTablet: () => {
        return window.innerWidth >= 768 && window.innerWidth < 992;
    },
    
    isDesktop: () => {
        return window.innerWidth >= 992;
    }
};
