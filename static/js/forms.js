function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            // Валидация email
            const emailInputs = this.querySelectorAll('input[type="email"]');
            emailInputs.forEach(input => {
                if (input.value && !isValidEmail(input.value)) {
                    input.classList.add('is-invalid');
                    isValid = false;
                }
            });

            // Валидация пароля
            const passwordInputs = this.querySelectorAll('input[type="password"]');
            if (passwordInputs.length > 1) {
                const password = passwordInputs[0].value;
                const confirmPassword = passwordInputs[1].value;
                
                if (password !== confirmPassword) {
                    passwordInputs[1].classList.add('is-invalid');
                    isValid = false;
                }
            }

            if (!isValid) {
                e.preventDefault();
                showToast('Пожалуйста, проверьте правильность заполнения полей', 'warning');
            } else {
                // Показываем индикатор загрузки
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Обработка...';
                }
            }
        });
    });

    // Убираем класс ошибки при вводе
    document.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            
            // Счетчик символов для textarea
            if (this.tagName === 'TEXTAREA' && this.maxLength) {
                updateCharCounter(this);
            }
        });
    });

    // Инициализация счетчиков символов
    initCharCounters();
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function initCharCounters() {
    document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'form-text text-end char-counter';
        counter.innerHTML = `<span class="char-count">0</span> / ${maxLength}`;
        textarea.parentNode.appendChild(counter);
        updateCharCounter(textarea);
    });
}

function updateCharCounter(textarea) {
    const counter = textarea.parentNode.querySelector('.char-counter');
    if (counter) {
        const count = textarea.value.length;
        const maxLength = textarea.getAttribute('maxlength');
        counter.querySelector('.char-count').textContent = count;
        
        if (count > maxLength * 0.9) {
            counter.classList.add('text-warning');
        } else {
            counter.classList.remove('text-warning');
        }
        
        if (count > maxLength) {
            counter.classList.add('text-danger');
        } else {
            counter.classList.remove('text-danger');
        }
    }
}