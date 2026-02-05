import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = True
    
    # MySQL Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'opd_admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'krithi_raj07')
    DB_NAME = os.getenv('DB_NAME', 'hospital_opd')
    
    # SocketIO
    SOCKETIO_MESSAGE_QUEUE = 'redis://localhost:6379/0'