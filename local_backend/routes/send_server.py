import requests
import json


def send_to_server(zip_local_path, session_json):
    # Make more robust eventually. Also, you will have to change it from 5003 to your port
    server_url = "http://100.82.85.28:5003/test_local_to_server"

    try:
        with open(zip_local_path, "rb") as file:
            files = {"file": file}
            data = {"json": json.dumps(session_json)}

            response = requests.post(server_url, files=files, data=data)

            if response.status_code == 200:
                print("Successfully sent results to server")
            else:
                print("Unexpected response:", response.status_code, response.text)

    except requests.exceptions.RequestException as e:
        print("Saving failed", e)
