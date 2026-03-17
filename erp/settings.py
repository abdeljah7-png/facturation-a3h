from pathlib import Path
import os

# ----------------------
# BASE DIRECTORY
# ----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------
# SECURITY
# ----------------------
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key')  # utiliser variable d'environnement en prod
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']  # en prod, mettre domaine réel

# ----------------------
# APPLICATIONS
# ----------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'produits',
    'clients',
    'fournisseurs',
    'achats',
    'ventes',
    'reglements',
    'comptes',
    'cbc',
]

# ----------------------
# MIDDLEWARE
# ----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # pour servir static en prod
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'erp.urls'

# ----------------------
# TEMPLATES
# ----------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # nécessaire pour admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'erp.wsgi.application'

# ----------------------
# DATABASE
# ----------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # si vous voulez garder la DB existante
    }
}

# ----------------------
# AUTHENTICATION
# ----------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Ajouter explicitement le backend standard pour éviter problème auth
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# ----------------------
# INTERNATIONALIZATION
# ----------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ----------------------
# STATIC FILES
# ----------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ----------------------
# EMAIL (console pour debug)
# ----------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ----------------------
# DEFAULT AUTO FIELD
# ----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CREATE_SUPERUSER = os.environ.get("CREATE_SUPERUSER", "False") == "True"

