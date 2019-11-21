import os
import random

import sys
import threading
import time
from socket import *
from queue import Queue
#
PrivateMessageSession = []
socketlist = []
download_buffer = {}
loginName = None

num_chunks = 10
global clientSocket
#PrivateSendSession = []

def checkInvalidLogin(receivedMessage):
    if (receivedMessage.decode()=="Invalid PassWord, Please try again" or receivedMessage.decode()=="User Already Login"):
        print(receivedMessage.decode())
        return True
    if(receivedMessage.decode()== "Invalid PassWord, You account has been blocked" or receivedMessage.decode()== "Still under Blocked"):
        #print("la")
        print(receivedMessage.decode())
        raise SystemExit
    if(receivedMessage.decode()==""):
        raise SystemExit
    if(receivedMessage.decode()=="Timeout"):
        print("\nTimeout")
        raise TimeoutError

    return False

def fileBuffer(file,size,name):
    global download_buffer

    count = 1
    with open(file,"rb") as f:
        while 1:
            r = f.read(size)
            if (r == b""):
                return
            if(count<10):
                final = name+"0"+str(count)
            else:
                final = name + str(count)
            download_buffer[final] = r

            count = count+1

def haveResource(filename,socket):
    global download_buffer
    global num_chunks
    result = p2pInitial(filename,"file")
    if result :
        for resource in download_buffer.keys():
            msg = "register "+filename+" "+resource+" "+str(num_chunks)+" "+ str(sys.getsizeof(download_buffer[resource])) +" NoReplay"
            socket.send(msg.encode())
            time.sleep(0.5)
        return True
    return False



def recv_handler(clientSocket,end,m,p2p,selfInfo):
    global loginName
    global num_chunks
    global download_buffer
    usr = input("UserName: \n")
    loginName = usr
    pw = input("PassWord: \n")
    message = usr + " " + pw
    clientSocket.send(message.encode())
    try:
        while 1:


            time.sleep(0.1)
            receive = clientSocket.recvfrom(2048)
            if (checkInvalidLogin(receive[0])):
                usr = input("UserName: \n")
                loginName = usr
                pw = input("PassWord: \n")
                message = usr + " " + pw

                clientSocket.send(message.encode())
                continue

            receivedMessage = receive[0]
            if (receivedMessage.decode().split()[0] == "private"):
                content = receivedMessage.decode().split()
                address = content[1]
                port = content[2]
                name = content[3]
                print("Start private messaging with "+ name)
                p2p.put((address,port,name))
                continue
            if( receivedMessage.decode().split()[0] == "personal" ):
                content = receivedMessage.decode().split()
                address = content[1]
                port = content[2]
                selfInfo.put((address, port))
                continue

            if (receivedMessage.decode().split()[0] == "request"):
                filename = receivedMessage.decode().split()[1]
                user = receivedMessage.decode().split()[2]
                if(haveResource(filename,clientSocket)):
                    msg = "SuccessRegister "+filename+ " "+user
                    clientSocket.send(msg.encode())
                continue
            if (receivedMessage.decode().split()[0] == "search"):
                filename = receivedMessage.decode().split()[1]
                haveResource(filename,clientSocket)
                continue

            if (receivedMessage.decode().split()[0] == "ChunkList"):
                filename = receivedMessage.decode().split()[1]
                chunklist = receivedMessage.decode().split()[2:]
                #if have no thing in the buffer, finish download or new
                if not (download_buffer):
                    for c in chunklist:
                        download_buffer[c] = None
                l = bufferlist(download_buffer)
                choose = random.choice(l)
                msg = "searchChunks "+filename+" "+choose

                clientSocket.send(msg.encode())
                continue

            if (receivedMessage.decode().split()[0] == "Available"):
                content = receivedMessage.decode().split()
                ori = content
                chunk = content[-1]
                filename = content[-2]

                content = content[:-2]
                namelist = content[1:]
                name = random.choice(namelist)

                # #To do need to limit the num of loop
                socket = checkPrivateMessageList(name)
                if not socket:
                    msg = "startprivate "+name
                    clientSocket.send(msg.encode())
                    time.sleep(1)
                    msg = " ".join(ori)
                    clientSocket.send(msg.encode())
                    continue
                print("Downloading.....")
                msg = "download "+filename+" "+chunk
                socket.sendMessage(msg)
                continue


            print(receive[0].decode())
            m.set()

    except (KeyboardInterrupt, SystemExit, EOFError,TimeoutError,ConnectionResetError):
        clientSocket.shutdown(1)
        clientSocket.close()
        end.set()

def bufferlist(buffer):
    l = []
    for key in buffer.keys():
        if(buffer[key]==None):
            l.append(key)
    return l

def checkPrivateMessageList(user):
    global PrivateMessageSession
    for p in PrivateMessageSession:
        if(p.name == user ):
            return p
    return None


def checkP2pMsg(msg):
    global loginNames
    global PrivateMessageSession
    content = msg.split()
    if(content==""):
        return False
    if(content[0]=="private"):
        p = checkPrivateMessageList(content[1])
        if(p!=None):
            if(content[2] == "download"):
                p.sendMessage(" ".join(content[2:]))
                return True

            m = " ".join(content[2:])
            m = str(loginName)+"(private)"+": "+m
            p.sendMessage(m)
        else:
            print("User haven't establish the connection or user offline")
        return True
    elif(content[0]=="stopprivate"):
        for p in PrivateMessageSession:
            if p.name == content[1]:
                print("Closing p2p message with "+ str(content[1]))
                p.closesocket()
                return True
        print("Invalid p2p messaging close. Can't find user in current p2p list")
        return True
    else:
        return False



def checkFileTransfer(message,socket):
    global num_chunks
    content = message.split(" ")
    if(content[0]=="register"):
        filename = content[1]
        ostat = os.stat(filename)
        if(ostat.st_size >  2048*num_chunks):
            print(str(num_chunks)+" chunks in this case can't hold it, make sure file smaller than 20kb ")
            return True
        try:
            with open(filename,"rb"):
                message = message+" Reply"
                socket.send(message.encode())
                return True
        except FileNotFoundError:
            print("File doesn't exist")
        return True
    return False

def checkdownload(message):
    if(message.split()[0]=="p2pDownload"):
        return True
    return False

def send_handler(clientSocket,end,m):
    global download_buffer
    try:
        while 1:
            while(m.isSet()):
                message = input()
                if(checkP2pMsg(message)):
                    continue
                if(checkFileTransfer(message,clientSocket)):
                    continue
                if(checkdownload(message)):
                    download_buffer= {}
                clientSocket.send(message.encode())

    except (KeyboardInterrupt, SystemExit, EOFError):
        clientSocket.shutdown(1)
        clientSocket.close()
        end.set()
def writeFile(buffer,file):
    with open("download_"+file,"ab") as f:
        print("start writing")
        for w in buffer.keys():
            f.write(buffer[w].encode("ISO-8859-1"))


def p2pInitial(file,chunk_name):
    if (os.path.exists(file)):
        if not (download_buffer):
            size = os.stat(file).st_size
            piece = int(size / num_chunks)+1
            if piece > 2048:
                piece = 2048
            print(piece)
            fileBuffer(file, piece, chunk_name)
            return piece
    return None

class socketprocess:
    def __init__(self,connect):
        self.connectionSocket = connect
        self.addr = None
        self.name = None
        self.thread = None
        self.run =  False

    def sendMessage(self, serverMessage):
        self.connectionSocket.send(serverMessage.encode())

    def receiveMessage(self):
        global download_buffer
        global num_chunks
        global clientSocket
        try:
            m = self.connectionSocket.recvfrom(2048)

            m = m[0].decode()
            if (m == ""):
                raise KeyboardInterrupt

            receivedMessage = m.split(" ")
            if(receivedMessage[0] == "name"):
                print("Establishing connection with a p2p client with " + receivedMessage[1])
                self.name = receivedMessage[1]
                return

            if (receivedMessage[0] == "download"):
                global download_buffer
                if (len(receivedMessage) != 3):
                    print("wrong download format")
                    return
                file = receivedMessage[1]
                chunk = receivedMessage[2]
                msg = download_buffer[chunk]
                msg = "file "+str(chunk)+" "+ msg.decode("ISO-8859-1") + " "+file
                self.connectionSocket.send(msg.encode())
                return

            if (receivedMessage[0] == "file"):
                print(receivedMessage)
                chunk_name = receivedMessage[1]
                receivedMessage = receivedMessage[2:]
                file_name = receivedMessage[-1]
                receivedMessage = receivedMessage[:-1]
                content = " ".join(receivedMessage)
                download_buffer[chunk_name] = content
                msg = "register "+file_name+" "+chunk_name+" "+str(num_chunks)+" "+str(sys.getsizeof(content))+" "+"NoReply"
                clientSocket.send(msg.encode())
                print("receive "+ chunk_name)

                msg = "send "+chunk_name
                self.connectionSocket.send(msg.encode())
                print(str((num_download(download_buffer)/num_chunks) * 100) + ("% complete"))
                time.sleep(1)
                if(num_download(download_buffer)==num_chunks):
                    writeFile(download_buffer,file_name )
                    download_buffer = {}
                    clientSocket.send("finishDownload".encode())
                    print("download_"+file_name+" done")
                    return
                msg = "Continue "+ file_name

                clientSocket.send(msg.encode())
                return



            print(m)
        except (OSError , KeyboardInterrupt, UnboundLocalError):
            self.ListRemove()
            self.closesocket()



    def closesocket(self):
        self.connectionSocket.close()

    def ListRemove(self):
        global PrivateMessageSession
        for p in PrivateMessageSession:
            if(self.name == p.name):
                PrivateMessageSession.remove(p)

def num_download(buffer):
    count = 0
    for b in buffer.keys():
        if buffer[b]!=None:
            count = count+1
    return count


def receiveThread(p):
    while p.run :
        p.receiveMessage()

def p2pConnect(socket):
    global PrivateMessageSession
    global socketlist
    while 1:
        connectionSocket, clientAddress = socket.accept()
        p = socketprocess(connectionSocket)
        p.addr = int(clientAddress[1])
        p.run = True
        p.thread = threading.Thread( target=receiveThread,args=(p,))
        p.thread.daemon = True
        p.thread.start()
        PrivateMessageSession.append(p)

if __name__ == "__main__":

    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])

    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientSocket.connect((serverName, serverPort))

    end = threading.Event()
    message = threading.Event()
    p2p = Queue()
    selfInfo = Queue()

    recv_thread = threading.Thread(name="RecvHandler", target=recv_handler,args=(clientSocket,end,message,p2p,selfInfo))
    recv_thread.daemon = True
    recv_thread.start()

    send_thread = threading.Thread(name="SendHandler", target=send_handler,args=(clientSocket,end,message))
    send_thread.daemon = True
    send_thread.start()



    while True:
        try:
            time.sleep(1)
            if(end.isSet()):
                raise KeyboardInterrupt
            while not p2p.empty():

                msg = p2p.get()
                p2pSocket = socket(AF_INET, SOCK_STREAM)
                p2pSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                p2pSocket.connect((msg[0],int(msg[1])))
                p = socketprocess(p2pSocket)
                p.addr = int(msg[1])
                p.name = msg[2]
                p.run = True
                p.thread = threading.Thread( target=receiveThread,args=(p,))
                p.thread.daemon = True
                p.thread.start()
                p.sendMessage("name "+loginName) #tell the p2p client what's the name
                PrivateMessageSession.append(p)


            if not selfInfo.empty():
                msg = selfInfo.get()
                port = int(msg[1])
                p2pReceiveSocket = socket(AF_INET, SOCK_STREAM)
                p2pReceiveSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                p2pReceiveSocket.bind(("localhost",port))
                p2pReceiveSocket.listen(1)
                p2pConnection = threading.Thread(target=p2pConnect, args=(p2pReceiveSocket,))
                p2pConnection.daemon = True
                p2pConnection.start()




        except (KeyboardInterrupt,OSError):
            try:
                clientSocket.send("logout".encode())
            except OSError:
                pass
            print("Client closing..")
            sys.exit(0)



