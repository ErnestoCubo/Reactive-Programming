import base64
import aiohttp
import asyncio
import aiofiles
import io
import rx
from tkinter import *
from tkinter.ttk import *
from urllib.request import urlopen
from PIL import ImageTk, Image
from bs4 import BeautifulSoup


class App:

    def buttonSearch(self):
        url = self.input.get()
        asyncio.get_event_loop().run_until_complete(self.main(url))

    def onSelect(self, event):
        position = self.listbox.curselection()
        imgName = self.listbox.get(position)
        index = self.imgs.index(imgName)
        imgSrc = self.bytesfoto[index]
        self.img = ImageTk.PhotoImage(data = imgSrc)
        self.canvas.create_image(20,20, anchor=NW, image=self.img)  
    
    async def main(self, urlToProcess):
        async def getSourceCode(url):
            async with aiohttp.ClientSession() as clientSession:
                serverResponse = await clientSession.get(url)
                sourceCode = await serverResponse.text()
                return sourceCode   
                
        sourceCode = await getSourceCode(urlToProcess)
        parsedSource = BeautifulSoup(sourceCode, 'html.parser')
        for imgItem in parsedSource.find_all('img', src=True):
            imgName = imgItem['alt']
            imgSrc = imgItem['src']
            if imgSrc.find('http') == True:
                if len(imgName) < 1 :
                    imgName = imgSrc
            elif imgSrc.startswith('//'):
                imgSrc = 'https:' + imgSrc
            else:
                urlSplit = urlToProcess.split('/')
                rootUrlPath = urlSplit[0] + '//' + urlSplit[2]
                imgSrc = rootUrlPath + imgSrc
                if len(imgItem['alt']) > 0 :
                    imgName = imgItem['alt']
                else:
                    imgName =  imgSrc
            if not imgName in self.imgs:
                async with aiohttp.ClientSession() as clientSession:
                    serverResponse = await clientSession.get(imgSrc)
                    responseStatus = serverResponse.status
                    imgBytes = await serverResponse.read()

                    # Estoy comparando el Status ya que es con lo que se debería comparar al no ser necesariamente asíncrono 
                    # porque lo es implicitamente en la petición anterior al servidor
                    if responseStatus == 200:
                        self.bytesfoto.append(imgBytes)
                        print(f'{imgName} : {imgSrc} -> STATUS OK : {responseStatus}')
                    else:
                        print(f'{imgName} : {imgSrc} -> STATUS FAILED : {responseStatus}')

    """
    Definicion de los atributos de la clase iniciales donde se guardan los datos que se usaran en el tkinter para la GUI

    contador -- es el que lleva la cuenta de la cantidad de imágenes que se añaden a la lista
    window -- define la ventana de la GUI
    imgs -- lista en la que se guardan las URLs de las imágenes
    bytesfoto -- lista en la que se guardan las fotos en bytes para poder guardarlas en memoria
    obsImg -- variable que convierte los links de las fotos en observables

    """

    def __init__(self):

        #Variables que contienen listas de imágenes nombres etc
        self.contador = 0
        self.window = Tk()
        self.window.title = "Reactive-Programming"
        self.imgs = []
        self.bytesfoto = []
        self.obsImg = rx.from_iterable(self.imgs)

        #Barra de búsqueda
        Label(text='Img Downlo4d3r', font=('Arial Bold', 14)).grid(columnspan = 2, row=0)
        self.input = Entry()
        self.input.grid(column=2, row=0)

        #Boton de buscar
        Button(text='Search', command=self.buttonSearch).grid(column=2, row=1)
        
        #Lista de imágenes
        self.listbox = Listbox(self.window)
        self.listbox.grid(column=0, row=2)
        self.listbox.bind('<<ListboxSelect>>', self.onSelect)

        #Render de la foto
        self.canvas = Canvas(width=300, height=300)
        self.canvas.grid(column=2, row=2)

        #Barra de progreso
        self.progressbar = Progressbar(self.window)
        self.progressbar.grid(column=2, row=3)

        self.window.mainloop()

if __name__ == '__main__':
    App()