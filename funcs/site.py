from urllib.request import urlopen
from bs4 import BeautifulSoup

def SiteTitle(msg,regex,soup):
    url = regex.group()
    try:
        page = urlopen(url)
        t = page.getheader("Content-Type")
        if(t.startswith("text")):
            sp = BeautifulSoup(page,"html.parser")
            soup.WriteMessage("[Site] " + sp.title.string)
        elif(t.startswith("image")):
            print("Got image")
            data = page.read()
            soup.UploadImage(data,t)
            print("Uploaded")
    except:
        pass# Oh well, probably a bad url
