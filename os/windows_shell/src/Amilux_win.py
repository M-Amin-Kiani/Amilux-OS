# mohammad amin kiani 4003613052
# yazdan afra 4003613005

import subprocess
import os
import sys
# import grp
# import pwd
import shutil
import signal
from datetime import datetime

import readline
readline.parse_and_bind("set history filename ~/.shelly_history")  # Enable history saving
readline.set_history_length(100)  # Set history length (optional)

class bcolors:
    FAIL = '\033[93m'
    ENDC = '\033[0m'


# column headers
header_filescmd = ["File Name", "Type"]
global dirpath
header_infocmd = ["File Name", "Type", "Owner User", "Owner Group", "Last modified time", "Size", "Executable" ]
width= [25, 11 , 20, 20, 26, 11, 11]


path = os.environ['PATH']
THE_PATH = path.split(':')

def get_owner_group(filename):

    import win32security

    sd = win32security.GetFileSecurity(filename, win32security.OWNER_SECURITY_INFORMATION)
    owner_sid = sd.GetSecurityDescriptorOwner()
    owner_name, owner_domain, _ = win32security.LookupAccountSid(None, owner_sid)

    sd = win32security.GetFileSecurity(filename, win32security.GROUP_SECURITY_INFORMATION)
    group_sid = sd.GetSecurityDescriptorGroup()
    group_name, group_domain, _ = win32security.LookupAccountSid(None, group_sid)

    return owner_name, group_name


def runCmd(fields):
    global PID, THE_PATH

    # Split commands and pipes
    commands = []
    current_command = []
    for field in fields:
        if field == "|":
            commands.append(current_command)
            current_command = []
        else:
            current_command.append(field)
    commands.append(current_command)

    try:
        # Create child processes and connect pipes
        processes = []
        for i, cmd in enumerate(commands):
            if cmd[0] == "info":  # Handle `info` command separately
                info_cmd(cmd[1:])
            else:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE if i < len(commands) - 1 else None)
                processes.append(proc)

            # Connect pipes between processes
            for j in range(len(processes) - 1):
                processes[j].stdout.pipe(processes[j + 1].stdin)

            # Wait for child processes to finish
        for proc in processes:
            proc.wait()

    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

# ========================
#    Constructs the full path used to run the external command
#    Checks to see if the file is executable
# ========================

def add_path(cmd, path):
    if cmd[0] not in ['/', '.']:
        for d in path:
            execname = d + "/" +cmd
            if os.path.isfile(execname) and os.access(execname, os.X_OK):
                return execname
        return False
    else:
        return cmd

# ========================
#   FILES COMMAND
#   List file and directory names
#   No arguments
# ========================
def files_cmd(fields, filename):
    global info

    info = []
    if checkArgs(fields, 0):
        info.append(filename)
        info.append(get_file_type(filename))


# ========================
#   INFO COMMAND
#   List file information
#   1 argument: file name
# ========================
def info_cmd(fields):
    global info
    info = []
    if checkArgs(fields, 1):
        argument = fields[1]

        if os.access(argument, os.F_OK):
            print_header("info")
            info.append(argument)
            info.append(get_file_type(argument))
            try:
                owner_name, group_name = get_owner_group(argument)
            except:
                owner_name = "N/A"
                group_name = "N/A"
            info.append(owner_name)
            info.append(group_name)
            info.append(datetime.fromtimestamp(os.stat(argument).st_mtime).strftime('%b %d %Y %H:%M:%S'))
            info.append(os.path.getsize(argument))
            if os.access(argument, os.X_OK):
                info.append("No")
            else:
                info.append("Yes")
        else:
            print("the file/dir doesn't exists...!")

# ========================
#   DELETE COMMAND
#   Delete the file
#   1 argument: file name
# ========================
def delete_cmd(fields):

    if checkArgs(fields, 1):
        argument = fields[1]

        if os.access(argument, os.F_OK):
            try:
                os.remove(argument)
                print ("the file deleted...!")
            except OSError:
                print("you can not delete this file (OS) ...!")

        else:
            print("the file/dir doesn't exists...!")


# ========================
#   COPY COMMAND
#   Copy the 'from' file to the 'to' file
#   2 arguments: 'from' file and 'to' file
# ========================
def copy_cmd(fields):
    if checkArgs(fields, 2):
        argument_1 = fields[1]
        argument_2 = fields[2]
        if os.access(argument_1, os.F_OK) and not os.access(argument_2, os.F_OK):
            shutil.copyfile(argument_1, argument_2)
        else:
            print("the source file or the destination file doesn't exists...!")


# ========================
#   WHERE COMMAND
#   Show the current directory
#   No arguments
# ========================
def where_cmd(fields):
    if checkArgs(fields, 0):
        dirpath = os.getcwd()
        print(dirpath)


# ========================
#   DOWN COMMAND
#   Change to the specified directory, inside the current directory
#   1 argument: directory name
# ========================
def down_cmd(fields):

    if checkArgs(fields, 1):
        argument = fields[1]
        if os.access(argument, os.F_OK):
            os.chdir(argument)
        else:
            print("the directory doesn't exists...!")


# ========================
#   UP COMMAND
#   Change to the parent of the current directory
#   No arguments
# ========================
def up_cmd(fields):
    if checkArgs(fields, 0):
        if os.path.realpath(dirpath) == os.path.realpath("/"):
            print("You can't go up, you're in the root!")
        else:
            os.chdir("../")


# ========================
#   FINISH COMMAND
#   Exits the shell
#   No arguments
# ========================
def finish_cmd(fields):
    if checkArgs(fields, 0):
        exit()

# ----------------------
# Other functions
# ----------------------
def checkArgs(fields, num):
    numArgs = len(fields) - 1
    if numArgs == num:
        return True
    if numArgs > num:
        print ("  Unexpected argument " + fields[num+1] + "for command " + fields[0])
    else:
        print ("  Missing argument for command " + fields[0])

    return False

def print_file_info():
    fieldNum = 0
    output = ''
    while fieldNum < len(info):
        output += '{field:{fill}<{width}}'.format(field=info[fieldNum], fill=' ', width=width[fieldNum])
        fieldNum += 1
    print (output)


# Print a header.
# Print the header entries, using the corresponding width entries.
def print_header(type_header):
    field_num = 0

    output = ''
    if type_header == "files":
        while field_num < 2:
            output += '{field:{fill}<{width}}'.format(field=header_infocmd[field_num], fill=' ', width=width[field_num])
            field_num += 1
        print  (output)
        print ('-' * 36)
    elif type_header == "info":
        while field_num < len(header_infocmd):
            output += '{field:{fill}<{width}}'.format(field=header_infocmd[field_num], fill=' ', width=width[field_num])
            field_num += 1
        print  (output)
        length = sum(width)
        print ('-' * length)


def get_file_type(filename):

  if os.path.isdir(filename):
    return "Dir"
  elif os.path.isfile(filename):
    return "File"
  elif os.path.islink(filename):
    return "Link"


def print_help():
    print("\x1b[47m{}\n{}\x1b[0m".format(
        """ the list of Builtin commands that you can use :
    - history: show your commands history
    - clear: clear the screen
    - clearhistory: clear your history
    - dirback/dirthen: change directory
    - where: see the directory that you are currently in
    - exit: exit the aminkiani_shell
    - help: it just me...""",
        'use \'|\' for piping and for file chaining use "<<" and ">>" '))


# ----------------------------------------------------------------------------------------------------------------------

while True:
        dirpath = os.getcwd()
        base = os.path.basename(dirpath)
        line = input(bcolors.FAIL + base + " AminKiani_Shell>> " +bcolors.ENDC)
        fields = line.split()
        # split the command into fields stored in the fields list
        # fields[0] is the command name and anything that follows (if it follows) is an argument to the command

        if fields[0] == "all":               # ls
            print_header("files")
            for filename in os.listdir('.'):
                files_cmd(fields, filename)
                print_file_info()
        elif fields[0] == "info":
            info_cmd(fields)
            print_file_info()
        elif fields[0] == "delete":
            delete_cmd(fields)
        elif fields[0] == "copy":
            copy_cmd(fields)
        elif fields[0] == "where":            # pwd
            where_cmd(fields)
        elif fields[0] == "dirthen":
            down_cmd(fields)
        elif fields[0] == "dirback":
            up_cmd(fields)
        elif fields[0] == "history":
            """Corrected code to iterate through history using indices"""
            if readline.get_history_length() > 0:  # Check if history exists
                for i in range(readline.get_history_length()):
                    item = readline.get_history_item(i + 1)  # Access items starting from 1
                    print("\x1b[35m{}\x1b[0m".format(item))
            else:
                print("No history available yet.")

        elif fields[0] == "clearhistory":
            finish_cmd(fields)
        elif fields[0] == "cls":
            if sys.platform.startswith('win'):
                os.system('cls')
            else:
                os.system('clear')

        elif fields[0] == "exit":
            finish_cmd(fields)
        elif fields[0] == "help":
            print_help()
        else:
            # Check if the command contains a pipe
            if "|" in fields:
                # Use the `runCmd` function to handle piping
                runCmd(fields)
            else:
                # Run the command as a normal command  ===> kali + win + ubu + ... else
                runCmd([fields])  # Enclose in a list for consistency