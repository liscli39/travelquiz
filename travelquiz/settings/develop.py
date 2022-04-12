from .travelquiz import *

# .envファイルから設定読み込み
# 開発環境では明示的に指定しない限り.envは読み込まない
READ_ENV_FILE = env.bool('DJANGO_READ_ENV_FILE', default=False)
if READ_ENV_FILE:
    env_file = str(BASE_DIR.path('.env'))
    env.read_env(env_file)

DEBUG = True
ENVIRONMENT = 'DEVELOP'

SECRET_KEY = env('SECRET_KEY')

# アクセスを許可するホスト
# ヘルスチェックは前段のnginxが担当するのでコンテナIPを許可する必要なし
ALLOWED_HOSTS = ["*"]

# CORSを許可するホスト
# CORS_ORIGIN_WHITELIST = [
#     "http://localhost",
# ]

# Database
DATABASES['default']['HOST'] = env('MYSQL_HOST')
DATABASES['default']['NAME'] = env('MYSQL_DATABASE')
DATABASES['default']['USER'] = env('MYSQL_USER')
DATABASES['default']['PASSWORD'] = env('MYSQL_PASSWORD')
