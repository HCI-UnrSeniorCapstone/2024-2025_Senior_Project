# Purpose: All functionalities for producing csvs and zips 


import os
import pandas as pd
import zipfile
import shutil  # used to remove folder once zip is created


# Ref https://www.tutorialspoint.com/how-to-get-the-home-directory-in-python#:~:text=By%20calling%20%22os.,regardless%20of%20the%20operating%20system.
def get_save_dir():
    dir_home = os.path.expanduser("~")
    dir_fulcrum = os.path.join(dir_home, "Fulcrum_Results")
    os.makedirs(dir_fulcrum, exist_ok = True)
    return dir_fulcrum 


# Generating a unique csv for each measurement type for each trial 
def write_to_csv(session_id, measurement_type, feature, arr_data, is_used, task, factor):    
    if not is_used:
        return

    task_name = task['taskName'].replace(" ","")
    factor_name = factor['factorName'].replace(" ","")

    dir_results = get_save_dir()
    dir_session = os.path.join(dir_results, f'Session_{session_id}')
    dir_trial = os.path.join(dir_session, f"{task_name}_{factor_name}")
    os.makedirs(dir_trial, exist_ok=True)
    filename = f"{session_id}_{task_name}_{factor_name}_{measurement_type}_data.csv"
    file_path = os.path.join(dir_trial, filename)
    
    # Prevent writing values that exceeded task duration due to delay between signaling task end and stopping tracking threads
    task_dur = task.get('taskDuration')
    if task_dur is not None:
        time_cutoff = float(task_dur)
    else:
        time_cutoff = float('inf')
    updated_data = [row for row in arr_data if float(row[1]) <= time_cutoff]
    
    # Convert to df 
    if feature == 'mouse':
        df = pd.DataFrame(updated_data, columns=['Time', 'running_time', 'x', 'y'])

    elif feature == 'keyboard':
        df = pd.DataFrame(updated_data, columns=['Time', 'running_time', 'keys'])

    if os.path.exists(file_path): # CSV already exists so we just append and don't add headers
        df.to_csv(file_path, mode='a', header=False, index=False)
    else: # CSV does not exist so have to create and add headers 
        df.to_csv(file_path, index=False)
    

    
def zip_folder(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zipf.write(file_path, arcname)


def package_session_results(session_id):
    dir_fulcrum = get_save_dir()
    dir_session = os.path.join(dir_fulcrum, f'Session_{session_id}')
        
    zip_path = os.path.join(dir_fulcrum, f"session_results_{session_id}.zip")
    try:
        zip_folder(dir_session, zip_path)
        shutil.rmtree(dir_session)
        print(f"Session {session_id} results saved!")
    except Exception as e:
        print(f"Error occured while trying to package session {session_id}: {e}")

    

###################################################

# @app.route("/retrieve_zip/<zip_name>", methods=["GET"])
# def retrieve_zip(zip_name):
#     z_path = os.path.join(os.getcwd(), zip_name)
#     if os.path.exists(z_path) and zip_name.endswith('.zip'):
#         return send_file(z_path, as_attachment=True)
#     else:
#         return "", 200

###################################################