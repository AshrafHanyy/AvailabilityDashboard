import os

class Config:
    # Generate a secure secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 40,          # Match user count
        'max_overflow': 10,
        'pool_pre_ping': True,    # Reconnect dead connections
        'pool_recycle': 3600,     # Recycle hourly
        'connect_args': {
            'timeout': 30,        # Longer wait for locks
            'check_same_thread': False  # Essential for threading
        }
    }
    # SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///teamdashboard.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Other configurations
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 2800  # 30 minutes