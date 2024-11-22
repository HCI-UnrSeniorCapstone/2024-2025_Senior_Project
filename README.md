# Fulcrum Platform

**Fulcrum** is a web-based platform designed to provide HCI researchers with a standardized interface and integrated tools for conducting studies. It streamlines the setup and operation of studies, centralizing many common tasks and reducing reliance on external tools like Excel or custom scripts.

## Key Features

1. **Pre-Built Toolset for Data Collection**

   - Offers ready-to-use tools for data collection (e.g., mouse tracking, keyboard input, eye tracking).
   - Reduces the need for repetitive setup across different studies.

2. **Dynamic Study Design**

   - Allows researchers to define studies through flexible forms, specifying parameters like tasks, data collection methods, and timings.

3. **Participant Management**

   - Collects participant data, including consent, and associates participants with specific studies.

4. **Data Access and Analysis**
   - Provides access to study data for completed sessions.
   - Includes a statistics workspace, allowing researchers to use predefined formulas and graphs or create custom analytics.

## External Components and Automation

For experiments conducted outside the platform (e.g., VR, web-based, PowerPoint):

- **Automated Script Generation**  
   Custom scripts are generated to match each study’s design, running on devices used in the study to handle data collection.
  - These scripts work with various data collection tools that require device permissions and specific hardware.

---

### Development Notes

- **Platform Compatibility**:  
   Due to hardware access needs, development will proceed on Windows to ensure native support for device permissions, rather than WSL.

- **Installing/Updating Dependencies**:  
   When developing, dependencies must be installed, but this process normally must be repeated by each developer on their own machine. For the Python code, every developer should [create their own venv virtual environment](https://realpython.com/python-virtual-environments-a-primer/) for `local_backend` and `server_backend`. These venvs should NOT be pushed to GitHub.

   1. **Frontend**  
      - **_Installing_**  
        - Go to the **frontend** folder  
        - Run `npm install`  

      - **_Updating_**  
        - This is automatically handled by npm :)  

   3. **Local_Backend**  
      - **_Installing_**  
        - Activate your **local_backend** venv  
        - Run `pip install -r requirements.txt`  

      - **_Updating_**  
        - Activate your **local_backend** venv  
        - Run `pip freeze > requirements.txt`  

   4. **Server_Backend**  
      - **_Installing_**  
        - Activate your **server_backend** venv  
        - Run `pip install -r requirements.txt`  

      - **_Updating_**  
        - Activate your **server_backend** venv  
        - Run `pip freeze > requirements.txt`  
  
  
- **Creating an Issue or Feature Request**:

  1.  **Navigate to the Project Board**

      - Go to the **Projects** tab in the repository.
      - Under the **Major Backlog** column, click on **Add Item** to start a new issue.

  2.  **Fill Out the Description**

      - Provide a clear description of the issue or feature.
      - Include any relevant notes and specify what the issue/feature should accomplish.

  3.  **Set Up Fields**

      - Assign the issue to team members by filling out the **Assignees** field.
      - Specify a priority or progress milestone in the **Milestone** field (e.g., `P1`, `P2`, or `P3`).

  4.  **Link Development with a Branch**
      - Under the **Development** section, click on **Create a branch**.
      - This links the issue to a branch, enabling automatic updates to the issue’s progress. As work is done, GitHub will move the issue through the stages:
        - **Backlog** → **In Progress** → **In Review** → **Done** → **Archived**.

  This setup keeps issues organized and connected to development, providing visibility into the progress of each feature or fix as it moves through the workflow.
