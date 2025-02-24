import json
import datetime
import os
import time
import plyer
from plyer import notification

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def remind(file_path):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    reminders = load_data(file_path)
    for r in reminders:
        if r["scheduled"] and r["datetime"] == now:
            notification.notify(
                title=r["title"],
                message=f"""Description: {r["description"]}\nSchedule: {r["datetime"]}\n""",
                timeout=10
            )
            if r["recurring"]:
                if r["recurrences"] > 0:
                    now_d = datetime.datetime.now().isoweekday()
                    date_time = datetime.datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M")
                    freq = r["req_freq"]
                    if freq == "ED":
                        new_date_time = date_time + datetime.timedelta(days=1)
                    elif freq == "EW":
                        new_date_time = date_time + datetime.timedelta(weeks=1)
                    elif freq == "EM":
                        new_date_time = date_time + datetime.timedelta(weeks=4.34524)
                    elif freq == "EY":
                        new_date_time = date_time + datetime.timedelta(weeks=52.1429)
                    elif freq == "EOD":
                        new_date_time = date_time + datetime.timedelta(days=2)
                    elif freq == "EOW":
                        new_date_time = date_time + datetime.timedelta(weeks=2)
                    elif freq == "EOM":
                        new_date_time = date_time + datetime.timedelta(weeks=8.69049)
                    elif freq == "EOY":
                        new_date_time = date_time + datetime.timedelta(weeks=104.357)
                    elif freq == "EWD":
                        if now_d < 5:
                            new_date_time = date_time + datetime.timedelta(days=1)
                        else:
                            new_date_time = date_time + datetime.timedelta(days=8 - now_d)
                    elif freq == "EWE":
                        if now_d == 6:
                            new_date_time = date_time + datetime.timedelta(days=1)
                        else:
                            new_date_time = date_time + datetime.timedelta(days=6 - now_d)
                    r["datetime"] = new_date_time.strftime("%Y-%m-%d %H:%M")
                    r["recurrences"] -= 1
            reminders.remove(r)
            save_data(file_path, reminders)

def background_service(file_path):
    while True:
        remind(file_path)
        time.sleep(1)  # Check every second

if __name__ == "__main__":
    file_path = os.path.join(os.path.expanduser("~"), "Documents", "reminder_app_data.json")
    background_service(file_path)
