class notifier:
    def __init__(self):
        self.current_list = []
        self.all_list = []

    def login(self,p):
        self.current_list.append(p)
        self.all_list.append(p)
        self.loginNotify(p)
    def logout(self,p):
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