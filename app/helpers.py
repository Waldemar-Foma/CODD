import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app
from time import * 


def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name

def save_uploaded_file(file, upload_folder, max_size=(1200, 1200), quality=85):
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        os.makedirs(upload_folder, exist_ok=True)
        filename = generate_unique_filename(secure_filename(file.filename))
        file_path = os.path.join(upload_folder, filename)
        
        if file.content_type.startswith('image/'):
            image = Image.open(file.stream)
            
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            image.save(file_path, 'JPEG' if filename.lower().endswith(('jpg', 'jpeg')) else 'PNG', 
                      quality=quality, optimize=True)
        else:
            file.save(file_path)
        
        return filename
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при сохранении файла: {e}")
        return None

def resize_image(image_path, output_path, size):
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(output_path)
        return True
    except Exception as e:
        current_app.logger.error(f"Ошибка при изменении размера изображения: {e}")
        return False

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except OSError:
        return "0 B"

def clean_upload_folder():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    try:
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                if stat.st_mtime < (time.time() - 30 * 86400):
                    os.remove(file_path)
                    current_app.logger.info(f"Удален старый файл: {filename}")
    except Exception as e:
        current_app.logger.error(f"Ошибка при очистке папки загрузок: {e}")

def validate_coordinates(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (TypeError, ValueError):
        return False

def format_datetime(value, format='medium'):
    if format == 'full':
        format = "%d.%m.%Y %H:%M:%S"
    elif format == 'medium':
        format = "%d.%m.%Y %H:%M"
    else:
        format = "%d.%m.%Y"
    
    return value.strftime(format)

def truncate_text(text, length=100, suffix='...'):
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + suffix
