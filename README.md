# University Course Registration and Grade Management System

A comprehensive database-driven application for managing university course registration, student enrollment, and grade management.

## Features

### Student Features
- User registration and authentication
- Course browsing and search
- Course enrollment with validation (prerequisites, time conflicts, credit limits)
- Schedule viewing (current semester, all semesters, specific semester)
- Course dropping
- Transcript viewing with GPA calculation
- Academic performance tracking

### Instructor Features
- User registration and authentication
- Section roster management
- Grade entry and updates
- Course statistics viewing
- Student performance tracking

### Administrator Features
- Department management (create, view)
- Course management (create, view, search)
- Section creation and management
- Student and instructor overview
- System statistics and reporting

## Technical Architecture

### Database Design
- **MySQL** database with comprehensive schema
- **Normalized design** (3NF/BCNF) with proper relationships
- **Business rule enforcement** through triggers and constraints
- **Performance optimization** with strategic indexing
- **Security** with role-based access control

### Application Architecture
- **Model-View-Controller (MVC)** pattern
- **Data Access Object (DAO)** pattern for database operations
- **Service layer** for business logic
- **Command-line interface** for user interaction

### Key Components
1. **Database Layer** (`database.py`) - Connection pooling and transaction management
2. **Data Models** (`models.py`) - Object-relational mapping
3. **Data Access Objects** (`dao.py`) - Database operations
4. **Business Services** (`services.py`) - Business logic and validation
5. **User Interface** (`ui.py`) - Command-line interface
6. **Configuration** (`config.py`) - Application and database settings

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Quick Setup
1. **Clone or download** the project files
2. **Run the setup script**:
   ```bash
   cd database_implementation
   python setup.py
   ```
3. **Follow the prompts** to configure the database
4. **Start the application**:
   ```bash
   python main.py
   ```

### Manual Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create the database**:
   ```bash
   mysql -u root -p < ../database_schema.sql
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Configuration

### Database Configuration
Edit the `.env` file or modify `config.py`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=course_app
DB_PASSWORD=CourseApp2024!
DB_NAME=CourseRegistrationDB
```

### Application Settings
- **Credit Limits**: 10-40 credits per semester
- **Grade Scale**: 4.0 GPA system
- **Session Timeout**: 1 hour
- **Display Settings**: Configurable pagination and table formatting

## Usage

### Default Login Credentials
- **Administrator**: `admin` / `admin123`
- **Student**: `john_doe` / `student123`
- **Instructor**: `prof_wang` / `instructor123`

### Student Workflow
1. **Login** with student credentials
2. **View Available Courses** for current or future semesters
3. **Enroll in Courses** with automatic validation
4. **View Schedule** to see enrolled courses
5. **Drop Courses** if needed
6. **View Transcript** and GPA information

### Instructor Workflow
1. **Login** with instructor credentials
2. **View Section Roster** for assigned courses
3. **Update Student Grades** at end of semester
4. **View Course Statistics** for performance analysis

### Administrator Workflow
1. **Login** with admin credentials
2. **Manage Departments** (create, view)
3. **Manage Courses** (create, search, view)
4. **Create Course Sections** for each semester
5. **View System Statistics** and user information

## Database Schema

The system uses a comprehensive MySQL database schema with the following key tables:

- **User**: Authentication and user management
- **Student**: Student personal information
- **Instructor**: Instructor information
- **Department**: Academic departments
- **Course**: Course catalog
- **Section**: Course sections per semester
- **Enrollment**: Student course enrollments
- **CoursePrereq**: Course prerequisites

### Key Features
- **Referential Integrity**: Foreign key constraints ensure data consistency
- **Business Rules**: Triggers enforce enrollment limits and grade calculations
- **Performance**: Strategic indexing for fast queries
- **Security**: Role-based access control and password hashing

## API Reference

### Service Layer
- `AuthenticationService`: User login/logout and session management
- `StudentService`: Student registration, enrollment, and academic records
- `InstructorService`: Instructor operations and grade management
- `CourseService`: Course and section management
- `AdminService`: Administrative functions and system statistics

### Data Access Layer
- `UserDAO`: User account operations
- `StudentDAO`: Student data management
- `InstructorDAO`: Instructor data management
- `CourseDAO`: Course catalog operations
- `SectionDAO`: Course section management
- `EnrollmentDAO`: Student enrollment operations

## Error Handling

The system includes comprehensive error handling:
- **Database Connection**: Automatic retry and connection pooling
- **Input Validation**: Type checking and business rule validation
- **Transaction Management**: Rollback on errors
- **Logging**: Detailed error logging for debugging

## Testing

### Manual Testing
1. Run the application: `python main.py`
2. Test each user role with provided credentials
3. Verify business rules (enrollment limits, prerequisites, etc.)
4. Test error scenarios (invalid input, capacity limits)

### Database Testing
1. Verify all tables are created correctly
2. Test stored procedures and triggers
3. Validate referential integrity constraints
4. Check performance with sample data

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify MySQL is running
   - Check database credentials in `.env`
   - Ensure database schema is created

2. **Import Errors**
   - Install required packages: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Permission Errors**
   - Verify database user permissions
   - Check file system permissions

### Logs
- Application logs: `course_system.log`
- Database errors are logged with full stack traces
- User actions are tracked for audit purposes

## Development

### Adding New Features
1. **Database Changes**: Update schema and migration scripts
2. **Models**: Add/modify data classes in `models.py`
3. **DAO Layer**: Implement data access methods
4. **Service Layer**: Add business logic
5. **UI Layer**: Update user interface

### Code Structure
```
report/
├── [2025] Database Design Project.docx  # project requirement
└── analysis.md                          # project analysis
src/
├── config.py          # Configuration settings
├── database.py        # Database connection management
├── models.py          # Data models and enums
├── dao.py             # Data access objects
├── services.py        # Business logic services
├── ui.py              # Command-line interface
├── main.py            # Application entry point
├── setup.py           # Installation script
├── requirements.txt   # Python dependencies
├── .env               # Environment configuration template
requirements.txt      # Python dependencies
README.md             # Just this file
database_schema.sql   # database schema document
database_design.md    # database design document
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the existing code style
4. Test thoroughly
5. Submit a pull request

## License

This project is developed for educational purposes as part of a database systems course.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Verify database schema and permissions
4. Test with sample data

## Version History

- **v1.0**: Initial implementation with core features
  - User authentication and role management
  - Course registration and enrollment
  - Grade management and GPA calculation
  - Administrative functions
  - Comprehensive database schema with business rules