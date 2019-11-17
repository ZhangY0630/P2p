# Sample code for Multi-Threaded Server
# Python 3
# Usage: python3 UDPserver3.py
# coding: utf-8
import sys
import threading
import time
from socket import *
import parseCommand
import notifiers

# Server will run on this port
#serverPort = 12345
t_lock = threading.Condition()
# will store clients info in this list
clients = []
blacklist = {}
currentBlockThread = []
startTimeRecord= {}

serverPort = int(sys.argv[1])
print(serverPort)
BlockTime = int(sys.argv[2])
print(BlockTime)
Timeout = int(sys.argv[3])
print(Timeout)




class Socketprocess:


    def __init__(self, connectionSocket, clientAddress):
        self.name = None;
        self.connectionSocket = connectionSocket
        self.clientAddress = clientAddress

    def setName(self,name):
        self.name= name;

    def DetectReceiveTimeout(self,e):

        start_time = time.time()
        while not e.isSet():

            if (time.time() - start_time > Timeout):
                print("Timeout Detect!")
                serverMessage = "Timeout"
                self.sendMessage(serverMessage)
                break

    def receiveMessage(self):

        ReceiveTimeout = threading.Event()
        print("loop")
        print(ReceiveTimeout.isSet())
        timeout_threading = threading.Thread(target= self.DetectReceiveTimeout,args=(ReceiveTimeout,))
        timeout_threading.start()
        message = self.connectionSocket.recvfrom(2048)
        ReceiveTimeout.set()



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

    if blacklist[username] < 3 :
        return "Invalid PassWord, Please try again"
    else:
        th = threading.Thread(name = username,target=blockUsr)
        th.start()
        currentBlockThread.append(th)
        return "Invalid PassWord, You account has been blocked"

def CheckBlockingDuratoin(username):
    global currentBlockThread

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
def RemoveFromBlacklist(username):
    global blacklist
    blacklist[username]=0



def recv_handler(connectionSocket, clientAddress,notifier):
    print("Conection set up...")
    p = Socketprocess(connectionSocket, clientAddress)
    Auth = False
    global t_lock
    global blacklist
    while 1:

        try:
            message = p.receiveMessage()
        except (KeyboardInterrupt, RuntimeError) as e:
            print(e)
            notifier.logout(p)
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
                    RemoveFromBlacklist(username)
                    clients.append(clientAddress)
                    p.setName(username)
                    notifier.login(p)
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
        #serverSocket.settimeout(Timeout);
    except:
        print("Could not create socket")
        sys.exit(0)

    print("[-] Socket Created")

    # bind socket
    try:
        serverSocket.bind(("localhost", serverPort))
        #serverSocket.setblocking(0)
        print("[-] Socket Bound to port " + str(serverPort))
    except:
        print("Bind Failed")
        sys.exit()

    serverSocket.listen(1)
    print("Listening...")
    return serverSocket


def connection_setup(serverSocket,notifier):
    try:

        connectionSocket, clientAddress = serverSocket.accept()

        send_thread = threading.Thread()

        recv_thread = threading.Thread(name=clientAddress, target=recv_handler,
                                       args=(connectionSocket, clientAddress,notifier))

        recv_thread.daemon = True
        recv_thread.start()
        #time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        print("\nClosing Server....")
        serverSocket.close()
        sys.exit(0)



if __name__ == "__main__":
    serverSocket = initialise_server()
    notifier = notifiers.notifier()
    while True:
        connection_setup(serverSocket,notifier)
