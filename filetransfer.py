class p2pFile():
    def __init__(self,file):
        self.name = file
        self.chunk = {}
        self.size = {}


    def addChunk(self,piece,user,size):
        for s in self.size.keys():
            if s == piece:
                break
        self.size[piece] = size


        for c in self.chunk.keys():
            if c == piece:
                if user not in self.chunk.keys():
                    self.chunk[c].append(user)
                return

        self.chunk[piece] = [user]
        return

    def checkDuplicateRegister(self,piece,user):
        if piece not in self.chunk.keys():
            return False

        if user not in self.chunk[piece]:
            return False
        return True
    def owner(self):
        reply = []
        for c in self.chunk.keys():
            for n in self.chunk[c]:
                if n not in reply:
                    reply.append(n)

        return reply
    def chunkOwner(self,c):
        reply = []
        if c not in self.chunk.keys():
            return reply
        for n in self.chunk[c]:
            if n not in reply:
                reply.append(n)

        return reply
    def chunklist(self):
        return list(self.chunk)
    def removeUser(self,name):
        for key in self.chunk.keys():
            if name in self.chunk[key]:
                self.chunk[key].remove(name)