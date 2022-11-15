from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'constance',
    'constance.backends.database',
]

PROJECT_APPS = [
    'user',
    'main',
    'viewer',
    'front',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hitomi_client.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hitomi_client.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CONSTANCE_CONFIG = {
    "SEO_SITE_NAME": ("HANA", "Site name that will be shown in SEO"),
    "SEO_SITE_DESCRIPTION": ("HANA is a modern-designed web client for Hitomi.la, also has very rich features.",
                             "Site description that will be shown in SEO"),
    "ROOT_URL": ("https://hana.sserve.work", "Site URL that will be shown in SEO"),
    "MAIL_SERVER": ("smtp.zoho.com", "Mail server"),
    "MAIL_PORT": (465, "Mail port"),
    "MAIL_USERNAME": ("", "Mail username"),
    "MAIL_PASSWORD": ("", "Mail password"),
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG_FIELDSETS = {
    'SEO': ('SEO_SITE_NAME', 'SEO_SITE_DESCRIPTION', 'ROOT_URL'),
    'MAIL PROVIDER': ('MAIL_SERVER', 'MAIL_PORT'),
    'MAIL USER': ('MAIL_USERNAME', 'MAIL_PASSWORD')
}

LOGIN_URL = 'front:index'  # 'user:login'

CRONJOBS = [
    # hourly
    ('0 * * * *', 'main.cron.update_gallery', '>> ' + str(BASE_DIR / 'gallery.log')),
]