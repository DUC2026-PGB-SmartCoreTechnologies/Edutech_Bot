-- ========================================================
-- 1. តារាង DEPARTMENTS (ដេប៉ាតឺម៉ង់/ផ្នែក)
-- ========================================================
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    department_name VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- 2. តារាង MAJORS (ជំនាញសិក្សា នៅក្នុងដេប៉ាតឺម៉ង់នីមួយៗ)
-- ========================================================
CREATE TABLE IF NOT EXISTS majors (
    id SERIAL PRIMARY KEY,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    major_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_major_per_dept UNIQUE (department_id, major_name)
);

-- ========================================================
-- 3. គណនីធំ USERS (សម្រាប់ទុកគណនីឆាតរបស់អ្នកប្រើប្រាស់ទាំងអស់)
-- ========================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    full_name VARCHAR(255) DEFAULT NULL,
    phone_number VARCHAR(50) DEFAULT NULL,
    student_id VARCHAR(50) DEFAULT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'PARENT', -- PRINCIPAL, TEACHER, PARENT
    status VARCHAR(50) DEFAULT 'NEW',           -- NEW, REG_MODE, LEAVE_MODE, APPROVED
    language VARCHAR(10) DEFAULT 'km',          -- km, en
    app_installed INT DEFAULT 0,                -- 0 = មិនទាន់ដំឡើង, 1 = បានដំឡើង
    last_login_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- 4. ព័ត៌មានលម្អិតរបស់គ្រូ TEACHERS
-- ========================================================
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id VARCHAR(50) PRIMARY KEY,
    telegram_id BIGINT UNIQUE REFERENCES users(telegram_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('M', 'F')),
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    major_id INT REFERENCES majors(id) ON DELETE SET NULL,
    is_homeroom BOOLEAN DEFAULT FALSE,
    attendance_status VARCHAR(50) DEFAULT 'PRESENT',
    ALTER TABLE public.teachers 
    ADD COLUMN subject text;
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- 5. បញ្ជីឈ្មោះសិស្សផ្លូវការ STUDENTS
-- ========================================================
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    parent_telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('M', 'F')),
    class_level VARCHAR(50) NOT NULL,       -- Class-PG_B, G12
    group_chat_id VARCHAR(100) DEFAULT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- 6. តារាង ADMINS (សម្រាប់ទុកលេខ ID របស់ Admin)
-- ========================================================
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'ADMIN', -- SUPER_ADMIN, ADMIN
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- 7. តារាង SCHEDULES (កាលវិភាគសិក្សា)
-- ========================================================
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    class_level VARCHAR(50) NOT NULL,
    subject_name VARCHAR(255) NOT NULL,
    teacher_id VARCHAR(50) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
    study_day VARCHAR(50) NOT NULL,         -- Monday, Tuesday, ...
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_class_schedule UNIQUE (class_level, study_day, start_time)
);


-- ========================================================
-- 8. តារាង ATTENDANCE (ប្រព័ន្ធវត្តមាន និងច្បាប់អនឡាញ)
-- ========================================================
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) REFERENCES students(student_id) ON DELETE CASCADE,
    class_level VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,            -- PRESENT, LATE, EXCUSED, UNEXCUSED
    roll_call_date DATE DEFAULT CURRENT_DATE,
    leave_requested_online BOOLEAN DEFAULT FALSE, 
    leave_approval_status VARCHAR(50) DEFAULT 'NONE', -- NONE, PENDING, APPROVED, REJECTED
    reason TEXT DEFAULT NULL,               
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_student_attendance_date UNIQUE (student_id, roll_call_date)
);

-- ========================================================
-- 9. តារាង HOMEWORK (ប្រព័ន្ធគ្រប់គ្រងការដាក់កិច្ចការផ្ទះ)
-- ========================================================
CREATE TABLE IF NOT EXISTS homework (
    id SERIAL PRIMARY KEY,
    class_level VARCHAR(50) NOT NULL,
    subject_name VARCHAR(255) NOT NULL,
    teacher_id VARCHAR(50) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    attachment_file VARCHAR(255) DEFAULT NULL,   
    attachment_type VARCHAR(50) DEFAULT NULL,   
    max_points INT DEFAULT 100,
    deadline_at TIMESTAMP WITH TIME ZONE NOT NULL,
    alert_sent INT DEFAULT 0,   
                    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- 10. តារាង STUDENT_SUBMISSIONS (ការប្រគល់កិច្ចការផ្ទះ)
-- ========================================================
CREATE TABLE IF NOT EXISTS student_submissions (
    id SERIAL PRIMARY KEY,
    homework_id INT REFERENCES homework(id) ON DELETE CASCADE,
    student_id VARCHAR(50) REFERENCES students(student_id) ON DELETE CASCADE,
    class_level VARCHAR(50) NOT NULL,
    submitted_file VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'SUBMITTED',     -- SUBMITTED, GRADED, OVERDUE
    grade_score NUMERIC(5,2) DEFAULT NULL,      
    teacher_feedback TEXT DEFAULT NULL,         
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_student_submission UNIQUE (homework_id, student_id)
);

-- ========================================================
-- 11. តារាង SCHOOL_NOTICES (សេចក្តីប្រកាសព័ត៌មានផ្លូវការ)
-- ========================================================
CREATE TABLE IF NOT EXISTS school_notices (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    notice_type VARCHAR(50) DEFAULT 'GENERAL', 
    created_by_telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11.1 តារាងរងតាមដានការអាន និងការចុះហត្ថលេខាឌីជីថល (Notice Engagement)
CREATE TABLE IF NOT EXISTS notice_engagements (
    id SERIAL PRIMARY KEY,
    notice_id INT REFERENCES school_notices(id) ON DELETE CASCADE,
    parent_telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    is_seen BOOLEAN DEFAULT FALSE,              
    seen_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    is_acknowledged BOOLEAN DEFAULT FALSE,      -- ប៊ូតុង "Acknowledge / Approve"
    acknowledged_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    CONSTRAINT unique_parent_notice_engagement UNIQUE (notice_id, parent_telegram_id)
);


-- ========================================================
-- 12. តារាង DISCIPLINE_RECORDS (ការគ្រប់គ្រងវិន័យសិស្ស)
-- ========================================================
CREATE TABLE IF NOT EXISTS discipline_records (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) REFERENCES students(student_id) ON DELETE CASCADE,
    incident_description TEXT NOT NULL,         
    corrective_action TEXT NOT NULL,            
    reported_by_teacher_id VARCHAR(50) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
    incident_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- 13. តារាង HOLIDAYS (ថ្ងៃឈប់សម្រាក)
-- ========================================================
CREATE TABLE IF NOT EXISTS holidays (
    id SERIAL PRIMARY KEY,
    event_name_km VARCHAR(255) NOT NULL,
    event_name_en VARCHAR(255) NOT NULL,
    holiday_date DATE NOT NULL,
    holiday_image VARCHAR(255) DEFAULT NULL,
    announcement_sent INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ១. ភ្ជាប់តារាង majors ទៅកាន់ departments
ALTER TABLE public.majors 
DROP CONSTRAINT IF EXISTS fk_majors_department,
ADD CONSTRAINT fk_majors_department 
FOREIGN KEY (department_id) REFERENCES public.departments(id) ON DELETE CASCADE;

-- ២. ភ្ជាប់តារាង teachers ទៅកាន់ departments និង majors
ALTER TABLE public.teachers 
DROP CONSTRAINT IF EXISTS fk_teachers_department,
DROP CONSTRAINT IF EXISTS fk_teachers_major,
ADD CONSTRAINT fk_teachers_department FOREIGN KEY (department_id) REFERENCES public.departments(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_teachers_major FOREIGN KEY (major_id) REFERENCES public.majors(id) ON DELETE SET NULL;

-- ៣. ភ្ជាប់តារាង schedules ទៅកាន់ teachers
ALTER TABLE public.schedules 
DROP CONSTRAINT IF EXISTS fk_schedules_teacher,
ADD CONSTRAINT fk_schedules_teacher 
FOREIGN KEY (teacher_id) REFERENCES public.teachers(teacher_id) ON DELETE SET NULL;