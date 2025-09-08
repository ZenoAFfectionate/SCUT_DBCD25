#!/usr/bin/env python3
"""
Database Setup and Initialization Script
University Course Registration and Grade Management System
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from pathlib import Path

def read_sql_file(file_path):
    """Read SQL file and return its content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: SQL file not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading SQL file: {e}")
        return None

def execute_sql_script(cursor, sql_script):
    """Execute SQL script with multiple statements"""
    try:
        # Split the script into individual statements
        statements = []
        current_statement = ""
        in_delimiter = False
        
        for line in sql_script.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('--'):
                continue
            
            # Handle DELIMITER changes
            if line.startswith('DELIMITER'):
                in_delimiter = True
                continue
            elif line == '//':
                if in_delimiter:
                    statements.append(current_statement.strip())
                    current_statement = ""
                    in_delimiter = False
                continue
            
            current_statement += line + "\n"
            
            # If not in delimiter block and line ends with semicolon, it's end of statement
            if not in_delimiter and line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # Execute each statement
        for i, statement in enumerate(statements):
            if statement:
                try:
                    # Handle multi-statement execution for procedures/triggers
                    if 'CREATE TRIGGER' in statement or 'CREATE PROCEDURE' in statement:
                        cursor.execute(statement, multi=True)
                    else:
                        cursor.execute(statement)
                    print(f"Executed statement {i+1}/{len(statements)}")
                except Error as e:
                    print(f"Error executing statement {i+1}: {e}")
                    print(f"Statement: {statement[:100]}...")
                    # Continue with other statements
        
        return True
        
    except Exception as e:
        print(f"Error executing SQL script: {e}")
        return False

def setup_database():
    """Set up the database from schema file"""
    print("Setting up University Course Registration Database...")
    
    # Database connection parameters
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',  # Use root for initial setup
        'charset': 'utf8mb4'
    }
    
    # Get root password
    root_password = input("Enter MySQL root password: ")
    config['password'] = root_password
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Connected to MySQL server successfully!")
        
        # Read and execute the schema file
        schema_file = Path(__file__).parent.parent / 'database_schema.sql'
        print(f"Reading schema file: {schema_file}")
        
        sql_script = read_sql_file(schema_file)
        if not sql_script:
            return False
        
        print("Executing database schema...")
        
        # Execute the schema script
        success = execute_sql_script(cursor, sql_script)
        
        if success:
            connection.commit()
            print("Database schema created successfully!")
            
            # Test the application user connection
            print("Testing application user connection...")
            test_connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='course_app',
                password='CourseApp2024!',
                database='CourseRegistrationDB'
            )
            
            if test_connection.is_connected():
                print("Application user connection successful!")
                test_connection.close()
                return True
            else:
                print("Application user connection failed!")
                return False
        else:
            print("Failed to create database schema!")
            return False
            
    except Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

def install_dependencies():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    
    try:
        import subprocess
        import sys
        
        # Read requirements file
        requirements_file = Path(__file__).parent / 'requirements.txt'
        
        if requirements_file.exists():
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Dependencies installed successfully!")
                return True
            else:
                print(f"Error installing dependencies: {result.stderr}")
                return False
        else:
            print("Requirements file not found!")
            return False
            
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from example"""
    env_file = Path(__file__).parent / '.env'
    env_example = Path(__file__).parent / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("Created .env file from example")
            print("Please review and update the .env file with your configuration")
            return True
        except Exception as e:
            print(f"Error creating .env file: {e}")
            return False
    elif env_file.exists():
        print(".env file already exists")
        return True
    else:
        print("No .env.example file found")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("University Course Registration System Setup")
    print("=" * 60)
    
    steps = [
        ("Installing Python dependencies", install_dependencies),
        ("Creating environment configuration", create_env_file),
        ("Setting up database", setup_database)
    ]
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        if not step_function():
            print(f"Setup failed at step: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nYou can now run the application with:")
    print("python main.py")
    print("\nDefault login credentials:")
    print("Admin: admin / admin123")
    print("Student: john_doe / student123")
    print("Instructor: prof_wang / instructor123")

if __name__ == "__main__":
    main()