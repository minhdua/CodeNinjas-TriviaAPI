import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def get_database_path(mode):
    """
    Get database path
    """
    host = os.environ.get(f'{mode}_HOST', "localhost")
    port = os.environ.get(f'{mode}_PORT', "5432")
    user = os.environ.get(f'{mode}_USER', "postgres")
    password = os.environ.get(f'{mode}_PASSWORD', "postgres")
    database = os.environ.get(f'{mode}_DATABASE', "trivia")
    # Connect to the database
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


# Configuration for this module. This module is used to generate queries that are valid for a given user
class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = get_database_path("PROD")


# Creates a ProductionConfig object that can be used to configure the production environment
class ProductionConfig(Config):
    pass


# Creates a DevelopmentConfig object that can be used to configure the development environment
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_database_path("DEV")


# Creates a TestingConfig object that can be used to configure the testing environment
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = get_database_path("TEST")
