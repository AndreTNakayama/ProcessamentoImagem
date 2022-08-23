import builtins
from email.mime import image
from fileinput import filename
import io
from optparse import Values
import os
from stat import FILE_ATTRIBUTE_NORMAL
import PySimpleGUI as sg
from PIL import Image
import pathlib
import urllib.request

def main():
    layout = [
        [sg.Image(key="-IMAGE-", size=(500, 500))],

        [
            sg.Text("Arquivo de Imagem"),
            sg.Input(size=(25,1), key="-FILE-"),
            sg.FileBrowse(file_types=[("JPEG (*.jpg)", "*.jpg"), ("Todos os ficheiros", "*.*")]),
            sg.Button("Carregar Imagem")
        ],
        
        [
            sg.Button("Salvar Thumbnail"), 
            sg.Button("Qualidade Reduzida"),
            sg.Combo(["JPEG", "GIF", "PNG", "BMP", "PDF", "SGV", "WEBP"], key="-COMBO-"),
            sg.Button("Salvar Imagem")
        ],

        [
            sg.Text("Endereço de Imagem"),
            sg.Input(size=(25,1), key="-URL-"),
            sg.Button("Carregar Endereço (URL)")
        ]
    ]

    window = sg.Window("Visualizador de Imagem", layout=layout)

    while True:
        event, value = window.read()
        if event == "Exit" or event == sg.WINDOW_CLOSED:
            break

        if event == "Carregar Imagem":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                image = Image.open(filename)
                image.thumbnail((500, 500))
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                window["-IMAGE-"].update(data=bio.getvalue(), size=(500,500))

        if event == "Salvar Thumbnail":
            filename = value["-FILE-"]

            if filename:
                image = Image.open(filename)
                MAX_SIZE = (100, 100) 
                image.thumbnail(MAX_SIZE) 
                image.save('thumbnail.png')

        if event == "Qualidade Reduzida":
            filename = value["-FILE-"]

            if filename:
                image = Image.open(filename)
                image.save("qualidade.jpg", quality=5) 

        if event == "Salvar Imagem":
            filename = value["-FILE-"]

            if filename:
                image = Image.open(filename)
                teste = value["-COMBO-"]
                image.save("Imagem." + teste, format=teste)

        if event == "Carregar Endereço (URL)":
            filename = value["-URL-"]

            if filename:
                urllib.request.urlretrieve(filename, "teste")
                image = Image.open("teste")
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                window["-IMAGE-"].update(data=bio.getvalue(), size=(500,500))
                

    window.close()
    os.remove("teste")

if __name__ == "__main__":
    main()