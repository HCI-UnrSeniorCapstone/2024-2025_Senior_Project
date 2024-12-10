USE DEVELOP_fulcrum;
CREATE TABLE user (
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE admin_user (
    admin_user_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    PRIMARY KEY (admin_user_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);
-- Within vs Between
CREATE TABLE study_design_type (
    study_design_type_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    study_design_type_description VARCHAR(255)
);
CREATE TABLE study (
    study_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    study_name VARCHAR(255) NOT NULL,
    study_description VARCHAR(255) NULL,
    expected_participants INT NOT NULL,
    study_design_type_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (study_design_type_id) REFERENCES study_design_type(study_design_type_id)
);
-- Read, Read/Write. No None cuz they just wouldn't be in the table
CREATE TABLE study_user_access_type (
    study_user_access_type_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    study_user_access_type_description VARCHAR(255)
);
-- Owner, Viewer, Editor
CREATE TABLE study_user_role_type (
    study_user_role_type_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
-- Study has many tasks
CREATE TABLE task (
    task_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    study_id INT,
    task_name VARCHAR(255) NOT NULL,
    task_description VARCHAR(255) NULL,
    -- Tells participant what to do
    task_directions VARCHAR(255) NULL,
    duration DECIMAL(6, 3) NULL,
    FOREIGN KEY (study_id) REFERENCES study(study_id)
);
-- Different tracking types
CREATE TABLE measurement_option (
    measurement_option_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    measurement_option_name VARCHAR(255)
);
CREATE TABLE task_measurement (
    task_id INT,
    measurement_option_id INT,
    PRIMARY KEY (task_id, measurement_option_id),
    FOREIGN KEY (task_id) REFERENCES task(task_id),
    FOREIGN KEY (measurement_option_id) REFERENCES measurement_option(measurement_option_id)
);
-- Study has many factors
CREATE TABLE factor (
    factor_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    study_id INT,
    factor_name VARCHAR(255) NOT NULL,
    factor_description VARCHAR(255) NULL,
    FOREIGN KEY (study_id) REFERENCES study(study_id)
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
-- Recorded instance when study happens
-- Will have to implement results to this however that is chosen
-- Participant should be generated


CREATE TABLE gender_type (
    gender_type_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    gender_description VARCHAR(255)
);

CREATE TABLE ethnicity_type (
    ethnicity_type_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ethnicity_description VARCHAR(255)
);

CREATE TABLE highest_education_type (
    highest_education_type_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    highest_education_description VARCHAR(255)
);

/*
 Session Rules to ensure:
 1: A particpant may do many sessions
 2: Every session has 1 participant
 3: A session may have many instances of the same task / factor
 */
CREATE TABLE participant (
    participant_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    age TINYINT UNSIGNED NULL,
    gender_type_id TINYINT UNSIGNED NULL,
    highest_education_type_id TINYINT UNSIGNED NULL,
    technology_competence TINYINT UNSIGNED NULL CHECK (technology_competence BETWEEN 0 AND 10),
    FOREIGN KEY (gender_type_id) REFERENCES gender_type(gender_type_id),
    FOREIGN KEY (highest_education_type_id) REFERENCES highest_education_type(highest_education_type_id)
);

-- Intersection Table
CREATE TABLE participant_ethnicity (
    participant_id INT,
    ethnicity_type_id TINYINT UNSIGNED,
    PRIMARY KEY (participant_id, ethnicity_type_id),
    FOREIGN KEY (participant_id) REFERENCES participant(participant_id),
    FOREIGN KEY (ethnicity_type_id) REFERENCES ethnicity_type(ethnicity_type_id)
);

-- NOTE: This is NOT an intersection. It's named this way since session is a SQL keyword
CREATE TABLE participant_session (
    participant_session_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    participant_id INT,
    study_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Should be updated and no longer null when session done
    ended_at TIMESTAMP NULL,
    comments VARCHAR(255) NULL,
    is_valid TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (participant_id) REFERENCES participant(participant_id),
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    CHECK (is_valid IN (0, 1))
);
/*
 NOTE: A session can do the same task / factor instance multiple times
 SINCE they are not PKs. Need to double check, but since their values
 are NOT unique, they should not be PKs
 */
CREATE TABLE session_data_instance (
    session_data_instance_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    participant_session_id INT,
    task_id INT,
    measurement_option_id INT,
    factor_id INT,
    -- This is where it is stored on hci
    csv_results_path VARCHAR(255) NULL,
    FOREIGN KEY (participant_session_id) REFERENCES participant_session(participant_session_id),
    FOREIGN KEY (task_id) REFERENCES task_measurement(task_id),
    FOREIGN KEY (measurement_option_id) REFERENCES task_measurement(measurement_option_id),
    FOREIGN KEY (factor_id) REFERENCES factor(factor_id)
);
CREATE TABLE deleted_study (
    study_id INT NOT NULL PRIMARY KEY,
    deleted_by_user_id INT NOT NULL,
    deletion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (study_id) REFERENCES study(study_id),
    FOREIGN KEY (deleted_by_user_id) REFERENCES user(user_id)
);
CREATE TABLE deleted_study_role (
    study_id INT NOT NULL,
    user_id INT NOT NULL,
    study_user_role_type_id INT NOT NULL,
    PRIMARY KEY (study_id, user_id),
    FOREIGN KEY (study_id) REFERENCES deleted_study(study_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (study_user_role_type_id) REFERENCES study_user_role_type(study_user_role_type_id)
);