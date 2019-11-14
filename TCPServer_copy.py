# Sample code for Multi-Threaded Server
# Python 3
# Usage: python3 UDPserver3.py
# coding: utf-8
import sys
import threading
import time
from socket import *

# Server will run on this port
serverPort = 12000
t_lock = threading.Condition()
# will store clients info in this list
clients = []
blocklist = {}
# would communicate with clients after every second
# UPDATE_INTERVAL = 1
timeout = False
currentBlockThread = []
def blockUsr():
    time.sleep(10)

class Socket():



    try:
        message = connectionSocket.recvfrom(2048)
        print("i receive a message")
        message = message[0].decode()
        username = message.split(" ")[0]
        if (message[0] == ""):
            raise KeyboardInterrupt
    except:
        print("Client Closing...")
        Auth = False
        connectionSocket.close()
        if (clientAddress in clients):
            clients.remove(clientAddress)
        connectionSocket, clientAddress = serverSocket.accept()


def recv_handler(connectionSocket, clientAddress):
    global t_lock
    global clients
    global blocklist
    global currentBlockThread
    Auth = False
    print('Server is ready for service')

    Blocked = False
    while (1):

        try:
            message = connectionSocket.recvfrom(2048)
            print("i receive a message")
            message = message[0].decode()
            username = message.split(" ")[0]
            if(message[0]==""):
                raise KeyboardInterrupt
        except:




        # if username not in blocklist : #have to handle not in list which don't need to record
        #     blocklist[username] = 0
        # else:
        #     if blocklist[username]>3:
        #         for block in currentBlockThread:
        #             if block.isAlive()==False:
        #                 currentBlockThread.remove(block)
        #             if block.getName == username:
        #                 serverMessage = "Blocked"
        #                 connectionSocket.send(serverMessage.encode())
        #                 continue


        # received data from the client, now we know who we are talking with
        # get lock as we might me accessing some shared data structures

        with t_lock:







            if clientAddress not in clients: # store client information (IP and Port No) in list

                            blocklist[username] = 0
                            print("pass")
                            Auth = True
                            clients.append(clientAddress)
                    serverMessage = "Welcome"
                if (not Auth):





                    # blocklist[username] = blocklist[username] + 1
                    # if(blocklist[username] <= 3):
                    #     serverMessage = "Invalid PassWord, Please try again"
                    # else:
                    serverMessage = "Invalid PassWord, You account has been blocked"
                        # thread = threading.Thread(name = username,target=blockUsr)
                        # currentBlockThread.append(thread)
                    print("wrong")

            else:
                print(message)

            t_lock.notify()

            # return
            # notify the thread waiting


try:
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
except socket.error as msg:
    print("Could not create socket. Error Code: ", str(msg[0]), "Error: ", msg[1])
    sys.exit(0)

print("[-] Socket Created")

# bind socket
try:
    serverSocket.bind(("localhost", serverPort))
    #serverSocket.setblocking(0)
    print("[-] Socket Bound to port " + str(serverPort))
except socket.error as msg:
    print("Bind Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]))
    sys.exit()



# this is the main thread

