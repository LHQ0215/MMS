-- =============================================
-- 基于AI问诊的医疗管理系统 - 数据库初始化脚本
-- MySQL 8.0, 严格第三范式(3NF)
-- =============================================

CREATE DATABASE IF NOT EXISTS medical_system
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE medical_system;

-- 1. 用户表
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  real_name VARCHAR(50) NOT NULL,
  role ENUM('admin', 'doctor', 'patient') NOT NULL DEFAULT 'patient',
  phone VARCHAR(20),
  email VARCHAR(100),
  avatar_url VARCHAR(255),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  last_login DATETIME,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_username (username),
  INDEX idx_role (role),
  INDEX idx_phone (phone)
) ENGINE=InnoDB;

-- 2. 科室表
CREATE TABLE departments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  location VARCHAR(200),
  parent_id INT DEFAULT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES departments(id) ON DELETE SET NULL,
  INDEX idx_parent (parent_id)
) ENGINE=InnoDB;

-- 3. 医生表
CREATE TABLE doctors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  title VARCHAR(50) NOT NULL COMMENT '职称',
  specialization VARCHAR(200) COMMENT '专业特长',
  department_id INT NOT NULL,
  license_number VARCHAR(50) NOT NULL UNIQUE COMMENT '执业证号',
  consultation_fee DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '挂号费',
  max_daily_patients INT NOT NULL DEFAULT 30,
  introduction TEXT,
  is_approved TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (department_id) REFERENCES departments(id),
  INDEX idx_department (department_id),
  INDEX idx_approved (is_approved)
) ENGINE=InnoDB;

-- 4. 患者表
CREATE TABLE patients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  gender ENUM('male', 'female', 'other') NOT NULL,
  birth_date DATE,
  id_card VARCHAR(18) UNIQUE COMMENT '身份证号',
  address VARCHAR(255),
  blood_type VARCHAR(5),
  height DECIMAL(5,2),
  weight DECIMAL(5,2),
  allergies TEXT COMMENT '过敏史',
  medical_history TEXT COMMENT '既往病史',
  emergency_contact VARCHAR(50),
  emergency_phone VARCHAR(20),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_id_card (id_card)
) ENGINE=InnoDB;

-- 5. 预约挂号表
CREATE TABLE appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  doctor_id INT NOT NULL,
  department_id INT NOT NULL,
  appointment_date DATE NOT NULL,
  time_slot ENUM('morning', 'afternoon', 'evening') NOT NULL,
  queue_number INT NOT NULL COMMENT '排队号',
  status ENUM('pending', 'confirmed', 'completed', 'cancelled', 'missed') NOT NULL DEFAULT 'pending',
  symptoms TEXT COMMENT '症状描述',
  notes TEXT COMMENT '备注',
  cancel_reason VARCHAR(255),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id),
  FOREIGN KEY (doctor_id) REFERENCES doctors(id),
  FOREIGN KEY (department_id) REFERENCES departments(id),
  INDEX idx_date (appointment_date),
  INDEX idx_doctor_date (doctor_id, appointment_date),
  INDEX idx_patient (patient_id),
  INDEX idx_status (status),
  INDEX idx_queue (doctor_id, appointment_date, time_slot)
) ENGINE=InnoDB;

-- 6. AI问诊记录表
CREATE TABLE ai_consultations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  symptoms TEXT NOT NULL COMMENT '患者症状描述',
  symptom_duration VARCHAR(100) COMMENT '症状持续时间',
  severity ENUM('mild', 'moderate', 'severe') NOT NULL DEFAULT 'mild',
  ai_diagnosis TEXT COMMENT 'AI诊断结果',
  confidence DECIMAL(5,2) COMMENT '置信度(%)',
  suggested_department VARCHAR(100) COMMENT '建议科室',
  suggested_doctor_id INT COMMENT '建议医生',
  risk_level ENUM('low', 'medium', 'high', 'emergency') NOT NULL DEFAULT 'low',
  advice TEXT COMMENT 'AI建议',
  is_referred TINYINT(1) NOT NULL DEFAULT 0,
  referred_appointment_id INT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id),
  FOREIGN KEY (suggested_doctor_id) REFERENCES doctors(id),
  FOREIGN KEY (referred_appointment_id) REFERENCES appointments(id),
  INDEX idx_patient (patient_id),
  INDEX idx_risk (risk_level),
  INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- 7. 诊疗记录表
CREATE TABLE diagnosis_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  appointment_id INT NOT NULL UNIQUE,
  patient_id INT NOT NULL,
  doctor_id INT NOT NULL,
  chief_complaint TEXT COMMENT '主诉',
  present_illness TEXT COMMENT '现病史',
  physical_examination TEXT COMMENT '体格检查',
  diagnosis TEXT NOT NULL COMMENT '诊断结果',
  treatment_plan TEXT COMMENT '治疗方案',
  notes TEXT COMMENT '医生备注',
  follow_up_date DATE COMMENT '复诊日期',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (appointment_id) REFERENCES appointments(id),
  FOREIGN KEY (patient_id) REFERENCES patients(id),
  FOREIGN KEY (doctor_id) REFERENCES doctors(id),
  INDEX idx_patient (patient_id),
  INDEX idx_doctor (doctor_id)
) ENGINE=InnoDB;

-- 8. 药品表
CREATE TABLE medicines (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  generic_name VARCHAR(100) COMMENT '通用名',
  category VARCHAR(50) COMMENT '药品分类',
  specification VARCHAR(100) COMMENT '规格',
  manufacturer VARCHAR(100),
  unit VARCHAR(10) NOT NULL COMMENT '单位(盒/瓶/支)',
  price DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL DEFAULT 0,
  requires_prescription TINYINT(1) NOT NULL DEFAULT 1,
  description TEXT,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_name (name),
  INDEX idx_category (category)
) ENGINE=InnoDB;

-- 9. 处方表
CREATE TABLE prescriptions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  record_id INT NOT NULL,
  medicine_id INT NOT NULL,
  doctor_id INT NOT NULL,
  patient_id INT NOT NULL,
  dosage VARCHAR(100) NOT NULL COMMENT '用量(如:1次1片)',
  frequency VARCHAR(100) NOT NULL COMMENT '频次(如:每日3次)',
  duration VARCHAR(100) NOT NULL COMMENT '疗程(如:7天)',
  route VARCHAR(50) NOT NULL DEFAULT '口服' COMMENT '给药途径',
  quantity INT NOT NULL COMMENT '数量',
  notes TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (record_id) REFERENCES diagnosis_records(id),
  FOREIGN KEY (medicine_id) REFERENCES medicines(id),
  FOREIGN KEY (doctor_id) REFERENCES doctors(id),
  FOREIGN KEY (patient_id) REFERENCES patients(id),
  INDEX idx_record (record_id),
  INDEX idx_patient (patient_id)
) ENGINE=InnoDB;

-- 10. 系统日志表
CREATE TABLE operation_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  username VARCHAR(50),
  action VARCHAR(50) NOT NULL COMMENT '操作类型',
  target_type VARCHAR(50) COMMENT '操作对象类型',
  target_id INT COMMENT '操作对象ID',
  detail TEXT COMMENT '操作详情',
  ip_address VARCHAR(45),
  user_agent VARCHAR(255),
  status ENUM('success', 'failure') NOT NULL DEFAULT 'success',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_action (action),
  INDEX idx_created (created_at),
  INDEX idx_target (target_type, target_id)
) ENGINE=InnoDB;

-- 11. 通知消息表
CREATE TABLE notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  type ENUM('appointment', 'diagnosis', 'prescription', 'system', 'reminder') NOT NULL DEFAULT 'system',
  is_read TINYINT(1) NOT NULL DEFAULT 0,
  read_at DATETIME,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_unread (user_id, is_read),
  INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- 初始数据：管理员账号（密码: admin123）
INSERT INTO users (username, password_hash, real_name, role) VALUES
('admin', '$2b$12$LJ3m4ys3Lk0TSwHCpNqr7eY.VJkY1rOgKz7kGXByHPq5L8pVB1GVe', '系统管理员', 'admin');

-- 初始数据：科室
INSERT INTO departments (id, name, description, parent_id) VALUES
(1, '内科', '内科是临床医学的综合性科室', NULL),
(2, '外科', '外科主要处理需要通过手术治疗的疾病', NULL),
(3, '儿科', '儿科专门诊治儿童疾病', NULL),
(4, '妇产科', '妇产科专门处理女性生殖系统疾病', NULL),
(5, '眼科', '眼科专门诊治眼部疾病', NULL),
(6, '耳鼻喉科', '耳鼻喉科专门诊治耳鼻喉疾病', NULL),
(7, '皮肤科', '皮肤科专门诊治皮肤疾病', NULL),
(8, '神经内科', '神经内科专门诊治神经系统疾病', 1),
(9, '心血管内科', '心血管内科专门诊治心血管疾病', 1),
(10, '骨科', '骨科专门诊治骨骼肌肉系统疾病', 2),
(11, '急诊科', '急诊科处理急危重症', NULL),
(12, '中医科', '中医科提供中医药诊疗服务', NULL);

-- 初始数据：药品
INSERT INTO medicines (name, generic_name, category, specification, manufacturer, unit, price, stock, requires_prescription) VALUES
('阿莫西林胶囊', 'Amoxicillin', '抗生素', '0.5g*24粒', '华北制药', '盒', 12.50, 500, TRUE),
('布洛芬缓释胶囊', 'Ibuprofen', '解热镇痛', '0.3g*20粒', '中美史克', '盒', 18.90, 800, FALSE),
('奥美拉唑肠溶胶囊', 'Omeprazole', '消化系统', '20mg*14粒', '丽珠集团', '盒', 25.00, 300, TRUE),
('氯雷他定片', 'Loratadine', '抗过敏', '10mg*12片', '先灵葆雅', '盒', 15.00, 400, FALSE),
('盐酸二甲双胍片', 'Metformin', '降糖药', '0.5g*60片', '施贵宝', '盒', 22.00, 200, TRUE),
('硝苯地平控释片', 'Nifedipine', '降压药', '30mg*28片', '拜耳', '盒', 35.00, 250, TRUE),
('阿托伐他汀钙片', 'Atorvastatin', '降脂药', '20mg*28片', '辉瑞', '盒', 45.00, 180, TRUE),
('维生素C片', 'Vitamin C', '维生素', '100mg*100片', '东北制药', '瓶', 5.00, 1000, FALSE),
('头孢克肟胶囊', 'Cefixime', '抗生素', '100mg*6粒', '广州白云山', '盒', 28.00, 350, TRUE),
('蒙脱石散', 'Montmorillonite', '消化系统', '3g*10袋', '博福-益普生', '盒', 12.00, 600, FALSE);
