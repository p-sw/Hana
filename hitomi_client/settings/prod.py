from secrets import token_hex
from .base import *

SECRET_KEY = token_hex(50)

DEBUG = False

ALLOWED_HOSTS = ["hana.sserve.work"]
CSRF_TRUSTED_ORIGINS = ["https://hana.sserve.work"]
