#!/usr/bin/env python3

# SoupBot 0.1
import sys
import string
import time
import re

from backends.matrix import MatrixBackend
from backends.message import SoupMessage
from datetime import datetime

from funcs.site import SiteTitle

class SoupBot:
    ShouldRun = True
    Backend = []
    channel_handlers = {}
    pm_handlers = {}
    def __init__(self,backend):
        self.Backend = backend

    def AddMessageHandler(self,command,function,privateonly = False):
        if privateonly:
            self.pm_handlers[command] = function
        else:
            self.channel_handlers[command] = function

    def WriteMessage(self,msg,roomid):
        self.Backend.write_message(msg,roomid)

    def UploadImage(self,content,content_type,roomid):
        self.Backend.write_image(content,content_type,roomid)

    def RunServer(self):
        while self.ShouldRun:
            for evt in self.Backend.EventQueue:
                for reg, func in self.channel_handlers.items():
                    check = re.match(reg,evt.Message,re.IGNORECASE)
                    if check != None:
                        func(evt,check,self)
            self.Backend.EventQueue.clear()
            time.sleep(1)


#Create a new Bot
print("Started Bot")
sBot = SoupBot(MatrixBackend())

# Soup function
def BringMeSoup(msg,match,soup):
    soup.WriteMessage("🍜",msg.RoomIndex)

sBot.AddMessageHandler("Bring me soup",BringMeSoup)
sBot.AddMessageHandler("Soup",BringMeSoup)
sBot.AddMessageHandler(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))',SiteTitle)
sBot.RunServer()
