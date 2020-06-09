from bs4 import BeautifulSoup
import requests

url = 'http://deeplabcut.rowland.harvard.edu/datasets/animal_ytVOS_images/images_jpg/'
ext = 'iso'

animals=['dog','cat','bear']
def write(data,fn="filelist.lst"):
    with open("filelist.lst", "w") as f:
        for s in data:
            f.write(str(s) +"\n")

def read(fn="filelist.lst"):
    with open("filelist.lst", "r") as f:
      for line in f:
        score.append(int(line.strip()))

def listurl(url,animals=None, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    all=[url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    if animals is not None: #then filter
        urls=[]
        for a in all:
            for animal in animals:
                if animal in str(a):
                    urls.append(a)
    else:
        urls=all
    return urls

def listimgurl(url,imtype='.jpg', ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    all=[url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    if animals is not None: #then filter
        urls=[]
        for a in all:
            if imtype in str(a):
                    urls.append(a)
    else:
        urls=all
    return urls

allanimalurls=listurl(url,animals)

imlist=[]
for allanimalurl in allanimalurls:
    imlist.extend(listimgurl(allanimalurl))

write(imlist,fn="filelist.lst")
