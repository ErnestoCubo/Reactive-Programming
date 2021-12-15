import base64
import aiohttp
import asyncio
import aiofiles
import io
import rx
import sys
from tkinter import *
from tkinter.ttk import *
from urllib.request import urlopen
from PIL import ImageTk, Image
from bs4 import BeautifulSoup

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
        
        def checkImgAlt(imgName, imgSrc):
            urlSplit = imgSrc.split('/')
            name = urlSplit.pop()
            if len(imgName) <= 0 :
                imgName = name
            return imgName
            
        async def getSourceCode(url):
            async with aiohttp.ClientSession() as clientSession:
                serverResponse = await clientSession.get(url)
                sourceCode = await serverResponse.text()
                return sourceCode   
                
        sourceCode = await getSourceCode(urlToProcess)
        parsedSource = BeautifulSoup(sourceCode, 'html.parser')
        
        for imgItem in parsedSource.find_all('img', src=True):
            
            try:
                imgName = imgItem['alt']
            except:
                imgName = ''
            imgSrc = imgItem['src']
                  
            if imgSrc.find('http') == -1:
                if imgSrc.startswith('//'):
                    
                    imgSrc = 'https:' + imgSrc
                else:
                    urlSplit = urlToProcess.split('/')
                    rootUrlPath = urlSplit[0] + '//' + urlSplit[2]
                    imgSrc = rootUrlPath + imgSrc
            
            imgName = checkImgAlt(imgName, imgSrc)
            
            if not imgName in self.imgs:
                
                #Como apunte el connector se trata de un checker para el scertificado en este caso como muchas páginas no verifican este 
                # certificado pues podemos también no verificarlo y de esta manera poder pasar el filtro y con trust_env=True 
                # poder decirle al prgrama que en este caso queremos que confí en la web siempre    
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False) ,trust_env=True) as clientSession:
                    serverResponse = await clientSession.get(imgSrc)
                    responseStatus = serverResponse.status
                    imgBytes = await serverResponse.read()

                    # Estoy comparando el Status ya que es con lo que se debería comparar al no ser necesariamente asíncrono 
                    # porque lo es implicitamente en la petición anterior al servidor
                    if responseStatus == 200:
                        self.bytesfoto.append(imgBytes)
                        sys.stdout.write(bcolors.OKGREEN)
                        print(f'{imgName} : {imgSrc} -> STATUS OK : {responseStatus}')
                        sys.stdout.write(bcolors.ENDC)
                    else:
                        sys.stdout.write(bcolors.FAIL)
                        print(f'{imgName} : {imgSrc} -> STATUS FAILED : {responseStatus}')
                        sys.stdout.write(bcolors.ENDC)

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