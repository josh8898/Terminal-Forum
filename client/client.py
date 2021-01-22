#coding: utf-8
from socket import *
import sys
import time
import os


serverName = 'localhost'

serverName = str(sys.argv[1])

serverPort = int(sys.argv[2]) 
if serverPort == 80 or serverPort == 8080 or serverPort < 1024:
    print("Invalid port choice.")
    sys.exit()

clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((serverName, serverPort))

logged_in = False
username = ""

while 1:
    if logged_in == False:
        userNamePrompt = clientSocket.recv(1024)
        user = input(userNamePrompt.decode('utf-8'))
        clientSocket.send(user.encode('utf-8'))
        passwordPrompt = clientSocket.recv(1024)
        if "has already logged in" in passwordPrompt.decode('utf-8'):
            print(passwordPrompt.decode('utf-8'))
            continue
        passw = input(passwordPrompt.decode('utf-8'))
        clientSocket.send(passw.encode('utf-8'))
        print(clientSocket.recv(1024).decode('utf-8'))
        auth_t = clientSocket.recv(1024).decode('utf-8')
        if auth_t == "AUTH":
            logged_in = True
            username = user
    
    user_cmd = input(clientSocket.recv(1024).decode('utf-8'))

    cmd_split = user_cmd.split(" ")
    if cmd_split[0] == "UPD":
        clientSocket.send((str(user) + ":" + user_cmd).encode('utf-8'))
        auth_1 = clientSocket.recv(1024).decode('utf-8')
        if auth_1 != "AUTH":
            print("Thread " + cmd_split[1] + " does not exist")
            continue
        else:
            file_to_send = open(cmd_split[2], "rb")
            clientSocket.send(str(os.path.getsize(cmd_split[2])).encode('utf-8'))
            time.sleep(0.001)
            f_chunk = file_to_send.read(1024)
            while f_chunk:
                clientSocket.sendall(f_chunk)
                f_chunk = file_to_send.read(1024)
                if (len(f_chunk) < 1024):
                    clientSocket.send(f_chunk)
                    break
            
            file_to_send.close()
    elif cmd_split[0] == "DWN":
        clientSocket.send((str(user) + ":" + user_cmd).encode('utf-8'))
        auth_1 = clientSocket.recv(1024).decode('utf-8')
        if auth_1 != "AUTH":
            print(auth_1)
            continue
        else:
            clientSocket.send(("FAUTH").encode('utf-8'))
            f = open(cmd_split[2], "wb")
            f_size = int(clientSocket.recv(1024).decode('utf-8'))
            f_written = 0
            f_data = clientSocket.recv(1024)
            while f_written < f_size:
                f.write(f_data)
                f_written = f_written + len(f_data)
                if len(f_data) < 1024:
                    f.write(f_data)
                    break
                if f_written >= f_size:
                    break
                f_data = clientSocket.recv(1024)
                
            f.close()

            clientSocket.send(("AUTH").encode('utf-8'))
    elif cmd_split[0] == "XIT":
        clientSocket.send((str(user) + ":" + user_cmd).encode('utf-8'))
        print(clientSocket.recv(1024).decode('utf-8'))
        clientSocket.close()
        break
    elif cmd_split[0] == "SHT":
        clientSocket.send((str(user) + ":" + user_cmd).encode('utf-8'))
        if clientSocket.recv(1024).decode("utf-8") == "SAUTH":
            print("Goodbye. Server shutting down")
            clientSocket.close()
            break
        else:
            print(clientSocket.recv(1024).decode('utf-8'))
    else:
        clientSocket.send((str(user) + ":" + user_cmd).encode('utf-8'))

    print(clientSocket.recv(1024).decode('utf-8'))
