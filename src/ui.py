"""
User Interface Module
University Course Registration and Grade Management System
Command Line Interface
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from tabulate import tabulate
from colorama import init, Fore, Back, Style
import logging

from services import *
from models import *
from config import AppConfig

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.WARNING)

class UIManager:
    """Main UI manager for the application"""
    
    def __init__(self):
        self.running = True
        self.current_menu = None
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN}{title.center(80)}")
        print(f"{Fore.CYAN}{'=' * 80}\n")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Fore.RED}✗ {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {message}")
    
    def get_input(self, prompt: str, input_type: type = str, required: bool = True):
        """Get user input with validation"""
        while True:
            try:
                value = input(f"{Fore.WHITE}{prompt}: ").strip()
                
                if not value and required:
                    self.print_error("This field is required")
                    continue
                
                if not value and not required:
                    return None
                
                if input_type == int:
                    return int(value)
                elif input_type == float:
                    return float(value)
                elif input_type == date:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                else:
                    return value
                    
            except ValueError as e:
                self.print_error(f"Invalid input format: {e}")
                continue
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return None
    
    def get_choice(self, prompt: str, choices: List[str], allow_cancel: bool = True) -> Optional[str]:
        """Get user choice from a list of options"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        if allow_cancel:
            print("0. Cancel")
        
        while True:
            try:
                choice_num = int(input("\nEnter your choice: "))
                
                if choice_num == 0 and allow_cancel:
                    return None
                elif 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    self.print_error("Invalid choice")
                    
            except ValueError:
                self.print_error("Please enter a number")
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return None
    
    def confirm_action(self, message: str) -> bool:
        """Get user confirmation"""
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                self.print_error("Please enter 'y' or 'n'")
    
    def display_table(self, data: List[Dict[str, Any]], headers: List[str] = None, title: str = None):
        """Display data in a formatted table"""
        if not data:
            self.print_info("No data to display")
            return
        
        if title:
            print(f"\n{Fore.CYAN}{title}")
            print(f"{Fore.CYAN}{'-' * len(title)}")
        
        if headers is None:
            headers = list(data[0].keys())
        
        # Prepare table data
        table_data = []
        for row in data:
            table_row = []
            for header in headers:
                value = row.get(header, '')
                if value is None:
                    value = ''
                elif isinstance(value, float):
                    value = f"{value:.2f}"
                table_row.append(str(value))
            table_data.append(table_row)
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def wait_for_key(self, message: str = "Press Enter to continue..."):
        """Wait for user to press a key"""
        input(f"\n{message}")
    
    def run(self):
        """Main application loop"""
        self.clear_screen()
        self.print_header("University Course Registration System")
        
        while self.running:
            try:
                if not auth_service.is_authenticated():
                    self.show_login_menu()
                else:
                    self.show_main_menu()
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                self.running = False
            except Exception as e:
                self.print_error(f"An unexpected error occurred: {e}")
                self.wait_for_key()

class LoginMenu:
    """Login and registration menu"""
    
    def __init__(self, ui: UIManager):
        self.ui = ui
    
    def show(self):
        """Show login menu"""
        self.ui.clear_screen()
        self.ui.print_header("Login / Registration")
        
        choices = [
            "Login",
            "Register as Student",
            "Register as Instructor",
            "Exit"
        ]
        
        choice = self.ui.get_choice("Please select an option:", choices, allow_cancel=False)
        
        if choice == "Login":
            self.login()
        elif choice == "Register as Student":
            self.register_student()
        elif choice == "Register as Instructor":
            self.register_instructor()
        elif choice == "Exit":
            self.ui.running = False
    
    def login(self):
        """Handle user login"""
        self.ui.clear_screen()
        self.ui.print_header("User Login")
        
        username = self.ui.get_input("Username")
        if not username:
            return
        
        password = self.ui.get_input("Password")
        if not password:
            return
        
        success, message, user = auth_service.login(username, password)
        
        if success:
            self.ui.print_success(message)
            self.ui.wait_for_key()
        else:
            self.ui.print_error(message)
            self.ui.wait_for_key()
    
    def register_student(self):
        """Handle student registration"""
        self.ui.clear_screen()
        self.ui.print_header("Student Registration")
        
        # Get user account info
        username = self.ui.get_input("Username")
        if not username:
            return
        
        password = self.ui.get_input("Password")
        if not password:
            return
        
        # Get student info
        student_id = self.ui.get_input("Student ID")
        name = self.ui.get_input("Full Name")
        
        gender_choices = ["Male", "Female", "Other"]
        gender_choice = self.ui.get_choice("Gender", gender_choices)
        gender = None
        if gender_choice:
            gender_map = {"Male": "M", "Female": "F", "Other": "Other"}
            gender = gender_map[gender_choice]
        
        birth_date = self.ui.get_input("Birth Date (YYYY-MM-DD)", date, required=False)
        email = self.ui.get_input("Email", required=False)
        phone = self.ui.get_input("Phone", required=False)
        
        # Get departments for college selection
        departments = admin_service.get_all_departments()
        if departments:
            dept_choices = [f"{d.dept_id} - {d.dept_name}" for d in departments]
            college_choice = self.ui.get_choice("College", dept_choices)
            college = college_choice.split(" - ")[0] if college_choice else None
        else:
            college = self.ui.get_input("College Code", required=False)
        
        major = self.ui.get_input("Major", required=False)
        enrollment_year = self.ui.get_input("Enrollment Year", int, required=False)
        
        # Prepare student data
        student_data = {
            'student_id': student_id,
            'name': name,
            'gender': gender,
            'birth_date': birth_date,
            'email': email,
            'phone': phone,
            'college': college,
            'major': major,
            'enrollment_year': enrollment_year
        }
        
        success, message = student_service.register_student(student_data, username, password)
        
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        
        self.ui.wait_for_key()
    
    def register_instructor(self):
        """Handle instructor registration"""
        self.ui.clear_screen()
        self.ui.print_header("Instructor Registration")
        
        # Get user account info
        username = self.ui.get_input("Username")
        if not username:
            return
        
        password = self.ui.get_input("Password")
        if not password:
            return
        
        # Get instructor info
        instructor_id = self.ui.get_input("Instructor ID")
        name = self.ui.get_input("Full Name")
        
        # Get departments
        departments = admin_service.get_all_departments()
        if departments:
            dept_choices = [f"{d.dept_id} - {d.dept_name}" for d in departments]
            dept_choice = self.ui.get_choice("Department", dept_choices)
            department = dept_choice.split(" - ")[0] if dept_choice else None
        else:
            department = self.ui.get_input("Department Code", required=False)
        
        email = self.ui.get_input("Email", required=False)
        phone = self.ui.get_input("Phone", required=False)
        title = self.ui.get_input("Title (e.g., Professor, Associate Professor)", required=False)
        
        # Prepare instructor data
        instructor_data = {
            'instructor_id': instructor_id,
            'name': name,
            'department': department,
            'email': email,
            'phone': phone,
            'title': title
        }
        
        success, message = instructor_service.register_instructor(instructor_data, username, password)
        
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        
        self.ui.wait_for_key()

class StudentMenu:
    """Student-specific menu"""
    
    def __init__(self, ui: UIManager):
        self.ui = ui
    
    def show(self):
        """Show student menu"""
        self.ui.clear_screen()
        user_info = auth_service.get_current_user_info()
        self.ui.print_header(f"Student Portal - {user_info.get('name', 'Student')}")
        
        choices = [
            "View Available Courses",
            "Enroll in Course",
            "View My Schedule",
            "Drop Course",
            "View Transcript",
            "View GPA",
            "Logout"
        ]
        
        choice = self.ui.get_choice("Please select an option:", choices, allow_cancel=False)
        
        if choice == "View Available Courses":
            self.view_available_courses()
        elif choice == "Enroll in Course":
            self.enroll_in_course()
        elif choice == "View My Schedule":
            self.view_schedule()
        elif choice == "Drop Course":
            self.drop_course()
        elif choice == "View Transcript":
            self.view_transcript()
        elif choice == "View GPA":
            self.view_gpa()
        elif choice == "Logout":
            auth_service.logout()
    
    def view_available_courses(self):
        """View available courses for enrollment"""
        self.ui.clear_screen()
        self.ui.print_header("Available Courses")
        
        # Get current semester info
        current_year = datetime.now().year
        semester_choices = ["Spring", "Summer", "Fall"]
        semester = self.ui.get_choice("Select Semester", semester_choices)
        if not semester:
            return
        
        year = self.ui.get_input("Year", int) or current_year
        
        user_info = auth_service.get_current_user_info()
        student_id = user_info.get('student_id')
        
        sections = student_service.get_available_courses(student_id, semester, year)
        
        if not sections:
            self.ui.print_info("No available courses found")
            self.ui.wait_for_key()
            return
        
        # Prepare table data
        table_data = []
        for section in sections:
            table_data.append({
                'Section ID': section.section_id,
                'Course ID': section.course_id,
                'Course Name': section.course_name,
                'Credits': section.credits,
                'Instructor': section.instructor_name or 'TBA',
                'Time': section.time_slot or 'TBA',
                'Location': section.location or 'TBA',
                'Available': f"{section.available_spots}/{section.max_capacity}",
                'Status': section.availability_status
            })
        
        self.ui.display_table(table_data, title="Available Courses")
        self.ui.wait_for_key()
    
    def enroll_in_course(self):
        """Enroll in a course"""
        self.ui.clear_screen()
        self.ui.print_header("Course Enrollment")
        
        section_id = self.ui.get_input("Enter Section ID to enroll", int)
        if not section_id:
            return
        
        user_info = auth_service.get_current_user_info()
        student_id = user_info.get('student_id')
        
        # Validate eligibility
        eligible, warnings = student_service.validate_enrollment_eligibility(student_id, section_id)
        
        if not eligible:
            for warning in warnings:
                self.ui.print_error(warning)
            self.ui.wait_for_key()
            return
        
        # Show warnings if any
        for warning in warnings:
            self.ui.print_warning(warning)
        
        if warnings and not self.ui.confirm_action("Do you want to continue?"):
            return
        
        # Attempt enrollment
        success, message = student_service.enroll_in_course(student_id, section_id)
        
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        
        self.ui.wait_for_key()
    
    def view_schedule(self):
        """View current schedule"""
        self.ui.clear_screen()
        self.ui.print_header("My Schedule")
        
        user_info = auth_service.get_current_user_info()
        student_id = user_info.get('student_id')
        
        # Get current semester
        current_year = datetime.now().year
        semester_choices = ["Current Semester", "All Semesters", "Specific Semester"]
        choice = self.ui.get_choice("Select view", semester_choices)
        
        if choice == "Current Semester":
            # Determine current semester
            month = datetime.now().month
            if 1 <= month <= 5:
                semester = "Spring"
            elif 6 <= month <= 8:
                semester = "Summer"
            else:
                semester = "Fall"
            
            enrollments = student_service.get_student_schedule(student_id, semester, current_year)
        elif choice == "Specific Semester":
            semester_choices = ["Spring", "Summer", "Fall"]
            semester = self.ui.get_choice("Select Semester", semester_choices)
            if not semester:
                return
            year = self.ui.get_input("Year", int) or current_year
            enrollments = student_service.get_student_schedule(student_id, semester, year)
        else:
            enrollments = student_service.get_student_schedule(student_id)
        
        if not enrollments:
            self.ui.print_info("No enrollments found")
            self.ui.wait_for_key()
            return
        
        # Prepare table data
        table_data = []
        for enrollment in enrollments:
            table_data.append({
                'Course ID': enrollment.course_id,
                'Course Name': enrollment.course_name,
                'Credits': enrollment.credits,
                'Semester': f"{enrollment.semester} {enrollment.year}",
                'Instructor': enrollment.instructor_name or 'TBA',
                'Time': enrollment.time_slot or 'TBA',
                'Location': enrollment.location or 'TBA',
                'Status': enrollment.status,
                'Grade': enrollment.final_grade if enrollment.final_grade else 'N/A'
            })
        
        self.ui.display_table(table_data, title="My Schedule")
        self.ui.wait_for_key()
    
    def drop_course(self):
        """Drop a course"""
        self.ui.clear_screen()
        self.ui.print_header("Drop Course")
        
        user_info = auth_service.get_current_user_info()
        student_id = user_info.get('student_id')
        
        # Get current enrollments
        current_year = datetime.now().year
        month = datetime.now().month
        if 1 <= month <= 5:
            semester = "Spring"
        elif 6 <= month <= 8:
            semester = "Summer"
        else:
            semester = "Fall"
        
        enrollments = student_service.get_student_schedule(student_id, semester, current_year)
        enrolled_courses = [e for e in enrollments if e.status == 'Enrolled']
        
        if not enrolled_courses:
            self.ui.print_info("No enrolled courses to drop")
            self.ui.wait_for_key()
            return
        
        # Show current enrollments
        print("\nCurrent Enrollments:")
        for i, enrollment in enumerate(enrolled_courses, 1):
            print(f"{i}. {enrollment.course_id} - {enrollment.course_name} (Section {enrollment.section_id})")
        
        try:
            choice = int(input("\nSelect course to drop (number): ")) - 1
            if 0 <= choice < len(enrolled_courses):
                selected_enrollment = enrolled_courses[choice]
                
                if self.ui.confirm_action(f"Are you sure you want to drop {selected_enrollment.course_name}?"):
                    success, message = student_service.drop_course(student_id, selected_enrollment.section_id)
                    
                    if success:
                        self.ui.print_success(message)
                    else:
                        self.ui.print_error(message)
            else:
                self.ui.print_error("Invalid selection")
        except ValueError:
            self.ui.print_error("Please enter a valid number")
        
        self.ui.wait_for_key()
    
    def view_transcript(self):
        """View complete transcript"""
        self.ui.clear_screen()
        self.ui.print_header("Academic Transcript")
        
        user_info = auth_service.get_current_user_info()
        student_id = user_info.get('student_id')
        
        enrollments, gpa_info = student_service.get_student_transcript(student_id)
        
        if not enrollments:
            self.ui.print_info("No academic records found")
            self.ui.wait_for_key()
            return
        
        # Group by semester
        semester_groups = {}
        for enrollment in enrollments:
            key = f"{enrollment.semester} {enrollment.year}"
            if key not in semester_groups:
                semester_groups[key] = []
            semester_groups[key].append(enrollment)
        
        # Display by semester
        for semester_key in sorted(semester_groups.keys()):
            semester_enrollments = semester_groups[semester_key]
            
            print(f"\n{Fore.CYAN}{semester_key}")
            print(f"{Fore.CYAN}{'-' * len(semester_key)}")
            
            table_data = []
            semester_credits = 0
            semester_points = 0
            
            for enrollment in semester_enrollments:
                table_data.append({
                    'Course ID': enrollment.course_id,
                    'Course Name': enrollment.course_name,
                    'Credits': enrollment.credits,
                    'Grade': enrollment.final_grade if enrollment.final_grade else 'N/A',
                    'Points': enrollment.grade_points if enrollment.grade_points else 'N/A',
                    'Status': enrollment.status
                })
                
                if enrollment.status == 'Completed' and enrollment.grade_points:
                    semester_credits += enrollment.credits
                    semester_points += enrollment.grade_points * enrollment.credits
            
            self.ui.display_table(table_data)
            
            if semester_credits > 0:
                semester_gpa = semester_points / semester_credits
                print(f"Semester Credits: {semester_credits:.1f}, Semester GPA: {semester_gpa:.2f}")
        
        # Display overall GPA
        if gpa_info:
            print(f"\n{Fore.GREEN}Overall Statistics:")
            print(f"Total Credits: {gpa_info.completed_credits:.1f}")
            print(f"Overall GPA: {gpa_info.gpa:.2f}")
            print(f"Completed Courses: {gpa_info.completed_courses}")
        
        self.ui.wait_for_key()
    
    def view_gpa(self):
        """View GPA information"""
        self.ui.clear_screen()
        self.ui.print_header("GPA Information")
        
        user_info = auth_service.get_current_user_info()
        student_id = user_info.get('student_id')
        
        gpa_info = student_service.statistics_dao.get_student_gpa(student_id)
        
        if not gpa_info:
            self.ui.print_info("No GPA information available")
            self.ui.wait_for_key()
            return
        
        print(f"Student: {gpa_info.student_name}")
        print(f"Student ID: {gpa_info.student_id}")
        print(f"Total Completed Credits: {gpa_info.completed_credits:.1f}")
        print(f"Overall GPA: {gpa_info.gpa:.2f}")
        print(f"Total Courses Taken: {gpa_info.total_courses}")
        print(f"Completed Courses: {gpa_info.completed_courses}")
        
        self.ui.wait_for_key()

class InstructorMenu:
    """Instructor-specific menu"""
    
    def __init__(self, ui: UIManager):
        self.ui = ui
    
    def show(self):
        """Show instructor menu"""
        self.ui.clear_screen()
        user_info = auth_service.get_current_user_info()
        self.ui.print_header(f"Instructor Portal - {user_info.get('name', 'Instructor')}")
        
        choices = [
            "View My Sections",
            "View Section Roster",
            "Update Student Grades",
            "View Course Statistics",
            "Logout"
        ]
        
        choice = self.ui.get_choice("Please select an option:", choices, allow_cancel=False)
        
        if choice == "View My Sections":
            self.view_my_sections()
        elif choice == "View Section Roster":
            self.view_section_roster()
        elif choice == "Update Student Grades":
            self.update_grades()
        elif choice == "View Course Statistics":
            self.view_course_statistics()
        elif choice == "Logout":
            auth_service.logout()
    
    def view_my_sections(self):
        """View instructor's sections"""
        self.ui.clear_screen()
        self.ui.print_header("My Sections")
        
        user_info = auth_service.get_current_user_info()
        instructor_id = user_info.get('instructor_id')
        
        sections = instructor_service.get_instructor_sections(instructor_id)
        
        if not sections:
            self.ui.print_info("No sections assigned")
            self.ui.wait_for_key()
            return
        
        # This would need implementation in the service layer
        self.ui.print_info("Feature not yet implemented")
        self.ui.wait_for_key()
    
    def view_section_roster(self):
        """View roster for a section"""
        self.ui.clear_screen()
        self.ui.print_header("Section Roster")
        
        section_id = self.ui.get_input("Enter Section ID", int)
        if not section_id:
            return
        
        roster = instructor_service.get_section_roster(section_id)
        
        if not roster:
            self.ui.print_info("No students enrolled in this section")
            self.ui.wait_for_key()
            return
        
        # Prepare table data
        table_data = []
        for enrollment in roster:
            table_data.append({
                'Student ID': enrollment.student_id,
                'Student Name': enrollment.student_name,
                'Status': enrollment.status,
                'Final Grade': enrollment.final_grade if enrollment.final_grade else 'N/A',
                'Grade Points': enrollment.grade_points if enrollment.grade_points else 'N/A',
                'Enrollment Date': enrollment.enrollment_date.strftime("%Y-%m-%d") if enrollment.enrollment_date else 'N/A'
            })
        
        self.ui.display_table(table_data, title=f"Section {section_id} Roster")
        self.ui.wait_for_key()
    
    def update_grades(self):
        """Update student grades"""
        self.ui.clear_screen()
        self.ui.print_header("Update Student Grades")
        
        section_id = self.ui.get_input("Enter Section ID", int)
        if not section_id:
            return
        
        roster = instructor_service.get_section_roster(section_id)
        
        if not roster:
            self.ui.print_info("No students enrolled in this section")
            self.ui.wait_for_key()
            return
        
        # Show current roster
        print("\nCurrent Roster:")
        enrolled_students = [e for e in roster if e.status in ['Enrolled', 'Completed']]
        
        for i, enrollment in enumerate(enrolled_students, 1):
            current_grade = enrollment.final_grade if enrollment.final_grade else 'N/A'
            print(f"{i}. {enrollment.student_name} ({enrollment.student_id}) - Current Grade: {current_grade}")
        
        try:
            choice = int(input("\nSelect student to update grade (number): ")) - 1
            if 0 <= choice < len(enrolled_students):
                selected_enrollment = enrolled_students[choice]
                
                print(f"\nUpdating grade for: {selected_enrollment.student_name}")
                new_grade = self.ui.get_input("Enter final grade (0-100)", float)
                
                if new_grade is not None:
                    success, message = instructor_service.update_student_grade(
                        selected_enrollment.enrollment_id, new_grade
                    )
                    
                    if success:
                        self.ui.print_success(message)
                    else:
                        self.ui.print_error(message)
            else:
                self.ui.print_error("Invalid selection")
        except ValueError:
            self.ui.print_error("Please enter a valid number")
        
        self.ui.wait_for_key()
    
    def view_course_statistics(self):
        """View course statistics"""
        self.ui.clear_screen()
        self.ui.print_header("Course Statistics")
        
        statistics = course_service.get_course_statistics()
        
        if not statistics:
            self.ui.print_info("No statistics available")
            self.ui.wait_for_key()
            return
        
        # Prepare table data
        table_data = []
        for stat in statistics:
            table_data.append({
                'Course ID': stat.course_id,
                'Course Name': stat.course_name,
                'Credits': stat.credits,
                'Department': stat.dept_name or stat.department,
                'Total Enrollments': stat.total_enrollments,
                'Current Enrolled': stat.current_enrollments,
                'Completed': stat.completed_enrollments,
                'Average Grade': stat.average_grade if stat.average_grade else 'N/A',
                'Pass Rate': f"{stat.pass_rate:.1f}%" if stat.pass_rate else 'N/A'
            })
        
        self.ui.display_table(table_data, title="Course Statistics")
        self.ui.wait_for_key()

class AdminMenu:
    """Administrator-specific menu"""
    
    def __init__(self, ui: UIManager):
        self.ui = ui
    
    def show(self):
        """Show admin menu"""
        self.ui.clear_screen()
        user_info = auth_service.get_current_user_info()
        self.ui.print_header(f"Administrator Portal - {user_info.get('username', 'Admin')}")
        
        choices = [
            "Manage Departments",
            "Manage Courses",
            "Create Course Section",
            "View All Students",
            "View All Instructors",
            "System Statistics",
            "Logout"
        ]
        
        choice = self.ui.get_choice("Please select an option:", choices, allow_cancel=False)
        
        if choice == "Manage Departments":
            self.manage_departments()
        elif choice == "Manage Courses":
            self.manage_courses()
        elif choice == "Create Course Section":
            self.create_section()
        elif choice == "View All Students":
            self.view_all_students()
        elif choice == "View All Instructors":
            self.view_all_instructors()
        elif choice == "System Statistics":
            self.view_system_statistics()
        elif choice == "Logout":
            auth_service.logout()
    
    def manage_departments(self):
        """Manage departments"""
        self.ui.clear_screen()
        self.ui.print_header("Department Management")
        
        choices = ["View All Departments", "Create New Department", "Back"]
        choice = self.ui.get_choice("Select action:", choices)
        
        if choice == "View All Departments":
            departments = admin_service.get_all_departments()
            
            if departments:
                table_data = []
                for dept in departments:
                    table_data.append({
                        'Department ID': dept.dept_id,
                        'Department Name': dept.dept_name,
                        'Department Head': dept.dept_head or 'N/A',
                        'Created': dept.created_date.strftime("%Y-%m-%d") if dept.created_date else 'N/A'
                    })
                
                self.ui.display_table(table_data, title="All Departments")
            else:
                self.ui.print_info("No departments found")
            
            self.ui.wait_for_key()
        
        elif choice == "Create New Department":
            dept_id = self.ui.get_input("Department ID")
            dept_name = self.ui.get_input("Department Name")
            dept_head = self.ui.get_input("Department Head", required=False)
            
            if dept_id and dept_name:
                dept_data = {
                    'dept_id': dept_id,
                    'dept_name': dept_name,
                    'dept_head': dept_head
                }
                
                success, message = admin_service.create_department(dept_data)
                
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
                
                self.ui.wait_for_key()
    
    def manage_courses(self):
        """Manage courses"""
        self.ui.clear_screen()
        self.ui.print_header("Course Management")
        
        choices = ["View All Courses", "Search Courses", "Create New Course", "Back"]
        choice = self.ui.get_choice("Select action:", choices)
        
        if choice == "View All Courses":
            courses = course_service.search_courses()
            
            if courses:
                table_data = []
                for course in courses:
                    table_data.append({
                        'Course ID': course.course_id,
                        'Course Name': course.course_name,
                        'Credits': course.credits,
                        'Department': course.department,
                        'Type': course.course_type.value,
                        'Description': course.description[:50] + '...' if course.description and len(course.description) > 50 else course.description or ''
                    })
                
                self.ui.display_table(table_data, title="All Courses")
            else:
                self.ui.print_info("No courses found")
            
            self.ui.wait_for_key()
        
        elif choice == "Search Courses":
            search_term = self.ui.get_input("Enter search term")
            if search_term:
                courses = course_service.search_courses(search_term)
                
                if courses:
                    table_data = []
                    for course in courses:
                        table_data.append({
                            'Course ID': course.course_id,
                            'Course Name': course.course_name,
                            'Credits': course.credits,
                            'Department': course.department,
                            'Type': course.course_type.value
                        })
                    
                    self.ui.display_table(table_data, title=f"Search Results for '{search_term}'")
                else:
                    self.ui.print_info("No courses found matching the search term")
                
                self.ui.wait_for_key()
        
        elif choice == "Create New Course":
            course_id = self.ui.get_input("Course ID")
            course_name = self.ui.get_input("Course Name")
            credits = self.ui.get_input("Credits", float)
            
            # Get departments
            departments = admin_service.get_all_departments()
            if departments:
                dept_choices = [f"{d.dept_id} - {d.dept_name}" for d in departments]
                dept_choice = self.ui.get_choice("Department", dept_choices)
                department = dept_choice.split(" - ")[0] if dept_choice else None
            else:
                department = self.ui.get_input("Department Code", required=False)
            
            # Course type
            type_choices = [ct.value for ct in CourseType]
            course_type_str = self.ui.get_choice("Course Type", type_choices)
            
            description = self.ui.get_input("Description", required=False)
            
            if course_id and course_name and credits and course_type_str:
                course_data = {
                    'course_id': course_id,
                    'course_name': course_name,
                    'credits': credits,
                    'department': department,
                    'course_type': course_type_str,
                    'description': description
                }
                
                success, message = course_service.create_course(course_data)
                
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
                
                self.ui.wait_for_key()
    
    def create_section(self):
        """Create a new course section"""
        self.ui.clear_screen()
        self.ui.print_header("Create Course Section")
        
        course_id = self.ui.get_input("Course ID")
        
        # Get instructors
        instructors = admin_service.get_all_instructors()
        if instructors:
            instructor_choices = [f"{i.instructor_id} - {i.name}" for i in instructors]
            instructor_choice = self.ui.get_choice("Instructor", instructor_choices)
            instructor_id = instructor_choice.split(" - ")[0] if instructor_choice else None
        else:
            instructor_id = self.ui.get_input("Instructor ID", required=False)
        
        semester_choices = ["Spring", "Summer", "Fall"]
        semester = self.ui.get_choice("Semester", semester_choices)
        
        year = self.ui.get_input("Year", int)
        max_capacity = self.ui.get_input("Maximum Capacity", int)
        time_slot = self.ui.get_input("Time Slot (e.g., MWF 09:00-09:50)", required=False)
        location = self.ui.get_input("Location", required=False)
        
        if course_id and semester and year and max_capacity:
            section_data = {
                'course_id': course_id,
                'instructor_id': instructor_id,
                'semester': semester,
                'year': year,
                'max_capacity': max_capacity,
                'time_slot': time_slot,
                'location': location
            }
            
            success, message = course_service.create_section(section_data)
            
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
            
            self.ui.wait_for_key()
    
    def view_all_students(self):
        """View all students"""
        self.ui.clear_screen()
        self.ui.print_header("All Students")
        
        students = admin_service.get_all_students(limit=50)  # Limit for display
        
        if students:
            table_data = []
            for student in students:
                table_data.append({
                    'Student ID': student.student_id,
                    'Name': student.name,
                    'Gender': student.gender.value if student.gender else 'N/A',
                    'Email': student.email or 'N/A',
                    'College': student.college or 'N/A',
                    'Major': student.major or 'N/A',
                    'Enrollment Year': student.enrollment_year or 'N/A'
                })
            
            self.ui.display_table(table_data, title="All Students (First 50)")
        else:
            self.ui.print_info("No students found")
        
        self.ui.wait_for_key()
    
    def view_all_instructors(self):
        """View all instructors"""
        self.ui.clear_screen()
        self.ui.print_header("All Instructors")
        
        instructors = admin_service.get_all_instructors()
        
        if instructors:
            table_data = []
            for instructor in instructors:
                table_data.append({
                    'Instructor ID': instructor.instructor_id,
                    'Name': instructor.name,
                    'Department': instructor.department or 'N/A',
                    'Title': instructor.title or 'N/A',
                    'Email': instructor.email or 'N/A',
                    'Phone': instructor.phone or 'N/A'
                })
            
            self.ui.display_table(table_data, title="All Instructors")
        else:
            self.ui.print_info("No instructors found")
        
        self.ui.wait_for_key()
    
    def view_system_statistics(self):
        """View system statistics"""
        self.ui.clear_screen()
        self.ui.print_header("System Statistics")
        
        stats = admin_service.get_system_statistics()
        
        if stats:
            print(f"Total Students: {stats.get('total_students', 0)}")
            print(f"Total Instructors: {stats.get('total_instructors', 0)}")
            print(f"Total Departments: {stats.get('total_departments', 0)}")
            print(f"Total Courses: {stats.get('total_courses', 0)}")
            print(f"Total Enrollments: {stats.get('total_enrollments', 0)}")
        else:
            self.ui.print_info("No statistics available")
        
        self.ui.wait_for_key()

# Main UI class that coordinates all menus
class CourseRegistrationUI:
    """Main UI coordinator"""
    
    def __init__(self):
        self.ui = UIManager()
        self.login_menu = LoginMenu(self.ui)
        self.student_menu = StudentMenu(self.ui)
        self.instructor_menu = InstructorMenu(self.ui)
        self.admin_menu = AdminMenu(self.ui)
    
    def show_login_menu(self):
        """Show login menu"""
        self.login_menu.show()
    
    def show_main_menu(self):
        """Show appropriate main menu based on user role"""
        if auth_service.has_role(UserType.STUDENT):
            self.student_menu.show()
        elif auth_service.has_role(UserType.INSTRUCTOR):
            self.instructor_menu.show()
        elif auth_service.has_role(UserType.ADMIN):
            self.admin_menu.show()
        else:
            self.ui.print_error("Unknown user role")
            auth_service.logout()
    
    def run(self):
        """Run the application"""
        self.ui.show_login_menu = self.show_login_menu
        self.ui.show_main_menu = self.show_main_menu
        self.ui.run()

if __name__ == "__main__":
    app = CourseRegistrationUI()
    app.run()