"""
Database Connection and Management Module
University Course Registration and Grade Management System
"""

import mysql.connector
from mysql.connector import pooling, Error
import logging
from contextlib import contextmanager
from config import DatabaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and transaction management"""
    
    def __init__(self):
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize database connection pool"""
        try:
            config = DatabaseConfig.get_connection_config()
            self.connection_pool = pooling.MySQLConnectionPool(**config)
            logger.info("Database connection pool initialized successfully")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool with context manager"""
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Get database cursor with context manager"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor, connection
            except Error as e:
                connection.rollback()
                logger.error(f"Database cursor error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        """Execute SELECT query and return results"""
        try:
            with self.get_cursor() as (cursor, connection):
                cursor.execute(query, params or ())
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor.rowcount
        except Error as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def execute_update(self, query, params=None, commit=True):
        """Execute INSERT, UPDATE, DELETE query"""
        try:
            with self.get_cursor() as (cursor, connection):
                cursor.execute(query, params or ())
                
                if commit:
                    connection.commit()
                
                return cursor.rowcount
        except Error as e:
            logger.error(f"Update execution error: {e}")
            raise
    
    def execute_many(self, query, params_list, commit=True):
        """Execute multiple queries with different parameters"""
        try:
            with self.get_cursor() as (cursor, connection):
                cursor.executemany(query, params_list)
                
                if commit:
                    connection.commit()
                
                return cursor.rowcount
        except Error as e:
            logger.error(f"Batch execution error: {e}")
            raise
    
    def call_procedure(self, proc_name, params=None):
        """Call stored procedure"""
        try:
            with self.get_cursor() as (cursor, connection):
                cursor.callproc(proc_name, params or ())
                
                # Get results
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                
                connection.commit()
                return results
        except Error as e:
            logger.error(f"Procedure call error: {e}")
            raise
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as connection:
                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    cursor.close()
                    return result[0] == 1
        except Error as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def close_pool(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            try:
                # Note: mysql-connector-python doesn't have a direct close_all method
                # The pool will be garbage collected
                self.connection_pool = None
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")

# Global database manager instance
db_manager = DatabaseManager()