import tkinter
import base64
import aiohttp
import asyncio
import aiofiles
import io
import rx
from urllib.request import urlopen
from PIL import ImageTk, Image
from bs4 import BeautifulSoup


class App:
    
    async def getSourceCode(url):
        async with aiohttp.ClientSession() as clientSession:
            serverResponse = await clientSession.get(url)
            sourceCode = await serverResponse.text()
            return sourceCode     
    
    async def main(self, urlToProcess):
        print('a')
        sourceCode = self.getSourceCode(urlToProcess)
        parsedSource = BeautifulSoup(sourceCode, 'html.parser')
        
        for imgItem in parsedSource.find_all('img', src=True):
            if imgItem['src'].find('http') == True:
                imgSrc = imgItem['src']
                
        
    """
    Definicion de los atributos de la clase iniciales donde se guardan los datos que se usaran en el tkinter para la GUI

    contador -- es el que lleva la cuenta de la cantidad de imágenes que se añaden a la lista
    window -- define la ventana de la GUI
    imgs -- lista en la que se guardan las URLs de las imágenes
    bytesfoto -- lista en la que se guardan las fotos en bytes para poder guardarlas en memoria
    objImg -- variable que convierte los links de las fotos en observables

    """

    def __init__(self):
        self.contador = 0
        self.window = Tk()
        self.window.title = "Reactive-Programming"
        self.imgs = []
        self.bytesfoto = []
        self.objImg = rx.from_iterable(self.imgs)