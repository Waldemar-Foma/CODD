from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.before_app_request
def before_request():
    """Действия перед каждым запросом"""
    if current_user.is_authenticated:
        current_user.update_last_login()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if current_user.is_authenticated:
        flash('Вы уже авторизованы', 'info')
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            user = User.query.filter(
                (User.username == form.username.data) | 
                (User.email == form.username.data)
            ).first()
            
            if user and user.check_password(form.password.data):
                if not user.is_active:
                    flash('⛔ Ваш аккаунт заблокирован. Обратитесь к администратору.', 'danger')
                    return render_template('auth/login.html', form=form)

                login_user(user, remember=form.remember_me.data)
                user.update_last_login()
                
                print(f'Пользователь {user.username} вошел в систему с IP: {request.remote_addr}')
                
                flash(f'✅ Добро пожаловать, {user.username}!', 'success')
                
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.index')
                return redirect(next_page)
            else:
                flash('❌ Неверное имя пользователя или пароль', 'danger')
                
        except Exception as e:
            flash('❌ Произошла ошибка при входе. Пожалуйста, попробуйте еще раз.', 'danger')
            print(f'Ошибка входа: {e}')
    
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'❌ {error}', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if current_user.is_authenticated:
        flash('Вы уже авторизованы', 'info')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter(
                (User.username == form.username.data) | 
                (User.email == form.email.data)
            ).first()
            
            if existing_user:
                if existing_user.username == form.username.data:
                    flash('❌ Пользователь с таким именем уже существует', 'danger')
                else:
                    flash('❌ Пользователь с таким email уже существует', 'danger')
                return render_template('auth/register.html', form=form)
            
            user = User(
                username=form.username.data,
                email=form.email.data,
                is_active=True
            )
            user.set_password(form.password.data)
            
            if User.query.count() == 0:
                user.is_admin = True
                user.is_active = True
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            user.update_last_login()
            
            flash(f'✅ Регистрация успешна! Добро пожаловать, {user.username}!', 'success')
            
            print(f'Зарегистрирован новый пользователь: {user.username} ({user.email})')
            
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.', 'danger')
            print(f'Ошибка регистрации: {e}')
    
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'❌ {error}', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash('✅ Вы успешно вышли из системы', 'success')
    
    print(f'Пользователь {username} вышел из системы')
    
    return redirect(url_for('main.index'))

@auth_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_profile():
    if not current_user.is_admin:
        flash('⛔ Удаление аккаунта недоступно', 'danger')
        return redirect(url_for('main.profile'))
    
    try:
        user_id = request.form.get('user_id')
        if user_id and current_user.is_admin:
            user = User.query.get(user_id)
            if user and user.id != current_user.id:
                db.session.delete(user)
                db.session.commit()
                flash('✅ Аккаунт пользователя удален', 'success')
            else:
                flash('❌ Нельзя удалить свой аккаунт', 'danger')
    except Exception as e:
        db.session.rollback()
        flash('❌ Ошибка при удалении аккаунта', 'danger')
        print(f'Ошибка удаления аккаунта: {e}')
    
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/forgot-password')
def forgot_password():
    flash('⚠️ Функция восстановления пароля временно недоступна. Обратитесь к администратору.', 'warning')
    return redirect(url_for('auth.login'))
