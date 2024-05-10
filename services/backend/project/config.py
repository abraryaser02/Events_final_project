# services/backend/project/config.py

import os

class BaseConfig:
    """Base configuration"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@backend-db:5432/backend_dev")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    DATABASE_URI = os.getenv("DATABASE_TEST_URL", "postgresql://postgres:postgres@localhost:5435/backend_test")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI

class ProductionConfig(BaseConfig):
    """Production configuration"""
    DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@backend-db:5432/backend_prod")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI

