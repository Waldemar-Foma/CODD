from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy import event
import uuid


def generate_uuid():
    return str(uuid.uuid4())

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    show_in_team = db.Column(db.Boolean, default=False)
    team_order = db.Column(db.Integer, default=0)
    profile_icon = db.Column(db.String(50), default='bi-person')  # Это класс иконки, а не путь к файлу
    
    # Связи
    tickets = db.relationship('Ticket', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    created_accidents = db.relationship('AccidentMarker', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def update_last_seen(self):
        self.last_seen = datetime.now(timezone.utc)
        db.session.commit()
    
    def get_stats(self):
        return {
            'total_tickets': self.tickets.count(),
            'open_tickets': self.tickets.filter_by(status='new').count(),
            'resolved_tickets': self.tickets.filter_by(status='resolved').count()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='new', index=True)
    priority = db.Column(db.String(20), default='medium')
    image_path = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fatalities = db.Column(db.Integer, default=0)  # Количество погибших в ДТП
    
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('ix_tickets_status_created', 'status', 'created_at'),
        db.Index('ix_tickets_user_created', 'user_id', 'created_at'),
    )
    
    STATUS_CHOICES = {
        'new': {'text': 'Новая', 'color': 'primary', 'icon': 'bi-plus-circle'},
        'in_progress': {'text': 'В работе', 'color': 'warning', 'icon': 'bi-gear'},
        'resolved': {'text': 'Решена', 'color': 'success', 'icon': 'bi-check-circle'},
        'closed': {'text': 'Закрыта', 'color': 'secondary', 'icon': 'bi-x-circle'}
    }
    
    PRIORITY_CHOICES = {
        'low': {'text': 'Низкий', 'color': 'info', 'icon': 'bi-arrow-down'},
        'medium': {'text': 'Средний', 'color': 'warning', 'icon': 'bi-dash'},
        'high': {'text': 'Высокий', 'color': 'danger', 'icon': 'bi-arrow-up'},
        'urgent': {'text': 'Срочный', 'color': 'danger', 'icon': 'bi-exclamation-triangle'}
    }
    
    def get_status_text(self):
        return self.STATUS_CHOICES.get(self.status, {}).get('text', self.status)
    
    def get_status_color(self):
        return self.STATUS_CHOICES.get(self.status, {}).get('color', 'secondary')
    
    def get_status_icon(self):
        return self.STATUS_CHOICES.get(self.status, {}).get('icon', 'bi-circle')
    
    def get_priority_text(self):
        return self.PRIORITY_CHOICES.get(self.priority, {}).get('text', self.priority)
    
    def get_priority_color(self):
        return self.PRIORITY_CHOICES.get(self.priority, {}).get('color', 'secondary')
    
    def can_edit(self, user):
        return user.is_admin or user.id == self.user_id
    
    def can_delete(self, user):
        return user.is_admin or (user.id == self.user_id and self.status == 'new')
    
    def __repr__(self):
        return f'<Ticket {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_internal = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    
    def __repr__(self):
        return f'<Comment {self.id} for Ticket {self.ticket_id}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, warning, error, success, accident, new_ticket, comment
    action_url = db.Column(db.String(500))
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'

class AccidentMarker(db.Model):
    __tablename__ = 'accident_markers'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    address = db.Column(db.String(300))
    active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<AccidentMarker {self.title}>'

class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300))
    image_path = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    author = db.relationship('User', backref='news_posts')
    
    def __repr__(self):
        return f'<News {self.title}>'

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50))
    is_commercial = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Service {self.name}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Document {self.title}>'

class Vacancy(db.Model):
    __tablename__ = 'vacancies'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Vacancy {self.title}>'

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    is_free = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Project {self.title}>'

class Partner(db.Model):
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(200))
    website = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Partner {self.name}>'

@event.listens_for(Ticket, 'before_update')
def update_timestamp_before_update(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@login_manager.unauthorized_handler
def unauthorized():
    from flask import flash, redirect, url_for, request
    flash('Пожалуйста, войдите для доступа к этой странице.', 'warning')
    return redirect(url_for('auth.login', next=request.url))