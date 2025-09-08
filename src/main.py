#!/usr/bin/env python3
"""
Main Application Entry Point
University Course Registration and Grade Management System
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from database import db_manager
from ui import CourseRegistrationUI
from config import DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('course_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if database connection is working"""
    try:
        if db_manager.test_connection():
            logger.info("Database connection successful")
            return True
        else:
            logger.error("Database connection failed")
            return False
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

def initialize_system():
    """Initialize the system"""
    print("Initializing University Course Registration System...")
    
    # Check database connection
    if not check_database_connection():
        print("ERROR: Cannot connect to database. Please check your configuration.")
        print("Make sure MySQL is running and the database schema is created.")
        print("Run the database_schema.sql script to create the database structure.")
        return False
    
    print("System initialized successfully!")
    return True

def main():
    """Main application entry point"""
    try:
        # Initialize system
        if not initialize_system():
            sys.exit(1)
        
        # Start the UI
        app = CourseRegistrationUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # Clean up database connections
        try:
            db_manager.close_pool()
            logger.info("Database connections closed")
        except Exception as e:
            logger.warning(f"Error closing database connections: {e}")

if __name__ == "__main__":
    main()