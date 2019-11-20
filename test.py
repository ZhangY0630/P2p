
from _thread import start_new_thread

HOST = 'localhost' # all availabe interfaces
PORT = 12345 # arbitrary non privileged port

try:
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
except socket.error as msg:
    print("Could not create socket. Error Code: ", str(msg[0]), "Error: ", msg[1])
    sys.exit(0)

print("[-] Socket Created")

# bind socket
try:
    s.bind(("localhost", PORT))
    print("[-] Socket Bound to port " + str(PORT))
except socket.error as msg:
    print("Bind Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]))
    sys.exit()

s.listen(1)
print("Listening...")

# The code below is what you're looking for ############

def client_thread(conn):
    conn.send("Welcome to the Server. Type messages and press enter to send.\n".encode())

    while True:
