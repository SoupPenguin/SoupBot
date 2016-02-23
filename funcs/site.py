from urllib.request import urlopen
from bs4 import BeautifulSoup

def SiteTitle(msg,regex,soup):
    url = regex.group()
    print(url)
    try:
        page = urlopen(url)
        t = page.getheader("Content-Type")
        print(t)
        if(t.startswith("text")):
            sp = BeautifulSoup(page,"html.parser")
            soup.WriteMessage("[Site] " + sp.title.string,msg.RoomIndex)
        elif(t.startswith("image")):
            print("Got image")
            data = page.read()
            print(msg.RoomIndex)
            soup.UploadImage(data,t,msg.RoomIndex)
            print("Uploaded")
        elif(t.startswith("video/webm")):
            print("Got webm")
            data = page.read()
            print(msg.RoomIndex)
            soup.UploadVideo(data,t,msg.RoomIndex)
            print("Uploaded")
    except Exception as e:
        print(e)
        pass# Oh well, probably a bad url
