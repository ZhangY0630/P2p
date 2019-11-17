import sys
import threading
import time
from socket import *
from queue import Queue



def checkInvalidLogin(receivedMessage):
    if (receivedMessage.decode()=="Invalid PassWord, Please try again"):
        return True
    if(receivedMessage.decode()== "Invalid PassWord, You account has been blocked" or receivedMessage.decode()== "Still under Blocked"):
        #print("la")
        print(receivedMessage.decode())
        raise SystemExit
    if(receivedMessage.decode()=="Timeout"):
        print("\nTimeout")
        raise TimeoutError


    return False

def recv_handler(clientSocket,end,message):
    try:
        while 1:
            receive = clientSocket.recvfrom(2048)

            if (checkInvalidLogin(receive[0])):

                usr = input("UserName: \n")
                pw = input("PassWord: \n")
                message = usr + " " + pw

                clientSocket.send(message.encode())
                continue
            # if (receive[0].decode() == "Welcome"):
            #     print(receive[0].decode())
            #     continue
            print(receive[0].decode())
            message.set()
    except (KeyboardInterrupt, SystemExit, EOFError,TimeoutError):
        clientSocket.shutdown(1)
        clientSocket.close()
        end.set()






def send_handler(clientSocket,end,m):
    usr = input("UserName: \n")
    pw = input("PassWord: \n")
    message = usr + " " + pw
    try:
        clientSocket.send(message.encode())
        while 1:
            while m.isSet() :
                message = input()
                clientSocket.send(message.encode())
                m.clear()
    except (KeyboardInterrupt, SystemExit, EOFError):
        clientSocket.shutdown(1)
        clientSocket.close()
        end.set()

if __name__ == "__main__":
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])

    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientSocket.connect((serverName, serverPort))

    end = threading.Event()
    message = threading.Event()

    recv_thread = threading.Thread(name="RecvHandler", target=recv_handler,args=(clientSocket,end,message))
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
        except KeyboardInterrupt:
            print("Client closing..")
            sys.exit(0)



