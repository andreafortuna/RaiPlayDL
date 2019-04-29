#!/usr/bin/env python3

import re, os, contextlib, sys
import urllib
import pydub
import glob
from os import path as path
from pydub import AudioSegment
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

class Raipodcast():
    def __init__(self, url):
        self.url = url
        
    def getFile (self, url,filename):
        request = requests.get(url, timeout=60, stream=True)
        with open(filename, 'wb') as fh:
            for chunk in request.iter_content(1024 * 1024):
                fh.write(chunk)

    def process(self, folder):
		#Clean tmp directory		
        files = glob.glob('tmp/*')
        for f in files:
            os.remove(f)
            
        result = requests.get(self.url)
        if result.status_code != 200:
            return None

        soup = BeautifulSoup(result.content, "html.parser")        
        header = soup.find("div", class_="descriptionProgramma")
        title = soup.find('title').text
        description = header.find(class_='textDescriptionProgramma').text
        image = urljoin(self.url, soup.find(class_='imgHomeProgramma')['src'])
        finalfilename = str(title).strip().replace(' ', '_')
        finalfilename = re.sub(r'(?u)[^-\w.]', '', finalfilename)    
        print ("Starting download for \"" + title + "\"")               
        print ("Download collection image...")
        urllib.request.urlretrieve (image, "tmp/" + finalfilename + ".jpg")
        
        allelements = soup.find_all(['li','div'])
        print ("Download single MP3s...")
        elementID = 1
        for element in allelements:
            if element.has_attr('data-mediapolis') and element.has_attr('data-title'):				
                mp3 = url = urljoin(self.url, element['data-mediapolis'])
                title = element['data-title']              
                filename = str(elementID).zfill(2) + "_"  + str(title).strip().replace(' ', '_')
                filename = re.sub(r'(?u)[^-\w.]', '', filename)                   
                elementID = elementID + 1
                print ("Download \"" + title + "\" (" + mp3 + ")")                
                self.getFile(mp3, "tmp/" + filename + ".mp3")

        print ("Merge all MP3 files...")
        playlist_songs = [AudioSegment.from_mp3(mp3_file) for mp3_file in sorted(glob.iglob("tmp/*.mp3"))] 
        combined = AudioSegment.empty()
        for song in playlist_songs:
            combined += song
        combined.export(finalfilename + ".mp3", format="mp3",tags={"title": title, "artist": "RaiPlay " + description},cover="tmp/" + finalfilename + ".jpg")
        print ("Done!\nFile saved on " + finalfilename + ".mp3")
        
def main():
    print ("""
 ____       _ ____  _             
|  _ \ __ _(_)  _ \| | __ _ _   _ 
| |_) / _` | | |_) | |/ _` | | | |
|  _ < (_| | |  __/| | (_| | |_| |
|_| \_\__,_|_|_|   |_|\__,_|\__, |
       Downloader           |___/     
 ---------------------------------
 Proudly developed by Andrea Fortuna
 andrea@andreafortuna.org
 https://www.andreafortuna.org
    """)
    if len(sys.argv) < 2:
        print('Need a url')
        exit(2)
        
    getPodcast = Raipodcast(sys.argv[1])
    getPodcast.process('.')
    
if __name__ == '__main__':
    main()
