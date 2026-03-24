from pathlib import Path
from datetime import datetime
import os

from pyarrow import timestamp

cd = Path('')

def get_files():
    files = []
    for item in cd.iterdir():
        files.append(item.name[:-3])
    return files

def get_time_ago(file_name):
    """Calculates how long ago a specific time was from right now."""

    timestamp_data = read_file(file_name)["data"][1]

    try:
        # Assuming your timestamp is a string like "2026-03-24 08:30:00"
        saved_time = datetime.fromisoformat(str(timestamp_data))
        now = datetime.now()

        diff = now - saved_time
        seconds = diff.total_seconds()

        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            return f"{int(seconds // 60)} min ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"

    except Exception as e:
        return "Unknown time"

def change_directory(directory):
    global cd
    cd = Path(directory)

def create_file(name="untitled", n=1):
    files = get_files()
    if f"{name}" in files:
        if n > 1:
            create_file(f"{name[0:-3]}({n})", n + 1)
        else:
            create_file(f"{name}({n})", n + 1)
        return
    try:
        with open(f"{cd}/{name}.md", 'w') as file:
            file.write(f"{datetime.now()}\n{datetime.now()}\n---\n{name}\n---\n")
        print(f"File '{name}' created and written successfully.")
    except IOError as e:
        print(f"An error occurred: {e}")

def rename_file(old_name, new_name, n=1):
    # this should probably end up being a "if it exists through a prompt to pick a new name, but for now this works"
    files = get_files()
    if f"{new_name}" in files:
        if new_name == old_name:
            pass
        elif n > 1:
            rename_file(old_name, f"{new_name[0:-3]}({n})", n + 1)
        else:
            rename_file(old_name, f"{new_name}({n})", n + 1)
    try:
        Path(f"{cd}/{old_name}.md").rename(f"{cd}/{new_name}.md")
        fileinfo = read_file(new_name)
        with open(f"{cd}/{new_name}.md", 'w') as f:
            f.write(f"{fileinfo["data"][0]}\n{datetime.now()}\n---\n{new_name}\n---\n")
            f.write(fileinfo["content"])

    except IOError as e:
        print(f"An error occurred: {e}")

def read_file(name):
    fileinfo = {
        "data": [],
        "title": '',
        "oldTitle": '',
        'content': ''
    }
    with open(f"{cd}/{name}.md", 'r') as file:
        for data in file:
            if data.rstrip('\n') == "---":
                break
            fileinfo["data"].append(data.rstrip('\n'))
        for title in file:
            if title.rstrip('\n') == "---":
                break
            fileinfo["title"] = title.rstrip('\n')
            fileinfo["oldTitle"] = title.rstrip('\n')
        for text in file:
            fileinfo["content"] += text

    return fileinfo

def save_file(oldName, name, text):
    print(oldName, name,"\n", text)
    rename_file(oldName, name)
    fileinfo = read_file(name)
    with open(f"{cd}/{name}.md", 'w') as file:
        file.write(f"{fileinfo["data"][0]}\n{datetime.now()}\n---\n{name}\n---\n")
        file.write(text)

def del_file(name):
    if os.path.exists(f"{cd}/{name}.md"):
        os.remove(f"{cd}/{name}.md")