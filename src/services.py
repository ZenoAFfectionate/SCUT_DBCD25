"""
Business Logic Services Module
University Course Registration and Grade Management System
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date
import logging
from dao import *
from models import *
from config import AppConfig

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Authentication and session management service"""
    
    def __init__(self):
        self.user_dao = UserDAO()
        self.student_dao = StudentDAO()
        self.instructor_dao = InstructorDAO()
        self.current_user = None
        self.current_student = None
        self.current_instructor = None
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Authenticate user login"""
        try:
            user = self.user_dao.authenticate_user(username, password)
            
            if user:
                self.current_user = user
                
                # Load role-specific information
                if user.user_type == UserType.STUDENT:
                    self.current_student = self.student_dao.get_student_by_user_id(user.user_id)
                elif user.user_type == UserType.INSTRUCTOR:
                    self.current_instructor = self.instructor_dao.get_instructor_by_user_id(user.user_id)
                
                return True, f"Welcome, {username}!", user
            else:
                return False, "Invalid username or password", None
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "Login failed due to system error", None
    
    def logout(self):
        """Clear current session"""
        self.current_user = None
        self.current_student = None
        self.current_instructor = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def has_role(self, role: UserType) -> bool:
        """Check if current user has specific role"""
        return self.current_user and self.current_user.user_type == role
    
    def get_current_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        if not self.current_user:
            return {}
        
        info = {
            'user_id': self.current_user.user_id,
            'username': self.current_user.username,
            'user_type': self.current_user.user_type.value,
            'status': self.current_user.status.value
        }
        
        if self.current_student:
            info.update({
                'student_id': self.current_student.student_id,
                'name': self.current_student.name,
                'college': self.current_student.college,
                'major': self.current_student.major
            })
        elif self.current_instructor:
            info.update({
                'instructor_id': self.current_instructor.instructor_id,
                'name': self.current_instructor.name,
                'department': self.current_instructor.department,
                'title': self.current_instructor.title
            })
        
        return info

class StudentService:
    """Student-related business logic service"""
    
    def __init__(self):
        self.student_dao = StudentDAO()
        self.enrollment_dao = EnrollmentDAO()
        self.section_dao = SectionDAO()
        self.statistics_dao = StatisticsDAO()
    
    def register_student(self, student_data: Dict[str, Any], username: str, password: str) -> Tuple[bool, str]:
        """Register a new student"""
        try:
            # Create user account
            user = User(
                username=username,
                password=password,
                user_type=UserType.STUDENT,
                status=UserStatus.ACTIVE
            )
            
            # Create student record
            student = Student(
                student_id=student_data['student_id'],
                name=student_data['name'],
                gender=Gender(student_data['gender']) if student_data.get('gender') else None,
                birth_date=student_data.get('birth_date'),
                email=student_data.get('email'),
                phone=student_data.get('phone'),
                college=student_data.get('college'),
                major=student_data.get('major'),
                enrollment_year=student_data.get('enrollment_year')
            )
            
            student_id = self.student_dao.create_student(student, user)
            return True, f"Student {student_id} registered successfully"
            
        except Exception as e:
            logger.error(f"Student registration error: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def get_available_courses(self, student_id: str, semester: str, year: int) -> List[SectionInfo]:
        """Get available courses for student enrollment"""
        try:
            return self.section_dao.get_available_sections(semester, year, student_id)
        except Exception as e:
            logger.error(f"Error getting available courses: {e}")
            return []
    
    def enroll_in_course(self, student_id: str, section_id: int) -> Tuple[bool, str]:
        """Enroll student in a course section"""
        try:
            success, message = self.enrollment_dao.enroll_student(student_id, section_id)
            return success, message
        except Exception as e:
            logger.error(f"Enrollment error: {e}")
            return False, f"Enrollment failed: {str(e)}"
    
    def drop_course(self, student_id: str, section_id: int) -> Tuple[bool, str]:
        """Drop student from a course section"""
        try:
            success = self.enrollment_dao.drop_enrollment(student_id, section_id)
            if success:
                return True, "Course dropped successfully"
            else:
                return False, "Failed to drop course - enrollment not found or already dropped"
        except Exception as e:
            logger.error(f"Drop course error: {e}")
            return False, f"Drop failed: {str(e)}"
    
    def get_student_schedule(self, student_id: str, semester: str = None, year: int = None) -> List[EnrollmentInfo]:
        """Get student's current schedule"""
        try:
            return self.enrollment_dao.get_student_enrollments(student_id, semester, year)
        except Exception as e:
            logger.error(f"Error getting student schedule: {e}")
            return []
    
    def get_student_transcript(self, student_id: str) -> Tuple[List[EnrollmentInfo], StudentGPA]:
        """Get student's complete transcript with GPA"""
        try:
            # Get all enrollments
            enrollments = self.enrollment_dao.get_student_enrollments(student_id)
            
            # Get GPA information
            gpa_info = self.statistics_dao.get_student_gpa(student_id)
            
            return enrollments, gpa_info
        except Exception as e:
            logger.error(f"Error getting student transcript: {e}")
            return [], None
    
    def validate_enrollment_eligibility(self, student_id: str, section_id: int) -> Tuple[bool, List[str]]:
        """Validate if student is eligible to enroll in a section"""
        try:
            warnings = []
            
            # Get section information
            section = self.section_dao.get_section_by_id(section_id)
            if not section:
                return False, ["Section not found"]
            
            # Check capacity
            if section.available_spots <= 0:
                return False, ["Section is full"]
            
            # Get current semester enrollments
            current_enrollments = self.enrollment_dao.get_student_enrollments(
                student_id, section.semester, section.year
            )
            
            # Check credit limits
            current_credits = sum(e.credits for e in current_enrollments if e.status == 'Enrolled')
            new_total_credits = current_credits + section.credits
            
            if new_total_credits > AppConfig.MAX_CREDITS_PER_SEMESTER:
                return False, [f"Exceeds maximum credit limit ({AppConfig.MAX_CREDITS_PER_SEMESTER})"]
            
            if new_total_credits < AppConfig.MIN_CREDITS_PER_SEMESTER and len(current_enrollments) == 0:
                warnings.append(f"Below minimum credit recommendation ({AppConfig.MIN_CREDITS_PER_SEMESTER})")
            
            # Check time conflicts
            for enrollment in current_enrollments:
                if (enrollment.status == 'Enrolled' and 
                    enrollment.time_slot and section.time_slot and
                    enrollment.time_slot == section.time_slot):
                    return False, ["Time conflict with existing enrollment"]
            
            # Check if already enrolled
            for enrollment in current_enrollments:
                if enrollment.section_id == section_id:
                    return False, ["Already enrolled in this section"]
            
            return True, warnings
            
        except Exception as e:
            logger.error(f"Enrollment validation error: {e}")
            return False, ["Validation failed due to system error"]

class InstructorService:
    """Instructor-related business logic service"""
    
    def __init__(self):
        self.instructor_dao = InstructorDAO()
        self.enrollment_dao = EnrollmentDAO()
        self.section_dao = SectionDAO()
    
    def register_instructor(self, instructor_data: Dict[str, Any], username: str, password: str) -> Tuple[bool, str]:
        """Register a new instructor"""
        try:
            # Create user account
            user = User(
                username=username,
                password=password,
                user_type=UserType.INSTRUCTOR,
                status=UserStatus.ACTIVE
            )
            
            # Create instructor record
            instructor = Instructor(
                instructor_id=instructor_data['instructor_id'],
                name=instructor_data['name'],
                department=instructor_data.get('department'),
                email=instructor_data.get('email'),
                phone=instructor_data.get('phone'),
                title=instructor_data.get('title')
            )
            
            instructor_id = self.instructor_dao.create_instructor(instructor, user)
            return True, f"Instructor {instructor_id} registered successfully"
            
        except Exception as e:
            logger.error(f"Instructor registration error: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def get_instructor_sections(self, instructor_id: str, semester: str = None, year: int = None) -> List[SectionInfo]:
        """Get sections taught by instructor"""
        try:
            # This would need a custom query in the DAO
            # For now, return empty list - would need to implement in SectionDAO
            return []
        except Exception as e:
            logger.error(f"Error getting instructor sections: {e}")
            return []
    
    def get_section_roster(self, section_id: int) -> List[EnrollmentInfo]:
        """Get roster for a section"""
        try:
            return self.enrollment_dao.get_section_enrollments(section_id)
        except Exception as e:
            logger.error(f"Error getting section roster: {e}")
            return []
    
    def update_student_grade(self, enrollment_id: int, final_grade: float) -> Tuple[bool, str]:
        """Update a student's final grade"""
        try:
            # Validate grade
            if not (0 <= final_grade <= 100):
                return False, "Grade must be between 0 and 100"
            
            success = self.enrollment_dao.update_grade(enrollment_id, final_grade)
            if success:
                return True, "Grade updated successfully"
            else:
                return False, "Failed to update grade - enrollment not found"
                
        except Exception as e:
            logger.error(f"Grade update error: {e}")
            return False, f"Grade update failed: {str(e)}"

class CourseService:
    """Course management service"""
    
    def __init__(self):
        self.course_dao = CourseDAO()
        self.section_dao = SectionDAO()
        self.statistics_dao = StatisticsDAO()
    
    def create_course(self, course_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Create a new course"""
        try:
            course = Course(
                course_id=course_data['course_id'],
                course_name=course_data['course_name'],
                credits=float(course_data['credits']),
                department=course_data.get('department'),
                course_type=CourseType(course_data['course_type']),
                description=course_data.get('description')
            )
            
            course_id = self.course_dao.create_course(course)
            return True, f"Course {course_id} created successfully"
            
        except Exception as e:
            logger.error(f"Course creation error: {e}")
            return False, f"Course creation failed: {str(e)}"
    
    def search_courses(self, search_term: str = None, department: str = None) -> List[Course]:
        """Search for courses"""
        try:
            if search_term:
                return self.course_dao.search_courses(search_term)
            else:
                return self.course_dao.get_all_courses(department)
        except Exception as e:
            logger.error(f"Course search error: {e}")
            return []
    
    def create_section(self, section_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Create a new course section"""
        try:
            section = Section(
                course_id=section_data['course_id'],
                instructor_id=section_data.get('instructor_id'),
                semester=Semester(section_data['semester']),
                year=int(section_data['year']),
                max_capacity=int(section_data['max_capacity']),
                time_slot=section_data.get('time_slot'),
                location=section_data.get('location')
            )
            
            section_id = self.section_dao.create_section(section)
            return True, f"Section {section_id} created successfully"
            
        except Exception as e:
            logger.error(f"Section creation error: {e}")
            return False, f"Section creation failed: {str(e)}"
    
    def get_course_statistics(self) -> List[CourseStatistics]:
        """Get course statistics"""
        try:
            return self.statistics_dao.get_course_statistics()
        except Exception as e:
            logger.error(f"Error getting course statistics: {e}")
            return []

class AdminService:
    """Administrative service"""
    
    def __init__(self):
        self.department_dao = DepartmentDAO()
        self.student_dao = StudentDAO()
        self.instructor_dao = InstructorDAO()
        self.course_dao = CourseDAO()
        self.statistics_dao = StatisticsDAO()
    
    def create_department(self, dept_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Create a new department"""
        try:
            department = Department(
                dept_id=dept_data['dept_id'],
                dept_name=dept_data['dept_name'],
                dept_head=dept_data.get('dept_head')
            )
            
            dept_id = self.department_dao.create_department(department)
            return True, f"Department {dept_id} created successfully"
            
        except Exception as e:
            logger.error(f"Department creation error: {e}")
            return False, f"Department creation failed: {str(e)}"
    
    def get_all_departments(self) -> List[Department]:
        """Get all departments"""
        try:
            return self.department_dao.get_all_departments()
        except Exception as e:
            logger.error(f"Error getting departments: {e}")
            return []
    
    def get_all_students(self, limit: int = 100, offset: int = 0) -> List[Student]:
        """Get all students with pagination"""
        try:
            return self.student_dao.get_all_students(limit, offset)
        except Exception as e:
            logger.error(f"Error getting students: {e}")
            return []
    
    def get_all_instructors(self) -> List[Instructor]:
        """Get all instructors"""
        try:
            return self.instructor_dao.get_all_instructors()
        except Exception as e:
            logger.error(f"Error getting instructors: {e}")
            return []
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        try:
            stats = {}
            
            # Get basic counts
            students = self.get_all_students(limit=1000)  # Get more for accurate count
            instructors = self.get_all_instructors()
            departments = self.get_all_departments()
            
            stats['total_students'] = len(students)
            stats['total_instructors'] = len(instructors)
            stats['total_departments'] = len(departments)
            
            # Get course statistics
            course_stats = self.statistics_dao.get_course_statistics()
            stats['total_courses'] = len(course_stats)
            stats['total_enrollments'] = sum(cs.total_enrollments for cs in course_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {}

# Global service instances
auth_service = AuthenticationService()
student_service = StudentService()
instructor_service = InstructorService()
course_service = CourseService()
admin_service = AdminService()