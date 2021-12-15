import base64
from tkinter import *
from tkinter.ttk import *
import rx
from PIL import ImageTk, Image
import aiohttp
import asyncio
import aiofiles
from bs4 import BeautifulSoup
import io
import base64
from urllib.request import urlopen


class App:

    def button_cont(self):

        url = self.entry.get()
        asyncio.get_event_loop().run_until_complete(self.main(url))

        # self.mostrar_imagen('Will Morbius & Doc Ock Form the Sinister Six?')



    def onselect(self, event):

        posicion = self.listbox.curselection()
        nombrefoto = self.listbox.get(posicion)
        indice = self.nombres.index(nombrefoto)

        urlfoto = self.fotobytes[indice]

        # self.image = urlopen(urlfoto).read()

        self.img = ImageTk.PhotoImage(data=urlfoto)
        self.cv.create_image(20, 20, anchor=NW, image=self.img)

    async def main(self, urls):

        async def pillarhtml(url):
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                html = await response.text()
                return html

        html = await pillarhtml(urls)
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        for img in soup.find_all('img',src=True):
            img_url = img['src']
            if img_url.find('http') == -1:
                img_url = 'http:'+img_url
            if img_url.endswith('.jpg') or img_url.endswith('.png'):
                if len(img['alt']) < 3:
                    img_name = img_url.split('/')[-1]
                else:
                    img_name = img['alt']

                if not img_name in self.nombres:
                    async with aiohttp.ClientSession() as session:
                        try:
                            response = await session.get(img_url)
                            a = await response.read()
                            #print(a)

                            if a:
                                self.fotobytes.append(a)
                                print(f'{img_name} : {img_url}')


                        except:
                            print("ERROR")
                            if len(self.nombres)>0:
                                self.nombres.pop()
                                self.__contador = self.__contador -1

                    self.nombres.append(img_name)
                    self.__contador = self.__contador + 1
        self.obslist.subscribe(
        on_next=lambda v: (
        self.listbox.insert(END, v),
        self.progressbar.step(1 / self.__contador * 99),
        self.text.configure(text=f'se encontraron {self.__contador} imágenes')),
        on_completed=print("terminado")
        )

                # await asyncio.sleep(0.1)

    def __init__(self):
        self.__contador = 0
        self.window = Tk()
        self.window.title = 'Practica1'
        self.nombres = []
        self.fotobytes = []
        self.obslist = rx.from_(self.nombres)

        # self.window.maxsize(width=300, height=200)
        # self.window.minsize(width=100, height=120)
        # self.window.geometry('800x400')

        # url a procesar
        Label(text='Url a procesar', font=('Arial Bold', 12)).grid(column=0, row=0)

        # barra de busqueda
        self.entry = Entry()
        self.entry.grid(column=2, row=0)

        # boton de buscar
        Button(text='Buscar', command=self.button_cont).grid(column=1, row=1)

        # listbox

        self.listbox = Listbox(self.window)

        self.listbox.grid(column=0, row=2)
        self.listbox.bind('<<ListboxSelect>>', self.onselect)

        # fotos

        # self.cv = Canvas(bg='white', width=300, height=300)
        self.cv = Canvas(width=300, height=300)

        self.cv.grid(row=2, column=1)

        # progressbar

        self.progressbar = Progressbar(self.window)
        self.progressbar.grid(column=2, row=3)
        ##self.progressbar.step(50)

        # encontradas

        self.text = Label(text=f'se encontraron {self.__contador} imágenes')
        self.text.grid(column=2, row=4)


        self.window.mainloop()


if __name__ == '__main__':
    App()