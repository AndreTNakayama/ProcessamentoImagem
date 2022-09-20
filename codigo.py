import io
import os
import webbrowser
import urllib.request
import PySimpleGUI as sg
from PIL import ImageColor
from  pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import ImageFilter

sg.theme('DarkAmber')

file_types = [("(JPEG (*.jpg)","*.jpg"),
              ("All files (*.*)", "*.*")]

fields = {
    "File name" : "File name",
    "File size" : "File size",
    "Model" : "Camera Model",
    "ExifImageWidth" : "Width",
    "ExifImageHeight" : "Height",
    "DateTime" : "Creating Date",
    "static_line" : "*",
    "MaxApertureValue" : "Aperture",
    "ExposureTime" : "Exposure",
    "FNumber" : "F-Stop",
    "Flash" : "Flash",
    "FocalLength" : "Focal Length",
    "ISOSpeedRatings" : "ISO",
    "ShutterSpeedValue" : "Shutter Speed",
    "GPSLatitude" : "GPS Latitude",
    "GPSLongitude" : "GPS Longitude"
}

def filter(input_image, output_image, type):
    image = Image.open(input_image)
    if type == "Blur":
        filtered_image = image.filter(ImageFilter.BLUR)
    if type == "BoxBlur":
        filtered_image = image.filter(ImageFilter.BoxBlur(radius=3))
    if type == "Contour":
        filtered_image = image.filter(ImageFilter.CONTOUR)
    if type == "Detail":
        filtered_image = image.filter(ImageFilter.DETAIL)
    if type == "Edge Enhance":
        filtered_image = image.filter(ImageFilter.EDGE_ENHANCE)
    if type == "Emboss":
        filtered_image = image.filter(ImageFilter.EMBOSS)
    if type == "Find Edges":
        filtered_image = image.filter(ImageFilter.FIND_EDGES)
    if type == "Gaussian Blur":
        filtered_image = image.filter(ImageFilter.GaussianBlur)
    if type == "Sharpen":
        filtered_image = image.filter(ImageFilter.SHARPEN)
    if type == "Smooth":
        filtered_image = image.filter(ImageFilter.SMOOTH)
    filtered_image.save(output_image)

def get_exif_data(path):
    exif_data = {}
    try:
        image = Image.open(path)
        info = image._getexif()
    except OSError:
        info = {}

    #Se não encontrar o arquivo
    if info is None:
        info = {}
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            gps_data = {}
            for gps_tag in value:
                sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                gps_data[sub_decoded] = value[gps_tag]
            exif_data[decoded] = gps_data
        else:
            exif_data[decoded] = value
    return exif_data

def muda_para_cinza(imagem_entrada, imagem_saida):
    imagem = Image.open(imagem_entrada)
    imagem = imagem.convert("L")
    imagem.save(imagem_saida)

def cria_imagem(filename, size):
    image = Image.new("RGBA", size)
    cor1 = ImageColor.getcolor("red", "RGBA")
    cor2 = ImageColor.getcolor("yellow", "RGBA")
    cor = cor1
    count = 0

    for y in range(size[1]):
        for x in range(size[0]):
            if  count == 5:
                cor = cor2 if cor1 == cor else cor1
                count = 0
            image.putpixel((x,y), cor)
            count += 1

    image.save(filename)    

def quantidade_cores(imagem_entrada, imagem_saida, quantidade):
    imagem = Image.open(imagem_entrada) 
    imagem = imagem.convert("P", palette=Image.Palette.ADAPTIVE, colors=quantidade)
    imagem.save(imagem_saida)

def carregarImagem(filename, window):
    image = Image.open(filename)
    image.thumbnail((500, 500))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    window["-IMAGE-"].update(data=bio.getvalue(), size=(500,500))

def calcula_paleta(branco):
    paleta = []
    r,g,b = branco
    for i in range(255):
        new_red = r * i // 255
        new_green = g * i // 255
        new_blue = b * i // 255
        paleta.extend((new_red, new_green, new_blue))
    return paleta 

def converte_sepia(input, output):
    branco = (170, 120, 95)
    paleta = calcula_paleta(branco)
    
    imagem = Image.open(input)
    imagem = imagem.convert("L")
    imagem.putpalette(paleta)
    sepia = imagem.convert("RGB")

    sepia.save(output)

def _get_if_exist(data, key):
    if key in data:
        return data[key]	
    return None
    
def defteste(value, event, window):
    filename = value["-FILE-"]
    if os.path.exists(filename):
        filter(filename, event + ".jpg", event)
        carregarImagem(event + ".jpg", window)

def main():
    menu_def=['&File', ['&Save', '&Open', '&Load Image Data', 'Filter', 
    ['Blur', 'BoxBlur', 'Contour', 'Detail', 'Edge Enhance', 'Emboss', 'Find Edges', 'Gaussian Blur', 'Sharpen', 'Smooth']]],['&Filtro(s)', ['Preto e branco', 'Quantidade de cores', 'Serpia', 'Criar Imagem']]

    layout = [
        [sg.Menu(menu_def, background_color='lightsteelblue',text_color='navy', 
            disabled_text_color='yellow', font='Verdana', pad=(10,10))],

        [sg.Combo([1, 4, 8, 16, 32, 64, 128], key="-QUANTIDADE-")],

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

        latitude = None
        longitude = None

        if event == "Exit" or event == sg.WINDOW_CLOSED:
            break

        if event == "Load Image Data":
            col1=[[sg.Image(key="-IMAGEPOPUP-", size=(410, 410))],
            [sg.FileBrowse("Select your image", file_types=file_types, key="-LOAD-", enable_events=True)]]
            col2=[]

            for field in fields:
                col2 += [[sg.Text(fields[field], size=(10,1)),sg.Text("", size=(25,1), key=field)]]

            col2 += [[sg.Button("Verificar local da foto")]]

            popup = [[sg.Column(col1), sg.Column(col2)]]
            popupWindow = sg.Window("Image information", popup)

            while True:
                event, values = popupWindow.read()
                if event == "Exit" or event == sg.WIN_CLOSED:
                    break
                
                if event == "-LOAD-":
                    image_path = Path(values["-LOAD-"])
                    
                    image = Image.open(image_path)
                    image.thumbnail((410, 410))
                    bio = io.BytesIO()
                    image.save(bio, format="PNG")
                    popupWindow["-IMAGEPOPUP-"].update(data=bio.getvalue(), size=(410,410))
                    
                    # image_path = Path(values["-LOAD-"])
                    exif_data = get_exif_data(image_path.absolute())

                    if "GPSInfo" in exif_data:		
                        gps_info = exif_data["GPSInfo"]

                    for field in fields:
                        if field == "File name":
                            popupWindow[field].update(image_path.name)
                        elif field == "File size":
                            popupWindow[field].update(image_path.stat().st_size)
                        elif field == "GPSLatitude" and "GPSInfo" in exif_data:
                            popupWindow[field].update(_get_if_exist(gps_info, "GPSLatitude"))
                            # latitude = 
                            x, y, z = _get_if_exist(gps_info, "GPSLatitude")
                            latitude = round(float(x + (y + (z/60))/60), 8)
                            print("", latitude)
                        elif field == "GPSLongitude" and "GPSInfo" in exif_data:
                            popupWindow[field].update(_get_if_exist(gps_info, "GPSLongitude"))
                            x, y, z = _get_if_exist(gps_info, "GPSLongitude")
                            longitude = round(float(x + (y + (z/60))/60), 8)
                            print("", longitude)
                        else:
                            popupWindow[field].update(exif_data.get(field, "No data"))

                if event == "Verificar local da foto":
                    if latitude != None and longitude != None:
                        webbrowser.open("https://www.google.com.br/maps/place/" + str(latitude) + ",-" + str(longitude))
                        latitude = None
                        longitude = None

        if event == "Blur" or event == "BoxBlur" or event == "Contour" or event == "Detail" or event == "Edge Enhance" or event == "Emboss" or event == "Find Edges" or event == "Gaussian Blur" or event == "Sharpen" or event == "Smooth":
            defteste(value, event, window)

        if event == "Preto e branco":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                muda_para_cinza(filename, "imagem_preto_branco.jpg")

        if event == "Quantidade de cores":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                quantidade = value["-QUANTIDADE-"]
                quantidade_cores(filename, "quantidade_cores.png", quantidade)

        if event == "Serpia":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                converte_sepia(filename, "serpia.png")

        if event == "Criar Imagem":
            cria_imagem("CriarImagem.png", (100, 100))

        if event == "Save":
            urllib.request.urlretrieve(filename, "teste")
            image = Image.open("teste")
            image.save("URL", format="PNG")

        if event == "Carregar Imagem":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                carregarImagem(filename, window)

        if event == "Salvar Thumbnail":
            filename = value["-FILE-"]
            url = value["-URL-"]

            if filename:
                image = Image.open(filename)
                MAX_SIZE = (100, 100) 
                image.thumbnail(MAX_SIZE) 
                image.save('thumbnail.png')
            if url:
                urllib.request.urlretrieve(url, "thumbnailURL")
                image = Image.open("thumbnailURL")
                MAX_SIZE = (100, 100) 
                image.thumbnail(MAX_SIZE) 
                # bio = io.BytesIO()
                image.save("thumbnailURL.png", format="PNG")

        if event == "Qualidade Reduzida":
            filename = value["-FILE-"]

            if filename:
                image = Image.open(filename)
                image.save("qualidade.jpg", quality=5) 

        if event == "Salvar Imagem":
            filename = value["-FILE-"]
            url = value["-URL-"]

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
    # os.remove("teste")
    os.remove("thumbnailURL")

if __name__ == "__main__":
    main()