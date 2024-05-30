from flask import Flask, request, make_response
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
app.config['SESSION_TYPE'] = 'filesystem'

CORS(app, resources={r"/api/*": {"origins": "*"}})
Session(app)

@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()
    elif request.method in ['POST', 'PUT', 'DELETE']:
        return build_actual_response()

def build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response

def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

from app import routes
