from flask import Flask
from flask_cors import CORS
from flask_session import Session
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

app.config['SESSION_TYPE'] = 'filesystem'

CORS(app, resources={r"/api/*": {"origins": "*"}})
Session(app)

from app import routes
