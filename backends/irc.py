HOST = "irc.freenode.net"
PORT = 6667
NICK = "SoupBot"
IDENT = "SoupBot"
REALNAME = "Soup Penguin"
CHANNEL = "#souppenguin"
MASTERS = ["Half-Shot"]#,"Raven67854]


class SoupBot:
    def __init__(self,host,port):
        self.hostname = host
        self.port = port
        self.connection = socket.socket( )
        self.readbuffer = ""
        self.__channel = ""
        self.channel_handlers = {}
        self.pm_handlers = {}
        self.messagequeue = queue.Queue(10)

    def Connect(self,nickname,ident,realname):
        self.connection.connect((self.hostname,self.port))
        self.SetNick(nickname);
        self.connection.send(bytes("USER %s 8 * :%s\r\n" % (IDENT, REALNAME), "UTF-8"))
        self.ShouldRun = True

    def SetNick(self,nickname):
        self.__nickname = nickname
        self.connection.send(bytes("NICK %s\r\n" % self.__nickname, "UTF-8"))

    def JoinChannel(self,channel):
        self.__channel = channel
        self.connection.send(bytes("JOIN %s\r\n" % self.__channel, "UTF-8"))

    def Message(self,user,text):
        if(user == False):
            user = self.__channel
        print("Messaging " + user)
        self.connection.send(bytes("PRIVMSG %s :%s \r\n" % (user, text), "UTF-8"))

    def HandleMessage(self,sender,message):
        private = (sender != self.__channel)
        commandFound = False
        for command, function in self.channel_handlers.items():
            if message.startswith(command):
                function(sender,message,self)
                commandFound = True
                break

        if private and commandFound == False:
            for command, function in self.pm_handlers.items():
                if message.startswith(command):
                    function(sender,message,self)
                    commandFound = True
                    break

    def AddMessageHandler(self,command,function,privateonly = True):
        if privateonly:
            self.pm_handlers[command] = function
        else:
            self.channel_handlers[command] = function

    def RunServer(self):
        while self.ShouldRun:
            self.readbuffer = self.readbuffer + self.connection.recv(1024).decode("UTF-8")
            temp = str.split(self.readbuffer, "\n")
            self.readbuffer=temp.pop( )
            for line in temp:
                line = str.rstrip(line)
                line = str.split(line)
                #Handle PING
                if(line[0] == "PING"):
                    self.connection.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))
                if(line[1] == "PRIVMSG"):
                    sender = ""
                    for char in line[0]:
                        if(char == "!"):
                            break
                        if(char != ":"):
                            sender += char
                    size = len(line)
                    i = 3
                    message = ""
                    while(i < size):
                        message += line[i] + " "
                        i = i + 1
                    message = message.lstrip(":")
                    message = message.rstrip()
                    if(len(message) > 1 and sender != self.__nickname):
                        print("Recieved from %s:'%s'" % (sender,message))
                        self.HandleMessage(sender,message)
            #Handle queue.
            try:
                message = self.messagequeue.get(False)
                self.Message(message[0],message[1])
            except queue.Empty:
                pass
