import os

# Директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(DATA_DIR, "temp")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# Создаем папки при запуске
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Токен бота (из .env)
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# AWS S3 настройки (или compatible)
AWS_ACCESS_KEY_ID = os.getenv("DO00A7FUG77B2E4L2GBA")  # Для Backblaze: applicationKeyId | Для DigitalOcean Spaces: Access Key из Spaces Keys
AWS_SECRET_ACCESS_KEY = os.getenv("IqSDoDf5IwpVP02KiuLohHwsvxVu81IGDCTm7PSR7tc")  # Для Backblaze: applicationKey | Для DigitalOcean Spaces: Secret Key из Spaces Keys
S3_BUCKET_NAME = os.getenv("yourfiles")  # Имя bucket в Spaces (например, my-sludge-bucket)
S3_REGION = os.getenv("S3_REGION", "fra1")
S3_ENDPOINT = os.getenv("https://fra1.digitaloceanspaces.com")  # Для DigitalOcean Spaces: https://[region].digitaloceanspaces.com (например, https://fra1.digitaloceanspaces.com)
