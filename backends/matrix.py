#!/usr/bin/python3
USERNAME="SoupBot"

from os.path import expanduser

# Get PWD

f = open(expanduser("~/.soupbot_matrix_pwd"),'r')
PWD = f.read().strip()
f.close()

from backends.matrix_client.client import MatrixClient
from backends.message import SoupMessage
from PIL import Image
from io import BytesIO

class MatrixBackend:
    __rooms = []
    __token = None
    __client = None
    EventQueue = []
    def __init__(self):
        self.__client = MatrixClient("https://souppenguin.com:8448")
        self.__token  = self.__client.login_with_password(username=USERNAME, password=PWD)
        for rstr in ["#general:souppenguin.com","#furry:souppenguin.com","#devtest:souppenguin.com"]:
            print("Joining ",rstr)
            room  = self.__client.join_room(rstr)
            room.add_listener(self.__on_message)
            self.__rooms.append(room)
        self.__client.start_listener_thread()

    def write_image(self,content,content_type,rid):
        url = self.__client.upload(content,content_type)
        byt = BytesIO(content)
        im = Image.open(byt)
        width, height = im.size
        return self.__rooms[rid].send_image(url,len(content),content_type,width,height)


    def write_message(self,msg,rid):
        self.__rooms[rid].send_text(msg)

    def __on_message(self,evt):
        if evt["type"] == "m.room.message" and evt["age"] < 1000:
            #Find room
            msg = SoupMessage()
            for i in range(0,len(self.__rooms)):
                if self.__rooms[i].room_id == evt["room_id"]:
                    msg.RoomIndex = i
                    break;

            msg.Nick = evt["sender"]
            msg.Message = evt["content"]["body"]
            msg.Time = evt["origin_server_ts"]
            self.EventQueue.append(msg)
