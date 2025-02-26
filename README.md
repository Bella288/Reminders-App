# Reminders-App
A simple Reminders App using Python
<br>
Latest Release Notes: [v1.0.2 Release Notes](https://github.com/Bella288/Reminders-App/wiki/v1.0.2-%E2%80%90-Release-Notes)
## Including
* Background Service - To serve notifications to the user even if the app is closed, as long as background_service.py is running.
* Tkinter-based Main App - For an easy-to-use user interface.
* JSON File - For saving user reminders easily.
* Audio File - Four Use as Notification Sound
## Notes
* This app is designed for Mac and Windows.
## How To Use
Note: Filenames shown here are ***not*** a recommendation, but are what they ***need*** to be named for the program to function as intended.
1. Open your coding program
2. In the terminal, type "pip install plyer playsound==1.2.2 runpy tkinter json datetime"
3. Download the file **"notif.mp3"** from this repository in your **DOCUMENTS** folder. (To download, go to the file and click **"Download Raw"**)
5. Create a Python file named **"todo_app.py"** in your **DOCUMENTS** folder.
6. Copy and paste the contents from **"todo_app.py"** in this repository to your file.
7. Save the file.
8. Create a Python file named **"background_service.py"** in your **DOCUMENTS** folder.
9. Copy and paste the contents from **"background_service.py"** in this repository to your file.
10. Save the file.
11. Create a JSON file named **"reminders_app_data.json"** in your **DOCUMENTS** folder.
12. In the file, write [ ]
13. Save the file.
14. To run, first run "todo_app.py". Then, open another Terminal instance and run "background_service.py".

