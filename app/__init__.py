from flask import Flask
from flask_cors import CORS
from flask_session import Session
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

app = Flask(__name__)

# Установка секретного ключа из переменных окружения
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Конфигурация для сессий
app.config['SESSION_TYPE'] = 'filesystem'  # Сессии будут храниться в файловой системе

CORS(app, resources={r"/api/*": {"origins": "*"}})
Session(app)

from app import routes