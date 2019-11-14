#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8
from socket import *
import sys

def checkInvalidLogin(receivedMessage):
    if (receivedMessage.decode()=="Invalid PassWord, Please try again"):
        return True
    if(receivedMessage.decode()== "Invalid PassWord, You account has been blocked" or receivedMessage.decode()== "Still under Blocked"):
        #print("la")
        print(receivedMessage.decode())
        raise SystemExit

        return True

    return False


#Server would be running on the same host as Client
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
clientSocket.connect((serverName,serverPort))




try:
    usr = input("UserName: \n")
    pw = input("PassWord: \n")
    message = usr + " " + pw

    clientSocket.send(message.encode())
    while(1):

        receivedMessage, serverAddress = clientSocket.recvfrom(2048)

        if(checkInvalidLogin(receivedMessage)):
            print(receivedMessage.decode())
            usr = input("UserName: \n")
            pw = input("PassWord: \n")
            message = usr + " " + pw

            clientSocket.send(message.encode())
            continue
        if(receivedMessage.decode()=="Welcome"):
            print(receivedMessage.decode())

        message = input("> ")
        clientSocket.send(message.encode())
except (KeyboardInterrupt,SystemExit,EOFError):
    clientSocket.shutdown(1)
    clientSocket.close()
    sys.exit(0)
    raise

# if (receivedMessage.decode()=='Welcome'):
#     #Wait for 10 back to back messages from server
#     for i in range(10):
#         receivedMessage, serverAddress = clientSocket.recvfrom(2048)
#         print(receivedMessage.decode())
# #prepare to exit. Send Unsubscribe message to server
# message='Unsubscribe'
# clientSocket.send(message.encode())

#Close the socket