#Written by Josh Mclellan, z5163204, for python3
import socket
import sys
import time
import os
import threading


def invalid_syntax_check(cmd, connectionSocket):
    if    (((cmd[0] == "LST" or cmd[0] == "XIT") and len(cmd) != 1) 
        or ((cmd[0] == "SHT" or cmd[0] == "RMV" or cmd[0] == "RDT" or cmd[0] == "CRT") and len(cmd) != 2)
        or ((cmd[0] == "DWN" or cmd[0] == "DLT" or cmd[0] == "MSG" or cmd[0] == "UPD") and len(cmd) != 3)
        or (cmd[0] == "EDT" and len(cmd) != 4)):
        connectionSocket.send(("Incorrect syntax for " + str(cmd[0])).encode('utf-8'))
        return 1
    return 0

def reorder_msgs(msg_list, last_deleted):
    for i in range(last_deleted-1, len(msg_list)):
        if (msg_list[i][0]).isdigit() and msg_list[i][1] == " ":
            curr = int(msg_list[i][0])
            curr = curr - 1
            new_str = str(curr) + msg_list[i][1:]
            msg_list[i] = new_str
        else:
            continue
    
    return

def write_msg_list_to_file(msg_list, filename):
    f = open(filename, "w+")
    f.write('\n'.join(msg_list) + '\n')
    f.close()
    return

def count_user_msgs_in_thread(msg_list):
    ret = 0
    for i in range(0, len(msg_list)):
        if (msg_list[i][0]).isdigit() and msg_list[i][1] == " ":
            ret = ret + 1
    return ret

def delete_files_from_thread(msg_list, thread_name):
    for i in range(0, len(msg_list)):
        if (msg_list[i][0]).isdigit() and msg_list[i][1] == " ":
            continue
        else:
            filename = msg_list[i].split(" ")[2]
            os.remove((thread_name + "-" + filename))



def delete_all_files_in_dir():
    for filename in os.listdir():
        if filename == "server.py" or filename == ".vscode" or os.path.isdir(filename):
            continue
        else:
            os.remove(filename)

def get_msg_index(msg_list, index):
    for i in range(0, len(msg_list)):
        if (msg_list[i][0]).isdigit() and int(msg_list[i][0]) == index and msg_list[i][1] == " ":
            return i
            


def handle_user_commands(connectionSocket):
    while 1:
        connectionSocket.send(("Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT, SHT: ").encode('utf-8'))
        try:
            user_cmd = connectionSocket.recv(1024).decode('utf-8')
        except Exception:
            return
        #print(user_cmd)
        first_split = user_cmd.split(":", 2)
        #print(first_split)
        username = first_split[0]
        cmd = first_split[1].split(" ")
        if cmd[0] == "MSG":
            cmd[2:] = [' '.join(cmd[2:])]
        if cmd[0] == "EDT":
            cmd[3:] = [' '.join(cmd[3:])]
        if (invalid_syntax_check(cmd, connectionSocket) == 1):
            continue
        if cmd[0] == "LST":
            print(username + " issued " + cmd[0] + " command")
            if bool(active_channels):
                string_to_send = '\n'.join(active_channels.keys())
                connectionSocket.send(string_to_send.encode("utf-8"))
            else:
                connectionSocket.send(("No channels to list").encode('utf-8'))
        elif cmd[0] == "CRT":
            print(username + " issued " + cmd[0] + " command")
            if user_cmd == "CRT" or user_cmd == "CRT ":
                print(("No name provided"))
                connectionSocket.send(("Please provide a name for thread").encode('utf-8'))
            else:
                if cmd[1] in active_channels.keys():
                    print("Thread " + cmd[1] + " exists")
                    connectionSocket.send(("Thread " + cmd[1] + " exists").encode('utf-8'))
                else:
                    active_channels[cmd[1]] = []
                    user_who_created_channel[username].append(cmd[1])
                    print("Thread " + cmd[1] + " created")
                    connectionSocket.send(("Thread " + cmd[1] + " created").encode('utf-8'))
                    open(str(cmd[1]), "w+")
        elif cmd[0] == "MSG":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] in active_channels.keys():
                string_to_append = str(count_user_msgs_in_thread(active_channels[cmd[1]]) + 1) + " " + str(username) + ": " + str(cmd[2])
                active_channels[cmd[1]].append(string_to_append)
                thread_file = open(str(cmd[1]), "a")
                thread_file.write(string_to_append + "\n")
                thread_file.close()
                print("Message posted to " + cmd[1] + " thread")
                connectionSocket.send(("Message posted to " + cmd[1] + " thread").encode('utf-8'))
            else:
                print("Thread " + cmd[1] + " does not exist")
                connectionSocket.send(("Thread " + cmd[1] + " does not exist").encode('utf-8'))
        elif cmd[0] == "RDT":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] in active_channels.keys():
                string_to_send = '\n'.join(active_channels[cmd[1]])
                connectionSocket.send(string_to_send.encode("utf-8"))
                print("Thread " + cmd[1] + " read")
            else:
                print("Thread " + cmd[1] + " does not exist")
                connectionSocket.send(("Thread " + cmd[1] + " does not exist").encode('utf-8'))
        elif cmd[0] == "RMV":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] in active_channels.keys():
                if cmd[1] in user_who_created_channel[username]:
                    user_who_created_channel[username].remove(cmd[1])
                    delete_files_from_thread(active_channels[cmd[1]], cmd[1])
                    del(active_channels[cmd[1]])
                    os.remove(str(cmd[1]))
                    print("Thread " + cmd[1] + " deleted")
                    connectionSocket.send(("Thread " + cmd[1] + " deleted").encode('utf-8'))
                else:
                    print("The thread was created by another user and cannot be removed")
                    connectionSocket.send(("The thread was created by another user and cannot be removed").encode('utf-8'))
            else:
                print("The thread does not exist or was already deleted")
                connectionSocket.send(("The thread does not exist or was already deleted").encode('utf-8'))
        elif cmd[0] == "DLT":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] in active_channels.keys():
                msg_position = int(cmd[2])
                if msg_position <= (count_user_msgs_in_thread(active_channels[cmd[1]])):
                    msg_index = get_msg_index(active_channels[cmd[1]], msg_position)
                    msg_split = active_channels[cmd[1]][msg_index].split(" ")
                    if (msg_split[0].isdigit() and int(msg_split[0]) == msg_position):
                        if msg_split[1][:-1] == username:
                            del(active_channels[cmd[1]][msg_index])
                            reorder_msgs(active_channels[cmd[1]], int(cmd[2]))
                            write_msg_list_to_file(active_channels[cmd[1]], str(cmd[1]))
                            print("The message has been deleted")
                            connectionSocket.send(("The message has been deleted").encode('utf-8'))
                        else:
                            print("The  message  belongs  to another user and cannot be deleted")
                            connectionSocket.send(("The  message  belongs  to another user and cannot be deleted").encode('utf-8'))
                    else:
                        print("A message with that index does not exist")
                        connectionSocket.send(("A message with that index does not exist").encode('utf-8'))
                else:
                    print("A message with that index does not exist")
                    connectionSocket.send(("A message with that index does not exist").encode('utf-8'))
            else:
                print("The thread does not exist")
                connectionSocket.send(("The thread does not exist").encode('utf-8'))
        elif cmd[0] == "EDT":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] in active_channels.keys():
                msg_position = int(cmd[2])
                if msg_position <= (count_user_msgs_in_thread(active_channels[cmd[1]])):
                    msg_index = get_msg_index(active_channels[cmd[1]], msg_position)
                    msg_split = active_channels[cmd[1]][msg_index].split(" ")
                    if msg_split[1][:-1] == username:
                        new_string = str(msg_position) + " " + str(username) + ": " + str(cmd[3])
                        active_channels[cmd[1]][msg_index] = new_string
                        print(active_channels)
                        write_msg_list_to_file(active_channels[cmd[1]], str(cmd[1]))
                        print("The message has been edited")
                        connectionSocket.send(("The message has been edited").encode('utf-8'))
                    else:
                        print("The  message  belongs  to another user and cannot be deleted")
                        connectionSocket.send(("The  message  belongs  to another user and cannot be edited").encode('utf-8'))
                else:
                    print("A message with that index does not exist")
                    connectionSocket.send(("A message with that index does not exist").encode('utf-8'))
            else:
                print("The thread does not exist")
                connectionSocket.send(("The thread does not exist").encode('utf-8'))
        elif cmd[0] == "UPD":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] in active_channels.keys():
                connectionSocket.send(("AUTH").encode('utf-8'))
                filename_to_rec = str(cmd[1]) + "-" + str(cmd[2])
                f = open(filename_to_rec, "wb")
                f_size = int(connectionSocket.recv(1024).decode('utf-8'))
                f_written = 0
                f_data = connectionSocket.recv(1024)
                while f_written < f_size:
                    f.write(f_data)
                    f_written = f_written + len(f_data)
                    if len(f_data) < 1024:
                        f.write(f_data)
                        break
                    if f_written >= f_size:
                        break
                    f_data = connectionSocket.recv(1024)


                f.close()
                active_channels[cmd[1]].append(username + " uploaded " + str(cmd[2]))
                thread_file = open(str(cmd[1]), "a")
                thread_file.write(username + " uploaded " + str(cmd[2]) + "\n")
                thread_file.close() 
                print(username + (str(cmd[2]) + " uploaded to " + cmd[1] + " thread")) 
                connectionSocket.send((str(cmd[2]) + " uploaded to " + cmd[1] + " thread").encode('utf-8'))

            else:
                connectionSocket.send(("NAUTH").encode('utf-8'))
        elif cmd[0] == "DWN":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] in active_channels.keys():
                file_name = str(cmd[1]) + "-"+ str(cmd[2])
                if os.path.exists(file_name):
                    connectionSocket.send(("AUTH").encode('utf-8'))
                    if connectionSocket.recv(1024).decode('utf-8') == "FAUTH":
                        file_to_send = open(file_name, "rb")
                        connectionSocket.send(str(os.path.getsize(file_name)).encode('utf-8'))
                        time.sleep(0.001)
                        f_chunk = file_to_send.read(1024)
                        while f_chunk:
                            connectionSocket.send(f_chunk)
                            f_chunk = file_to_send.read(1024)

                        file_to_send.close()
                        auth_2 = connectionSocket.recv(1024).decode('utf-8')
                        if auth_2 == "AUTH":
                            print(username + " successfully downloaded " + cmd[2])
                            connectionSocket.send((cmd[2] + " successfully downloaded").encode('utf-8'))
                        else:
                            connectionSocket.send(("Download failed. Please try again").encode('utf-8'))
                    else:
                        connectionSocket.send(("Download failed. Please try again").encode('utf-8'))
                else:
                    print("The file does not exist in this thread")
                    connectionSocket.send(("The file does not exist in this thread").encode('utf-8'))
            else:
                print("The thread does not exist")
                connectionSocket.send(("The thread does not exist").encode('utf-8'))
        elif cmd[0] == "XIT":
            print(username + " issued " + cmd[0] + " command")
            #time.sleep(0.1)
            #connectionSocket.send(("XAUTH").encode('utf-8'))
            print(username + " left the server")
            connectionSocket.send(("Goodbye").encode('utf-8'))
            active_users.remove(username)
            connectionSocket.close()
            return 1
        elif cmd[0] == "SHT":
            print(username + " issued " + cmd[0] + " command")
            if cmd[1] == admin_password:
                #NEED TO ADD SHUTDOWNS FOR MULTIPLE USERS
                print(username + " shut down the server")
                connectionSocket.send(("SAUTH").encode('utf-8'))
                connectionSocket.close()
                #active_users = []
                #active_channels = {}
                #user_who_created_channel = {}
                delete_all_files_in_dir()
                return 0
            else:
                connectionSocket.send(("Incorrect password").encode('utf-8'))
        else:
            connectionSocket.send(("Invalid command").encode('utf-8'))


        time.sleep(0.001)
            

def authenticate_user(connectionSocket):
    user_flag = 0
    pass_flag = 0
    print("Client connected")
    while(pass_flag == 0):
        f = open("credentials.txt", 'r')
        connectionSocket.send(("Enter username: ").encode('utf-8'))
        username = connectionSocket.recv(1024).decode('utf-8')
        if username in active_users:
            connectionSocket.send((username +" has already logged in").encode('utf-8'))
            print(username +" has already logged in")
            continue
        else:
            for line in f:
                if line.split()[0] == username:
                    connectionSocket.send(("Enter password: ").encode('utf-8'))
                    user_flag = 1
                    password = connectionSocket.recv(1024).decode('utf-8')
                    if line.split()[1] == password:
                        connectionSocket.send(("Welcome back, "+ username).encode('utf-8'))
                        time.sleep(0.001)
                        connectionSocket.send(("AUTH").encode('utf-8'))
                        pass_flag = 1
                        active_users.append(username)
                        user_who_created_channel[username] = []
                        return
                    else:
                        print("Incorrect password")
                        connectionSocket.send(("Invalid password").encode('utf-8'))
                        connectionSocket.send(("NAUTH").encode('utf-8'))
                        break
                    
            if user_flag == 0:
                print("New user")
                connectionSocket.send(("Enter new password for " + username + ": ").encode('utf-8'))
                newpwd = connectionSocket.recv(1024).decode('utf-8')
                connectionSocket.send(("Welcome to the forum, "+ username).encode('utf-8'))
                time.sleep(0.001)
                connectionSocket.send(("AUTH").encode('utf-8'))
                r = open("credentials.txt", 'a')
                r.write('\n')
                r.write(username + " " + newpwd)
                r.close()
                active_users.append(username)
                user_who_created_channel[username] = []
                return

def handle_user_connection(connectionSocket):
    authenticate_user(connectionSocket)
    if handle_user_commands(connectionSocket) == 1:
        return
    else:
        sockets.remove(connectionSocket)
        #socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('localhost', serverPort))

        #serverSocket.shutdown(socket.SHUT_RDWR)
        serverSocket.close()
        return


serverPort = int(sys.argv[1]) 
if serverPort == 80 or serverPort == 8080 or serverPort < 1024:
    print("Invalid port choice.")
    sys.exit()


admin_password = str(sys.argv[2]) 

active_users = []
active_channels = {}
user_who_created_channel = {}


serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('localhost', serverPort))

#f = open("credentials.txt", 'r')

serverSocket.listen(1)

threads = []
sockets = []

try:
    while 1:

        print("Waiting for clients")
        connectionSocket, addr = serverSocket.accept()
        t = threading.Thread(target=handle_user_connection, args=(connectionSocket, ))
        threads.append(t)
        sockets.append(connectionSocket)
        t.start()
except socket.error:
    for s in sockets:
        #s.shutdown(socket.SHUT_RDWR)
        s.close()
    #for t in threads:
     #   print("hi")
    #    t.join()

    print("Server shutting down")

    #authenticate_user(connectionSocket)
    #if handle_user_commands(connectionSocket) == 1:
    #    continue
    #else:
    #    print("Server shutting down")
    #    break

    """
    connectionSocket.send(("Enter username: ").encode('utf-8'))
    username = connectionSocket.recv(1024).decode('utf-8')
    user_flag = 0
    for line in f:
        if line.split()[0] == username:
            connectionSocket.send(("Enter password: ").encode('utf-8'))
            user_flag = 1
            password = connectionSocket.recv(1024).decode('utf-8')
            if line.split()[1] == password:
                connectionSocket.send(("Welcome back, "+ username).encode('utf-8'))
                break
                
    if user_flag == 0:
        connectionSocket.send(("Enter new password for " + username + ": ").encode('utf-8')) 
    """
    




