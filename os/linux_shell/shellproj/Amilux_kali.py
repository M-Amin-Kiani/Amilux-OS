
# mohammad amin kiani 4003613052
# yazdan afra 4003613005

import subprocess
import os
import sys
import grp
import pwd
import shutil
import signal
from datetime import datetime

class bcolors:
    FAIL = '\033[93m'
    ENDC = '\033[0m'

# kali shell :
# COMMANDS        
# 1. info XX    - Checks file/dir exists
# 2. all        - Shows files in directory
# 3. delete XX  - Checks directory/ file exists and delete it
# 4. copy XX YY - Copies XX in YY
# 5. where      - Shows current directory
# 6. dirgo DD   - Checks directory exists and enters
# 7. dirback    - Check you're not in the root and goes up in the directory tree
# 8. exit       - terminate program
# 9. help       - SOS for you!
# 10. history
# 11. scmd
# 12. clear
# 11. program name to run external program
# Type any linux command!

 # column headers
header_filescmd = ["File Name", "Type"] 
global dirpath
header_infocmd = ["File Name", "Type", "Owner User", "Owner Group", "Last modified time", "Size", "Executable" ]
width= [25, 11 , 20, 20, 26, 11, 11]


path = os.environ['PATH']
THE_PATH = path.split(':')

# ----------------------
# History features
# ----------------------
history_file = 'kali_shell_history.txt'

def save_command_to_history(command):
    with open("history.jiz", 'a') as history_file:
        history_file.write(command + '\n')

def print_history():
    with open("history.jiz", 'r') as history_file:
        print(history_file.read())

def run_command_from_history(index):
    with open("history.jiz", 'r', encoding='utf-8') as history_file:
        commands = history_file.readlines()
        if 0 <= index < len(commands):
            command_to_run = commands[index].split()[0]  # Extract only the first word (command name)
            runCmd(command_to_run.strip().split())  # Strip newline and split into fields
        else:
            print("Invalid history index.")

def clear_history():
    with open("history.jiz", 'w'):
        pass

# ========================
#    Run command
#    Run an executable somewhere on the path
#    Any number of arguments
# ========================
def runCmd(fields):
  global PID, THE_PATH

  cmd = fields[0]
  cnt = 0
  args = []
  while cnt < len(fields):
      args.append(fields[cnt])
      cnt += 1

  execname = add_path(cmd, THE_PATH)

  # run the executable
  if not execname:
      print ('Executable file ' + str(cmd) +' not found')
  else:
    # execute the command
    print(execname)

  # execv executes a new program, replacing the current process; on success, it does not return.
  # On Unix, the new executable is loaded into  the current process, and will have the same process id as the caller.
  try:
    pid = os.fork()
    if pid == 0:
      os.execv(execname, args)
      os.exit(0)
    else:
      # wait for the child process to exit
      # the 'status' variable is updated with the exit status

      # If we pass 0 to os.waitpid, the request is for the status of
      # any child in the process group of the current process.
      # If we pass -1, the request pertains to any child of the current process.
      _, status = os.waitpid(0, 0)
      # this function gets the exit code from the status
      #if os.WIFSIGNALED(status):
        #returnedsig = os.WTERMSIG(status)
        #signal.signal(signal.SIGINT, sigint_handler)
      exitCode = os.WEXITSTATUS(status)
      if exitCode == 0:
        print ("Complete with return code %d" % (exitCode))
  except :
    print ('Something went wrong there...!')
    os._exit(0)

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
            stat_info = os.stat(argument)
            uid = stat_info.st_uid
            gid = stat_info.st_gid
            user = pwd.getpwuid(uid)[0]
            group = grp.getgrgid(gid)[0]
            info.append(user)
            info.append(group)
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
                print ("File deleted :)")
            except OSError:
                print("you cannot delete this file...!")

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
        print(output)
        print('-' * 36)
    elif type_header == "info":
        while field_num < len(header_infocmd):
            output += '{field:{fill}<{width}}'.format(field=header_infocmd[field_num], fill=' ', width=width[field_num])
            field_num += 1
        print(output)
        length = sum(width)
        print('-' * length)


def get_file_type(filename):

  if os.path.isdir(filename):
    return "Dir"
  elif os.path.isfile(filename):
    return "File"
  elif os.path.islink(filename):
    return "Link"


def print_help():
    print("\x1b[42m{}\n{}\x1b[0m".format(
        """ the list of Builtin commands that you can use :
    - history: show your commands history
    - all: the same as dir
    - info: the details of...
    - clear: clear the screen
    - delete: del
    - copy: ctrl + c
    - clearhistory: clear your history
    - dirback/dirgo: change directory
    - where: see the directory that you are currently in
    - exit: exit the aminkiani_shell
    - help: it just me...""",
        'use \'|\' for piping and for file chaining use "<<" and ">>" '))


# - main : ------------------------------------------------------------------------------------------------------------

while True:

    dirpath = os.getcwd()
    base = os.path.basename(dirpath)
    line = input(bcolors.FAIL + base + " AminKiani_Shell>> " +bcolors.ENDC)
    fields = line.split()
    # split the command into fields stored in the fields list
    # fields[0] is the command name and anything that follows (if it follows) is an argument to the command
    # Save command to history
    save_command_to_history(' '.join(fields))  # Join fields back into a full command

    if fields[0] == "all":
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
    elif fields[0] == "where":
        where_cmd(fields)
    elif fields[0] == "dirgo":
        down_cmd(fields)
    elif fields[0] == "dirback":
        up_cmd(fields)
    elif fields[0] == "exit":
        finish_cmd(fields)
    elif fields[0] == "help":
        print_help()
    elif fields[0] == "history":  # نگهداری تاریخچه دستورات وارد شده توسط کاربر.
        print_history()
    elif fields[0] == "scmd":  # امکان مشاهده و اجرای مجدد دستورات از تاریخچه
        if len(fields) > 1:
            try:
                index = int(fields[1].strip())
                run_command_from_history(index - 1)
            except ValueError:
                print("Invalid history index. Please enter a number.")
        else:
            print("Usage: scmd <index>")
    elif fields[0] == "clearhistory":   # امکان پاکسازی تاریخچه دستورات.
        clear_history()
        print("History cleared.")
    else:                     # اجرای دستورات:
        runCmd(fields)        # do all of kali cmd ( not my cmd )