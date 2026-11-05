import os
import re
from datetime import timedelta


def _database_url():
    url = os.environ.get('DATABASE_URL', 'sqlite:///presupuesto.db')
    # Neon/Render entregan postgres:// o postgresql://; la app usa psycopg2
    return re.sub(r'^postgres(ql)?://', 'postgresql+psycopg2://', url)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-this')
    SQLALCHEMY_DATABASE_URI = _database_url()
    # Neon cierra conexiones inactivas; se verifican antes de usarlas
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session security (OWASP A07)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # WTF CSRF (OWASP A03)
    WTF_CSRF_TIME_LIMIT = 3600

    # Rate limiting (OWASP A07)
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
    RATELIMIT_STORAGE_URL = 'memory://'

    # AI floor plan
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
