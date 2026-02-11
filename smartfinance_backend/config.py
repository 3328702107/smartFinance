import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:123456@localhost:3306/smartfinance?charset=utf8mb4"
        # "mysql+pymysql://sf_app:YourStrongPass!123@localhost:3306/smartfinance?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ===== Model service configs =====
    # Single-image detection service
    IMAGE_DETECTOR_BASE_URL = os.environ.get("IMAGE_DETECTOR_BASE_URL", "http://10.86.148.254:5000")
    IMAGE_DETECTOR_TIMEOUT_SECONDS = int(os.environ.get("IMAGE_DETECTOR_TIMEOUT_SECONDS", "15"))
    IMAGE_DETECTOR_PREDICT_PATH = os.environ.get("IMAGE_DETECTOR_PREDICT_PATH", "/predict")
    IMAGE_DETECTOR_HEALTH_PATH = os.environ.get("IMAGE_DETECTOR_HEALTH_PATH", "/health")
    IMAGE_DETECTOR_REQUEST_MODE = os.environ.get("IMAGE_DETECTOR_REQUEST_MODE", "auto")

    # Qianfan AppBuilder
    QIANFAN_APPBUILDER_SHARE_URL = os.environ.get(
        "QIANFAN_APPBUILDER_SHARE_URL",
        "https://appbuilder.baidu.com/s/llPiaMnf",
    )
    QIANFAN_APPBUILDER_API_URL = os.environ.get(
        "QIANFAN_APPBUILDER_API_URL",
        "https://qianfan.baidubce.com/v2/app/conversation/runs",
    )
    QIANFAN_APPBUILDER_APP_ID = os.environ.get("QIANFAN_APPBUILDER_APP_ID", "")
    QIANFAN_APPBUILDER_TOKEN = os.environ.get("QIANFAN_APPBUILDER_TOKEN", "")
    QIANFAN_RESPONSE_MODE = os.environ.get("QIANFAN_RESPONSE_MODE", "blocking")
    QIANFAN_TIMEOUT_SECONDS = int(os.environ.get("QIANFAN_TIMEOUT_SECONDS", "20"))
    QIANFAN_MAX_RETRIES = int(os.environ.get("QIANFAN_MAX_RETRIES", "2"))
    QIANFAN_RETRY_BACKOFF_SECONDS = float(os.environ.get("QIANFAN_RETRY_BACKOFF_SECONDS", "1.0"))

class DevConfig(Config):
    DEBUG = True

config_map = {
    "dev": DevConfig,
    "default": DevConfig
}
