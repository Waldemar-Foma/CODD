from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required, fresh_login_required
from flask import abort
from app import db
from datetime import datetime, timezone, timedelta
from app.models import Ticket, User, Comment, News, Service, Document, Vacancy, Project, Partner, Notification, AccidentMarker
from app.forms import TicketForm, CommentForm, ProfileForm, SearchForm, ContactForm, NewsForm, AccidentMarkerForm
from app.helpers import allowed_file, save_uploaded_file
import os
from datetime import datetime, timezone
from sqlalchemy import or_, and_, func
import json
import csv
from io import StringIO

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'app_name': 'ЦОДД Смоленской области',
        'app_version': '2.0.0'
    }

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    stats = {
        'total_tickets': Ticket.query.count(),
        'resolved_tickets': Ticket.query.filter_by(status='resolved').count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'new_tickets_today': Ticket.query.filter(
            Ticket.created_at >= datetime.now(timezone.utc).date()
        ).count()
    }
    
    recent_news = News.query.filter_by(active=True).order_by(
        News.created_at.desc()
    ).limit(3).all()
    
    active_projects = Project.query.filter_by(active=True, is_free=True).limit(3).all()
    
    partners = Partner.query.filter_by(active=True).all()
    
    return render_template('index.html', 
                         stats=stats, 
                         recent_news=recent_news,
                         active_projects=active_projects,
                         partners=partners)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('main.admin_dashboard'))
    
    # Статистика ДТП для обычных пользователей
    accident_stats = {
        'last_month': Ticket.query.filter(
            Ticket.priority == 'urgent',
            Ticket.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
        ).count(),
        'last_year': Ticket.query.filter(
            Ticket.priority == 'urgent',
            Ticket.created_at >= datetime.now(timezone.utc) - timedelta(days=365)
        ).count(),
        'fatalities_month': db.session.query(func.sum(Ticket.fatalities)).filter(
            Ticket.priority == 'urgent',
            Ticket.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
        ).scalar() or 0,
        'fatalities_year': db.session.query(func.sum(Ticket.fatalities)).filter(
            Ticket.priority == 'urgent',
            Ticket.created_at >= datetime.now(timezone.utc) - timedelta(days=365)
        ).scalar() or 0,
        'resolved_accidents': Ticket.query.filter(
            Ticket.priority == 'urgent',
            Ticket.status == 'resolved'
        ).count()
    }
    
    # Последние новости
    recent_news = News.query.filter_by(active=True).order_by(
        News.created_at.desc()
    ).limit(5).all()
    
    # Последние ДТП
    recent_accidents = Ticket.query.filter_by(priority='urgent').order_by(
        Ticket.created_at.desc()
    ).limit(5).all()
    
    return render_template('user_dashboard.html',
                         accident_stats=accident_stats,
                         recent_news=recent_news,
                         recent_accidents=recent_accidents,
                         title='Панель управления')

@main_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('⛔ Доступ к панели управления ограничен', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        stats = {
            'total_tickets': Ticket.query.count(),
            'new_tickets': Ticket.query.filter_by(status='new').count(),
            'in_progress_tickets': Ticket.query.filter_by(status='in_progress').count(),
            'resolved_tickets': Ticket.query.filter_by(status='resolved').count(),
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_services': Service.query.filter_by(active=True).count(),
            'active_projects': Project.query.filter_by(active=True).count(),
            'new_tickets_today': Ticket.query.filter(
                Ticket.created_at >= datetime.now(timezone.utc).date()
            ).count(),
            'urgent_tickets': Ticket.query.filter_by(priority='urgent').count()
        }
        
        # Срочные обращения и ДТП
        urgent_tickets = Ticket.query.filter(
            or_(Ticket.priority == 'urgent', Ticket.status == 'new')
        ).order_by(Ticket.created_at.desc()).limit(10).all()
        
        recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_news = News.query.order_by(News.created_at.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html',
                             stats=stats,
                             urgent_tickets=urgent_tickets,
                             recent_tickets=recent_tickets,
                             recent_users=recent_users,
                             recent_news=recent_news,
                             title='Панель управления администратора')
    
    except Exception as e:
        current_app.logger.error(f'Ошибка в admin_dashboard: {e}')
        flash('❌ Ошибка при загрузке панели управления', 'danger')
        return redirect(url_for('main.index'))
    
@main_bp.route('/about')
def about():
    return render_template('about.html', 
                         title='О ЦОДД Смоленской области')

@main_bp.route('/terms_of_using')
def terms_of_using():
    return render_template('terms_of_using.html', 
                         title='Правила пользования сайтом ЦОДД Смоленской области')

@main_bp.route('/privacy_politics')
def privacy_politics():
    return render_template('privacy_politics.html', 
                         title='Политика конфиденциальности сайта ЦОДД Смоленской области')

@main_bp.route('/documents')
def documents():
    documents = Document.query.filter_by(active=True).order_by(
        Document.category.asc(), 
        Document.created_at.desc()
    ).all()
    
    categories = {}
    for doc in documents:
        if doc.category not in categories:
            categories[doc.category] = []
        categories[doc.category].append(doc)
    
    return render_template('documents.html', 
                         categories=categories,
                         title='Документы')

@main_bp.route('/team')
def team():
    team_members = User.query.filter_by(is_active=True, show_in_team=True).order_by(
        User.team_order.asc()
    ).all()
    
    return render_template('team.html', 
                         team_members=team_members,
                         title='Наша команда')

@main_bp.route('/projects')
def projects():
    projects = Project.query.filter_by(active=True, is_free=True).order_by(
        Project.created_at.desc()
    ).all()
    
    return render_template('projects.html', 
                         projects=projects,
                         title='Бесплатные проекты')

@main_bp.route('/news')
def news():
    news_list = News.query.filter_by(active=True).order_by(
        News.created_at.desc()
    ).all()
    
    return render_template('news.html', 
                         news=news_list,
                         title='Новости')

@main_bp.route('/vacancies')
def vacancies():
    vacancies = Vacancy.query.filter_by(active=True).order_by(
        Vacancy.created_at.desc()
    ).all()
    
    return render_template('vacancies.html', 
                         vacancies=vacancies,
                         title='Вакансии')

@main_bp.route('/api/get-current-user')
@login_required
def get_current_user_api():
    return jsonify({
        'username': current_user.username,
        'profile_icon': current_user.profile_icon
    })

@main_bp.route('/contacts', methods=['GET', 'POST'])
def contacts():
    form = ContactForm()
    
    if form.validate_on_submit():
        flash('Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('main.contacts'))
    
    departments = [
        {
            'name': 'Технический отдел',
            'phone': '+7 (4812) 33-99-70',
            'email': 'tech@codd-smolensk.ru',
            'hours': 'Пн-Пт: 8:00-17:00',
            'icon': 'bi-tools'
        },
        {
            'name': 'Отдел проектирования',
            'phone': '+7 (4812) 33-99-71',
            'email': 'project@codd-smolensk.ru',
            'hours': 'Пн-Пт: 9:00-18:00',
            'icon': 'bi-clipboard-check'
        },
        {
            'name': 'Служба поддержки',
            'phone': '+7 (4812) 33-99-69',
            'email': 'support@codd-smolensk.ru',
            'hours': 'Пн-Пт: 9:00-18:00',
            'icon': 'bi-headset'
        }
    ]
    
    return render_template('contacts.html', 
                         form=form,
                         departments=departments,
                         title='Контакты')

@main_bp.route('/services')
def services():
    services_list = Service.query.filter_by(active=True, is_commercial=True).order_by(
        Service.price.asc()
    ).all()
    
    return render_template('services.html', 
                         services=services_list,
                         title='Коммерческие услуги')

@main_bp.route('/free-services')
def free_services():
    free_services_list = Service.query.filter_by(active=True, is_commercial=False).order_by(
        Service.name.asc()
    ).all()
    
    return render_template('free_services.html', 
                         services=free_services_list,
                         title='Бесплатные сервисы')

@main_bp.route('/service/<int:service_id>')
def service_details(service_id):
    service = Service.query.get_or_404(service_id)
    
    return render_template('service_details.html', 
                         service=service,
                         title=service.name)

@main_bp.route('/service/<int:service_id>/order', methods=['GET', 'POST'])
@login_required
def order_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        flash(f'Заказ на услугу "{service.name}" успешно оформлен! Мы свяжемся с вами для уточнения деталей.', 'success')
        return redirect(url_for('main.services'))
    
    return render_template('order_service.html', 
                         service=service,
                         title=f'Заказ услуги: {service.name}')

@main_bp.route('/map')
def map():
    tickets = Ticket.query.filter(
        Ticket.lat.isnot(None),
        Ticket.lng.isnot(None),
        Ticket.status.in_(['new', 'in_progress'])
    ).all()
    
    # Получаем метки ДТП
    accident_markers = AccidentMarker.query.filter_by(active=True).all()
    
    map_stats = {
        'accidents': Ticket.query.filter_by(priority='urgent').count(),
        'works': Ticket.query.filter_by(status='in_progress').count(),
        'new': Ticket.query.filter_by(status='new').count(),
        'resolved_today': Ticket.query.filter(
            Ticket.status == 'resolved',
            Ticket.updated_at >= datetime.now(timezone.utc).date()
        ).count()
    }
    
    return render_template('map.html', 
                         tickets=tickets, 
                         accident_markers=accident_markers,
                         map_stats=map_stats,
                         yandex_api_key=current_app.config.get('YANDEX_MAPS_API_KEY', ''))

@main_bp.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    
    if form.validate_on_submit():
        try:
            ticket = Ticket(
                title=form.title.data,
                description=form.description.data,
                location=form.location.data,
                lat=request.form.get('lat', type=float),
                lng=request.form.get('lng', type=float),
                priority=form.priority.data,
                author=current_user
            )
            
            if form.image.data and allowed_file(form.image.data.filename):
                filename = save_uploaded_file(form.image.data, current_app.config['UPLOAD_FOLDER'])
                if filename:
                    ticket.image_path = filename
            
            db.session.add(ticket)
            db.session.commit()
            
            # Создаем уведомление для администраторов
            admins = User.query.filter_by(is_admin=True).all()
            for admin in admins:
                notification = Notification(
                    user_id=admin.id,
                    title='Новое обращение',
                    message=f'Создано новое обращение: {ticket.title}',
                    type='new_ticket',
                    action_url=url_for('main.ticket_details', ticket_id=ticket.id),
                    priority='medium'
                )
                db.session.add(notification)
            
            db.session.commit()
            
            flash('✅ Ваше обращение успешно создано! Мы уже работаем над его решением.', 'success')
            return redirect(url_for('main.ticket_details', ticket_id=ticket.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Ошибка при создании обращения: {e}')
            flash('❌ Произошла ошибка при создании обращения. Пожалуйста, попробуйте еще раз.', 'danger')
    
    default_lat = 54.7826
    default_lng = 32.0453
    
    return render_template('create_ticket.html', 
                         form=form, 
                         default_lat=default_lat, 
                         default_lng=default_lng,
                         title='Сообщить о проблеме')

@main_bp.route('/ticket/<int:ticket_id>')
def ticket_details(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    comment_form = CommentForm()
    
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('⛔ Доступ к этому обращению ограничен', 'danger')
        return redirect(url_for('main.tickets_list'))
    
    return render_template('ticket_details.html', 
                         ticket=ticket, 
                         comment_form=comment_form,
                         title=f'Обращение #{ticket_id}')

@main_bp.route('/ticket/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = CommentForm()
    
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('⛔ Недостаточно прав для добавления комментария', 'danger')
        return redirect(url_for('main.ticket_details', ticket_id=ticket_id))
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            is_internal=form.is_internal.data and current_user.is_admin,
            author=current_user,
            ticket=ticket
        )
        
        db.session.add(comment)
        
        # Создаем уведомление для автора тикета (если комментарий не от автора)
        if ticket.user_id != current_user.id:
            notification = Notification(
                user_id=ticket.user_id,
                title='Новый комментарий',
                message=f'Добавлен комментарий к вашему обращению: {ticket.title}',
                type='comment',
                action_url=url_for('main.ticket_details', ticket_id=ticket.id),
                priority='medium'
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('✅ Комментарий успешно добавлен', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'❌ Ошибка в поле {getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('main.ticket_details', ticket_id=ticket_id))

@main_bp.route('/tickets')
@login_required
def tickets_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    status_filter = request.args.get('status', 'all')
    
    if not current_user.is_admin:
        tickets_query = Ticket.query.filter_by(user_id=current_user.id)
    else:
        tickets_query = Ticket.query
    
    if status_filter != 'all':
        tickets_query = tickets_query.filter_by(status=status_filter)
    
    tickets = tickets_query.order_by(Ticket.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Статистика для фильтров
    stats = {
        'all': tickets_query.count(),
        'new': Ticket.query.filter_by(status='new').count(),
        'in_progress': Ticket.query.filter_by(status='in_progress').count(),
        'resolved': Ticket.query.filter_by(status='resolved').count(),
    }
    
    return render_template('tickets.html', 
                         tickets=tickets,
                         stats=stats,
                         status_filter=status_filter,
                         title='Мои обращения')

@main_bp.route('/admin/tickets')
@login_required
def admin_tickets():
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    
    # Базовый запрос
    tickets_query = Ticket.query
    
    # Фильтры
    if status_filter != 'all':
        tickets_query = tickets_query.filter_by(status=status_filter)
    
    if priority_filter != 'all':
        tickets_query = tickets_query.filter_by(priority=priority_filter)
    
    tickets = tickets_query.order_by(Ticket.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Статистика для фильтров
    stats = {
        'all': Ticket.query.count(),
        'new': Ticket.query.filter_by(status='new').count(),
        'in_progress': Ticket.query.filter_by(status='in_progress').count(),
        'resolved': Ticket.query.filter_by(status='resolved').count(),
        'urgent': Ticket.query.filter_by(priority='urgent').count(),
    }
    
    return render_template('admin/tickets.html',
                         tickets=tickets,
                         stats=stats,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         title='Управление обращениями')

@main_bp.route('/admin/analytics')
@login_required
def admin_analytics():
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    # Статистика по дням (последние 30 дней)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    daily_stats = db.session.query(
        func.date(Ticket.created_at).label('date'),
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.created_at >= thirty_days_ago
    ).group_by(
        func.date(Ticket.created_at)
    ).order_by('date').all()
    
    # Преобразуем даты в правильный формат для отображения
    formatted_daily_stats = []
    for stat in daily_stats:
        # В SQLite stat.date - это строка, преобразуем в datetime если нужно
        if isinstance(stat.date, str):
            date_obj = datetime.strptime(stat.date, '%Y-%m-%d').date()
        else:
            date_obj = stat.date
        formatted_daily_stats.append({
            'date': date_obj.strftime('%d.%m.%Y'),
            'count': stat.count
        })
    
    # Статистика по статусам
    status_stats = db.session.query(
        Ticket.status,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.status).all()
    
    # Статистика по приоритетам
    priority_stats = db.session.query(
        Ticket.priority,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.priority).all()
    
    # Статистика ДТП по месяцам (совместимо с SQLite)
    accident_stats_monthly = db.session.query(
        func.strftime('%Y-%m', Ticket.created_at).label('month'),
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.priority == 'urgent',
        Ticket.created_at >= datetime.now(timezone.utc) - timedelta(days=365)
    ).group_by(
        func.strftime('%Y-%m', Ticket.created_at)
    ).order_by('month').all()
    
    # Статистика по времени решения (в днях)
    resolution_stats = db.session.query(
        func.avg(
            func.julianday(Ticket.updated_at) - func.julianday(Ticket.created_at)
        ).label('avg_resolution_days')
    ).filter(
        Ticket.status == 'resolved',
        Ticket.updated_at.isnot(None)
    ).first()
    
    # Топ активных пользователей
    active_users = db.session.query(
        User.username,
        func.count(Ticket.id).label('ticket_count')
    ).join(Ticket).group_by(User.id, User.username).order_by(
        func.count(Ticket.id).desc()
    ).limit(10).all()
    
    # Последние обращения для таблицы
    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()
    
    return render_template('admin/analytics.html',
                         daily_stats=formatted_daily_stats,  # Используем отформатированные данные
                         status_stats=status_stats,
                         priority_stats=priority_stats,
                         accident_stats_monthly=accident_stats_monthly,
                         resolution_stats=resolution_stats,
                         active_users=active_users,
                         recent_tickets=recent_tickets,
                         title='Аналитика')

@main_bp.route('/api/admin/chart-data')
@login_required
def admin_chart_data():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Данные для круговой диаграммы статусов
        status_data = []
        status_stats = db.session.query(
            Ticket.status,
            func.count(Ticket.id).label('count')
        ).group_by(Ticket.status).all()
        
        status_colors = {
            'new': '#4CAF50',
            'in_progress': '#FF9800', 
            'resolved': '#2196F3',
            'closed': '#9E9E9E'
        }
        
        for status, count in status_stats:
            status_data.append({
                'status': status,
                'count': count,
                'color': status_colors.get(status, '#CCCCCC')
            })
        
        # Данные для графика по дням (последние 7 дней)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        daily_data = db.session.query(
            func.date(Ticket.created_at).label('date'),
            func.count(Ticket.id).label('count')
        ).filter(
            Ticket.created_at >= seven_days_ago
        ).group_by(
            func.date(Ticket.created_at)
        ).order_by('date').all()
        
        # Создаем полный список дат за последние 7 дней
        dates = []
        counts = []
        current_date = seven_days_ago.date()
        
        for i in range(7):
            date_str = current_date.strftime('%d.%m')
            dates.append(date_str)
            
            # Находим количество обращений для этой даты
            count = 0
            for day in daily_data:
                # В SQLite func.date() возвращает строку, поэтому сравниваем как строки
                if str(day.date) == str(current_date):
                    count = day.count
                    break
            
            counts.append(count)
            current_date += timedelta(days=1)
        
        # Данные для ДТП по месяцам (совместимо с SQLite)
        accident_monthly_data = db.session.query(
            func.strftime('%Y-%m', Ticket.created_at).label('month'),
            func.count(Ticket.id).label('count')
        ).filter(
            Ticket.priority == 'urgent',
            Ticket.created_at >= datetime.now(timezone.utc) - timedelta(days=365)
        ).group_by(
            func.strftime('%Y-%m', Ticket.created_at)
        ).order_by('month').all()
        
        accident_months = []
        accident_counts = []
        for month_data in accident_monthly_data:
            # Преобразуем "2024-10" в "Окт 2024"
            year, month = month_data.month.split('-')
            month_names = {
                '01': 'Янв', '02': 'Фев', '03': 'Мар', '04': 'Апр',
                '05': 'Май', '06': 'Июн', '07': 'Июл', '08': 'Авг',
                '09': 'Сен', '10': 'Окт', '11': 'Ноя', '12': 'Дек'
            }
            accident_months.append(f"{month_names.get(month, month)} {year}")
            accident_counts.append(month_data.count)
        
        return jsonify({
            'status_data': status_data,
            'daily_data': {
                'dates': dates,
                'counts': counts
            },
            'accident_data': {
                'months': accident_months,
                'counts': accident_counts
            }
        })
    
    except Exception as e:
        current_app.logger.error(f'Error in admin_chart_data: {e}')
        # Возвращаем тестовые данные при ошибке
        return jsonify({
            'status_data': [
                {'status': 'new', 'count': 10, 'color': '#4CAF50'},
                {'status': 'in_progress', 'count': 5, 'color': '#FF9800'},
                {'status': 'resolved', 'count': 25, 'color': '#2196F3'}
            ],
            'daily_data': {
                'dates': ['01.10', '02.10', '03.10', '04.10', '05.10', '06.10', '07.10'],
                'counts': [3, 5, 2, 7, 4, 6, 3]
            },
            'accident_data': {
                'months': ['Сен 2024', 'Окт 2024'],
                'counts': [8, 12]
            }
        })

@main_bp.route('/admin/export-analytics/<export_type>')
@login_required
def export_analytics(export_type):
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    if export_type == 'csv':
        # Экспорт в CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Заголовки
        writer.writerow(['Дата', 'Количество обращений', 'Новые', 'В работе', 'Решено'])
        
        # Данные за последние 30 дней
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        daily_stats = db.session.query(
            func.date(Ticket.created_at).label('date'),
            func.count(Ticket.id).label('total'),
            func.sum(func.case((Ticket.status == 'new', 1), else_=0)).label('new'),
            func.sum(func.case((Ticket.status == 'in_progress', 1), else_=0)).label('in_progress'),
            func.sum(func.case((Ticket.status == 'resolved', 1), else_=0)).label('resolved')
        ).filter(
            Ticket.created_at >= thirty_days_ago
        ).group_by(
            func.date(Ticket.created_at)
        ).order_by('date').all()
        
        for stat in daily_stats:
            writer.writerow([
                stat.date.strftime('%Y-%m-%d'),
                stat.total,
                stat.new or 0,
                stat.in_progress or 0,
                stat.resolved or 0
            ])
        
        output.seek(0)
        return current_app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=analytics.csv'}
        )
    
    elif export_type == 'json':
        # Экспорт в JSON
        stats = {
            'total_tickets': Ticket.query.count(),
            'new_tickets': Ticket.query.filter_by(status='new').count(),
            'in_progress_tickets': Ticket.query.filter_by(status='in_progress').count(),
            'resolved_tickets': Ticket.query.filter_by(status='resolved').count(),
            'urgent_tickets': Ticket.query.filter_by(priority='urgent').count(),
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'exported_at': datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify(stats)
    
    else:
        flash('❌ Неподдерживаемый формат экспорта', 'danger')
        return redirect(url_for('main.admin_analytics'))

@main_bp.route('/ticket/<int:ticket_id>/update_status/<status>')
@login_required
def update_status(ticket_id, status):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('⛔ Недостаточно прав для выполнения этого действия', 'danger')
        return redirect(url_for('main.index'))
    
    if status in ['new', 'in_progress', 'resolved']:
        ticket.status = status
        ticket.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f'✅ Статус обращения обновлен', 'success')
    else:
        flash('❌ Неверный статус', 'danger')
    
    return redirect(request.referrer or url_for('main.tickets_list'))

@main_bp.route('/ticket/<int:ticket_id>/confirm-accident', methods=['POST'])
@login_required
def confirm_accident(ticket_id):
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Создаем метку ДТП
    accident_marker = AccidentMarker(
        lat=ticket.lat or 54.7826,
        lng=ticket.lng or 32.0453,
        title=f'ДТП #{ticket.id} - {ticket.title}',
        description=ticket.description,
        severity='high',
        address=ticket.location or 'Неизвестное местоположение',
        created_by=current_user.id
    )
    
    db.session.add(accident_marker)
    
    # Создаем уведомления для всех пользователей
    users = User.query.filter_by(is_active=True).all()
    for user in users:
        notification = Notification(
            user_id=user.id,
            title='Подтверждено ДТП',
            message=f'Подтверждено ДТП на {ticket.location or "неизвестной улице"}',
            type='accident',
            action_url=url_for('main.map', _external=True) + f'?accident={accident_marker.id}',
            priority='high'
        )
        db.session.add(notification)
    
    # Обновляем статус тикета
    ticket.status = 'resolved'
    ticket.updated_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    flash('✅ ДТП подтверждено и уведомления отправлены', 'success')
    return redirect(url_for('main.admin_tickets'))

@main_bp.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('⛔ Недостаточно прав для удаления', 'danger')
        return redirect(url_for('main.tickets_list'))
    
    try:
        # Удаляем связанные комментарии
        Comment.query.filter_by(ticket_id=ticket_id).delete()
        # Удаляем сам тикет
        db.session.delete(ticket)
        db.session.commit()
        flash('✅ Обращение успешно удалено', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Ошибка при удалении обращения', 'danger')
        current_app.logger.error(f'Ошибка удаления тикета: {e}')
    
    return redirect(request.referrer or url_for('main.tickets_list'))

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(original_username=current_user.username,
                      original_email=current_user.email,
                      obj=current_user)
    
    if form.validate_on_submit():
        try:
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            if form.new_password.data:
                if form.current_password.data and current_user.check_password(form.current_password.data):
                    current_user.set_password(form.new_password.data)
                    flash('✅ Пароль успешно изменен', 'success')
                else:
                    flash('❌ Текущий пароль указан неверно', 'danger')
                    return render_template('profile.html', form=form)
            
            db.session.commit()
            flash('✅ Профиль успешно обновлен', 'success')
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('❌ Ошибка при обновлении профиля', 'danger')
            current_app.logger.error(f'Ошибка обновления профиля: {e}')
    
    return render_template('profile.html', 
                         form=form,
                         title='Профиль пользователя')

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html',
                         title='Настройки')

# API для уведомлений
@main_bp.route('/api/notifications')
@login_required
def api_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        read=False
    ).order_by(Notification.created_at.desc()).limit(20).all()
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'action_url': notification.action_url,
            'created_at': notification.created_at.isoformat(),
            'priority': notification.priority
        })
    
    return jsonify(notifications_data)

@main_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})

@main_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(
        user_id=current_user.id,
        read=False
    ).update({'read': True})
    
    db.session.commit()
    
    return jsonify({'success': True})

# API для меток ДТП
@main_bp.route('/api/accident-markers', methods=['GET'])
def api_accident_markers():
    markers = AccidentMarker.query.filter_by(active=True).all()
    
    markers_data = []
    for marker in markers:
        markers_data.append({
            'id': marker.id,
            'lat': marker.lat,
            'lng': marker.lng,
            'title': marker.title,
            'description': marker.description,
            'severity': marker.severity,
            'created_at': marker.created_at.isoformat(),
            'address': marker.address
        })
    
    return jsonify(markers_data)

@main_bp.route('/admin/accident-markers')
@login_required
def admin_accident_markers():
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    form = AccidentMarkerForm()
    markers = AccidentMarker.query.order_by(AccidentMarker.created_at.desc()).all()
    
    return render_template('admin/accident_markers.html',
                         form=form,
                         markers=markers,
                         title='Управление метками ДТП')

@main_bp.route('/api/accident-markers', methods=['POST'])
@login_required
def create_accident_marker():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    marker = AccidentMarker(
        lat=data['lat'],
        lng=data['lng'],
        title=data['title'],
        description=data.get('description', ''),
        severity=data.get('severity', 'medium'),
        address=data.get('address', ''),
        created_by=current_user.id
    )
    
    db.session.add(marker)
    db.session.commit()
    
    # Создаем уведомление для всех пользователей
    users = User.query.filter_by(is_active=True).all()
    for user in users:
        notification = Notification(
            user_id=user.id,
            title='Новое ДТП',
            message=f'Произошло ДТП на {data.get("address", "неизвестной улице")}',
            type='accident',
            action_url=url_for('main.map', _external=True) + f'?accident={marker.id}',
            priority='high'
        )
        db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'marker': {
            'id': marker.id,
            'lat': marker.lat,
            'lng': marker.lng,
            'title': marker.title
        }
    })

@main_bp.route('/api/accident-markers/<int:marker_id>', methods=['DELETE'])
@login_required
def delete_accident_marker(marker_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    marker = AccidentMarker.query.get_or_404(marker_id)
    db.session.delete(marker)
    db.session.commit()
    
    return jsonify({'success': True})

# Управление новостями
@main_bp.route('/admin/news')
@login_required
def admin_news():
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    news_list = News.query.order_by(News.created_at.desc()).all()
    form = NewsForm()
    
    return render_template('admin/news.html',
                         news_list=news_list,
                         form=form,
                         title='Управление новостями')

@main_bp.route('/admin/news/create', methods=['POST'])
@login_required
def create_news():
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    form = NewsForm()
    
    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            author_id=current_user.id,
            active=form.active.data
        )
        
        db.session.add(news)
        db.session.commit()
        
        flash('✅ Новость успешно создана', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'❌ Ошибка в поле {getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('main.admin_news'))

@main_bp.route('/admin/news/<int:news_id>/edit', methods=['POST'])
@login_required
def edit_news(news_id):
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    news = News.query.get_or_404(news_id)
    form = NewsForm()
    
    if form.validate_on_submit():
        news.title = form.title.data
        news.content = form.content.data
        news.excerpt = form.excerpt.data
        news.active = form.active.data
        news.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        flash('✅ Новость успешно обновлена', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'❌ Ошибка в поле {getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('main.admin_news'))

@main_bp.route('/admin/news/<int:news_id>/delete', methods=['POST'])
@login_required
def delete_news(news_id):
    if not current_user.is_admin:
        flash('⛔ Доступ ограничен', 'danger')
        return redirect(url_for('main.index'))
    
    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    
    flash('✅ Новость успешно удалена', 'success')
    return redirect(url_for('main.admin_news'))

@main_bp.route('/api/tickets')
def api_tickets():
    tickets = Ticket.query.filter(
        Ticket.lat.isnot(None),
        Ticket.lng.isnot(None),
        Ticket.status.in_(['new', 'in_progress'])
    ).all()
    
    tickets_data = []
    for ticket in tickets:
        tickets_data.append({
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'lat': ticket.lat,
            'lng': ticket.lng,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created_at.isoformat(),
            'image_url': url_for('static', filename=f'uploads/{ticket.image_path}') if ticket.image_path else None
        })
    
    return jsonify(tickets_data)

@main_bp.route('/api/stats')
def api_stats():
    stats = {
        'total_tickets': Ticket.query.count(),
        'new_tickets': Ticket.query.filter_by(status='new').count(),
        'in_progress_tickets': Ticket.query.filter_by(status='in_progress').count(),
        'resolved_tickets': Ticket.query.filter_by(status='resolved').count(),
        'total_users': User.query.count(),
        'online_users': User.query.filter(
            User.last_seen >= datetime.now(timezone.utc) - timedelta(minutes=5)
        ).count()
    }
    
    return jsonify(stats)

@main_bp.route('/api/traffic-data')
def api_traffic_data():
    data = {
        'congestion_level': 'medium',
        'incidents': [
            {
                'type': 'accident', 
                'location': [54.7826, 32.0453], 
                'description': 'ДТП на перекрестке',
                'severity': 'high'
            },
            {
                'type': 'repair', 
                'location': [54.7865, 32.0387], 
                'description': 'Дорожные работы',
                'severity': 'medium'
            }
        ],
        'updated': datetime.now(timezone.utc).isoformat()
    }
    
    return jsonify(data)

@main_bp.route('/api/services')
def api_services():
    services = Service.query.filter_by(active=True).all()
    
    services_data = []
    for service in services:
        services_data.append({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'price': service.price,
            'category': service.category,
            'is_commercial': service.is_commercial
        })
    
    return jsonify(services_data)

@main_bp.route('/api/create-test-notification/<notification_type>')
@login_required
def create_test_notification(notification_type):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification_types = {
        'accident': {
            'title': 'Новое ДТП',
            'message': 'Зарегистрировано ДТП на пересечении ул. Ленина и ул. Гагарина',
            'type': 'accident',
            'priority': 'high'
        },
        'new_ticket': {
            'title': 'Новое обращение',
            'message': 'Пользователь создал новое обращение о проблеме на дороге',
            'type': 'new_ticket',
            'priority': 'medium'
        },
        'road_work': {
            'title': 'Дорожные работы',
            'message': 'Запланированы дорожные работы на пр. Гагарина с 10:00 до 16:00',
            'type': 'road_work',
            'priority': 'warning'
        },
        'status_update': {
            'title': 'Статус обновлен',
            'message': 'Обращение #245 переведено в статус "В работе"',
            'type': 'status_update',
            'priority': 'info'
        }
    }
    
    notif_data = notification_types.get(notification_type, notification_types['new_ticket'])
    
    return jsonify({
        'success': True,
        'notification': notif_data
    })

@main_bp.route('/api/search-index')
def search_index():
    try:
        search_index = []
        
        pages = [
            {
                'id': 'home',
                'title': 'Главная - ЦОДД Смоленской области',
                'content': 'Центр организации дорожного движения Смоленской области. Безопасность и комфорт на дорогах региона.',
                'url': url_for('main.index'),
                'type': 'page'
            },
            {
                'id': 'about',
                'title': 'О ЦОДД Смоленской области',
                'content': 'Информация о Центре организации дорожного движения Смоленской области, наши цели и задачи',
                'url': url_for('main.about'),
                'type': 'page'
            },
            {
                'id': 'services',
                'title': 'Услуги ЦОДД',
                'content': 'Профессиональные услуги по организации дорожного движения, проектирование, экспертиза',
                'url': url_for('main.services'),
                'type': 'page'
            },
            {
                'id': 'map',
                'title': 'Карта дорог Смоленской области',
                'content': 'Интерактивная карта дорожной ситуации, камеры, дорожные работы',
                'url': url_for('main.map'),
                'type': 'page'
            },
            {
                'id': 'news',
                'title': 'Новости ЦОДД',
                'content': 'Последние новости и события в сфере дорожного движения Смоленской области',
                'url': url_for('main.news'),
                'type': 'page'
            },
            {
                'id': 'contacts',
                'title': 'Контакты ЦОДД',
                'content': 'Контактная информация Центра организации дорожного движения Смоленской области',
                'url': url_for('main.contacts'),
                'type': 'page'
            }
        ]
        
        search_index.extend(pages)
        
        services = Service.query.filter_by(active=True).all()
        for service in services:
            search_index.append({
                'id': f'service-{service.id}',
                'title': f'{service.name} - Услуги ЦОДД',
                'content': service.description,
                'url': url_for('main.service_details', service_id=service.id),
                'type': 'service'
            })
        
        news_items = News.query.filter_by(active=True).limit(10).all()
        for news in news_items:
            search_index.append({
                'id': f'news-{news.id}',
                'title': news.title,
                'content': news.excerpt or news.content[:200] if news.content else '',
                'url': url_for('main.news') + f'#news-{news.id}',
                'type': 'news'
            })
        
        return jsonify(search_index)
        
    except Exception as e:
        current_app.logger.error(f'Error creating search index: {e}')
        return jsonify([])

@main_bp.route('/api/update-profile-icon', methods=['POST'])
@login_required
def update_profile_icon():
    data = request.get_json()
    profile_icon = data.get('profile_icon')
    
    if profile_icon:
        allowed_icons = [
            'bi-person', 'bi-person-circle', 'bi-person-square', 'bi-person-badge',
            'bi-person-gear', 'bi-person-check', 'bi-star', 'bi-star-fill',
            'bi-gear', 'bi-gear-fill', 'bi-shield', 'bi-shield-check',
            'bi-heart', 'bi-heart-fill', 'bi-flag', 'bi-flag-fill',
            'bi-bookmark', 'bi-bookmark-fill', 'bi-award', 'bi-trophy',
            'bi-emoji-smile', 'bi-emoji-laughing', 'bi-lightning', 'bi-lightning-charge',
            'bi-sun', 'bi-moon', 'bi-cloud', 'bi-cloud-rain'
        ]
        
        if profile_icon in allowed_icons:
            current_user.profile_icon = profile_icon
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Недопустимая иконка профиля'}), 400
    
    return jsonify({'success': False, 'error': 'Иконка не указана'}), 400

@main_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    
    if query and len(query) >= 2:
        try:
            services = Service.query.filter(
                (Service.name.ilike(f'%{query}%')) | 
                (Service.description.ilike(f'%{query}%'))
            ).filter_by(active=True).all()
            
            for service in services:
                results.append({
                    'title': service.name,
                    'content': service.description,
                    'url': url_for('main.service_details', service_id=service.id),
                    'type': 'Услуга'
                })
            
            news_items = News.query.filter(
                (News.title.ilike(f'%{query}%')) | 
                (News.content.ilike(f'%{query}%'))
            ).filter_by(active=True).all()
            
            for news in news_items:
                results.append({
                    'title': news.title,
                    'content': news.excerpt or news.content[:200] if news.content else '',
                    'url': url_for('main.news') + f'#news-{news.id}',
                    'type': 'Новость'
                })
                
        except Exception as e:
            current_app.logger.error(f'Search error: {e}')
            flash('Произошла ошибка при поиске', 'error')
    
    return render_template('search.html', 
                         query=query, 
                         results=results,
                         title=f'Поиск: {query}' if query else 'Поиск')

@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    return render_template('errors/500.html', current_time=current_time), 500

@main_bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403