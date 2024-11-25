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
    -- Tells participant what to do
    task_advice VARCHAR(255),
    duration DECIMAL(6, 3)
);
-- Different tracking types
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
-- Within vs Between
CREATE TABLE study_design_type (
    study_design_type_id INT PRIMARY KEY,
    study_design_type_description VARCHAR(255)
);
CREATE TABLE study (
    study_id INT PRIMARY KEY,
    study_name VARCHAR(255),
    study_description VARCHAR(255),
    expected_participants INT,
    study_design_type_id INT,
    created_at TIMESTAMP,
    FOREIGN KEY (study_design_type_id) REFERENCES study_design_type(study_design_type_id)
);
-- Read, Read/Write. No None cuz they just wouldn't be in the table
CREATE TABLE study_user_access_type (
    study_user_access_type_id INT PRIMARY KEY,
    study_user_access_type_description VARCHAR(255)
);
-- Owner, Viewer, Editor
CREATE TABLE study_user_role_type (
    study_user_role_type_id INT PRIMARY KEY,
    study_user_role_description VARCHAR(255),
    study_user_access_type_id INT,
    FOREIGN KEY (study_user_access_type_id) REFERENCES study_user_access_type (study_user_access_type_id)
);
-- All users who have access to a study and their permission types
CREATE TABLE study_user_role (
    user_id INT,
    study_id INT,
    study_user_role_type_id INT,
    PRIMARY KEY (user_id, study_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    FOREIGN KEY (study_user_role_type_id) REFERENCES study_user_role_type(study_user_role_type_id)
);
-- This assumes every task has the same factors. need to double-check
-- CREATE TABLE study_task_factor (
--     study_id INT,
--     task_id INT,
--     factor_id INT,
--     PRIMARY KEY (study_id, task_id),
--     FOREIGN KEY (study_id) REFERENCES study(study_id),
--     FOREIGN KEY (task_id) REFERENCES task(task_id),
--     FOREIGN KEY (factor_id) REFERENCES factor(factor_id)
-- );
-- Study has many tasks
CREATE TABLE study_task (
    study_id INT,
    task_id INT,
    PRIMARY KEY (study_id, task_id),
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    FOREIGN KEY (task_id) REFERENCES task(task_id)
);
-- Study has many factors
CREATE TABLE study_factor (
    study_id INT,
    factor_id INT,
    PRIMARY KEY (study_id, factor_id),
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    FOREIGN KEY (factor_id) REFERENCES factor(factor_id)
);
-- Recorded instance when study happens
-- Will have to implement results to this however that is chosen
-- Participant should be generated
CREATE TABLE participant_study_session (
    study_id INT,
    participant_id INT,
    task_id INT,
    factor_id INT,
    PRIMARY KEY (study_id, participant_id, task_id, factor_id),
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    FOREIGN KEY (task_id) REFERENCES task(task_id),
    FOREIGN KEY (factor_id) REFERENCES factor(factor_id)
);