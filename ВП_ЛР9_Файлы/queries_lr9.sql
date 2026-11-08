-- Создание базы данных
CREATE DATABASE IF NOT EXISTS lab_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE lab_db;

-- Создание таблицы students
CREATE TABLE students (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    group_num VARCHAR(10) DEFAULT NULL,
    birth_date DATE DEFAULT NULL,
    avg_grade DECIMAL(3,2) DEFAULT 0.00,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Добавление 5 записей в таблицу students
INSERT INTO students (name, group_num, birth_date, avg_grade) VALUES
('Иванов Иван', 'ИС-101', '2000-05-15', 4.50),
('Петрова Анна', 'ИС-101', '2001-03-22', 4.75),
('Сидоров Алексей', 'ИС-102', '2000-11-08', 4.20),
('Козлова Мария', 'ИС-101', '2001-07-19', 4.90),
('Новиков Дмитрий', 'ИС-102', '2000-09-30', 4.10);

-- Выборка всех студентов
SELECT * FROM students;

-- Фильтрация по группе
SELECT name, avg_grade FROM students WHERE group_num = 'ИС-101';

-- Обновление оценки
UPDATE students SET avg_grade = 4.8 WHERE name = 'Иванов Иван';

-- Удаление записи
DELETE FROM students WHERE id = 1;

-- Создание таблицы courses
CREATE TABLE courses (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO courses (title, credits) VALUES
('Веб-программирование', 4),
('Базы данных и СУБД', 5),
('Компьютерные сети', 3),
('Проектирование информационных систем', 4);

-- Промежуточная таблица для связи многие ко многим
CREATE TABLE student_courses (
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    PRIMARY KEY (student_id, course_id),
    CONSTRAINT fk_student_courses_student
        FOREIGN KEY (student_id) REFERENCES students (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_student_courses_course
        FOREIGN KEY (course_id) REFERENCES courses (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO student_courses (student_id, course_id) VALUES
(2, 1),
(2, 2),
(3, 1),
(3, 3),
(4, 2),
(4, 4),
(5, 1),
(5, 3);

-- JOIN запрос для вывода списка студентов и их курсов
SELECT s.name, s.group_num, c.title, c.credits
FROM students s
INNER JOIN student_courses sc ON s.id = sc.student_id
INNER JOIN courses c ON sc.course_id = c.id
ORDER BY s.name, c.title;
