from pathlib import Path
from datetime import datetime

import os
import sys
from xmlrpc.client import FastParser





class functions:


    def __init__(self, directory):
        self.defaultDir = directory
        self.cd = Path(self.defaultDir)

    def get_files(self):
        files = []
        for item in self.cd.iterdir():
            files.append(item.name[:-3])
        return files

    def change_directory(self, directory):
        self.cd = Path(directory)

    def create_file(self,name="untitled",n=1):
        files = self.get_files()
        if f"{name}" in files:
            if n > 1:
                self.create_file(f"{name[0:-3]}({n})", n + 1)
            else:
                self.create_file(f"{name}({n})",n+1)
            return
        try:
            with open(f"{self.cd}/{name}.md", 'w') as file:
                file.write(f"{datetime.now()}\n{datetime.now()}\n{name}\n")
            print(f"File '{name}' created and written successfully.")
        except IOError as e:
            print(f"An error occurred: {e}")

    def rename_file(self,old_name,new_name,n=1):
        #this should probably end up being a "if it exists through a prompt to pick a new name, but for now this works"
        files = self.get_files()
        if f"{new_name}" in files:
            if n > 1:
                self.rename_file(old_name,f"{new_name[0:-3]}({n})", n + 1)
            else:
                self.rename_file(old_name,f"{new_name}({n})", n + 1)
        try:
            Path(f"{self.cd}/{old_name}.md").rename(f"{self.cd}/{new_name}.md")
            fileinfo = self.read_file(new_name)
            with open(f"{self.cd}/{new_name}.md", 'w') as f:
                f.write(f"{fileinfo[0]}{datetime.now()}\n{new_name}\n")
                for line in fileinfo[3]:
                    f.write(line)

        except IOError as e:
            print(f"An error occurred: {e}")

    def read_file(name):
        fileinfo = {

        }
        with open(f"{self.cd}/{name}.md", 'r') as file:
            #stores creation date
            fileinfo.append(file.readline())
            #stores modification date
            fileinfo.append(file.readline())
            #stores name
            fileinfo.append(file.readline())
            #stores text
            fileinfo.append(file.readlines())
        return fileinfo

    def write_file(self,name,text):
        fileinfo = self.read_file(name)
        with open(f"{self.cd}/{name}.md", 'w') as file:
            file.write(f"{fileinfo[0]}{datetime.now()}\n{fileinfo[2]}")
            file.write(text)

    def del_file(self,name):
        if os.path.exists(f"{self.cd}/{name}.md"):
            os.remove(f"{self.cd}/{name}.md")




    def select_file(self,name):
        opts = ["edit","rename","delete","back"]
        os.system('cls' if os.name == 'nt' else 'clear')
        cursor = 0
        inMenu=True
        key = ""
        while inMenu:
            if key == 'UP' or key == 'LEFT':
                cursor -= 1
                if cursor < 0:
                    cursor = 0
            if key == 'DOWN' or key == 'RIGHT':
                cursor += 1
                if cursor > len(opts) - 1:
                    cursor = len(opts) - 1

            for i in range(len(opts)):
                if i == cursor:
                    print(f"[{opts[i]}]\n", end="", flush=True)
                else:
                    print(f" {opts[i]}\n", end="", flush=True)

            if key == '\r':
                if cursor == 3:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    inMenu = False
                    continue
                if cursor == 2:
                    self.del_file(name)
                    inMenu = False
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                if cursor == 1:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    inp = input("what would you like to change the file name too?\n")
                    self.rename_file(name, inp)
                    inMenu = False
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                if cursor == 0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.editor(name)
                    inMenu = False
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

            if not inMenu:
                os.system('cls' if os.name == 'nt' else 'clear')
                key = ''
                continue

            key = get_key()
            os.system('cls' if os.name == 'nt' else 'clear')


def get_time_ago(edited_time_str, current_time_str):
    try:
        t1 = datetime.fromisoformat(edited_time_str.strip())
        t2 = datetime.fromisoformat(current_time_str.strip())
    except ValueError:
        return "unknown time"
    delta = t2 - t1
    seconds = delta.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} sec"
    elif seconds < 3600:
        return f"{int(seconds // 60)} min"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours"
    else:
        return f"{int(seconds // 86400)} days"

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    app = functions("resources")
    cursor = 0
    files = app.get_files()
    key = ""
    running = True
    skip = False


    while running:


        if key == 'UP' or key == 'LEFT':
            cursor -= 1
            if cursor < 0:
                cursor = 0
        if key == 'DOWN' or key == 'RIGHT':
            cursor += 1
            if cursor > len(files)-1:
                cursor = len(files)-1

        files = app.get_files()
        filelen = len(files)
        files.append("new file")
        files.append("exit")

        for i in range(filelen):
            file = app.read_file(files[i])
            name = file[2][:-1]
            if len(name) > 11:
                name = name[:8] + "..."
            else:
                name = name
            if i == cursor:
                print(f"[{name:<11.11}]  last edited {get_time_ago(file[1],str(datetime.now()))} ago\n", end="", flush=True)
                if key == '\r':
                    app.select_file(file[2][:-1])
                    skip = True
                    continue
            else:
                print(f" {name:<11.11}   last edited {get_time_ago(file[1],str(datetime.now()))} ago\n", end="", flush=True)

        for i in range(filelen,len(files)):
            if i == cursor:
                print(f"[{files[i]}]\n", end="", flush=True)
                if files[i] == "exit" and key == '\r':
                    running = False
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("goodbye")
                    skip = True
                    continue
                if files[i] == "new file" and key == '\r':
                    app.create_file()
                    skip = True
                    continue
            else:
                print(f" {files[i]}\n", end="", flush=True)

        if skip:
            os.system('cls' if os.name == 'nt' else 'clear')
            key = ''
            skip = False
            continue


        key = get_key()
        os.system('cls' if os.name == 'nt' else 'clear')






main()