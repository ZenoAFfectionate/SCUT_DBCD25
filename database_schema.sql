-- =====================================================
-- 大学课程注册与成绩管理数据库系统 - SQL DDL脚本
-- 创建日期: 2025-01-27
-- 数据库: MySQL 8.0+
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS university_course_system 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE university_course_system;

-- =====================================================
-- 1. 基础数据表
-- =====================================================

-- 院系表
CREATE TABLE Departments (
    department_id VARCHAR(10) PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    department_code VARCHAR(10) UNIQUE NOT NULL,
    college VARCHAR(100),
    head_instructor_id VARCHAR(20),
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='院系信息表';

-- 时间段表
CREATE TABLE TimeSlots (
    time_slot_id VARCHAR(20) PRIMARY KEY,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    time_description VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_time_order CHECK (start_time < end_time)
) ENGINE=InnoDB COMMENT='时间段信息表';

-- 学期表
CREATE TABLE Semesters (
    semester_id VARCHAR(20) PRIMARY KEY,
    semester_name VARCHAR(50) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    registration_start DATE NOT NULL,
    registration_end DATE NOT NULL,
    status ENUM('upcoming', 'registration_open', 'in_progress', 'completed') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_semester_dates CHECK (start_date < end_date),
    CONSTRAINT chk_registration_dates CHECK (registration_start <= registration_end),
    CONSTRAINT chk_registration_before_start CHECK (registration_end <= start_date)
) ENGINE=InnoDB COMMENT='学期信息表';

-- =====================================================
-- 2. 用户管理表
-- =====================================================

-- 用户基础信息表
CREATE TABLE Users (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT 'SHA-256 hashed password',
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    user_type ENUM('student', 'instructor', 'administrator') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL
) ENGINE=InnoDB COMMENT='用户基础信息表';

-- 学生信息表
CREATE TABLE Students (
    student_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    student_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    gender ENUM('M', 'F', 'Other'),
    birth_date DATE,
    department_id VARCHAR(10) NOT NULL,
    major VARCHAR(100),
    admission_year YEAR,
    status ENUM('active', 'graduated', 'suspended', 'withdrawn') DEFAULT 'active',
    gpa DECIMAL(3,2) DEFAULT 0.00,
    total_credits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id),
    CONSTRAINT chk_gpa CHECK (gpa >= 0.00 AND gpa <= 4.00)
) ENGINE=InnoDB COMMENT='学生信息表';

-- 教师信息表
CREATE TABLE Instructors (
    instructor_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department_id VARCHAR(10) NOT NULL,
    title VARCHAR(50),
    office_location VARCHAR(100),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
) ENGINE=InnoDB COMMENT='教师信息表';

-- 管理员信息表
CREATE TABLE Administrators (
    admin_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='管理员信息表';

-- =====================================================
-- 3. 学术管理表
-- =====================================================

-- 课程信息表
CREATE TABLE Courses (
    course_id VARCHAR(20) PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    credits INTEGER NOT NULL,
    department_id VARCHAR(10) NOT NULL,
    course_type ENUM('general_required', 'major_required', 'major_elective', 'general_elective', 'practical') NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id),
    CONSTRAINT chk_credits CHECK (credits BETWEEN 1 AND 10)
) ENGINE=InnoDB COMMENT='课程信息表';

-- 先修课程关系表
CREATE TABLE CoursePrerequisites (
    prereq_id VARCHAR(20) PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL,
    prerequisite_course_id VARCHAR(20) NOT NULL,
    minimum_grade DECIMAL(3,1) NOT NULL DEFAULT 2.0,
    grade_type ENUM('numeric', 'letter') DEFAULT 'numeric',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_course_id) REFERENCES Courses(course_id),
    UNIQUE KEY unique_prerequisite (course_id, prerequisite_course_id),
    CONSTRAINT chk_different_courses CHECK (course_id != prerequisite_course_id),
    CONSTRAINT chk_min_grade CHECK (minimum_grade >= 0.0 AND minimum_grade <= 4.0)
) ENGINE=InnoDB COMMENT='先修课程关系表';

-- 课程班次表
CREATE TABLE Sections (
    section_id VARCHAR(20) PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL,
    semester_id VARCHAR(20) NOT NULL,
    instructor_id VARCHAR(20) NOT NULL,
    section_number VARCHAR(10) NOT NULL,
    max_capacity INTEGER NOT NULL,
    current_enrollment INTEGER DEFAULT 0,
    classroom VARCHAR(50),
    time_slot_id VARCHAR(20) NOT NULL,
    status ENUM('open', 'closed', 'cancelled') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (semester_id) REFERENCES Semesters(semester_id),
    FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id),
    FOREIGN KEY (time_slot_id) REFERENCES TimeSlots(time_slot_id),
    UNIQUE KEY unique_section (course_id, semester_id, section_number),
    CONSTRAINT chk_capacity CHECK (max_capacity > 0),
    CONSTRAINT chk_enrollment_count CHECK (current_enrollment >= 0 AND current_enrollment <= max_capacity)
) ENGINE=InnoDB COMMENT='课程班次表';

-- =====================================================
-- 4. 选课与成绩表
-- =====================================================

-- 选课记录表
CREATE TABLE Enrollments (
    enrollment_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    section_id VARCHAR(20) NOT NULL,
    semester_id VARCHAR(20) NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('enrolled', 'dropped', 'completed', 'failed') DEFAULT 'enrolled',
    is_retake BOOLEAN DEFAULT FALSE,
    approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'approved',
    drop_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES Sections(section_id),
    FOREIGN KEY (semester_id) REFERENCES Semesters(semester_id),
    UNIQUE KEY unique_enrollment (student_id, section_id)
) ENGINE=InnoDB COMMENT='选课记录表';

-- 成绩记录表
CREATE TABLE Grades (
    grade_id VARCHAR(20) PRIMARY KEY,
    enrollment_id VARCHAR(20) NOT NULL,
    numeric_grade DECIMAL(4,2),
    letter_grade CHAR(2),
    grade_points DECIMAL(3,2),
    submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_by VARCHAR(20) NOT NULL,
    grade_type ENUM('midterm', 'final', 'assignment', 'quiz') DEFAULT 'final',
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES Enrollments(enrollment_id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by) REFERENCES Instructors(instructor_id),
    UNIQUE KEY unique_grade (enrollment_id, grade_type),
    CONSTRAINT chk_numeric_grade CHECK (numeric_grade IS NULL OR (numeric_grade >= 0 AND numeric_grade <= 100)),
    CONSTRAINT chk_grade_points CHECK (grade_points IS NULL OR (grade_points >= 0 AND grade_points <= 4.0))
) ENGINE=InnoDB COMMENT='成绩记录表';

-- =====================================================
-- 5. 系统管理表
-- =====================================================

-- 操作日志表
CREATE TABLE AuditLogs (
    log_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id VARCHAR(20),
    old_values JSON,
    new_values JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action_type)
) ENGINE=InnoDB COMMENT='操作日志表';

-- 系统配置表
CREATE TABLE SystemConfigs (
    config_id VARCHAR(20) PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    category VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(20),
    FOREIGN KEY (updated_by) REFERENCES Users(user_id)
) ENGINE=InnoDB COMMENT='系统配置表';

-- =====================================================
-- 6. 创建索引
-- =====================================================

-- 用户表索引
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_type ON Users(user_type);
CREATE INDEX idx_users_active ON Users(is_active);

-- 学生表索引
CREATE INDEX idx_students_number ON Students(student_number);
CREATE INDEX idx_students_department ON Students(department_id);
CREATE INDEX idx_students_status ON Students(status);
CREATE INDEX idx_students_admission_year ON Students(admission_year);

-- 教师表索引
CREATE INDEX idx_instructors_employee ON Instructors(employee_number);
CREATE INDEX idx_instructors_department ON Instructors(department_id);

-- 课程表索引
CREATE INDEX idx_courses_code ON Courses(course_code);
CREATE INDEX idx_courses_department ON Courses(department_id);
CREATE INDEX idx_courses_type ON Courses(course_type);
CREATE INDEX idx_courses_active ON Courses(is_active);

-- 课程班次索引
CREATE INDEX idx_sections_course ON Sections(course_id);
CREATE INDEX idx_sections_semester ON Sections(semester_id);
CREATE INDEX idx_sections_instructor ON Sections(instructor_id);
CREATE INDEX idx_sections_time ON Sections(time_slot_id);
CREATE INDEX idx_sections_status ON Sections(status);

-- 选课记录索引
CREATE INDEX idx_enrollments_student ON Enrollments(student_id);
CREATE INDEX idx_enrollments_section ON Enrollments(section_id);
CREATE INDEX idx_enrollments_semester ON Enrollments(semester_id);
CREATE INDEX idx_enrollments_status ON Enrollments(status);
CREATE INDEX idx_enrollments_date ON Enrollments(enrollment_date);

-- 成绩表索引
CREATE INDEX idx_grades_enrollment ON Grades(enrollment_id);
CREATE INDEX idx_grades_submitted_by ON Grades(submitted_by);
CREATE INDEX idx_grades_submitted_date ON Grades(submitted_date);
CREATE INDEX idx_grades_type ON Grades(grade_type);

-- 复合索引
CREATE INDEX idx_sections_course_semester ON Sections(course_id, semester_id);
CREATE INDEX idx_enrollments_student_semester ON Enrollments(student_id, semester_id);
CREATE INDEX idx_time_conflict ON Sections(time_slot_id, semester_id);
CREATE INDEX idx_instructor_time_conflict ON Sections(instructor_id, time_slot_id, semester_id);

-- =====================================================
-- 7. 创建触发器
-- =====================================================

-- 选课学分限制检查触发器
DELIMITER //
CREATE TRIGGER check_credit_limit_before_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW
BEGIN
    DECLARE total_credits INT DEFAULT 0;
    DECLARE max_credits INT DEFAULT 40;
    DECLARE min_credits INT DEFAULT 10;
    DECLARE current_course_credits INT DEFAULT 0;
    
    -- 获取当前学期已选课程的总学分
    SELECT COALESCE(SUM(c.credits), 0) INTO total_credits
    FROM Enrollments e
    JOIN Sections s ON e.section_id = s.section_id
    JOIN Courses c ON s.course_id = c.course_id
    WHERE e.student_id = NEW.student_id 
    AND e.semester_id = NEW.semester_id
    AND e.status IN ('enrolled', 'completed');
    
    -- 获取当前要选课程的学分
    SELECT c.credits INTO current_course_credits
    FROM Sections s
    JOIN Courses c ON s.course_id = c.course_id
    WHERE s.section_id = NEW.section_id;
    
    -- 检查是否超过最大学分限制
    IF (total_credits + current_course_credits) > max_credits THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exceeds maximum credit limit of 40';
    END IF;
END//
DELIMITER ;

-- 时间冲突检查触发器
DELIMITER //
CREATE TRIGGER check_time_conflict_before_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- 检查学生时间冲突
    SELECT COUNT(*) INTO conflict_count
    FROM Enrollments e1
    JOIN Sections s1 ON e1.section_id = s1.section_id
    JOIN Sections s2 ON s2.section_id = NEW.section_id
    WHERE e1.student_id = NEW.student_id
    AND e1.semester_id = NEW.semester_id
    AND e1.status = 'enrolled'
    AND s1.time_slot_id = s2.time_slot_id;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Time conflict with existing enrollment';
    END IF;
END//
DELIMITER ;

-- 先修课程检查触发器
DELIMITER //
CREATE TRIGGER check_prerequisites_before_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW
BEGIN
    DECLARE prereq_count INT DEFAULT 0;
    DECLARE completed_count INT DEFAULT 0;
    
    -- 获取该课程的先修课程数量
    SELECT COUNT(*) INTO prereq_count
    FROM CoursePrerequisites cp
    JOIN Sections s ON s.section_id = NEW.section_id
    WHERE cp.course_id = s.course_id;
    
    IF prereq_count > 0 THEN
        -- 检查学生已完成的先修课程数量
        SELECT COUNT(*) INTO completed_count
        FROM CoursePrerequisites cp
        JOIN Sections s ON s.section_id = NEW.section_id
        JOIN Enrollments e ON e.student_id = NEW.student_id
        JOIN Sections s2 ON e.section_id = s2.section_id
        JOIN Grades g ON g.enrollment_id = e.enrollment_id
        WHERE cp.course_id = s.course_id
        AND s2.course_id = cp.prerequisite_course_id
        AND g.grade_points >= cp.minimum_grade
        AND e.status = 'completed';
        
        IF completed_count < prereq_count THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prerequisites not satisfied';
        END IF;
    END IF;
END//
DELIMITER ;

-- 容量检查触发器
DELIMITER //
CREATE TRIGGER check_section_capacity_before_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW
BEGIN
    DECLARE current_count INT;
    DECLARE max_count INT;
    
    SELECT current_enrollment, max_capacity INTO current_count, max_count
    FROM Sections WHERE section_id = NEW.section_id;
    
    IF current_count >= max_count THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Section is full';
    END IF;
END//
DELIMITER ;

-- 更新选课人数触发器
DELIMITER //
CREATE TRIGGER update_enrollment_count_after_insert
AFTER INSERT ON Enrollments
FOR EACH ROW
BEGIN
    IF NEW.status = 'enrolled' THEN
        UPDATE Sections 
        SET current_enrollment = current_enrollment + 1
        WHERE section_id = NEW.section_id;
    END IF;
END//

CREATE TRIGGER update_enrollment_count_after_update
AFTER UPDATE ON Enrollments
FOR EACH ROW
BEGIN
    -- 如果状态从enrolled变为其他状态，减少人数
    IF OLD.status = 'enrolled' AND NEW.status != 'enrolled' THEN
        UPDATE Sections 
        SET current_enrollment = current_enrollment - 1
        WHERE section_id = NEW.section_id;
    -- 如果状态从其他状态变为enrolled，增加人数
    ELSEIF OLD.status != 'enrolled' AND NEW.status = 'enrolled' THEN
        UPDATE Sections 
        SET current_enrollment = current_enrollment + 1
        WHERE section_id = NEW.section_id;
    END IF;
END//

CREATE TRIGGER update_enrollment_count_after_delete
AFTER DELETE ON Enrollments
FOR EACH ROW
BEGIN
    IF OLD.status = 'enrolled' THEN
        UPDATE Sections 
        SET current_enrollment = current_enrollment - 1
        WHERE section_id = OLD.section_id;
    END IF;
END//
DELIMITER ;

-- 成绩录入后更新选课状态触发器
DELIMITER //
CREATE TRIGGER update_enrollment_status_after_grade
AFTER INSERT ON Grades
FOR EACH ROW
BEGIN
    DECLARE pass_threshold DECIMAL(3,2) DEFAULT 2.0;
    
    IF NEW.grade_points IS NOT NULL THEN
        IF NEW.grade_points >= pass_threshold THEN
            UPDATE Enrollments 
            SET status = 'completed'
            WHERE enrollment_id = NEW.enrollment_id;
        ELSE
            UPDATE Enrollments 
            SET status = 'failed'
            WHERE enrollment_id = NEW.enrollment_id;
        END IF;
    END IF;
END//
DELIMITER ;

-- GPA计算触发器
DELIMITER //
CREATE TRIGGER update_student_gpa_after_grade
AFTER INSERT ON Grades
FOR EACH ROW
BEGIN
    DECLARE student_gpa DECIMAL(3,2);
    DECLARE student_credits INT;
    DECLARE student_id_var VARCHAR(20);
    
    -- 获取学生ID
    SELECT e.student_id INTO student_id_var
    FROM Enrollments e
    WHERE e.enrollment_id = NEW.enrollment_id;
    
    -- 计算GPA和总学分
    SELECT 
        COALESCE(SUM(g.grade_points * c.credits) / SUM(c.credits), 0.00),
        COALESCE(SUM(c.credits), 0)
    INTO student_gpa, student_credits
    FROM Enrollments e
    JOIN Sections s ON e.section_id = s.section_id
    JOIN Courses c ON s.course_id = c.course_id
    JOIN Grades g ON e.enrollment_id = g.enrollment_id
    WHERE e.student_id = student_id_var
    AND e.status = 'completed'
    AND g.grade_points IS NOT NULL;
    
    -- 更新学生GPA和总学分
    UPDATE Students 
    SET gpa = student_gpa, total_credits = student_credits
    WHERE student_id = student_id_var;
END//
DELIMITER ;

-- =====================================================
-- 8. 创建视图
-- =====================================================

-- 学生成绩视图
CREATE VIEW student_grades_view AS
SELECT 
    s.student_id,
    s.student_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.course_code,
    c.course_name,
    c.credits,
    g.numeric_grade,
    g.letter_grade,
    g.grade_points,
    sem.semester_name,
    sem.academic_year,
    e.status AS enrollment_status
FROM Students s
JOIN Enrollments e ON s.student_id = e.student_id
JOIN Sections sec ON e.section_id = sec.section_id
JOIN Courses c ON sec.course_id = c.course_id
LEFT JOIN Grades g ON e.enrollment_id = g.enrollment_id
JOIN Semesters sem ON e.semester_id = sem.semester_id
WHERE s.status = 'active';

-- 教师课程视图
CREATE VIEW instructor_sections_view AS
SELECT 
    i.instructor_id,
    i.employee_number,
    CONCAT(i.first_name, ' ', i.last_name) AS instructor_name,
    s.section_id,
    c.course_code,
    c.course_name,
    s.section_number,
    s.max_capacity,
    s.current_enrollment,
    s.classroom,
    ts.day_of_week,
    ts.start_time,
    ts.end_time,
    sem.semester_name,
    sem.academic_year
FROM Instructors i
JOIN Sections s ON i.instructor_id = s.instructor_id
JOIN Courses c ON s.course_id = c.course_id
JOIN TimeSlots ts ON s.time_slot_id = ts.time_slot_id
JOIN Semesters sem ON s.semester_id = sem.semester_id;

-- 课程统计视图
CREATE VIEW course_statistics_view AS
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    c.credits,
    d.department_name,
    COUNT(DISTINCT s.section_id) AS total_sections,
    COUNT(DISTINCT e.student_id) AS total_enrollments,
    AVG(g.grade_points) AS average_gpa,
    COUNT(CASE WHEN g.grade_points >= 2.0 THEN 1 END) * 100.0 / COUNT(g.grade_points) AS pass_rate
FROM Courses c
LEFT JOIN Sections s ON c.course_id = s.course_id
LEFT JOIN Enrollments e ON s.section_id = e.section_id
LEFT JOIN Grades g ON e.enrollment_id = g.enrollment_id
JOIN Departments d ON c.department_id = d.department_id
GROUP BY c.course_id, c.course_code, c.course_name, c.credits, d.department_name;

-- =====================================================
-- 9. 插入默认数据
-- =====================================================

-- 插入系统配置
INSERT INTO SystemConfigs (config_id, config_key, config_value, description, category) VALUES
('CFG001', 'max_credits_per_semester', '40', 'Maximum credits a student can take per semester', 'academic'),
('CFG002', 'min_credits_per_semester', '10', 'Minimum credits a student must take per semester', 'academic'),
('CFG003', 'pass_grade_threshold', '2.0', 'Minimum grade points required to pass a course', 'grading'),
('CFG004', 'registration_deadline_days', '7', 'Days before semester start when registration closes', 'registration'),
('CFG005', 'drop_deadline_days', '14', 'Days after semester start when students can drop courses', 'registration');

-- 插入默认时间段
INSERT INTO TimeSlots (time_slot_id, day_of_week, start_time, end_time, time_description) VALUES
('TS001', 'Monday', '08:00:00', '09:30:00', 'Monday 8:00-9:30 AM'),
('TS002', 'Monday', '10:00:00', '11:30:00', 'Monday 10:00-11:30 AM'),
('TS003', 'Monday', '13:00:00', '14:30:00', 'Monday 1:00-2:30 PM'),
('TS004', 'Monday', '15:00:00', '16:30:00', 'Monday 3:00-4:30 PM'),
('TS005', 'Tuesday', '08:00:00', '09:30:00', 'Tuesday 8:00-9:30 AM'),
('TS006', 'Tuesday', '10:00:00', '11:30:00', 'Tuesday 10:00-11:30 AM'),
('TS007', 'Wednesday', '08:00:00', '09:30:00', 'Wednesday 8:00-9:30 AM'),
('TS008', 'Wednesday', '10:00:00', '11:30:00', 'Wednesday 10:00-11:30 AM'),
('TS009', 'Thursday', '08:00:00', '09:30:00', 'Thursday 8:00-9:30 AM'),
('TS010', 'Thursday', '10:00:00', '11:30:00', 'Thursday 10:00-11:30 AM'),
('TS011', 'Friday', '08:00:00', '09:30:00', 'Friday 8:00-9:30 AM'),
('TS012', 'Friday', '10:00:00', '11:30:00', 'Friday 10:00-11:30 AM');

-- 插入示例院系
INSERT INTO Departments (department_id, department_name, department_code, college) VALUES
('DEPT001', 'Computer Science', 'CS', 'College of Engineering'),
('DEPT002', 'Mathematics', 'MATH', 'College of Sciences'),
('DEPT003', 'Physics', 'PHYS', 'College of Sciences'),
('DEPT004', 'English Literature', 'ENG', 'College of Liberal Arts'),
('DEPT005', 'Business Administration', 'BUS', 'College of Business');

-- 插入示例学期
INSERT INTO Semesters (semester_id, semester_name, academic_year, start_date, end_date, registration_start, registration_end, status) VALUES
('SEM2025S', 'Spring 2025', '2024-2025', '2025-02-01', '2025-06-15', '2025-01-15', '2025-01-31', 'registration_open'),
('SEM2025F', 'Fall 2025', '2025-2026', '2025-09-01', '2026-01-15', '2025-08-15', '2025-08-31', 'upcoming');

-- =====================================================
-- 10. 创建用户和权限
-- =====================================================

-- 创建角色
CREATE ROLE IF NOT EXISTS 'student_role';
CREATE ROLE IF NOT EXISTS 'instructor_role';
CREATE ROLE IF NOT EXISTS 'admin_role';

-- 学生权限
GRANT SELECT ON Students TO 'student_role';
GRANT SELECT ON Courses TO 'student_role';
GRANT SELECT ON Sections TO 'student_role';
GRANT SELECT ON Enrollments TO 'student_role';
GRANT SELECT ON Grades TO 'student_role';
GRANT SELECT ON student_grades_view TO 'student_role';
GRANT INSERT, UPDATE ON Enrollments TO 'student_role';

-- 教师权限
GRANT SELECT ON Instructors TO 'instructor_role';
GRANT SELECT ON Courses TO 'instructor_role';
GRANT SELECT ON Sections TO 'instructor_role';
GRANT SELECT ON Enrollments TO 'instructor_role';
GRANT SELECT, INSERT, UPDATE ON Grades TO 'instructor_role';
GRANT SELECT ON instructor_sections_view TO 'instructor_role';

-- 管理员权限（根据需要限制）
GRANT SELECT, INSERT, UPDATE, DELETE ON Departments TO 'admin_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON Courses TO 'admin_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON Sections TO 'admin_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON Semesters TO 'admin_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON TimeSlots TO 'admin_role';
GRANT SELECT ON AuditLogs TO 'admin_role';
GRANT SELECT, INSERT, UPDATE ON SystemConfigs TO 'admin_role';

-- =====================================================
-- 11. 存储过程
-- =====================================================

-- 学生选课存储过程
DELIMITER //
CREATE PROCEDURE EnrollStudent(
    IN p_student_id VARCHAR(20),
    IN p_section_id VARCHAR(20),
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_error_msg VARCHAR(255) DEFAULT '';
    DECLARE v_enrollment_id VARCHAR(20);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 v_error_msg = MESSAGE_TEXT;
        SET p_result = CONCAT('Error: ', v_error_msg);
    END;
    
    START TRANSACTION;
    
    -- 生成选课记录ID
    SET v_enrollment_id = CONCAT('ENR', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(CONNECTION_ID(), 6, '0'));
    
    -- 获取学期ID
    SET @semester_id = (SELECT semester_id FROM Sections WHERE section_id = p_section_id);
    
    -- 插入选课记录
    INSERT INTO Enrollments (enrollment_id, student_id, section_id, semester_id, status)
    VALUES (v_enrollment_id, p_student_id, p_section_id, @semester_id, 'enrolled');
    
    COMMIT;
    SET p_result = 'Success: Student enrolled successfully';
END//
DELIMITER ;

-- 计算学生GPA存储过程
DELIMITER //
CREATE PROCEDURE CalculateStudentGPA(
    IN p_student_id VARCHAR(20),
    IN p_semester_id VARCHAR(20),
    OUT p_gpa DECIMAL(3,2)
)
BEGIN
    SELECT 
        COALESCE(SUM(g.grade_points * c.credits) / SUM(c.credits), 0.00)
    INTO p_gpa
    FROM Enrollments e
    JOIN Sections s ON e.section_id = s.section_id
    JOIN Courses c ON s.course_id = c.course_id
    JOIN Grades g ON e.enrollment_id = g.enrollment_id
    WHERE e.student_id = p_student_id
    AND (p_semester_id IS NULL OR e.semester_id = p_semester_id)
    AND e.status = 'completed'
    AND g.grade_points IS NOT NULL;
END//
DELIMITER ;

-- =====================================================
-- 12. 函数
-- =====================================================

-- 检查时间冲突函数
DELIMITER //
CREATE FUNCTION CheckTimeConflict(
    p_student_id VARCHAR(20),
    p_section_id VARCHAR(20),
    p_semester_id VARCHAR(20)
) RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    SELECT COUNT(*) INTO conflict_count
    FROM Enrollments e1
    JOIN Sections s1 ON e1.section_id = s1.section_id
    JOIN Sections s2 ON s2.section_id = p_section_id
    WHERE e1.student_id = p_student_id
    AND e1.semester_id = p_semester_id
    AND e1.status = 'enrolled'
    AND s1.time_slot_id = s2.time_slot_id;
    
    RETURN conflict_count > 0;
END//
DELIMITER ;

-- 转换数字成绩为字母等级函数
DELIMITER //
CREATE FUNCTION ConvertGradeToLetter(p_numeric_grade DECIMAL(4,2))
RETURNS CHAR(2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE letter_grade CHAR(2);
    
    CASE
        WHEN p_numeric_grade >= 97 THEN SET letter_grade = 'A+';
        WHEN p_numeric_grade >= 93 THEN SET letter_grade = 'A';
        WHEN p_numeric_grade >= 90 THEN SET letter_grade = 'A-';
        WHEN p_numeric_grade >= 87 THEN SET letter_grade = 'B+';
        WHEN p_numeric_grade >= 83 THEN SET letter_grade = 'B';
        WHEN p_numeric_grade >= 80 THEN SET letter_grade = 'B-';
        WHEN p_numeric_grade >= 77 THEN SET letter_grade = 'C+';
        WHEN p_numeric_grade >= 73 THEN SET letter_grade = 'C';
        WHEN p_numeric_grade >= 70 THEN SET letter_grade = 'C-';
        WHEN p_numeric_grade >= 67 THEN SET letter_grade = 'D+';
        WHEN p_numeric_grade >= 65 THEN SET letter_grade = 'D';
        ELSE SET letter_grade = 'F';
    END CASE;
    
    RETURN letter_grade;
END//
DELIMITER ;

-- =====================================================
-- 脚本执行完成
-- =====================================================

SELECT 'Database schema created successfully!' AS Status;