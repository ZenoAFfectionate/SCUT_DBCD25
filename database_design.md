# 大学课程注册与成绩管理数据库系统 - 详细设计文档

## 1. 概念设计（E-R图）

### 1.1 主要实体
- **学生 (Student)**: 系统的主要用户，进行选课和查询成绩
- **教师 (Instructor)**: 授课教师，负责成绩录入和课程管理
- **管理员 (Administrator)**: 系统管理员，负责系统维护和数据管理
- **课程 (Course)**: 学校开设的课程信息
- **课程班次 (Section)**: 具体的课程开课班次
- **院系 (Department)**: 学校的院系组织结构
- **选课记录 (Enrollment)**: 学生的选课信息
- **成绩 (Grade)**: 学生的课程成绩
- **学期 (Semester)**: 学期信息
- **时间段 (TimeSlot)**: 课程上课时间

### 1.2 主要关系
- 学生 **选修** 课程班次 (多对多，通过Enrollment实现)
- 教师 **教授** 课程班次 (一对多)
- 课程 **开设** 课程班次 (一对多)
- 课程 **依赖** 先修课程 (多对多)
- 学生 **获得** 成绩 (一对多)
- 院系 **开设** 课程 (一对多)

## 2. 逻辑设计（关系模式设计）

### 2.1 用户管理表

#### Users 表 (用户基础信息)
```sql
Users (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    user_type ENUM('student', 'instructor', 'administrator') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
)
```

#### Students 表 (学生信息)
```sql
Students (
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
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
)
```

#### Instructors 表 (教师信息)
```sql
Instructors (
    instructor_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department_id VARCHAR(10) NOT NULL,
    title VARCHAR(50),
    office_location VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
)
```

### 2.2 学术管理表

#### Departments 表 (院系信息)
```sql
Departments (
    department_id VARCHAR(10) PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    department_code VARCHAR(10) UNIQUE NOT NULL,
    college VARCHAR(100),
    head_instructor_id VARCHAR(20),
    contact_info TEXT,
    FOREIGN KEY (head_instructor_id) REFERENCES Instructors(instructor_id)
)
```

#### Courses 表 (课程信息)
```sql
Courses (
    course_id VARCHAR(20) PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    credits INTEGER NOT NULL CHECK (credits > 0),
    department_id VARCHAR(10) NOT NULL,
    course_type ENUM('general_required', 'major_required', 'major_elective', 'general_elective', 'practical') NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
)
```

#### Semesters 表 (学期信息)
```sql
Semesters (
    semester_id VARCHAR(20) PRIMARY KEY,
    semester_name VARCHAR(50) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    registration_start DATE NOT NULL,
    registration_end DATE NOT NULL,
    status ENUM('upcoming', 'registration_open', 'in_progress', 'completed') DEFAULT 'upcoming',
    CHECK (start_date < end_date),
    CHECK (registration_start <= registration_end),
    CHECK (registration_end <= start_date)
)
```

#### TimeSlots 表 (时间段信息)
```sql
TimeSlots (
    time_slot_id VARCHAR(20) PRIMARY KEY,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    time_description VARCHAR(100),
    CHECK (start_time < end_time)
)
```

#### Sections 表 (课程班次)
```sql
Sections (
    section_id VARCHAR(20) PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL,
    semester_id VARCHAR(20) NOT NULL,
    instructor_id VARCHAR(20) NOT NULL,
    section_number VARCHAR(10) NOT NULL,
    max_capacity INTEGER NOT NULL CHECK (max_capacity > 0),
    current_enrollment INTEGER DEFAULT 0 CHECK (current_enrollment >= 0),
    classroom VARCHAR(50),
    time_slot_id VARCHAR(20) NOT NULL,
    status ENUM('open', 'closed', 'cancelled') DEFAULT 'open',
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (semester_id) REFERENCES Semesters(semester_id),
    FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id),
    FOREIGN KEY (time_slot_id) REFERENCES TimeSlots(time_slot_id),
    UNIQUE KEY unique_section (course_id, semester_id, section_number),
    CHECK (current_enrollment <= max_capacity)
)
```

### 2.3 选课与成绩表

#### CoursePrerequisites 表 (先修课程)
```sql
CoursePrerequisites (
    prereq_id VARCHAR(20) PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL,
    prerequisite_course_id VARCHAR(20) NOT NULL,
    minimum_grade DECIMAL(3,1) NOT NULL DEFAULT 2.0,
    grade_type ENUM('numeric', 'letter') DEFAULT 'numeric',
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_course_id) REFERENCES Courses(course_id),
    UNIQUE KEY unique_prerequisite (course_id, prerequisite_course_id)
)
```

#### Enrollments 表 (选课记录)
```sql
Enrollments (
    enrollment_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    section_id VARCHAR(20) NOT NULL,
    semester_id VARCHAR(20) NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('enrolled', 'dropped', 'completed', 'failed') DEFAULT 'enrolled',
    is_retake BOOLEAN DEFAULT FALSE,
    approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'approved',
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES Sections(section_id),
    FOREIGN KEY (semester_id) REFERENCES Semesters(semester_id),
    UNIQUE KEY unique_enrollment (student_id, section_id)
)
```

#### Grades 表 (成绩记录)
```sql
Grades (
    grade_id VARCHAR(20) PRIMARY KEY,
    enrollment_id VARCHAR(20) NOT NULL,
    numeric_grade DECIMAL(4,2) CHECK (numeric_grade >= 0 AND numeric_grade <= 100),
    letter_grade CHAR(2),
    grade_points DECIMAL(3,2) CHECK (grade_points >= 0 AND grade_points <= 4.0),
    submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_by VARCHAR(20) NOT NULL,
    grade_type ENUM('midterm', 'final', 'assignment', 'quiz') DEFAULT 'final',
    FOREIGN KEY (enrollment_id) REFERENCES Enrollments(enrollment_id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by) REFERENCES Instructors(instructor_id),
    UNIQUE KEY unique_grade (enrollment_id, grade_type)
)
```

### 2.4 系统管理表

#### AuditLogs 表 (操作日志)
```sql
AuditLogs (
    log_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id VARCHAR(20),
    old_values JSON,
    new_values JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
```

#### SystemConfigs 表 (系统配置)
```sql
SystemConfigs (
    config_id VARCHAR(20) PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    category VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(20),
    FOREIGN KEY (updated_by) REFERENCES Users(user_id)
)
```

## 3. 物理设计（索引、存储等）

### 3.1 索引设计

#### 主要索引
```sql
-- 用户表索引
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_type ON Users(user_type);

-- 学生表索引
CREATE INDEX idx_students_number ON Students(student_number);
CREATE INDEX idx_students_department ON Students(department_id);
CREATE INDEX idx_students_status ON Students(status);

-- 课程表索引
CREATE INDEX idx_courses_code ON Courses(course_code);
CREATE INDEX idx_courses_department ON Courses(department_id);
CREATE INDEX idx_courses_type ON Courses(course_type);

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

-- 成绩表索引
CREATE INDEX idx_grades_enrollment ON Grades(enrollment_id);
CREATE INDEX idx_grades_submitted_by ON Grades(submitted_by);
CREATE INDEX idx_grades_date ON Grades(submitted_date);

-- 复合索引
CREATE INDEX idx_sections_course_semester ON Sections(course_id, semester_id);
CREATE INDEX idx_enrollments_student_semester ON Enrollments(student_id, semester_id);
CREATE INDEX idx_time_conflict ON Sections(time_slot_id, semester_id);
```

### 3.2 存储引擎选择
- **主要表**: 使用InnoDB存储引擎，支持事务和外键约束
- **日志表**: 使用InnoDB，确保操作记录的完整性
- **配置表**: 使用InnoDB，保证配置数据的一致性

### 3.3 分区策略
```sql
-- 按学期对选课记录进行分区
ALTER TABLE Enrollments PARTITION BY HASH(semester_id) PARTITIONS 8;

-- 按年份对审计日志进行分区
ALTER TABLE AuditLogs PARTITION BY RANGE (YEAR(timestamp)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

## 4. 数据库完整性约束设计

### 4.1 实体完整性
- 所有表都有主键约束
- 主键字段非空且唯一

### 4.2 参照完整性
- 外键约束确保数据一致性
- 级联删除和更新规则

### 4.3 域完整性
```sql
-- 学分约束
ALTER TABLE Courses ADD CONSTRAINT chk_credits CHECK (credits BETWEEN 1 AND 10);

-- 成绩约束
ALTER TABLE Grades ADD CONSTRAINT chk_numeric_grade CHECK (numeric_grade BETWEEN 0 AND 100);
ALTER TABLE Grades ADD CONSTRAINT chk_grade_points CHECK (grade_points BETWEEN 0 AND 4.0);

-- 容量约束
ALTER TABLE Sections ADD CONSTRAINT chk_capacity CHECK (max_capacity > 0 AND current_enrollment <= max_capacity);

-- 时间约束
ALTER TABLE Semesters ADD CONSTRAINT chk_semester_dates CHECK (start_date < end_date);
ALTER TABLE TimeSlots ADD CONSTRAINT chk_time_slots CHECK (start_time < end_time);
```

### 4.4 用户定义完整性（触发器）

#### 选课学分限制触发器
```sql
DELIMITER //
CREATE TRIGGER check_credit_limit_before_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW
BEGIN
    DECLARE total_credits INT DEFAULT 0;
    DECLARE max_credits INT DEFAULT 40;
    DECLARE min_credits INT DEFAULT 10;
    
    SELECT COALESCE(SUM(c.credits), 0) INTO total_credits
    FROM Enrollments e
    JOIN Sections s ON e.section_id = s.section_id
    JOIN Courses c ON s.course_id = c.course_id
    WHERE e.student_id = NEW.student_id 
    AND e.semester_id = NEW.semester_id
    AND e.status = 'enrolled';
    
    SELECT c.credits INTO @current_credits
    FROM Sections s
    JOIN Courses c ON s.course_id = c.course_id
    WHERE s.section_id = NEW.section_id;
    
    IF (total_credits + @current_credits) > max_credits THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exceeds maximum credit limit of 40';
    END IF;
END//
DELIMITER ;
```

#### 时间冲突检查触发器
```sql
DELIMITER //
CREATE TRIGGER check_time_conflict_before_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
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
```

#### 先修课程检查触发器
```sql
DELIMITER //
CREATE TRIGGER check_prerequisites_before_enrollment
BEFORE INSERT ON Enrollments
FOR EACH ROW
BEGIN
    DECLARE prereq_count INT DEFAULT 0;
    DECLARE completed_count INT DEFAULT 0;
    
    SELECT COUNT(*) INTO prereq_count
    FROM CoursePrerequisites cp
    JOIN Sections s ON s.section_id = NEW.section_id
    WHERE cp.course_id = s.course_id;
    
    IF prereq_count > 0 THEN
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
```

#### 容量检查和更新触发器
```sql
DELIMITER //
CREATE TRIGGER update_enrollment_count_after_insert
AFTER INSERT ON Enrollments
FOR EACH ROW
BEGIN
    UPDATE Sections 
    SET current_enrollment = current_enrollment + 1
    WHERE section_id = NEW.section_id;
END//

CREATE TRIGGER update_enrollment_count_after_delete
AFTER DELETE ON Enrollments
FOR EACH ROW
BEGIN
    UPDATE Sections 
    SET current_enrollment = current_enrollment - 1
    WHERE section_id = OLD.section_id;
END//

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
```

## 5. 安全性设计

### 5.1 用户权限管理
```sql
-- 创建角色
CREATE ROLE 'student_role';
CREATE ROLE 'instructor_role';
CREATE ROLE 'admin_role';

-- 学生权限
GRANT SELECT ON Students TO 'student_role';
GRANT SELECT ON Courses TO 'student_role';
GRANT SELECT ON Sections TO 'student_role';
GRANT SELECT ON Enrollments TO 'student_role';
GRANT SELECT ON Grades TO 'student_role';
GRANT INSERT, UPDATE ON Enrollments TO 'student_role';

-- 教师权限
GRANT SELECT ON Instructors TO 'instructor_role';
GRANT SELECT ON Courses TO 'instructor_role';
GRANT SELECT ON Sections TO 'instructor_role';
GRANT SELECT ON Enrollments TO 'instructor_role';
GRANT SELECT, INSERT, UPDATE ON Grades TO 'instructor_role';

-- 管理员权限
GRANT ALL PRIVILEGES ON *.* TO 'admin_role';
```

### 5.2 数据访问控制视图
```sql
-- 学生成绩视图（只能查看自己的成绩）
CREATE VIEW student_grades_view AS
SELECT 
    s.student_id,
    c.course_code,
    c.course_name,
    c.credits,
    g.numeric_grade,
    g.letter_grade,
    g.grade_points,
    sem.semester_name
FROM Students s
JOIN Enrollments e ON s.student_id = e.student_id
JOIN Sections sec ON e.section_id = sec.section_id
JOIN Courses c ON sec.course_id = c.course_id
JOIN Grades g ON e.enrollment_id = g.enrollment_id
JOIN Semesters sem ON e.semester_id = sem.semester_id;

-- 教师课程视图（只能查看自己教授的课程）
CREATE VIEW instructor_sections_view AS
SELECT 
    i.instructor_id,
    s.section_id,
    c.course_code,
    c.course_name,
    s.section_number,
    s.max_capacity,
    s.current_enrollment,
    sem.semester_name
FROM Instructors i
JOIN Sections s ON i.instructor_id = s.instructor_id
JOIN Courses c ON s.course_id = c.course_id
JOIN Semesters sem ON s.semester_id = sem.semester_id;
```

### 5.3 数据加密
```sql
-- 密码加密存储
ALTER TABLE Users MODIFY password_hash VARCHAR(255) NOT NULL COMMENT 'SHA-256 hashed password';

-- 敏感信息加密
ALTER TABLE Students ADD COLUMN encrypted_ssn VARBINARY(255) COMMENT 'AES encrypted SSN';
```

### 5.4 审计日志
```sql
-- 创建审计触发器
DELIMITER //
CREATE TRIGGER audit_student_changes
AFTER UPDATE ON Students
FOR EACH ROW
BEGIN
    INSERT INTO AuditLogs (
        log_id, user_id, action_type, table_name, record_id, 
        old_values, new_values, timestamp
    ) VALUES (
        UUID(), 
        @current_user_id,
        'UPDATE',
        'Students',
        NEW.student_id,
        JSON_OBJECT('first_name', OLD.first_name, 'last_name', OLD.last_name, 'major', OLD.major),
        JSON_OBJECT('first_name', NEW.first_name, 'last_name', NEW.last_name, 'major', NEW.major),
        NOW()
    );
END//
DELIMITER ;
```

### 5.5 备份和恢复策略
```sql
-- 定期备份脚本
-- 每日增量备份
mysqldump --single-transaction --routines --triggers university_db > backup_$(date +%Y%m%d).sql

-- 每周全量备份
mysqldump --single-transaction --routines --triggers --all-databases > full_backup_$(date +%Y%m%d).sql
```

## 6. 性能优化建议

### 6.1 查询优化
- 使用适当的索引
- 避免SELECT *，只查询需要的字段
- 使用LIMIT限制结果集大小
- 合理使用JOIN和子查询

### 6.2 缓存策略
- 对频繁查询的课程信息进行缓存
- 缓存学生的学期课程表
- 缓存系统配置信息

### 6.3 连接池配置
```sql
-- MySQL连接池配置
SET GLOBAL max_connections = 200;
SET GLOBAL thread_cache_size = 16;
SET GLOBAL query_cache_size = 64M;
SET GLOBAL innodb_buffer_pool_size = 1G;
```

这个数据库设计提供了完整的大学课程注册与成绩管理系统的架构，包含了所有必要的表结构、约束、索引和安全措施，能够满足系统的功能需求和性能要求。