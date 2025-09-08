"""
Database Configuration Module
University Course Registration and Grade Management System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration settings"""
    
    # MySQL Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'course_app')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'CourseApp2024!')
    DB_NAME = os.getenv('DB_NAME', 'CourseRegistrationDB')
    
    # Connection Pool Settings
    POOL_NAME = 'course_pool'
    POOL_SIZE = 10
    POOL_RESET_SESSION = True
    
    # Application Settings
    SESSION_TIMEOUT = 3600  # 1 hour
    MAX_LOGIN_ATTEMPTS = 3
    PASSWORD_MIN_LENGTH = 8
    
    @classmethod
    def get_connection_config(cls):
        """Get database connection configuration"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': 'utf8mb4',
            'autocommit': False,
            'pool_name': cls.POOL_NAME,
            'pool_size': cls.POOL_SIZE,
            'pool_reset_session': cls.POOL_RESET_SESSION
        }

class AppConfig:
    """Application configuration settings"""
    
    # UI Settings
    ITEMS_PER_PAGE = 10
    MAX_DISPLAY_WIDTH = 120
    
    # Business Rules
    MIN_CREDITS_PER_SEMESTER = 10
    MAX_CREDITS_PER_SEMESTER = 40
    PASSING_GRADE = 60.0
    MAX_GPA = 4.0
    
    # Grade Point Scale
    GRADE_SCALE = {
        (97, 100): 4.0,
        (93, 96): 3.7,
        (90, 92): 3.3,
        (87, 89): 3.0,
        (83, 86): 2.7,
        (80, 82): 2.3,
        (77, 79): 2.0,
        (73, 76): 1.7,
        (70, 72): 1.3,
        (67, 69): 1.0,
        (65, 66): 0.7,
        (0, 64): 0.0
    }
    
    @classmethod
    def calculate_grade_points(cls, grade):
        """Calculate grade points from numerical grade"""
        if grade is None:
            return None
        
        for (min_grade, max_grade), points in cls.GRADE_SCALE.items():
            if min_grade <= grade <= max_grade:
                return points
        return 0.0