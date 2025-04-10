/*
 CURRENT RULES:
 - Every study must have at least 1 task and 1 factor
 - A task may have 0-M measurement options
 - A user may have no studies 
 - A study may have many users with varying Read OR Read / Write Prviliges
 */
-- Users
INSERT INTO user (
        user_id,
        first_name,
        last_name,
        email,
        created_at,
        user_password
    )
VALUES (
        1,
        'John',
        'Doe',
        'john.doe@example.com',
        '2024-11-01 10:15:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        2,
        'Jane',
        'Smith',
        'jane.smith@example.com',
        '2024-11-02 12:30:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        3,
        'Henry',
        'Brown',
        'henry.brown@example.com',
        '2024-11-03 14:45:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        4,
        'Emily',
        'Davis',
        'emily.davis@example.com',
        '2024-11-04 16:00:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        5,
        'Chris',
        'Wilson',
        'chris.wilson@example.com',
        '2024-11-05 18:15:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        6,
        'Anna',
        'Taylor',
        'anna.taylor@example.com',
        '2024-11-06 09:20:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        7,
        'Robert',
        'Johnson',
        'robert.johnson@example.com',
        '2024-11-07 11:50:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        8,
        'Sophia',
        'Martinez',
        'sophia.martinez@example.com',
        '2024-11-08 13:10:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        9,
        'Daniel',
        'Hernandez',
        'daniel.hernandez@example.com',
        '2024-11-09 15:35:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    ),
    (
        10,
        'Isabella',
        'Moore',
        'isabella.moore@example.com',
        '2024-11-10 17:40:00',
        '$argon2id$v=19$m=65536,t=3,p=4$+f8/J0QIYYwxBqDUGoOw9g$gP0G2PD3YrAI7ZsY9QrCmA8zzzJz+aF4sQXDNSRsyBA'
    );

INSERT INTO role_type(
    role_type_name,
    role_type_description
)
VALUES ('Researcher', 'Making and running studies'), ('Facilitator', 'Managing researchers');

INSERT INTO users_roles(user_id, role_type_id)
VALUES (1, 1),(2, 1),(3, 1),(4, 1),(5, 1),(6, 1),(7, 1),(8, 1),(9, 1),(10, 1);

-- Study Design Types
INSERT INTO study_design_type (
        study_design_type_id,
        study_design_type_description
    )
VALUES (1, 'Within'),
    (2, 'Between');
-- Studies
INSERT INTO study (
        study_id,
        study_name,
        study_description,
        expected_participants,
        study_design_type_id
    )
VALUES (
        1,
        'Memory and Attention',
        'Study on memory retention and focus.',
        50,
        1
    ),
    (
        2,
        'Reaction Speed',
        'Testing reaction times under various conditions.',
        30,
        2
    ),
    (
        3,
        'Cognitive Load',
        'Exploring cognitive strain with multitasking.',
        40,
        1
    ),
    (
        4,
        'Visual Perception',
        'Examining color and shape recognition.',
        25,
        2
    ),
    (
        5,
        'Decision Making',
        'Study on how participants make decisions under pressure.',
        45,
        1
    ),
    (
        6,
        'Language Processing',
        'Exploring how people process language in real-time.',
        35,
        2
    ),
    (
        7,
        'Memory Recall',
        'Study on the accuracy of memory recall over time.',
        50,
        1
    ),
    (
        8,
        'Social Interactions',
        'Exploring how people interact in group settings.',
        60,
        2
    ),
    (
        9,
        'Stress and Performance',
        'Investigating the impact of stress on performance.',
        40,
        1
    ),
    (
        10,
        'Motor Skills',
        'A study on fine and gross motor skills development.',
        30,
        2
    );
-- Read, Read/Write. No None cuz they just wouldn't be in the table
INSERT INTO study_user_access_type (
        study_user_access_type_id,
        study_user_access_type_description
    )
VALUES (1, 'Read'),
    (2, 'Read/Write');
-- Owner, Viewer, Editor
INSERT INTO study_user_role_type (
        study_user_role_type_id,
        study_user_role_description,
        study_user_access_type_id
    )
VALUES (1, 'Owner', 2),
    (2, 'Viewer', 1),
    (3, 'Editor', 2);
-- Study User Role
INSERT INTO study_user_role (study_id, user_id, study_user_role_type_id)
VALUES (1, 1, 1),
    (2, 2, 1),
    (3, 3, 1),
    (4, 4, 1),
    (5, 5, 1),
    (6, 6, 1),
    (7, 7, 1),
    (8, 8, 1),
    (9, 9, 1),
    (10, 10, 1),
    -- END OF OWNERS
    (10, 1, 2),
    (9, 2, 2),
    (8, 3, 2),
    (7, 4, 2),
    (6, 5, 2),
    -- END OF VIEWERS
    (8, 1, 3),
    (7, 2, 3),
    (6, 3, 3) -- END OF EDITORS
;
-- Tasks
INSERT INTO task (
        task_id,
        study_id,
        task_name,
        task_description,
        task_directions,
        duration
    )
VALUES (
        1,
        1,
        'Memory Test',
        'A test to assess short-term memory retention',
        'Perform the task without visual input. Ensure a safe environment.',
        10.000
    ),
    (
        2,
        1,
        'Reaction Time',
        'A test to measure how quickly participants respond to stimuli',
        'Use only one hand to complete the task. Specify the hand based on the study setup.',
        5.000
    ),
    (
        3,
        2,
        'Math Problems',
        'A test involving solving simple math problems under time pressure',
        'Complete the task within a strict time constraint. Provide clear timing instructions.',
        15.000
    ),
    (
        4,
        2,
        'Shape Matching',
        'A task where participants match shapes based on predefined criteria',
        'Perform the task while standing upright. Ensure participants are comfortable.',
        20.000
    ),
    (
        5,
        3,
        'Color Recognition',
        'A task to identify colors in different environments',
        'Introduce background noise or visual distractions during the task.',
        8.000
    ),
    (
        6,
        3,
        'Word Search',
        'A task to identify words in a grid',
        'Use the non-dominant hand for the task. Provide clear instructions for participants.',
        15.000
    ),
    (
        7,
        4,
        'Puzzle Solving',
        'A task involving solving a jigsaw puzzle',
        'Perform the task in low-light conditions. Ensure safety and visibility of critical elements.',
        20.000
    ),
    (
        8,
        4,
        'Attention Focus',
        'A task to measure sustained attention during a period of inactivity',
        'Perform the task while simultaneously handling a secondary task. Provide clear secondary task details.',
        12.000
    ),
    (
        9,
        5,
        'Word Association',
        'Participants are given words and must respond with associated terms',
        'Complete the task without prior instructions. Observe natural responses.',
        18.000
    ),
    (
        10,
        5,
        'Spatial Awareness',
        'Test to evaluate awareness of surroundings without direct visual input',
        'Use only the dominant hand for all task interactions.',
        15.000
    ),
    (
        11,
        6,
        'Decision Making',
        'A task to assess decision-making skills under pressure',
        'Perform the task while listening to music. Specify volume and type of music.',
        10.000
    ),
    (
        12,
        6,
        'Hand-Eye Coordination',
        'A task to evaluate the ability to coordinate hand movements with visual input',
        'Conduct the task in a cooler-than-usual environment. Monitor participant comfort.',
        12.000
    ),
    (
        13,
        7,
        'Auditory Perception',
        'A task to measure the ability to identify and respond to sounds',
        'Participants should attempt the task as quickly as possible without sacrificing accuracy.',
        10.000
    ),
    (
        14,
        7,
        'Speed Reading',
        'A task to assess reading speed and comprehension',
        'Perform the task after an energy-draining activity. Assess performance under fatigue.',
        8.000
    ),
    (
        15,
        8,
        'Pattern Recognition',
        'A test to identify patterns in sequences of images or numbers',
        'Perform the task with guidance or assistance from a partner.',
        20.000
    ),
    (
        16,
        8,
        'Memory Recall',
        'A task to test long-term memory recall of specific information',
        'Introduce a stressor like a countdown timer or competitive scenario during the task.',
        15.000
    ),
    (
        17,
        9,
        'Multitasking',
        'A test to assess the ability to handle multiple tasks simultaneously',
        'Complete the task while exposed to ambient background noise.',
        18.000
    ),
    (
        18,
        9,
        'Problem Solving',
        'A task requiring the solving of complex problems under time pressure',
        'Task designed with accessibility in mind, such as larger buttons or on-screen cues.',
        25.000
    ),
    (
        19,
        10,
        'Logical Reasoning',
        'A test to assess the ability to think logically and reason through problems',
        'Perform the task in a virtual environment, simulating real-world conditions.',
        10.000
    ),
    (
        20,
        10,
        'Verbal Fluency',
        'A task to assess the ability to generate words based on specific criteria',
        'Complete the task while collaborating with others remotely via video or chat.',
        12.000
    );
-- Measurement Types
INSERT INTO measurement_option (measurement_option_id, measurement_option_name)
VALUES (1, 'Mouse Movement'),
    (2, 'Mouse Scrolls'),
    (3, 'Mouse Clicks'),
    (4, 'Keyboard Inputs'),
    (5, 'Screen Recording'),
    (6, 'Heat Map');
-- Task Measurement
INSERT INTO task_measurement (task_id, measurement_option_id)
VALUES (1, 1),
    -- Memory Test (Mouse Movement)
    (1, 2),
    -- Memory Test (Mouse Scrolls)
    (1, 3),
    -- Memory Test (Mouse Clicks)
    (1, 4),
    -- Memory Test (Keyboard Inputs)
    (2, 1),
    -- Reaction Time (Mouse Movement)
    (2, 3),
    -- Reaction Time (Mouse Clicks)
    /*
     NO tasks for 3 since that is the empty options
     */
    -- Math Problems (Keyboard Inputs)
    (4, 1),
    -- Shape Matching (Mouse Movement)
    (4, 2),
    -- Shape Matching (Mouse Scrolls)
    (4, 3),
    -- Shape Matching (Mouse Clicks)
    (4, 4),
    -- Shape Matching (Keyboard Inputs)
    (5, 1),
    -- Color Recognition (Mouse Movement)
    (5, 3),
    -- Color Recognition (Mouse Clicks)
    (6, 1),
    -- Word Search (Mouse Movement)
    (6, 2),
    -- Word Search (Mouse Scrolls)
    (6, 4),
    -- Word Search (Keyboard Inputs)
    (7, 1),
    -- Puzzle Solving (Mouse Movement)
    (7, 3),
    -- Puzzle Solving (Mouse Clicks)
    (7, 4),
    -- Puzzle Solving (Keyboard Inputs)
    (8, 1),
    -- Attention Focus (Mouse Movement)
    (8, 2),
    -- Attention Focus (Mouse Scrolls)
    (8, 4),
    -- Attention Focus (Keyboard Inputs)
    (9, 1),
    -- Word Association (Mouse Movement)
    (9, 3),
    -- Word Association (Mouse Clicks)
    (10, 1),
    -- Spatial Awareness (Mouse Movement)
    (10, 2),
    -- Spatial Awareness (Mouse Scrolls)
    (10, 3),
    -- Spatial Awareness (Mouse Clicks)
    (10, 4),
    -- Spatial Awareness (Keyboard Inputs)
    (11, 1),
    -- Decision Making (Mouse Movement)
    (11, 3),
    -- Decision Making (Mouse Clicks)
    (11, 4),
    -- Decision Making (Keyboard Inputs)
    (12, 1),
    -- Hand-Eye Coordination (Mouse Movement)
    (12, 2),
    -- Hand-Eye Coordination (Mouse Scrolls)
    (12, 3),
    -- Hand-Eye Coordination (Mouse Clicks)
    (13, 1),
    -- Auditory Perception (Mouse Movement)
    (13, 4),
    -- Auditory Perception (Keyboard Inputs)
    (14, 1),
    -- Speed Reading (Mouse Movement)
    (14, 3),
    -- Speed Reading (Mouse Clicks)
    (15, 1),
    -- Pattern Recognition (Mouse Movement)
    (15, 2),
    -- Pattern Recognition (Mouse Scrolls)
    (15, 3),
    -- Pattern Recognition (Mouse Clicks)
    (16, 1),
    -- Memory Recall (Mouse Movement)
    (16, 2),
    -- Memory Recall (Mouse Scrolls)
    (16, 3),
    -- Memory Recall (Mouse Clicks)
    (17, 1),
    -- Multitasking (Mouse Movement)
    (17, 2),
    -- Multitasking (Mouse Scrolls)
    (17, 3),
    -- Multitasking (Mouse Clicks)
    (17, 4),
    -- Multitasking (Keyboard Inputs)
    (18, 1),
    -- Problem Solving (Mouse Movement)
    (18, 3),
    -- Problem Solving (Mouse Clicks)
    (18, 4),
    -- Problem Solving (Keyboard Inputs)
    (19, 1),
    -- Logical Reasoning (Mouse Movement)
    (19, 3),
    -- Logical Reasoning (Mouse Clicks)
    (20, 1),
    -- Verbal Fluency (Mouse Movement)
    (20, 4);
-- Verbal Fluency (Keyboard Inputs)
-- Factors
INSERT INTO factor (
        factor_id,
        study_id,
        factor_name,
        factor_description
    )
VALUES (
        1,
        1,
        'Blindfolded',
        'Participants are blindfolded to limit their visual perception.'
    ),
    (
        2,
        1,
        'One-Handed',
        'Participants are required to complete tasks using only one hand.'
    ),
    (
        3,
        1,
        'Time-Limited',
        'Tasks must be completed within a specified time limit.'
    ),
    (
        4,
        2,
        'Standing',
        'Participants must complete the task while standing, no sitting allowed.'
    ),
    (
        5,
        3,
        'Distraction Present',
        'Participants will be exposed to distractions during the task.'
    ),
    (
        6,
        3,
        'Opposite-Handed',
        'Participants must perform the task using their non-dominant hand.'
    ),
    (
        7,
        4,
        'Dim Lighting',
        'The environment is dimly lit, limiting visual clarity.'
    ),
    (
        8,
        4,
        'Multitasking',
        'Participants are asked to handle multiple tasks simultaneously.'
    ),
    (
        9,
        5,
        'No Instructions',
        'Participants are not given instructions and must figure out the task on their own.'
    ),
    (
        10,
        5,
        'Dominant Hand Only',
        'Only the participant’s dominant hand can be used to complete the task.'
    ),
    (
        11,
        6,
        'Distracted with Music',
        'Participants will be listening to music while performing the task.'
    ),
    (
        12,
        6,
        'Cold Room',
        'The room temperature is set to be uncomfortably cold during the task.'
    ),
    (
        13,
        7,
        'Fast-Paced',
        'The task requires participants to complete actions quickly, with a high tempo.'
    ),
    (
        14,
        7,
        'Low Energy',
        'Participants are expected to complete the task with limited energy or stamina.'
    ),
    (
        15,
        8,
        'Partner-Assisted',
        'Participants work alongside a partner to complete the task.'
    ),
    (
        16,
        8,
        'Simulated Stress',
        'The environment is designed to induce a sense of stress or pressure during the task.'
    ),
    (
        17,
        9,
        'Noisy Environment',
        'Participants are exposed to a noisy environment during the task.'
    ),
    (
        18,
        9,
        'Handicap Access',
        'The task is designed to accommodate participants with physical disabilities.'
    ),
    (
        19,
        10,
        'Virtual Reality',
        'Participants engage with the task in a virtual reality setting.'
    ),
    (
        20,
        10,
        'Remote Collaboration',
        'Participants complete the task in collaboration with others remotely.'
    );
INSERT INTO gender_type (gender_description) VALUES 
('Male'),
('Female'),
('Non-Binary'),
('Other'),
('Prefer Not to Say');

INSERT INTO ethnicity_type (ethnicity_description) VALUES 
('American Indian or Alaska Native'),
('Asian'),
('Black or African American'),
('Hispanic or Latino'),
('Native Hawaiian or Other Pacific Islander'),
('White');

INSERT INTO highest_education_type (highest_education_description) VALUES 
('Some High School'),
('High School Graduate or Equivalent'),
('Some College'),
('Associate''s Degree'),
('Bachelor''s Degree'),
('Master''s Degree'),
('Doctorate');


-- This guy should be participant 1
INSERT INTO participant (age, gender_type_id, highest_education_type_id, technology_competence)
VALUES (25, 1, 1, 1);
INSERT INTO participant (age, gender_type_id, highest_education_type_id, technology_competence)
VALUES (37, 1, 1, 1);
INSERT INTO participant (age, gender_type_id, highest_education_type_id, technology_competence)
VALUES (49, 1, 1, 1);

-- This guy will have no sessions
INSERT INTO participant (age, gender_type_id, highest_education_type_id, technology_competence)
VALUES (49, 1, 1, 1);

INSERT INTO participant_ethnicity (participant_id, ethnicity_type_id)
VALUES 
    (1, 1),
    (1, 2),
    (1, 3),
    (4, 3);


-- INSERT INTO participant_session (participant_id, study_id, ended_at, comments, is_valid)
-- VALUES (1, 1, NOW() + INTERVAL 30 MINUTE, "Participant is too smart. Terminate him", 0),
-- (2, 1, NULL, "They were very nice", 1),
-- (3, 1, NOW() + INTERVAL 23 MINUTE, "Thank you for reading this message", 1);