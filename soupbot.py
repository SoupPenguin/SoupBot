#!/usr/bin/env python3
 
# SoupBot 0.1

import sys
import socket
import string
import time
import threading
import feedparser
import queue
import email.utils #Used for publish dates
from datetime import datetime

#Watch site for changes.
def SoupWatch(queue):
    url = 'http://souppenguin.com/toasty/index.php?request=rss'
    stillNewFor = 60
    while 1:
        print("Checking for new articles.")
        feed = feedparser.parse(url)
        currentTime = datetime.now()
        for item in feed["items"]:
            t = email.utils.parsedate_tz(item["published"])
            postTime = datetime(t[0],t[1],t[2],t[3],t[4],t[5]);
            timeDelta = currentTime - postTime
            if timeDelta.seconds < (stillNewFor * 2) - 1:
                message = "New Post: %s at %s" % (item["title"],item["links"][0]["href"])
                print("SoupWatch::" + message)
                queue.put((False,message),False)
        time.sleep(stillNewFor) #Sleep for 1 minute
        
def getCurrentTime(sender,message,bot):
    localtime   = time.localtime()
    timeString  = time.strftime("%X on %A the %d of %B", localtime)
    bot.Message(sender,"The time is %s" % timeString)

def patBot(sender,message,bot):
    bot.Message(sender,":)")
    
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
        
HOST = "irc.freenode.net"
PORT = 6667
 
NICK = "SoupBot"
IDENT = "SoupBot"
REALNAME = "Soup Penguin"
MASTERS = ["Half-Shot "]#,"Raven67854]
CHANNEL = "#souppenguin"
ShouldRun = True

#Create a new Bot
print("Started Bot")
sBot = SoupBot(HOST,PORT)
print("Connecting to %s" % HOST )
sBot.Connect(NICK,IDENT,REALNAME)
print("Connected" )
sBot.JoinChannel(CHANNEL)
print("Joined Channel %s" % CHANNEL )
for master in MASTERS:
    sBot.Message(master,"SoupBot started")
    
sBot.AddMessageHandler("What is the time?",getCurrentTime,False)
sBot.AddMessageHandler("Pat " + NICK ,patBot,False)

#Start Threads

t1 = threading.Thread(target=SoupWatch,args=(sBot.messagequeue,))
t1.start()

sBot.RunServer()
