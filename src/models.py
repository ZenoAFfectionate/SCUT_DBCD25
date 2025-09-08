"""
Data Models Module
University Course Registration and Grade Management System
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class UserType(Enum):
    STUDENT = "Student"
    INSTRUCTOR = "Instructor"
    ADMIN = "Admin"

class UserStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"

class Semester(Enum):
    SPRING = "Spring"
    SUMMER = "Summer"
    FALL = "Fall"

class EnrollmentStatus(Enum):
    ENROLLED = "Enrolled"
    DROPPED = "Dropped"
    COMPLETED = "Completed"
    FAILED = "Failed"

class CourseType(Enum):
    GENERAL_REQUIRED = "通识必修"
    MAJOR_REQUIRED = "专业必修"
    MAJOR_ELECTIVE = "专业选修"
    UNIVERSITY_ELECTIVE = "全校选修"
    PRACTICAL = "实践课程"

class Gender(Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "Other"

@dataclass
class User:
    user_id: Optional[int] = None
    username: str = ""
    password: str = ""
    user_type: UserType = UserType.STUDENT
    created_date: Optional[datetime] = None
    status: UserStatus = UserStatus.PENDING
    last_login_date: Optional[datetime] = None

@dataclass
class Department:
    dept_id: str = ""
    dept_name: str = ""
    dept_head: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

@dataclass
class Student:
    student_id: str = ""
    user_id: Optional[int] = None
    name: str = ""
    gender: Optional[Gender] = None
    birth_date: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    major: Optional[str] = None
    enrollment_year: Optional[int] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

@dataclass
class Instructor:
    instructor_id: str = ""
    user_id: Optional[int] = None
    name: str = ""
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

@dataclass
class Course:
    course_id: str = ""
    course_name: str = ""
    credits: float = 0.0
    department: Optional[str] = None
    course_type: CourseType = CourseType.MAJOR_REQUIRED
    description: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

@dataclass
class Section:
    section_id: Optional[int] = None
    course_id: str = ""
    instructor_id: Optional[str] = None
    semester: Semester = Semester.FALL
    year: int = 2024
    max_capacity: int = 30
    time_slot: Optional[str] = None
    location: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

@dataclass
class Enrollment:
    enrollment_id: Optional[int] = None
    student_id: str = ""
    section_id: int = 0
    enrollment_date: Optional[datetime] = None
    status: EnrollmentStatus = EnrollmentStatus.ENROLLED
    final_grade: Optional[float] = None
    grade_points: Optional[float] = None
    updated_date: Optional[datetime] = None

@dataclass
class CoursePrereq:
    course_id: str = ""
    prereq_course_id: str = ""
    min_grade: float = 60.0
    created_date: Optional[datetime] = None

@dataclass
class EnrollmentInfo:
    """Extended enrollment information with related data"""
    enrollment_id: Optional[int] = None
    student_id: str = ""
    student_name: str = ""
    course_id: str = ""
    course_name: str = ""
    credits: float = 0.0
    section_id: int = 0
    semester: str = ""
    year: int = 2024
    time_slot: Optional[str] = None
    location: Optional[str] = None
    instructor_name: Optional[str] = None
    status: str = ""
    final_grade: Optional[float] = None
    grade_points: Optional[float] = None
    enrollment_date: Optional[datetime] = None

@dataclass
class SectionInfo:
    """Extended section information with related data"""
    section_id: int = 0
    course_id: str = ""
    course_name: str = ""
    credits: float = 0.0
    course_type: str = ""
    semester: str = ""
    year: int = 2024
    max_capacity: int = 30
    current_enrollment: int = 0
    available_spots: int = 30
    time_slot: Optional[str] = None
    location: Optional[str] = None
    instructor_name: Optional[str] = None
    availability_status: str = "Available"

@dataclass
class StudentGPA:
    """Student GPA information"""
    student_id: str = ""
    student_name: str = ""
    total_credits: float = 0.0
    completed_credits: float = 0.0
    gpa: float = 0.0
    semester_gpa: Optional[float] = None
    total_courses: int = 0
    completed_courses: int = 0

@dataclass
class CourseStatistics:
    """Course statistics information"""
    course_id: str = ""
    course_name: str = ""
    credits: float = 0.0
    department: str = ""
    dept_name: str = ""
    total_enrollments: int = 0
    current_enrollments: int = 0
    completed_enrollments: int = 0
    average_grade: Optional[float] = None
    pass_count: int = 0
    fail_count: int = 0
    pass_rate: Optional[float] = None

@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: Optional[int] = None
    user_id: Optional[int] = None
    table_name: str = ""
    operation: str = ""
    record_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None

# Utility functions for model conversion
def dict_to_model(data_dict: Dict[str, Any], model_class):
    """Convert dictionary to model instance"""
    if not data_dict:
        return None
    
    # Filter out None values and keys not in model
    filtered_data = {k: v for k, v in data_dict.items() if v is not None}
    
    try:
        return model_class(**filtered_data)
    except TypeError as e:
        # Handle cases where dict keys don't match model fields
        model_fields = {field.name for field in model_class.__dataclass_fields__.values()}
        valid_data = {k: v for k, v in filtered_data.items() if k in model_fields}
        return model_class(**valid_data)

def model_to_dict(model_instance) -> Dict[str, Any]:
    """Convert model instance to dictionary"""
    if not model_instance:
        return {}
    
    result = {}
    for field_name, field_value in model_instance.__dict__.items():
        if isinstance(field_value, Enum):
            result[field_name] = field_value.value
        elif isinstance(field_value, (datetime, date)):
            result[field_name] = field_value.isoformat() if field_value else None
        else:
            result[field_name] = field_value
    
    return result