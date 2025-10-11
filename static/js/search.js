class SearchManager {
    constructor() {
        this.searchIndex = [];
        this.init();
    }

    async init() {
        await this.loadSearchIndex();
        this.bindEvents();
        this.setupMobileSearch();
    }

    async loadSearchIndex() {
        try {
            const response = await fetch('/api/search-index');
            if (response.ok) {
                this.searchIndex = await response.json();
            }
        } catch (error) {
            console.error('Ошибка загрузки поискового индекса:', error);
            this.loadFallbackIndex();
        }
    }

    loadFallbackIndex() {
        this.searchIndex = [
            {
                id: 'home',
                title: 'Главная страница',
                content: 'Центр организации дорожного движения Смоленской области',
                url: '/',
                category: 'Страница'
            },
            {
                id: 'services',
                title: 'Услуги',
                content: 'Профессиональные услуги по организации дорожного движения',
                url: '/services',
                category: 'Услуги'
            },
            {
                id: 'map',
                title: 'Карта дорог',
                content: 'Интерактивная карта дорожной ситуации Смоленской области',
                url: '/map',
                category: 'Сервис'
            },
            {
                id: 'news',
                title: 'Новости',
                content: 'Последние новости о дорожной ситуации и проектах ЦОДД',
                url: '/news',
                category: 'Новости'
            },
            {
                id: 'contacts',
                title: 'Контакты',
                content: 'Контактная информация ЦОДД Смоленской области',
                url: '/contacts',
                category: 'Контакты'
            },
            {
                id: 'create-ticket',
                title: 'Сообщить о проблеме',
                content: 'Форма для обращения граждан о проблемах на дорогах',
                url: '/create_ticket',
                category: 'Сервис'
            },
            {
                id: 'documents',
                title: 'Документы',
                content: 'Официальная документация и нормативные акты',
                url: '/documents',
                category: 'Документы'
            },
            {
                id: 'about',
                title: 'О ЦОДД',
                content: 'Информация о Центре организации дорожного движения',
                url: '/about',
                category: 'О центре'
            }
        ];
    }

    setupMobileSearch() {
        if (!document.getElementById('searchInputMobile')) {
            this.createMobileSearch();
        }
    }

    createMobileSearch() {
        const mobileMenu = document.querySelector('.mobile-menu-content');
        if (!mobileMenu) return;

        const searchHTML = `
            <div class="mobile-search mb-3">
                <form id="searchFormMobile" class="search-form-mobile">
                    <div class="search-input-group">
                        <input 
                            type="text" 
                            id="searchInputMobile"
                            class="search-input" 
                            placeholder="Поиск по сайту..."
                            autocomplete="off"
                        >
                        <button type="submit" class="search-btn">
                            <i class="bi bi-search"></i>
                        </button>
                    </div>
                    <div id="searchSuggestionsMobile" class="search-suggestions"></div>
                </form>
            </div>
        `;

        mobileMenu.insertAdjacentHTML('afterbegin', searchHTML);
        this.bindMobileEvents();
    }

    bindMobileEvents() {
        const searchInputMobile = document.getElementById('searchInputMobile');
        const searchFormMobile = document.getElementById('searchFormMobile');
        const searchSuggestionsMobile = document.getElementById('searchSuggestionsMobile');

        if (searchInputMobile && searchFormMobile) {
            searchInputMobile.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value, 'mobile');
            });

            searchInputMobile.addEventListener('focus', () => {
                if (searchInputMobile.value.length >= 2) {
                    this.handleSearchInput(searchInputMobile.value, 'mobile');
                }
            });

            searchFormMobile.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performSearch(searchInputMobile.value);
                this.closeMobileMenu();
            });

            document.addEventListener('click', (e) => {
                if (!searchFormMobile.contains(e.target)) {
                    this.hideSuggestions('mobile');
                }
            });
        }
    }

    bindEvents() {
        const searchInputDesktop = document.getElementById('searchInputDesktop');
        const searchFormDesktop = document.getElementById('searchFormDesktop');
        const searchSuggestionsDesktop = document.getElementById('searchSuggestionsDesktop');

        if (searchInputDesktop && searchFormDesktop) {
            searchInputDesktop.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value, 'desktop');
            });

            searchInputDesktop.addEventListener('focus', () => {
                if (searchInputDesktop.value.length >= 2) {
                    this.handleSearchInput(searchInputDesktop.value, 'desktop');
                }
            });

            searchFormDesktop.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performSearch(searchInputDesktop.value);
            });

            document.addEventListener('click', (e) => {
                if (!searchFormDesktop.contains(e.target)) {
                    this.hideSuggestions('desktop');
                }
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllSuggestions();
            }
            
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('searchInputDesktop') || 
                                 document.getElementById('searchInputMobile');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
        });
    }

    handleSearchInput(query, type) {
        if (query.length < 2) {
            this.hideSuggestions(type);
            return;
        }

        const results = this.search(query);
        this.displaySuggestions(results, query, type);
    }

    search(query) {
        const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
        
        return this.searchIndex.filter(item => {
            const searchableText = `${item.title} ${item.content} ${item.category}`.toLowerCase();
            return searchTerms.some(term => searchableText.includes(term));
        }).slice(0, 5);
    }

    displaySuggestions(results, query, type) {
        const containerId = type === 'mobile' ? 'searchSuggestionsMobile' : 'searchSuggestionsDesktop';
        const container = document.getElementById(containerId);
        
        if (!container) return;

        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = `
                <div class="search-no-results">
                    Ничего не найдено для "${query}"
                </div>
            `;
        } else {
            results.forEach(result => {
                const suggestion = document.createElement('a');
                suggestion.href = result.url;
                suggestion.className = 'search-suggestion';
                suggestion.innerHTML = `
                    <span class="suggestion-title">${this.highlightText(result.title, query)}</span>
                    <span class="suggestion-content">${this.highlightText(result.content, query)}</span>
                    <span class="suggestion-category">${result.category}</span>
                `;
                container.appendChild(suggestion);
            });
        }

        this.showSuggestions(type);
    }

    highlightText(text, query) {
        const terms = query.toLowerCase().split(' ');
        let highlighted = text;
        
        terms.forEach(term => {
            if (term.length > 1) {
                const regex = new RegExp(`(${term})`, 'gi');
                highlighted = highlighted.replace(regex, '<mark>$1</mark>');
            }
        });
        
        return highlighted;
    }

    showSuggestions(type) {
        const containerId = type === 'mobile' ? 'searchSuggestionsMobile' : 'searchSuggestionsDesktop';
        const container = document.getElementById(containerId);
        
        if (container) {
            container.classList.add('show');
        }
    }

    hideSuggestions(type) {
        const containerId = type === 'mobile' ? 'searchSuggestionsMobile' : 'searchSuggestionsDesktop';
        const container = document.getElementById(containerId);
        
        if (container) {
            container.classList.remove('show');
        }
    }

    hideAllSuggestions() {
        this.hideSuggestions('desktop');
        this.hideSuggestions('mobile');
    }

    performSearch(query) {
        const trimmedQuery = query.trim();
        if (trimmedQuery) {
            window.location.href = `/search?q=${encodeURIComponent(trimmedQuery)}`;
        }
    }

    closeMobileMenu() {
        const mobileMenu = document.getElementById('mobileMenu');
        if (mobileMenu && mobileMenu.classList.contains('open')) {
            mobileMenu.classList.remove('open');
            document.body.style.overflow = '';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SearchManager();
});