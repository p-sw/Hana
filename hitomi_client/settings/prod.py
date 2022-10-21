from secrets import token_hex
from . import base

SECRET_KEY = token_hex(50)

DEBUG = False

ALLOWED_HOSTS = ["sserve.work"]
CSRF_TRUSTED_ORIGINS = ["https://hc.sserve.work"]