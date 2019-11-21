from filetransfer import *
class notifier:
    def __init__(self):
        self.current_list = []
        self.all_list = []
        # add all possible user to list
        with open('./credentials.txt', "r+") as file:
            for data in file:
                data = data.rstrip()
                data = data.split(" ")
                self.all_list.append(data[0])


        self.storelist = {}
        self.filelist = []

    def checkDuplicateRegister(self,name,piece,user):
        for file in self.filelist:
            if(file.name == name):
                if(file.checkDuplicateRegister(piece,user)):
                    return True
        return False
    def addFileList(self,name,chunk,user,size):
        for file in self.filelist:
            if(file.name == name):

                file.addChunk(chunk,user,size)
                return
        new = p2pFile(name)
        new.addChunk(chunk,user,size)
        self.filelist.append(new)
    # get chunks in that name
    def file(self,filename):
        for file in self.filelist:
            if(file.name == filename):
                return file.chunk

    def fileSearch(self,name,user):
        for file in self.filelist:
            if(file.name == name):
                l = file.owner()
                if len(l)> 0:
                    if( user in l):
                        l.remove(user)
                    msg = "Available "+" ".join(l)
                    return msg

        return "Not Available"

    def chunkSearch(self,name,chunk):
        l = None
        for file in self.filelist:
            if(file.name == name):
                l = file.chunkOwner(chunk)
        for user in l:
            if not (self.checkCurrentuser(user)):
                l.remove(user)

        if len(l)> 0:
            msg = "Available "+" ".join(l) +" "+name +" "+chunk
            print("message "+msg)
            return msg
        return "NotAvailable"

    def login(self,p):
        self.current_list.append(p)
        self.loginNotify(p)
    def logout(self,p):
        if(p in self.current_list):
            self.current_list.remove(p)
        self.logoutNotify(p)

    def loginNotify(self,p):
        for socketProcess in self.current_list:
            if socketProcess != p:
                socketProcess.sendMessage(p.name + " login")

    def logoutNotify(self,p):
        for socketProcess in self.current_list:
            if socketProcess != p:
                socketProcess.sendMessage(p.name + " logout")
    def whoElse(self,p):
        msg = ''
        for socketProcess in self.current_list:
            if socketProcess != p:
                msg = msg+str(socketProcess.name)+"\n"
        msg = msg[:-1]
        return msg
    def checkuser(self,name):
        for othername in self.all_list:
            if othername == name:
                return True
        return False
    def checkCurrentuser(self,name):
        for socket in self.current_list:
            if socket.name == name:
                return True
        return False
    def sendMessage(self,p,user,text):
        Block = False
        for socketProcess in self.current_list:
            if socketProcess.name == user:
                if (socketProcess.checkBlockUser(p.name)):
                    Block = True
                    break
                socketProcess.sendMessage(text)
                return
        if (Block):
            p.sendMessage("your message could not be delivery as the recipient block u ")

        self.storelist[user] = text
        print(self.storelist)
        return

    def broadcast(self,p,msg):
        Block = False
        for socketProcess in self.current_list:
            if socketProcess != p:
                if(socketProcess.checkBlockUser(p.name)):
                    Block  = True
                    continue
                socketProcess.sendMessage(msg)

        if(Block):
            p.sendMessage("your message could not be delivery to some recipent")

    def checkOfflineMessage(self,p):
        if p.name in self.storelist.keys():
            p.sendMessage("offline message: \n"+self.storelist[p.name])
            del self.storelist[p.name]
            return False
        return True
    def fetchInfo(self,user):

        for socketProcess in self.current_list:
            if socketProcess.name == user :
                return socketProcess
        return None

    def searchAvailable(self,filename,user):
        find = False
        for p in self.current_list:
            if user != p.name:
                p.sendMessage("request "+ filename +" "+user)
                find = True
        if(find == False):
            self.find(user).sendMessage("No available User")
    def search(self,filename,user):
        for p in self.current_list:
            if user != p.name:
                p.sendMessage("search "+ filename)
    def find(self,name):
        for p in self.current_list:
            if name == p.name:
                return p
    def chunklist(self,name):
        for p in self.filelist:
            if name == p.name:
                return p.chunklist()
    def removeRegister(self,name):
        for f in self.filelist:
            f.removeUser(name)