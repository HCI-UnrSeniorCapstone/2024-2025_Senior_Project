def set_available_features(task_measurments):
    # makes sures the default taks are false
    default_tasks = {'Mouse Movement': False, 'Mouse Scrolls': False,
                     'Mouse Clicks': False, 'Keyboard Inputs': False}

    # checks if features are in the array, then it will change hash into true
    for task in task_measurments:
        if task in default_tasks:
            default_tasks[task] = True

    return default_tasks


def get_study_detail(subData):
    study_name = subData.get('studyName')
    study_desc = subData.get('studyDescription')
    study_design = subData.get('studyDesignType')
    people_count = subData.get('participantCount')

    return study_name, study_desc, study_design, people_count