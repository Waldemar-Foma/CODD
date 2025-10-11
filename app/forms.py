from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User
import re

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=3, max=64, message='Логин должен быть от 3 до 64 символов')
    ], render_kw={
        "placeholder": "Введите ваш логин",
        "class": "form-control-lg"
    })
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле обязательно для заполнения')
    ], render_kw={
        "placeholder": "Введите ваш пароль", 
        "class": "form-control-lg"
    })
    
    remember_me = BooleanField('Запомнить меня')
    
    submit = SubmitField('Войти', render_kw={
        "class": "btn-primary btn-lg w-100"
    })

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=3, max=64, message='Логин должен быть от 3 до 64 символов')
    ], render_kw={
        "placeholder": "Придумайте логин",
        "class": "form-control-lg"
    })
    
    email = StringField('Email', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Email(message='Введите корректный email адрес'),
        Length(max=120, message='Email должен быть не длиннее 120 символов')
    ], render_kw={
        "placeholder": "example@mail.ru",
        "class": "form-control-lg"
    })
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ], render_kw={
        "placeholder": "Придумайте пароль",
        "class": "form-control-lg"
    })
    
    password2 = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        EqualTo('password', message='Пароли должны совпадать')
    ], render_kw={
        "placeholder": "Повторите пароль",
        "class": "form-control-lg"
    })
    
    agree_terms = BooleanField('Я согласен с условиями использования', validators=[
        DataRequired(message='Необходимо принять условия использования')
    ])
    
    submit = SubmitField('Зарегистрироваться', render_kw={
        "class": "btn-primary btn-lg w-100"
    })

    def validate_username(self, username):
        # Проверка на допустимые символы
        if not re.match(r'^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('Логин может содержать только буквы, цифры и символ подчеркивания')
        
        # Проверка на занятость имени
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован. Пожалуйста, используйте другой email.')

class TicketForm(FlaskForm):
    title = StringField('Заголовок проблемы', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=5, max=100, message='Заголовок должен содержать от 5 до 100 символов')
    ], render_kw={
        "placeholder": "Кратко опишите проблему",
        "class": "form-control-lg"
    })
    
    description = TextAreaField('Подробное описание', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=10, max=1000, message='Описание должно содержать от 10 до 1000 символов')
    ], render_kw={
        "placeholder": "Опишите проблему подробно...",
        "rows": 5,
        "class": "form-control-lg"
    })
    
    location = StringField('Местоположение', validators=[
        DataRequired(message='Укажите местоположение проблемы'),
        Length(min=5, max=200, message='Местоположение должно содержать от 5 до 200 символов')
    ], render_kw={
        "placeholder": "Улица, дом, ориентир",
        "class": "form-control-lg"
    })
    
    priority = SelectField('Приоритет', choices=[
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный')
    ], default='medium', validators=[DataRequired()])
    
    image = FileField('Фотография проблемы', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                   'Разрешены только изображения (JPG, PNG, GIF, WebP)'),
        Optional()
    ])
    
    submit = SubmitField('Создать обращение', render_kw={
        "class": "btn-primary btn-lg"
    })

    def validate_title(self, title):
        if len(title.data.strip()) < 5:
            raise ValidationError('Заголовок слишком короткий. Минимум 5 символов.')
        if len(title.data.strip()) > 100:
            raise ValidationError('Заголовок слишком длинный. Максимум 100 символов.')

    def validate_description(self, description):
        if len(description.data.strip()) < 10:
            raise ValidationError('Описание слишком короткое. Минимум 10 символов.')
        if len(description.data.strip()) > 1000:
            raise ValidationError('Описание слишком длинное. Максимум 1000 символов.')

    def validate_location(self, location):
        if len(location.data.strip()) < 5:
            raise ValidationError('Местоположение слишком короткое. Минимум 5 символов.')

class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=1, max=1000, message='Комментарий должен содержать от 1 до 1000 символов')
    ], render_kw={
        "placeholder": "Введите ваш комментарий...",
        "rows": 3,
        "class": "form-control-lg"
    })
    
    is_internal = BooleanField('Внутренний комментарий (виден только администраторам)')
    
    submit = SubmitField('Добавить комментарий', render_kw={
        "class": "btn-primary"
    })

class ProfileForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=3, max=64, message='Логин должен содержать от 3 до 64 символов')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Email(message='Введите корректный email адрес')
    ])
    
    current_password = PasswordField('Текущий пароль', validators=[Optional()])
    
    new_password = PasswordField('Новый пароль', validators=[
        Optional(),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[
        EqualTo('new_password', message='Пароли должны совпадать')
    ])
    
    submit = SubmitField('Сохранить изменения')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Это имя пользователя уже занято.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Этот email уже зарегистрирован.')

class SearchForm(FlaskForm):
    query = StringField('Поиск', validators=[
        DataRequired(message='Введите поисковый запрос'),
        Length(min=2, max=100, message='Запрос должен содержать от 2 до 100 символов')
    ], render_kw={
        "placeholder": "Поиск обращений, пользователей...",
        "class": "form-control-lg"
    })
    
    submit = SubmitField('Найти')

class ContactForm(FlaskForm):
    name = StringField('Ваше имя', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=2, max=100, message='Имя должно содержать от 2 до 100 символов')
    ], render_kw={
        "placeholder": "Введите ваше имя",
        "class": "form-control-lg"
    })
    
    email = StringField('Email', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Email(message='Введите корректный email адрес'),
        Length(max=120, message='Email должен быть не длиннее 120 символов')
    ], render_kw={
        "placeholder": "example@mail.ru",
        "class": "form-control-lg"
    })
    
    phone = StringField('Телефон', validators=[
        Optional(),
        Length(max=20, message='Телефон не должен превышать 20 символов')
    ], render_kw={
        "placeholder": "+7 (XXX) XXX-XX-XX",
        "class": "form-control-lg"
    })
    
    subject = StringField('Тема сообщения', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=5, max=200, message='Тема должна содержать от 5 до 200 символов')
    ], render_kw={
        "placeholder": "Тема вашего сообщения",
        "class": "form-control-lg"
    })
    
    message = TextAreaField('Сообщение', validators=[
        DataRequired(message='Поле обязательно для заполнения'),
        Length(min=10, max=1000, message='Сообщение должно содержать от 10 до 1000 символов')
    ], render_kw={
        "placeholder": "Введите ваше сообщение...",
        "rows": 5,
        "class": "form-control-lg"
    })
    
    submit = SubmitField('Отправить сообщение', render_kw={
        "class": "btn-primary btn-lg w-100"
    })

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=200)])
    excerpt = TextAreaField('Краткое описание', validators=[Length(max=500)])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    active = BooleanField('Активно')
    submit = SubmitField('Сохранить')

class AccidentMarkerForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание')
    address = StringField('Адрес', validators=[DataRequired()])
    severity = SelectField('Серьезность', choices=[
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
        ('critical', 'Критическая')
    ], default='medium')
    lat = StringField('Широта', validators=[DataRequired()])
    lng = StringField('Долгота', validators=[DataRequired()])
    submit = SubmitField('Добавить метку')
