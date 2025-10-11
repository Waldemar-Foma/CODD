// profile-icons.js
class ProfileIconManager {
    constructor() {
        this.selectedIcon = null;
        this.init();
    }

    init() {
        this.loadProfileIcons();
        this.bindEvents();
    }

    loadProfileIcons() {
        const iconsGrid = document.getElementById('profileIcons');
        if (!iconsGrid) return;

        // Список доступных иконок Bootstrap
        const icons = [
            'bi-person', 'bi-person-circle', 'bi-person-square', 'bi-person-badge',
            'bi-person-gear', 'bi-person-check', 'bi-star', 'bi-star-fill',
            'bi-gear', 'bi-gear-fill', 'bi-shield', 'bi-shield-check',
            'bi-heart', 'bi-heart-fill', 'bi-flag', 'bi-flag-fill',
            'bi-bookmark', 'bi-bookmark-fill', 'bi-award', 'bi-trophy',
            'bi-emoji-smile', 'bi-emoji-laughing', 'bi-lightning', 'bi-lightning-charge',
            'bi-sun', 'bi-moon', 'bi-cloud', 'bi-cloud-rain'
        ];

        // Создаем сетку иконок
        iconsGrid.innerHTML = icons.map(icon => `
            <div class="col-2 text-center mb-3">
                <button type="button" 
                        class="btn btn-outline-primary w-100 h-100 icon-select ${this.isCurrentIcon(icon) ? 'active' : ''}" 
                        data-icon="${icon}"
                        style="height: 80px; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                    <i class="${icon} fs-4 mb-1"></i>
                    <small class="text-muted">${this.getIconName(icon)}</small>
                </button>
            </div>
        `).join('');

        // Загружаем текущую иконку пользователя
        this.loadCurrentUserIcon();
    }

    bindEvents() {
        // Выбор иконки
        document.addEventListener('click', (e) => {
            if (e.target.closest('.icon-select')) {
                const button = e.target.closest('.icon-select');
                this.selectIcon(button);
            }
        });

        // Сохранение иконки при клике на кнопку выбора
        document.querySelectorAll('.icon-select').forEach(button => {
            button.addEventListener('click', () => {
                this.saveProfileIcon();
            });
        });
    }

    selectIcon(button) {
        // Снимаем выделение со всех иконок
        document.querySelectorAll('.icon-select').forEach(btn => {
            btn.classList.remove('active', 'btn-primary');
            btn.classList.add('btn-outline-primary');
        });

        // Выделяем выбранную иконку
        button.classList.remove('btn-outline-primary');
        button.classList.add('active', 'btn-primary');
        this.selectedIcon = button.dataset.icon;
    }

    async saveProfileIcon() {
        if (!this.selectedIcon) {
            this.showNotification('Пожалуйста, выберите иконку', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/update-profile-icon', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    profile_icon: this.selectedIcon
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Иконка профиля успешно обновлена', 'success');
                this.updateUserInterface(this.selectedIcon);
            } else {
                this.showNotification(result.error || 'Ошибка при обновлении иконки', 'error');
            }
        } catch (error) {
            console.error('Error updating profile icon:', error);
            this.showNotification('Ошибка при обновлении иконки', 'error');
        }
    }

    updateUserInterface(iconName) {
        // Обновляем иконку в хедере
        const userButtons = document.querySelectorAll('.btn-user, .user-avatar');
        userButtons.forEach(element => {
            const iconElement = element.querySelector('i');
            if (iconElement) {
                iconElement.className = `${iconName} profile-icon-icon`;
            }
        });

        // Обновляем иконку в профиле
        const profileAvatar = document.querySelector('.avatar-profile i');
        if (profileAvatar) {
            profileAvatar.className = `${iconName} fs-1`;
        }

        // Обновляем выделение в сетке иконок
        document.querySelectorAll('.icon-select').forEach(button => {
            button.classList.remove('active', 'btn-primary');
            button.classList.add('btn-outline-primary');
            
            if (button.dataset.icon === iconName) {
                button.classList.remove('btn-outline-primary');
                button.classList.add('active', 'btn-primary');
            }
        });
    }

    async loadCurrentUserIcon() {
        try {
            const response = await fetch('/api/get-current-user');
            const user = await response.json();
            
            if (user.profile_icon) {
                this.selectedIcon = user.profile_icon;
                this.updateUserInterface(user.profile_icon);
            }
        } catch (error) {
            console.error('Error loading current user icon:', error);
        }
    }

    isCurrentIcon(icon) {
        // Проверяем, является ли иконка текущей (для начальной загрузки)
        const userIconElement = document.querySelector('.btn-user i');
        if (userIconElement) {
            return userIconElement.className.includes(icon);
        }
        return false;
    }

    getIconName(icon) {
        // Преобразуем имя класса в читаемое название
        const names = {
            'bi-person': 'Персона',
            'bi-person-circle': 'Круг',
            'bi-person-square': 'Квадрат',
            'bi-person-badge': 'Значок',
            'bi-person-gear': 'Настройки',
            'bi-person-check': 'Галочка',
            'bi-star': 'Звезда',
            'bi-star-fill': 'Звезда зал.',
            'bi-gear': 'Шестерня',
            'bi-gear-fill': 'Шестерня зал.',
            'bi-shield': 'Щит',
            'bi-shield-check': 'Щит с галочкой',
            'bi-heart': 'Сердце',
            'bi-heart-fill': 'Сердце зал.',
            'bi-flag': 'Флаг',
            'bi-flag-fill': 'Флаг зал.',
            'bi-bookmark': 'Закладка',
            'bi-bookmark-fill': 'Закладка зал.',
            'bi-award': 'Награда',
            'bi-trophy': 'Трофей',
            'bi-emoji-smile': 'Смайл',
            'bi-emoji-laughing': 'Смех',
            'bi-lightning': 'Молния',
            'bi-lightning-charge': 'Заряд',
            'bi-sun': 'Солнце',
            'bi-moon': 'Луна',
            'bi-cloud': 'Облако',
            'bi-cloud-rain': 'Дождь'
        };
        
        return names[icon] || icon.replace('bi-', '');
    }

    getCSRFToken() {
        // Получаем CSRF токен из формы
        const csrfToken = document.querySelector('input[name="csrf_token"]');
        return csrfToken ? csrfToken.value : '';
    }

    showNotification(message, type = 'info') {
        // Используем существующую систему уведомлений или создаем простую
        if (window.notificationManager) {
            window.notificationManager.addNotification('Иконка профиля', message, type);
        } else {
            // Простой fallback
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            alert.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
            alert.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi ${this.getAlertIcon(type)} me-2"></i>
                    <span>${message}</span>
                    <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            document.body.appendChild(alert);
            
            // Автоматическое скрытие
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 3000);
        }
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-exclamation-triangle-fill',
            'warning': 'bi-exclamation-circle-fill',
            'info': 'bi-info-circle-fill'
        };
        return icons[type] || 'bi-info-circle-fill';
    }
}

// Функция для проверки допустимости иконки
function isValidProfileIcon(icon) {
    const allowedIcons = [
        'bi-person', 'bi-person-circle', 'bi-person-square', 'bi-person-badge',
        'bi-person-gear', 'bi-person-check', 'bi-star', 'bi-star-fill',
        'bi-gear', 'bi-gear-fill', 'bi-shield', 'bi-shield-check',
        'bi-heart', 'bi-heart-fill', 'bi-flag', 'bi-flag-fill',
        'bi-bookmark', 'bi-bookmark-fill', 'bi-award', 'bi-trophy',
        'bi-emoji-smile', 'bi-emoji-laughing', 'bi-lightning', 'bi-lightning-charge',
        'bi-sun', 'bi-moon', 'bi-cloud', 'bi-cloud-rain'
    ];
    return allowedIcons.includes(icon);
}

// Глобальная функция для тестирования
window.testProfileIcon = function(icon) {
    if (isValidProfileIcon(icon)) {
        if (window.profileIconManager) {
            window.profileIconManager.selectedIcon = icon;
            window.profileIconManager.updateUserInterface(icon);
        }
    } else {
        console.warn('Недопустимая иконка:', icon);
    }
};

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.profileIconManager = new ProfileIconManager();
});