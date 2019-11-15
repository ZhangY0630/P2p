# Sample code for Multi-Threaded Server
# Python 3
# Usage: python3 UDPserver3.py
# coding: utf-8
import sys
import threading
import time
from socket import *
from time import sleep
import select

# Server will run on this port
#serverPort = 12345
t_lock = threading.Condition()
# will store clients info in this list
clients = []
blacklist = {}
currentBlockThread = []


serverPort = int(sys.argv[1])
print(serverPort)
BlockTime = int(sys.argv[2])
print(BlockTime)
Timeout = float(sys.argv[3])
print(Timeout)


class Socketprocess:
    global clients

    def __init__(self, connectionSocket, clientAddress):
        self.connectionSocket = connectionSocket
        self.clientAddress = clientAddress

    def receiveMessage(self):
        # try:
        #     ready = select.select([self.connectionSocket], [], [], timeout)
        # except:
        #     print(ready)
        # if ready[0]:
        #     message = self.connectionSocket.recvfrom(2048)
        # else:
        #     message = "timeout"
        #     print("timeout")

        #readable, writable, exceptional = select.select(self.connectionSocket, [], [],timeout)

        message = self.connectionSocket.recvfrom(2048)
        print("message received...")
        message = message[0].decode()
        if (message == ""):
            raise KeyboardInterrupt
        message = message.split(" ")
        print(message)
        return message

    def closeSocket(self):
        print("Client Closing...")
        self.connectionSocket.close()
        # if self.clientAddress in clients:
        #     clients.remove(self.clientAddress)

    def sendMessage(self, serverMessage):
        self.connectionSocket.send(serverMessage.encode())


def userAuth(username, password):
    with open('./credentials.txt', "r+") as file:
        for data in file:
            data = data.rstrip()
            data = data.split(" ")
            if data[0] == username and data[1] == password:
                return True
    return False
def NameOnList(username):
    with open('./credentials.txt', "r+") as file:
        for data in file:
            data = data.rstrip()
            data = data.split(" ")
            if data[0] == username :
                return True
    return False

def blockUsr():

    time.sleep(BlockTime)

def UserLoginFailAttempt(username):
    global blacklist
    if username not in blacklist and NameOnList(username):
         blacklist[username]=0
    if( not  NameOnList(username)):
        return "Invalid PassWord, Please try again"

    blacklist[username] = blacklist[username] + 1

    if blacklist[username] <= 3 :
        return "Invalid PassWord, Please try again"
    else:
        th = threading.Thread(name = username,target=blockUsr)
        th.start()
        currentBlockThread.append(th)
        return "Invalid PassWord, You account has been blocked"

def CheckBlockingDuratoin(username):
    global blacklist

    for b in currentBlockThread:
        print(b.getName())
        if(b.getName()== username):
            print(b.isAlive())
            if( b.isAlive()):
                return True
            else:
                currentBlockThread.remove(b)
                print(currentBlockThread)
                return False
def recv_handler(connectionSocket, clientAddress):
    print("Conection set up...")
    p = Socketprocess(connectionSocket, clientAddress)
    Auth = False
    global t_lock
    global blacklist
    while 1:

        try:
            message = p.receiveMessage()
        except :
            p.closeSocket()
            Auth = False
            connectionSocket, clientAddress = serverSocket.accept()
            p = Socketprocess(connectionSocket,clientAddress)
            continue
        serverMessage = "Recived Command"
        with t_lock:
            if(not Auth):
                username = message[0]
                if(CheckBlockingDuratoin(username)):
                    serverMessage = "Still under Blocked"
                    p.sendMessage(serverMessage)
                    t_lock.notify()
                    continue;


                if(userAuth(username,message[1])):
                    clients.append(clientAddress)
                    Auth = True
                    serverMessage = "Welcome"
                else:
                    serverMessage = UserLoginFailAttempt(username)
            else:
                serverMessage = message[0]
            p.sendMessage(serverMessage)
            t_lock.notify()


def initialise_server():
    # socket setup
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    except:
        print("Could not create socket")
        sys.exit(0)

    print("[-] Socket Created")

    # bind socket
    try:
        serverSocket.bind(("localhost", serverPort))
        serverSocket.setblocking(0)
        print("[-] Socket Bound to port " + str(serverPort))
    except:
        print("Bind Failed")
        sys.exit()

    serverSocket.listen(1)
    print("Listening...")
    serverSocket.setblocking(0)
    return serverSocket


def connection_setup(server_socket,read_list):
    # try:
    #     connectionSocket, clientAddress = serverSocket.accept()
    #     recv_thread = threading.Thread(name=clientAddress, target=recv_handler,
    #                                    args=(connectionSocket, clientAddress))
    #     recv_thread.daemon = True
    #     recv_thread.start()
    #     time.sleep(2)
    # except (KeyboardInterrupt, SystemExit):
    #     print("\nClosing Server....")
    #     serverSocket.close()
    #     sys.exit(0)


    readable, writable, errored = select.select(read_list, [], [], 3)
    for s in readable:
        if s is server_socket:
            client_socket, address = server_socket.accept()
            read_list.append(client_socket)
        else:
            print("go client")
            data = s.recv(1024)
            if data:
                s.send(data)
            else:
                s.close()
                read_list.remove(s)



if __name__ == "__main__":

    #server_socket = initialise_server()
    # read_list = [server_socket]
    # while True:
    #     connection_setup(server_socket,read_list)

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    server_socket.setblocking(0)

    read_list = [server_socket]
    while True:
        print(read_list)
        readable, writable, errored = select.select(read_list, [], [],6)
        if(readable or writable or errored):
            for s in readable:
                if s is server_socket:
                    client_socket, address = server_socket.accept()
                    read_list.append(client_socket)
                    print("Connection from", address)
                else:
                    data = s.recv(1024)
                    if data:
                        s.send(data)
                    else:
                        s.close()
                        read_list.remove(s)
        else:
            print("timeout happen")