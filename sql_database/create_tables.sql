USE DEVELOP_fulcrum;
CREATE TABLE user (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP
);
CREATE TABLE admin_user (
    admin_user_id INT,
    user_id INT,
    PRIMARY KEY (admin_user_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);
CREATE TABLE task (
    task_id INT PRIMARY KEY,
    task_name VARCHAR(255),
    task_description VARCHAR(255),
    duration DECIMAL(6, 3)
);
CREATE TABLE measurement_type (
    measurement_type_id INT PRIMARY KEY,
    measurement_type_name VARCHAR(255)
);
CREATE TABLE task_measurement (
    task_id INT,
    measurement_type_id INT,
    PRIMARY KEY (task_id, measurement_type_id),
    FOREIGN KEY (task_id) REFERENCES task(task_id),
    FOREIGN KEY (measurement_type_id) REFERENCES measurement_type(measurement_type_id)
);
CREATE TABLE factor (
    factor_id INT PRIMARY KEY,
    factor_description VARCHAR(255)
);
CREATE TABLE study (
    study_id INT PRIMARY KEY,
    study_name VARCHAR(255),
    study_description VARCHAR(255),
    expected_participants INT
);
-- Read, Write, Read/Write. No None cuz they just wouldn't be in the table
CREATE TABLE study_user_access_type (
    study_user_access_type_id INT PRIMARY KEY,
    description VARCHAR(255)
);
-- All users who have access to a study and their permission types
CREATE TABLE study_user_access (
    user_id INT,
    study_id INT,
    access_type INT,
    PRIMARY KEY (user_id, study_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    FOREIGN KEY (access_type) REFERENCES study_user_access_type(study_user_access_type_id)
);
-- This assumes every task has the same factors. need to double-check
CREATE TABLE study_task_factor (
    study_id INT,
    task_id INT,
    factor_id INT,
    PRIMARY KEY (study_id, task_id),
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    FOREIGN KEY (task_id) REFERENCES task(task_id),
    FOREIGN KEY (factor_id) REFERENCES factor(factor_id)
)