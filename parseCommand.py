import random
import time


def parse(message,p,notifier,starttime):
    command = message[0]

    if command=="whoelse":
        msg = notifier.whoElse(p)
        return msg

    if command == "message":
        if not (notifier.checkuser(message[1])):
            msg = "Error. Invalid User"
            return msg
        user = message[1]
        content = message[2:]
        msg = ' '.join(word for word in content)
        msg = p.name + ": " + msg
        notifier.sendMessage(p,user,msg)
        return ''
    if command == "broadcast":
        content = message[1:]
        msg = ' '.join(word for word in content)
        msg = p.name + ": " + msg
        notifier.broadcast(p,msg)
        return ''

    if command == "block":
        user = message[1]
        if(user == p.name):
            return "Error. Can't block your self"
        p.addBlockUser(user)
        return user + ' is blocked'
    if command == "unblock":
        print(p.block)
        usr = message[1]
        if(p.checkBlockUser(usr)):
            p.removeBlockUser(usr)
            return str(usr)+' is unblocked'
        return "Error "+ str(usr) + " was not blocked"

    if command == "logout":
        raise KeyboardInterrupt
        return
    if command == "whoelsesince":
        desired_time = message[1]
        msg = ''
        for user in starttime.keys():
            if(float(desired_time) > (time.time()- starttime[user]) and user != p.name):
                msg = msg + user + "\n"
        msg = msg[:-1]
        print(msg)
        return msg

    if command == "startprivate":
        user = message[1]
        socket = notifier.fetchInfo(user)
        if(socket!=None):
            if(socket.name == p.name):
                return "can't private message yourself"
            if(p.name in socket.block):
                return "User has block u"
            return "private "+ str(socket.clientAddress[0])+ " " + str(socket.clientAddress[1]) + " " + user
        return "User not exist"

    if(command == "register"):
        message = message[1:]
        flag = message[-1]
        message = message[:-1]
        try:
            if len(message)==4:
                print("get 4")
                filename = message[0]
                chunk = message[1]
                size = message[3]
                if(notifier.checkDuplicateRegister(filename,chunk,p.name)):
                    return "User has already registered"
                notifier.addFileList(filename,chunk,p.name,size)
                if(flag == "NoReplay"):
                    return ""
                return "register OK"

            if len(message)==6:
                print("get 4")
                filename = message[0]
                chunk_style = message[1][:-2]
                chunk_start = int(message[1][-2:])
                chunk_end = int(message[3][-2:])+1
                size = message[5]
                for n in range(chunk_start,chunk_end):
                    if n<10:
                        if (notifier.checkDuplicateRegister(filename, chunk_style+"0"+str(n), p.name)):
                            return "User has already registered"
                        notifier.addFileList(filename,chunk_style+"0"+str(n),p.name,size)
                    else:
                        if (notifier.checkDuplicateRegister(filename, chunk_style+str(n), p.name)):
                            return "User has already registered"
                        notifier.addFileList(filename, chunk_style + str(n), p.name, size)
                if (flag == "NoReplay"):
                    return ""
                return "register OK"
            return "Invalid formate. Please follow follow the style like:\nregister mf mf01 to mf09 9 1024 or register mf mf10 930."
        except IndexError:
            return "Invalid formate. Please follow follow the style like:\nregister mf mf01 to mf09 9 1024 or register mf mf10 930."
    if command == "searchFile":
        filename = message[1]
        notifier.search(filename, p.name)
        msg = notifier.fileSearch(filename)
        return msg
    if command == "searchChunks":
        filename = message[1]
        chunk = message[2]
        return notifier.chunkSearch(filename,chunk)
    if command == "p2pDownload":
        filename = message[1]
        notifier.searchAvailable(filename,p.name)
        return ""
    if command == "SuccessRegister":
        if(p.startDownload==False):
            user = message[1]
            filename = message[2]
            chunklist = notifier.file(filename)
            for c in chunklist.keys():
                choose = random.choice(chunklist[c])
                msg = "private "+user+" download "+filename+" "+c
                msg = "Forward "+ msg
                socket = notifier.find(choose)
                socket.sendMessage(msg)
            p.startDownload = True
        return ""
    if command == "finishDownload":
        p.startDownload = False
        return ""
    msg = "Error. Invalid command"
    return msg

