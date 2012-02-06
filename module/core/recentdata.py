import time
class UserData():

    def __init__(self,nick,ident,host):
        self.nick = nick
        self.ident = ident
        self.host = host
        self.data = []

    def msg(self,channel,message):
        self.data.append({'time' : time.time(), 'channel': channel, 'msg': message})

    def lastMsg(self):
        return self.data[-1]

class Data(): 
   

    def __init__(self):
        self.users = {}
        self.userhost = lambda a,b,c: a+b+c

    def store(self,nick,ident,host,channel,message):
        print self.userhost(nick,ident,host)

        if (self.userhost(nick,ident,host) not in self.users):
            self.users[self.userhost(nick,ident,host)] = UserData(nick,ident,host)

        self.users[self.userhost(nick,ident,host)].msg(channel,message)

    def user(self,nick,ident,host):
        return self.users[(nick+ident+host)]

