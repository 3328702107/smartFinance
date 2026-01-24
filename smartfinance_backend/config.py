import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://sf_app:YourStrongPass!123@localhost:3306/smartfinance?charset=utf8mb4"
        # "mysql+pymysql://sf_app:YourStrongPass!123@localhost:3306/smartfinance?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    DEBUG = True

config_map = {
    "dev": DevConfig,
    "default": DevConfig
}