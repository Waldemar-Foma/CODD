from app import create_app
import os
import logging
from logging.handlers import RotatingFileHandler

app = create_app()

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/codd.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Запуск ЦОДД Смоленск v2.0')

if __name__ == '__main__':
    print("=" * 60)
    print("СмолЦОДД - Система v2.0")
    print("=" * 60)
    print(f"Режим: {'Разработка' if app.debug else 'Производство'}")
    print(f"База данных: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Яндекс Карты: {'Доступны' if app.config['YANDEX_MAPS_API_KEY'] else 'Не настроены'}")
    print("=" * 60)
    
    try:
        app.run(
            debug=False,
            host='0.0.0.0', 
            port=1488,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")