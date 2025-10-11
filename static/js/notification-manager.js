// static/js/notification-manager.js
class NotificationManager {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.isPolling = false;
        this.init();
    }

    init() {
        console.log('NotificationManager initialized');
        this.loadNotifications();
        this.setupEventHandlers();
        this.updateBadge();
        this.startPolling();
    }

    startPolling() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        
        // Опрос сервера каждые 10 секунд для новых уведомлений
        setInterval(() => {
            this.checkServerNotifications();
        }, 10000);
        
        // Первая проверка при загрузке
        setTimeout(() => this.checkServerNotifications(), 2000);
    }

    async checkServerNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (response.ok) {
                const serverNotifications = await response.json();
                await this.processServerNotifications(serverNotifications);
            }
        } catch (error) {
            console.error('Ошибка получения уведомлений с сервера:', error);
        }
    }

    async processServerNotifications(serverNotifications) {
        let hasNew = false;
        
        for (const serverNotif of serverNotifications) {
            const exists = this.notifications.find(n => n.server_id === serverNotif.id);
            if (!exists) {
                // Добавляем новое уведомление
                const notification = {
                    id: Date.now().toString() + Math.random(),
                    server_id: serverNotif.id,
                    title: serverNotif.title,
                    message: serverNotif.message,
                    type: serverNotif.type || 'info',
                    actionUrl: serverNotif.action_url,
                    timestamp: serverNotif.created_at,
                    priority: serverNotif.priority || 'medium',
                    read: false
                };
                
                this.notifications.unshift(notification);
                this.unreadCount++;
                hasNew = true;
                
                // Показываем toast для важных уведомлений
                if (serverNotif.priority === 'high' || serverNotif.type === 'accident') {
                    this.showToast(notification);
                }
                
                // Помечаем как прочитанное на сервере
                await this.markServerNotificationRead(serverNotif.id);
            }
        }
        
        if (hasNew) {
            this.saveNotifications();
            this.renderNotifications();
            this.updateBadge();
        }
    }

    async markServerNotificationRead(serverId) {
        try {
            await fetch(`/api/notifications/${serverId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
        } catch (error) {
            console.error('Ошибка отметки уведомления как прочитанного:', error);
        }
    }

    async markAllServerNotificationsRead() {
        try {
            await fetch('/api/notifications/read-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
        } catch (error) {
            console.error('Ошибка отметки всех уведомлений как прочитанных:', error);
        }
    }

    loadNotifications() {
        const saved = localStorage.getItem('codd_notifications');
        if (saved) {
            try {
                this.notifications = JSON.parse(saved);
                this.unreadCount = this.notifications.filter(n => !n.read).length;
            } catch (e) {
                console.error('Ошибка загрузки уведомлений:', e);
                this.notifications = [];
            }
        }
        this.renderNotifications();
    }

    setupEventHandlers() {
        const clearBtn = document.getElementById('clearNotifications');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAll());
        }

        const markAllReadBtn = document.getElementById('markAllRead');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => this.markAllAsRead());
        }

        document.addEventListener('click', (e) => {
            const dropdown = document.querySelector('.notification-dropdown');
            const toggle = document.querySelector('[data-bs-toggle="dropdown"]');
            
            if (dropdown && toggle && 
                !dropdown.contains(e.target) && 
                !toggle.contains(e.target)) {
                this.closeDropdown();
            }
        });

        this.setupMobileHandlers();
    }

    setupMobileHandlers() {
        const dropdown = document.querySelector('.notification-dropdown');
        if (dropdown) {
            dropdown.addEventListener('shown.bs.dropdown', () => {
                this.adjustMobilePosition();
            });
        }

        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.adjustMobilePosition(), 100);
        });

        window.addEventListener('resize', () => {
            this.adjustMobilePosition();
        });
    }

    adjustMobilePosition() {
        const dropdown = document.querySelector('.notification-dropdown');
        if (!dropdown) return;

        const toggle = document.querySelector('[data-bs-toggle="dropdown"]');
        if (!toggle) return;

        if (window.innerWidth > 768) return;

        const toggleRect = toggle.getBoundingClientRect();
        const dropdownRect = dropdown.getBoundingClientRect();
        const viewportHeight = window.innerHeight;

        if (toggleRect.bottom + dropdownRect.height > viewportHeight) {
            const overflow = (toggleRect.bottom + dropdownRect.height) - viewportHeight;
            dropdown.style.transform = `translateY(-${overflow + 10}px)`;
        }

        if (dropdownRect.right > window.innerWidth) {
            const overflow = dropdownRect.right - window.innerWidth;
            dropdown.style.transform = `translateX(-${overflow + 10}px)`;
        }
    }

    renderNotifications() {
        const container = document.getElementById('notificationList');
        if (!container) return;

        if (this.notifications.length === 0) {
            container.innerHTML = `
                <div class="notification-empty">
                    <i class="bi bi-bell-slash"></i>
                    <p>Нет новых уведомлений</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.notifications.map(notification => `
            <div class="notification-item ${notification.read ? '' : 'unread'}" 
                 data-id="${notification.id}">
                <div class="notification-icon ${notification.type}">
                    <i class="bi ${this.getNotificationIcon(notification.type)}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${this.escapeHtml(notification.title)}</div>
                    <div class="notification-text">${this.escapeHtml(notification.message)}</div>
                    <div class="notification-time">${this.formatTime(notification.timestamp)}</div>
                </div>
                <button class="notification-close" data-id="${notification.id}">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        `).join('');

        // Обработчики для элементов уведомлений
        container.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.notification-close')) {
                    const id = item.dataset.id;
                    this.markAsRead(id);
                    this.handleNotificationClick(id);
                }
            });
        });

        // Обработчики для кнопок закрытия
        container.querySelectorAll('.notification-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                this.removeNotification(id);
            });
        });
    }

    addNotification(title, message, type = 'info', actionUrl = null) {
        const notification = {
            id: Date.now().toString(),
            title,
            message,
            type,
            actionUrl,
            timestamp: new Date().toISOString(),
            read: false
        };

        this.notifications.unshift(notification);
        this.unreadCount++;
        
        this.saveNotifications();
        this.renderNotifications();
        this.updateBadge();
        this.showToast(notification);
    }

    markAsRead(id) {
        const notification = this.notifications.find(n => n.id === id);
        if (notification && !notification.read) {
            notification.read = true;
            this.unreadCount--;
            this.saveNotifications();
            this.renderNotifications();
            this.updateBadge();
        }
    }

    async markAllAsRead() {
        // Помечаем все как прочитанные на сервере
        await this.markAllServerNotificationsRead();
        
        // Помечаем все как прочитанные локально
        this.notifications.forEach(notification => {
            if (!notification.read) {
                notification.read = true;
            }
        });
        this.unreadCount = 0;
        this.saveNotifications();
        this.renderNotifications();
        this.updateBadge();
    }

    removeNotification(id) {
        this.notifications = this.notifications.filter(n => n.id !== id);
        this.unreadCount = this.notifications.filter(n => !n.read).length;
        this.saveNotifications();
        this.renderNotifications();
        this.updateBadge();
    }

    clearAll() {
        this.notifications = [];
        this.unreadCount = 0;
        this.saveNotifications();
        this.renderNotifications();
        this.updateBadge();
        
        this.showToast({
            title: 'Уведомления очищены',
            message: 'Все уведомления были удалены',
            type: 'success'
        });
    }

    updateBadge() {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount.toString();
            badge.style.display = this.unreadCount > 0 ? 'flex' : 'none';
        }
    }

    saveNotifications() {
        try {
            localStorage.setItem('codd_notifications', JSON.stringify(this.notifications));
        } catch (e) {
            console.error('Ошибка сохранения уведомлений:', e);
        }
    }

    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = `toast notification-toast align-items-center text-bg-${this.getTypeColor(notification.type)} border-0`;
        toast.style.zIndex = '1080';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body" style="cursor: pointer;">
                    <div class="d-flex align-items-center">
                        <i class="bi ${this.getNotificationIcon(notification.type)} me-2"></i>
                        <div>
                            <strong>${this.escapeHtml(notification.title)}</strong><br>
                            <small>${this.escapeHtml(notification.message)}</small>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button>
            </div>
        `;

        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, {
            autohide: notification.priority === 'high' ? false : true,
            delay: notification.priority === 'high' ? 10000 : 5000
        });

        // Добавляем обработчик клика для перенаправления
        toast.querySelector('.toast-body').addEventListener('click', () => {
            bsToast.hide();
            this.handleNotificationClick(notification.id);
        });

        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1080';
        document.body.appendChild(container);
        return container;
    }

    handleNotificationClick(id) {
        const notification = this.notifications.find(n => n.id === id);
        if (notification) {
            this.markAsRead(id);
            
            if (notification.actionUrl) {
                window.location.href = notification.actionUrl;
            } else if (notification.type === 'accident') {
                // Перенаправляем на карту для уведомлений о ДТП
                window.location.href = '/map';
            }
        }
    }

    closeDropdown() {
        const dropdownElement = document.querySelector('.notification-dropdown');
        if (dropdownElement) {
            const dropdown = bootstrap.Dropdown.getInstance(dropdownElement);
            if (dropdown) {
                dropdown.hide();
            }
        }
    }

    getNotificationIcon(type) {
        const icons = {
            'accident': 'bi-exclamation-triangle-fill',
            'new_ticket': 'bi-megaphone',
            'comment': 'bi-chat-dots',
            'road_work': 'bi-cone-striped',
            'status_update': 'bi-check-circle-fill',
            'info': 'bi-info-circle-fill',
            'warning': 'bi-exclamation-circle-fill',
            'error': 'bi-x-circle-fill',
            'success': 'bi-check-circle-fill'
        };
        return icons[type] || 'bi-bell-fill';
    }

    getTypeColor(type) {
        const colors = {
            'info': 'primary',
            'success': 'success',
            'warning': 'warning',
            'error': 'danger',
            'accident': 'danger',
            'new_ticket': 'info',
            'comment': 'info',
            'road_work': 'warning'
        };
        return colors[type] || 'primary';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'только что';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} мин назад`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} ч назад`;
        return date.toLocaleDateString('ru-RU');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        const input = document.querySelector('input[name="csrf_token"]');
        return input ? input.value : '';
    }
}

// Глобальные методы для тестирования
window.testNotification = (type) => {
    if (window.notificationManager) {
        const testNotifications = {
            'accident': {
                title: 'Новое ДТП',
                message: 'Зарегистрировано ДТП на пересечении ул. Ленина и ул. Гагарина',
                type: 'accident'
            },
            'new_ticket': {
                title: 'Новое обращение',
                message: 'Пользователь создал новое обращение о проблеме на дороге',
                type: 'new_ticket'
            },
            'comment': {
                title: 'Новый комментарий',
                message: 'Добавлен комментарий к вашему обращению #123',
                type: 'comment'
            }
        };
        
        const notif = testNotifications[type] || testNotifications.new_ticket;
        window.notificationManager.addNotification(notif.title, notif.message, notif.type);
    }
};

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
});