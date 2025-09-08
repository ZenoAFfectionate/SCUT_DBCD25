"""
Data Access Object (DAO) Module
University Course Registration and Grade Management System
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
import logging
from database import db_manager
from models import *
from config import AppConfig
import bcrypt

logger = logging.getLogger(__name__)

class BaseDAO:
    """Base Data Access Object with common operations"""
    
    def __init__(self):
        self.db = db_manager
    
    def _handle_db_error(self, operation: str, error: Exception):
        """Handle database errors consistently"""
        logger.error(f"Database error in {operation}: {error}")
        raise Exception(f"Database operation failed: {operation}")

class UserDAO(BaseDAO):
    """User data access operations"""
    
    def create_user(self, user: User) -> int:
        """Create a new user"""
        try:
            # Hash password
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
            
            query = """
                INSERT INTO User (Username, Password, UserType, Status)
                VALUES (%s, %s, %s, %s)
            """
            params = (user.username, hashed_password.decode('utf-8'), 
                     user.user_type.value, user.status.value)
            
            self.db.execute_update(query, params)
            
            # Get the created user ID
            user_id_query = "SELECT LAST_INSERT_ID()"
            result = self.db.execute_query(user_id_query, fetch_one=True)
            return result['LAST_INSERT_ID()']
            
        except Exception as e:
            self._handle_db_error("create_user", e)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user login"""
        try:
            query = """
                SELECT UserID, Username, Password, UserType, Status, LastLoginDate
                FROM User 
                WHERE Username = %s AND Status = 'Active'
            """
            result = self.db.execute_query(query, (username,), fetch_one=True)
            
            if result and bcrypt.checkpw(password.encode('utf-8'), result['Password'].encode('utf-8')):
                # Update last login date
                self.update_last_login(result['UserID'])
                
                return User(
                    user_id=result['UserID'],
                    username=result['Username'],
                    user_type=UserType(result['UserType']),
                    status=UserStatus(result['Status']),
                    last_login_date=result['LastLoginDate']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("authenticate_user", e)
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        try:
            query = "UPDATE User SET LastLoginDate = NOW() WHERE UserID = %s"
            self.db.execute_update(query, (user_id,))
        except Exception as e:
            logger.warning(f"Failed to update last login for user {user_id}: {e}")
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            query = """
                SELECT UserID, Username, UserType, CreatedDate, Status, LastLoginDate
                FROM User WHERE UserID = %s
            """
            result = self.db.execute_query(query, (user_id,), fetch_one=True)
            
            if result:
                return User(
                    user_id=result['UserID'],
                    username=result['Username'],
                    user_type=UserType(result['UserType']),
                    created_date=result['CreatedDate'],
                    status=UserStatus(result['Status']),
                    last_login_date=result['LastLoginDate']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_user_by_id", e)

class StudentDAO(BaseDAO):
    """Student data access operations"""
    
    def create_student(self, student: Student, user: User) -> str:
        """Create a new student with associated user account"""
        try:
            # First create user account
            user_dao = UserDAO()
            user_id = user_dao.create_user(user)
            
            # Then create student record
            query = """
                INSERT INTO Student (StudentID, UserID, Name, Gender, BirthDate, 
                                   Email, Phone, College, Major, EnrollmentYear)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                student.student_id, user_id, student.name,
                student.gender.value if student.gender else None,
                student.birth_date, student.email, student.phone,
                student.college, student.major, student.enrollment_year
            )
            
            self.db.execute_update(query, params)
            return student.student_id
            
        except Exception as e:
            self._handle_db_error("create_student", e)
    
    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        try:
            query = """
                SELECT s.*, d.DeptName as CollegeName
                FROM Student s
                LEFT JOIN Department d ON s.College = d.DeptID
                WHERE s.StudentID = %s
            """
            result = self.db.execute_query(query, (student_id,), fetch_one=True)
            
            if result:
                return Student(
                    student_id=result['StudentID'],
                    user_id=result['UserID'],
                    name=result['Name'],
                    gender=Gender(result['Gender']) if result['Gender'] else None,
                    birth_date=result['BirthDate'],
                    email=result['Email'],
                    phone=result['Phone'],
                    college=result['College'],
                    major=result['Major'],
                    enrollment_year=result['EnrollmentYear'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_student_by_id", e)
    
    def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        """Get student by user ID"""
        try:
            query = """
                SELECT s.*, d.DeptName as CollegeName
                FROM Student s
                LEFT JOIN Department d ON s.College = d.DeptID
                WHERE s.UserID = %s
            """
            result = self.db.execute_query(query, (user_id,), fetch_one=True)
            
            if result:
                return Student(
                    student_id=result['StudentID'],
                    user_id=result['UserID'],
                    name=result['Name'],
                    gender=Gender(result['Gender']) if result['Gender'] else None,
                    birth_date=result['BirthDate'],
                    email=result['Email'],
                    phone=result['Phone'],
                    college=result['College'],
                    major=result['Major'],
                    enrollment_year=result['EnrollmentYear'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_student_by_user_id", e)
    
    def update_student(self, student: Student) -> bool:
        """Update student information"""
        try:
            query = """
                UPDATE Student 
                SET Name = %s, Gender = %s, BirthDate = %s, Email = %s, 
                    Phone = %s, College = %s, Major = %s, EnrollmentYear = %s
                WHERE StudentID = %s
            """
            params = (
                student.name,
                student.gender.value if student.gender else None,
                student.birth_date, student.email, student.phone,
                student.college, student.major, student.enrollment_year,
                student.student_id
            )
            
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            self._handle_db_error("update_student", e)
    
    def get_all_students(self, limit: int = 100, offset: int = 0) -> List[Student]:
        """Get all students with pagination"""
        try:
            query = """
                SELECT s.*, d.DeptName as CollegeName
                FROM Student s
                LEFT JOIN Department d ON s.College = d.DeptID
                ORDER BY s.StudentID
                LIMIT %s OFFSET %s
            """
            results = self.db.execute_query(query, (limit, offset))
            
            students = []
            for result in results:
                students.append(Student(
                    student_id=result['StudentID'],
                    user_id=result['UserID'],
                    name=result['Name'],
                    gender=Gender(result['Gender']) if result['Gender'] else None,
                    birth_date=result['BirthDate'],
                    email=result['Email'],
                    phone=result['Phone'],
                    college=result['College'],
                    major=result['Major'],
                    enrollment_year=result['EnrollmentYear'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                ))
            
            return students
            
        except Exception as e:
            self._handle_db_error("get_all_students", e)

class InstructorDAO(BaseDAO):
    """Instructor data access operations"""
    
    def create_instructor(self, instructor: Instructor, user: User) -> str:
        """Create a new instructor with associated user account"""
        try:
            # First create user account
            user_dao = UserDAO()
            user_id = user_dao.create_user(user)
            
            # Then create instructor record
            query = """
                INSERT INTO Instructor (InstructorID, UserID, Name, Department, 
                                      Email, Phone, Title)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                instructor.instructor_id, user_id, instructor.name,
                instructor.department, instructor.email, instructor.phone,
                instructor.title
            )
            
            self.db.execute_update(query, params)
            return instructor.instructor_id
            
        except Exception as e:
            self._handle_db_error("create_instructor", e)
    
    def get_instructor_by_id(self, instructor_id: str) -> Optional[Instructor]:
        """Get instructor by ID"""
        try:
            query = """
                SELECT i.*, d.DeptName as DepartmentName
                FROM Instructor i
                LEFT JOIN Department d ON i.Department = d.DeptID
                WHERE i.InstructorID = %s
            """
            result = self.db.execute_query(query, (instructor_id,), fetch_one=True)
            
            if result:
                return Instructor(
                    instructor_id=result['InstructorID'],
                    user_id=result['UserID'],
                    name=result['Name'],
                    department=result['Department'],
                    email=result['Email'],
                    phone=result['Phone'],
                    title=result['Title'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_instructor_by_id", e)
    
    def get_instructor_by_user_id(self, user_id: int) -> Optional[Instructor]:
        """Get instructor by user ID"""
        try:
            query = """
                SELECT i.*, d.DeptName as DepartmentName
                FROM Instructor i
                LEFT JOIN Department d ON i.Department = d.DeptID
                WHERE i.UserID = %s
            """
            result = self.db.execute_query(query, (user_id,), fetch_one=True)
            
            if result:
                return Instructor(
                    instructor_id=result['InstructorID'],
                    user_id=result['UserID'],
                    name=result['Name'],
                    department=result['Department'],
                    email=result['Email'],
                    phone=result['Phone'],
                    title=result['Title'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_instructor_by_user_id", e)
    
    def get_all_instructors(self) -> List[Instructor]:
        """Get all instructors"""
        try:
            query = """
                SELECT i.*, d.DeptName as DepartmentName
                FROM Instructor i
                LEFT JOIN Department d ON i.Department = d.DeptID
                ORDER BY i.Name
            """
            results = self.db.execute_query(query)
            
            instructors = []
            for result in results:
                instructors.append(Instructor(
                    instructor_id=result['InstructorID'],
                    user_id=result['UserID'],
                    name=result['Name'],
                    department=result['Department'],
                    email=result['Email'],
                    phone=result['Phone'],
                    title=result['Title'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                ))
            
            return instructors
            
        except Exception as e:
            self._handle_db_error("get_all_instructors", e)

class CourseDAO(BaseDAO):
    """Course data access operations"""
    
    def create_course(self, course: Course) -> str:
        """Create a new course"""
        try:
            query = """
                INSERT INTO Course (CourseID, CourseName, Credits, Department, 
                                  CourseType, Description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                course.course_id, course.course_name, course.credits,
                course.department, course.course_type.value, course.description
            )
            
            self.db.execute_update(query, params)
            return course.course_id
            
        except Exception as e:
            self._handle_db_error("create_course", e)
    
    def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID"""
        try:
            query = """
                SELECT c.*, d.DeptName as DepartmentName
                FROM Course c
                LEFT JOIN Department d ON c.Department = d.DeptID
                WHERE c.CourseID = %s
            """
            result = self.db.execute_query(query, (course_id,), fetch_one=True)
            
            if result:
                return Course(
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    department=result['Department'],
                    course_type=CourseType(result['CourseType']),
                    description=result['Description'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_course_by_id", e)
    
    def get_all_courses(self, department: str = None) -> List[Course]:
        """Get all courses, optionally filtered by department"""
        try:
            if department:
                query = """
                    SELECT c.*, d.DeptName as DepartmentName
                    FROM Course c
                    LEFT JOIN Department d ON c.Department = d.DeptID
                    WHERE c.Department = %s
                    ORDER BY c.CourseID
                """
                params = (department,)
            else:
                query = """
                    SELECT c.*, d.DeptName as DepartmentName
                    FROM Course c
                    LEFT JOIN Department d ON c.Department = d.DeptID
                    ORDER BY c.CourseID
                """
                params = None
            
            results = self.db.execute_query(query, params)
            
            courses = []
            for result in results:
                courses.append(Course(
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    department=result['Department'],
                    course_type=CourseType(result['CourseType']),
                    description=result['Description'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                ))
            
            return courses
            
        except Exception as e:
            self._handle_db_error("get_all_courses", e)
    
    def search_courses(self, search_term: str) -> List[Course]:
        """Search courses by name or description"""
        try:
            query = """
                SELECT c.*, d.DeptName as DepartmentName
                FROM Course c
                LEFT JOIN Department d ON c.Department = d.DeptID
                WHERE c.CourseName LIKE %s OR c.Description LIKE %s
                ORDER BY c.CourseID
            """
            search_pattern = f"%{search_term}%"
            results = self.db.execute_query(query, (search_pattern, search_pattern))
            
            courses = []
            for result in results:
                courses.append(Course(
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    department=result['Department'],
                    course_type=CourseType(result['CourseType']),
                    description=result['Description'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                ))
            
            return courses
            
        except Exception as e:
            self._handle_db_error("search_courses", e)

class SectionDAO(BaseDAO):
    """Section data access operations"""
    
    def create_section(self, section: Section) -> int:
        """Create a new section"""
        try:
            query = """
                INSERT INTO Section (CourseID, InstructorID, Semester, Year, 
                                   MaxCapacity, TimeSlot, Location)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                section.course_id, section.instructor_id, section.semester.value,
                section.year, section.max_capacity, section.time_slot, section.location
            )
            
            self.db.execute_update(query, params)
            
            # Get the created section ID
            section_id_query = "SELECT LAST_INSERT_ID()"
            result = self.db.execute_query(section_id_query, fetch_one=True)
            return result['LAST_INSERT_ID()']
            
        except Exception as e:
            self._handle_db_error("create_section", e)
    
    def get_available_sections(self, semester: str, year: int, student_id: str = None) -> List[SectionInfo]:
        """Get available sections for enrollment"""
        try:
            if student_id:
                # Use stored procedure for student-specific availability
                results = self.db.call_procedure('sp_GetAvailableSections', [semester, year, student_id])
            else:
                # Get all sections with basic availability info
                query = """
                    SELECT 
                        sec.SectionID,
                        c.CourseID,
                        c.CourseName,
                        c.Credits,
                        c.CourseType,
                        sec.Semester,
                        sec.Year,
                        sec.MaxCapacity,
                        COALESCE(enrolled.CurrentCount, 0) as CurrentEnrollment,
                        (sec.MaxCapacity - COALESCE(enrolled.CurrentCount, 0)) as AvailableSpots,
                        sec.TimeSlot,
                        sec.Location,
                        i.Name as InstructorName,
                        CASE 
                            WHEN (sec.MaxCapacity - COALESCE(enrolled.CurrentCount, 0)) <= 0 THEN 'Full'
                            ELSE 'Available'
                        END as AvailabilityStatus
                    FROM Section sec
                    JOIN Course c ON sec.CourseID = c.CourseID
                    LEFT JOIN Instructor i ON sec.InstructorID = i.InstructorID
                    LEFT JOIN (
                        SELECT SectionID, COUNT(*) as CurrentCount
                        FROM Enrollment 
                        WHERE Status = 'Enrolled'
                        GROUP BY SectionID
                    ) enrolled ON sec.SectionID = enrolled.SectionID
                    WHERE sec.Semester = %s AND sec.Year = %s
                    ORDER BY c.CourseID, sec.SectionID
                """
                results = self.db.execute_query(query, (semester, year))
            
            sections = []
            for result in results:
                sections.append(SectionInfo(
                    section_id=result['SectionID'],
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    course_type=result['CourseType'],
                    semester=result['Semester'],
                    year=result['Year'],
                    max_capacity=result['MaxCapacity'],
                    current_enrollment=result['CurrentEnrollment'],
                    available_spots=result['AvailableSpots'],
                    time_slot=result['TimeSlot'],
                    location=result['Location'],
                    instructor_name=result['InstructorName'],
                    availability_status=result['AvailabilityStatus']
                ))
            
            return sections
            
        except Exception as e:
            self._handle_db_error("get_available_sections", e)
    
    def get_section_by_id(self, section_id: int) -> Optional[SectionInfo]:
        """Get section by ID with detailed information"""
        try:
            query = """
                SELECT 
                    sec.SectionID,
                    c.CourseID,
                    c.CourseName,
                    c.Credits,
                    c.CourseType,
                    sec.Semester,
                    sec.Year,
                    sec.MaxCapacity,
                    COALESCE(enrolled.CurrentCount, 0) as CurrentEnrollment,
                    (sec.MaxCapacity - COALESCE(enrolled.CurrentCount, 0)) as AvailableSpots,
                    sec.TimeSlot,
                    sec.Location,
                    i.Name as InstructorName
                FROM Section sec
                JOIN Course c ON sec.CourseID = c.CourseID
                LEFT JOIN Instructor i ON sec.InstructorID = i.InstructorID
                LEFT JOIN (
                    SELECT SectionID, COUNT(*) as CurrentCount
                    FROM Enrollment 
                    WHERE Status = 'Enrolled'
                    GROUP BY SectionID
                ) enrolled ON sec.SectionID = enrolled.SectionID
                WHERE sec.SectionID = %s
            """
            result = self.db.execute_query(query, (section_id,), fetch_one=True)
            
            if result:
                return SectionInfo(
                    section_id=result['SectionID'],
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    course_type=result['CourseType'],
                    semester=result['Semester'],
                    year=result['Year'],
                    max_capacity=result['MaxCapacity'],
                    current_enrollment=result['CurrentEnrollment'],
                    available_spots=result['AvailableSpots'],
                    time_slot=result['TimeSlot'],
                    location=result['Location'],
                    instructor_name=result['InstructorName']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_section_by_id", e)

class EnrollmentDAO(BaseDAO):
    """Enrollment data access operations"""
    
    def enroll_student(self, student_id: str, section_id: int) -> Tuple[bool, str]:
        """Enroll student in a section using stored procedure"""
        try:
            # Call stored procedure
            query = "CALL sp_EnrollStudent(%s, %s, @result, @success)"
            self.db.execute_update(query, (student_id, section_id))
            
            # Get results
            result_query = "SELECT @result as result, @success as success"
            result = self.db.execute_query(result_query, fetch_one=True)
            
            success = result['success'] == 1 if result['success'] is not None else False
            message = result['result'] or "Unknown error"
            
            return success, message
            
        except Exception as e:
            error_msg = str(e)
            if "Error:" in error_msg:
                return False, error_msg
            else:
                self._handle_db_error("enroll_student", e)
    
    def drop_enrollment(self, student_id: str, section_id: int) -> bool:
        """Drop student enrollment"""
        try:
            query = """
                UPDATE Enrollment 
                SET Status = 'Dropped' 
                WHERE StudentID = %s AND SectionID = %s AND Status = 'Enrolled'
            """
            rows_affected = self.db.execute_update(query, (student_id, section_id))
            return rows_affected > 0
            
        except Exception as e:
            self._handle_db_error("drop_enrollment", e)
    
    def update_grade(self, enrollment_id: int, final_grade: float) -> bool:
        """Update student's final grade"""
        try:
            # Calculate grade points
            grade_points = AppConfig.calculate_grade_points(final_grade)
            
            query = """
                UPDATE Enrollment 
                SET FinalGrade = %s, GradePoints = %s,
                    Status = CASE WHEN %s >= 60 THEN 'Completed' ELSE 'Failed' END
                WHERE EnrollmentID = %s
            """
            params = (final_grade, grade_points, final_grade, enrollment_id)
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            self._handle_db_error("update_grade", e)
    
    def get_student_enrollments(self, student_id: str, semester: str = None, year: int = None) -> List[EnrollmentInfo]:
        """Get student's enrollment information"""
        try:
            base_query = """
                SELECT 
                    e.EnrollmentID,
                    e.StudentID,
                    s.Name as StudentName,
                    c.CourseID,
                    c.CourseName,
                    c.Credits,
                    sec.SectionID,
                    sec.Semester,
                    sec.Year,
                    sec.TimeSlot,
                    sec.Location,
                    i.Name as InstructorName,
                    e.Status,
                    e.FinalGrade,
                    e.GradePoints,
                    e.EnrollmentDate
                FROM Enrollment e
                JOIN Student s ON e.StudentID = s.StudentID
                JOIN Section sec ON e.SectionID = sec.SectionID
                JOIN Course c ON sec.CourseID = c.CourseID
                LEFT JOIN Instructor i ON sec.InstructorID = i.InstructorID
                WHERE e.StudentID = %s
            """
            
            params = [student_id]
            
            if semester and year:
                base_query += " AND sec.Semester = %s AND sec.Year = %s"
                params.extend([semester, year])
            
            base_query += " ORDER BY sec.Year DESC, sec.Semester, c.CourseID"
            
            results = self.db.execute_query(base_query, params)
            
            enrollments = []
            for result in results:
                enrollments.append(EnrollmentInfo(
                    enrollment_id=result['EnrollmentID'],
                    student_id=result['StudentID'],
                    student_name=result['StudentName'],
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    section_id=result['SectionID'],
                    semester=result['Semester'],
                    year=result['Year'],
                    time_slot=result['TimeSlot'],
                    location=result['Location'],
                    instructor_name=result['InstructorName'],
                    status=result['Status'],
                    final_grade=float(result['FinalGrade']) if result['FinalGrade'] else None,
                    grade_points=float(result['GradePoints']) if result['GradePoints'] else None,
                    enrollment_date=result['EnrollmentDate']
                ))
            
            return enrollments
            
        except Exception as e:
            self._handle_db_error("get_student_enrollments", e)
    
    def get_section_enrollments(self, section_id: int) -> List[EnrollmentInfo]:
        """Get all enrollments for a section"""
        try:
            query = """
                SELECT 
                    e.EnrollmentID,
                    e.StudentID,
                    s.Name as StudentName,
                    c.CourseID,
                    c.CourseName,
                    c.Credits,
                    sec.SectionID,
                    sec.Semester,
                    sec.Year,
                    sec.TimeSlot,
                    sec.Location,
                    i.Name as InstructorName,
                    e.Status,
                    e.FinalGrade,
                    e.GradePoints,
                    e.EnrollmentDate
                FROM Enrollment e
                JOIN Student s ON e.StudentID = s.StudentID
                JOIN Section sec ON e.SectionID = sec.SectionID
                JOIN Course c ON sec.CourseID = c.CourseID
                LEFT JOIN Instructor i ON sec.InstructorID = i.InstructorID
                WHERE e.SectionID = %s
                ORDER BY s.Name
            """
            
            results = self.db.execute_query(query, (section_id,))
            
            enrollments = []
            for result in results:
                enrollments.append(EnrollmentInfo(
                    enrollment_id=result['EnrollmentID'],
                    student_id=result['StudentID'],
                    student_name=result['StudentName'],
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    section_id=result['SectionID'],
                    semester=result['Semester'],
                    year=result['Year'],
                    time_slot=result['TimeSlot'],
                    location=result['Location'],
                    instructor_name=result['InstructorName'],
                    status=result['Status'],
                    final_grade=float(result['FinalGrade']) if result['FinalGrade'] else None,
                    grade_points=float(result['GradePoints']) if result['GradePoints'] else None,
                    enrollment_date=result['EnrollmentDate']
                ))
            
            return enrollments
            
        except Exception as e:
            self._handle_db_error("get_section_enrollments", e)

class DepartmentDAO(BaseDAO):
    """Department data access operations"""
    
    def get_all_departments(self) -> List[Department]:
        """Get all departments"""
        try:
            query = "SELECT * FROM Department ORDER BY DeptName"
            results = self.db.execute_query(query)
            
            departments = []
            for result in results:
                departments.append(Department(
                    dept_id=result['DeptID'],
                    dept_name=result['DeptName'],
                    dept_head=result['DeptHead'],
                    created_date=result['CreatedDate'],
                    updated_date=result['UpdatedDate']
                ))
            
            return departments
            
        except Exception as e:
            self._handle_db_error("get_all_departments", e)
    
    def create_department(self, department: Department) -> str:
        """Create a new department"""
        try:
            query = """
                INSERT INTO Department (DeptID, DeptName, DeptHead)
                VALUES (%s, %s, %s)
            """
            params = (department.dept_id, department.dept_name, department.dept_head)
            
            self.db.execute_update(query, params)
            return department.dept_id
            
        except Exception as e:
            self._handle_db_error("create_department", e)

class StatisticsDAO(BaseDAO):
    """Statistics and reporting data access operations"""
    
    def get_student_gpa(self, student_id: str) -> Optional[StudentGPA]:
        """Get student's GPA information"""
        try:
            # Use stored procedure
            query = "CALL sp_CalculateGPA(%s, @gpa, @total_credits)"
            self.db.execute_update(query, (student_id,))
            
            # Get results
            result_query = "SELECT @gpa as gpa, @total_credits as total_credits"
            result = self.db.execute_query(result_query, fetch_one=True)
            
            # Get additional student info
            student_query = """
                SELECT s.Name,
                       COUNT(e.EnrollmentID) as TotalCourses,
                       COUNT(CASE WHEN e.Status = 'Completed' THEN 1 END) as CompletedCourses
                FROM Student s
                LEFT JOIN Enrollment e ON s.StudentID = e.StudentID
                WHERE s.StudentID = %s
                GROUP BY s.StudentID, s.Name
            """
            student_info = self.db.execute_query(student_query, (student_id,), fetch_one=True)
            
            if student_info:
                return StudentGPA(
                    student_id=student_id,
                    student_name=student_info['Name'],
                    total_credits=float(result['total_credits']) if result['total_credits'] else 0.0,
                    completed_credits=float(result['total_credits']) if result['total_credits'] else 0.0,
                    gpa=float(result['gpa']) if result['gpa'] else 0.0,
                    total_courses=student_info['TotalCourses'],
                    completed_courses=student_info['CompletedCourses']
                )
            return None
            
        except Exception as e:
            self._handle_db_error("get_student_gpa", e)
    
    def get_course_statistics(self) -> List[CourseStatistics]:
        """Get course statistics from view"""
        try:
            query = "SELECT * FROM CourseStatistics ORDER BY CourseID"
            results = self.db.execute_query(query)
            
            statistics = []
            for result in results:
                statistics.append(CourseStatistics(
                    course_id=result['CourseID'],
                    course_name=result['CourseName'],
                    credits=float(result['Credits']),
                    department=result['Department'],
                    dept_name=result['DeptName'] or '',
                    total_enrollments=result['TotalEnrollments'],
                    current_enrollments=result['CurrentEnrollments'],
                    completed_enrollments=result['CompletedEnrollments'],
                    average_grade=float(result['AverageGrade']) if result['AverageGrade'] else None,
                    pass_count=result['PassCount'],
                    fail_count=result['FailCount'],
                    pass_rate=float(result['PassRate']) if result['PassRate'] else None
                ))
            
            return statistics
            
        except Exception as e:
            self._handle_db_error("get_course_statistics", e)