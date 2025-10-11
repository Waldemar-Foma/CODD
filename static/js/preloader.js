// Упрощенный прелоадер с быстрой загрузкой
document.addEventListener('DOMContentLoaded', function() {
    const preloader = document.getElementById('preloader');
    
    // Минимальное время показа прелоадера - 300ms
    setTimeout(() => {
        preloader.classList.add('fade-out');
        
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 300);
    }, 300);
    
    // На всякий случай скрываем через 2 секунды
    setTimeout(() => {
        if (preloader.style.display !== 'none') {
            preloader.classList.add('fade-out');
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 300);
        }
    }, 2000);
});