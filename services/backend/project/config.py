# services/backend/project/config.py

import os

class BaseConfig:
    """Base configuration"""
    TESTING = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@backend-db:5432/backend_dev")

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    DATABASE_URI = os.getenv("DATABASE_TEST_URL", "postgresql://postgres:postgres@backend-db:5432/backend_test")

class ProductionConfig(BaseConfig):
    """Production configuration"""
    DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@backend-db:5432/backend_prod")

