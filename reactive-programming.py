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
        asyncio.get_event_loop().run_until_complete(self.main('https://es.wikipedia.org/wiki/38M_Toldi'))

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
            imgName = ''
            if imgItem['src'].find('http') == True:
                imgSrc = imgItem['src']
                if len(imgItem['alt']) > 0 :
                    imgName = imgItem['alt']
                else:
                    imgName = imgSrc
            if not imgName in self.imgs:
                async with aiohttp.ClientSession() as clientSession:
                    try:
                        serverResponse = await clientSession.get(imgSrc)
                        imgBytes = await serverResponse.read(serverResponse)

                        if imgBytes:
                            self.bytesfoto.append(imgBytes)
                            print(f'{imgName} : {imgSrc}')

                    except:
                        print('Error al descargar la foto')
    """
    Definicion de los atributos de la clase iniciales donde se guardan los datos que se usaran en el tkinter para la GUI

    contador -- es el que lleva la cuenta de la cantidad de imágenes que se añaden a la lista
    window -- define la ventana de la GUI
    imgs -- lista en la que se guardan las URLs de las imágenes
    bytesfoto -- lista en la que se guardan las fotos en bytes para poder guardarlas en memoria
    objImg -- variable que convierte los links de las fotos en observables

    """

    def __init__(self):

        #Variables que contienen listas de imágenes nombres etc
        self.contador = 0
        self.window = Tk()
        self.window.title = "Reactive-Programming"
        self.imgs = []
        self.bytesfoto = []
        self.objImg = rx.from_iterable(self.imgs)

        #Barra de búsqueda
        Label(text='URL', font=('Arial Bold', 14)).grid(column=0, row=0)
        self.input = Entry()
        self.input.grid(column=2, row=0)

        #Boton de buscar
        Button(text='Search', command=self.buttonSearch()).grid(column=1, row=1)
        
        #Lista de imágenes
        self.listbox = Listbox(self.window)
        self.listbox.grid(column=0, row=2)
        self.listbox.bind('<<ListboxSelect>>', self.onSelect())

        #Render de la foto
        self.canvas = Canvas(width=300, height=300)
        self.canvas.grid(column=2, row=1)

        #Barra de progreso
        self.progressbar = Progressbar(self.window)
        self.progressbar.grid(column=2, row=3)

        self.window.mainloop()

if __name__ == '__main__':
    App()