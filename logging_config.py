import logging

def setup_logging():
    # Создаем файловый обработчик
    file_handler = logging.FileHandler("bot.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Настраиваем логгирование только с файловым обработчиком
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler]
    )

    # Получаем логгер SQLAlchemy
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.ERROR)  # Устанавливаем уровень логирования для SQLAlchemy
    sqlalchemy_logger.addHandler(file_handler)  # Добавляем файловый обработчик
    sqlalchemy_logger.propagate = False  # Отключаем распространение на родительские логгеры

    # Убираем все обработчики у root логгера, кроме нашего файлового обработчика
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)
