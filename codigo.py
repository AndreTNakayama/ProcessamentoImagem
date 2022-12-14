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
import shutil
import tempfile
from PIL import ImageEnhance
  

sg.theme('DarkAmber')

# file_types = [("(JPEG (*.jpg)","*.jpg"),
#               ("All files (*.*)", "*.*")]

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

def brilho(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Brightness(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

def contraste(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Contrast(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

def cores(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Color(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

def nitidez(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Sharpness(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

efeitos = {
    "Normal": shutil.copy,
    "Brilho": brilho,
    "Cores": cores,
    "Contraste": contraste,
    "Nitidez": nitidez
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

    #Se n??o encontrar o arquivo
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

def carregarImagem(ids, filename, window):
    if ids is not None:
        window["-IMAGE-"].delete_figure(ids)

    image = Image.open(filename)
    image.thumbnail((500,500))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    return window["-IMAGE-"].draw_image(data=bio.getvalue(), location=(0,400))
    # image = Image.open(filename)
    # image.thumbnail((500, 500))
    # bio = io.BytesIO()
    # image.save(bio, format="PNG")
    # window["-IMAGE-"].update(data=bio.getvalue(), size=(500,500))

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

def mirror(image_path, output_image_path):
    image = Image.open(image_path)
    mirror_image = image.transpose(Image.FLIP_LEFT_RIGHT) #FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, TRANSPOSE
    mirror_image.save(output_image_path)

def rotate(image_path, degrees_to_rotate, output_image_path, backup_rotate):
    image_obj = Image.open(image_path)
    rotated_image = image_obj.rotate(degrees_to_rotate + backup_rotate)
    rotated_image.save(output_image_path)
    return degrees_to_rotate + backup_rotate

def crop_image(image_path, coords, output_image_path):
    image = Image.open(image_path)
    cropped_image = image.crop(coords)
    cropped_image.save(output_image_path)
    cropped_image.show()

def resize(input_image_path, output_image_path, size):
    image = Image.open(input_image_path)
    percentual_largura = float(size) / float(image.width)
    altura_desejada = int((image.height * percentual_largura))
    resized_image = image.resize((size, altura_desejada), Image.ANTIALIAS)
    resized_image.save(output_image_path)

def salvar_url(filename):
    urllib.request.urlretrieve(filename, "backup_URL")
    image = Image.open("backup_URL")
    MAX_SIZE = (500, 500) 
    image.thumbnail(MAX_SIZE) 
    # bio = io.BytesIO()
    image.save("backup_URL.png", format="PNG")

def aplica_efeito(ids, values, window, url):
    efeito_selecionado = values["-EFEITOS-"]
    factor = values["-FATOR-"]

    if url == True:
        filename = values["-URL-"]
        salvar_url(filename)
        filename = os.path.abspath("backup_URL.png")
    else:
        filename = values["-FILE-"]

    if filename:
        if efeito_selecionado == "Normal":
            efeitos[efeito_selecionado](filename, tmp_file)
        else:
            efeitos[efeito_selecionado](filename, factor, tmp_file)
        # image = Image.open(tmp_file)
        # image.thumbnail((100, 100))
        # bio = io.BytesIO()
        # image.save(bio, format="PNG")
        # window["-IMAGEFILTRO-"].update(data=bio.getvalue(), size=(100, 100))
        
        if ids is not None:
            window["-IMAGE-"].delete_figure(ids)
        
        image = Image.open(tmp_file)
        image.thumbnail((500,500))
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        return window["-IMAGE-"].draw_image(data=bio.getvalue(), location=(0,400))
            
        
def save_image(filename):
    save_filename = sg.popup_get_file("Salvar", file_types=file_types, save_as=True, no_window=True)
    if save_filename == filename:
        sg.popup_error("Voc?? n??o pode substituir a imagem original!")
    else:
        if save_filename:
            shutil.copy(tmp_file, save_filename)
            sg.popup(f"Arquivo {save_filename}, salvo com sucesso!")

def salvar_thumbnail(filename, bool, thumbnail):
    if thumbnail == True:
        if bool == True:
            image = Image.open(filename)
            MAX_SIZE = (100, 100) 
            image.thumbnail(MAX_SIZE) 
            image.save('thumbnail.png')
            image.show()
        else:
            urllib.request.urlretrieve(filename, "thumbnailURL")
            image = Image.open("thumbnailURL")
            MAX_SIZE = (100, 100) 
            image.thumbnail(MAX_SIZE) 
            # bio = io.BytesIO()
            image.save("thumbnailURL.png", format="PNG")
            image.show()
    else:
        save_image(filename)

file_types = [("JPEG (*.jpg)", "*.jpg"), ("PNG (*.png)", "*.png"), ("All files (*.*)", "*.*")]
tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg").name

def main():
    effect_names = list(efeitos.keys())

    menu_def=['&File', ['&Save', '&Open', 'Salvar Thumbnail','Salvar URL', 'Salvar a Imagem', '&Load Image Data', 'Salvar Imagem',
    ['JPEG', 'GIF', 'PNG', 'BMP', 'PDF', 'SGV', 'WEBP']]],['&Filtro(s)', ['Preto e branco', 'Qualidade Reduzida', 'Filter', ['Blur', 'BoxBlur', 'Contour', 'Detail', 'Edge Enhance', 'Emboss', 'Find Edges', 'Gaussian Blur', 'Sharpen', 'Smooth',], 'Quantidade de cores',['1', '4', '8', '16', '32', '64', '128'], 'Serpia', 'Criar Imagem']],['&Mais Filtros', ['Mirror', 'Rotacionar',['90', '-90'], 'Cortar', 'Resize']]

    layout = [
        [sg.Menu(menu_def, background_color='ivory',text_color='black', 
            disabled_text_color='yellow', font='Verdana', pad=(10,10))],

        # [sg.Image(key="-IMAGEFILTRO-", size=(100, 100))],
        [sg.Graph(key="-IMAGE-", canvas_size=(500, 400), graph_bottom_left=(0, 0), 
        graph_top_right=(500, 400), change_submits=True, background_color='seashell', drag_submits=True)],

        [
            sg.Text("Arquivo de Imagem"),
            sg.Input(size=(25,1), key="-FILE-"),
            sg.FileBrowse(file_types=[("JPEG (*.jpg)", "*.jpg"), ("Todos os ficheiros", "*.*")]),
            sg.Button("Carregar Imagem")
        ],

        # [
        #     sg.Text("Imagem: "),
        #     sg.Input(size=(25, 1), key="-FILEFILTRO-"),
        #     sg.FileBrowse(file_types=file_types),
        #     sg.Button("Carregar a Imagem")
        # ],

        [
            sg.Text("Endere??o de Imagem"),
            sg.Input(size=(25,1), key="-URL-"),
            sg.Button("Carregar Endere??o (URL)")
        ],

        [
            sg.Text("Efeito"),
            sg.Combo(effect_names, default_value="Normal", key="-EFEITOS-", enable_events=True, readonly=True),
        ],

        [sg.Slider(range=(0, 5), default_value=2, resolution=0.1, orientation="h", enable_events=True, key="-FATOR-")],
    ]

    window = sg.Window("Visualizador de Imagem", layout=layout)
    # window = sg.Window("Visualizador de Imagem", layout=layout).Finalize()
    # window.Maximize()

    dragging = False
    ponto_inicial = ponto_final = retangulo = None

    ids = None
    backup_rotate = 0

    while True:
        event, value = window.read()

        latitude = None
        longitude = None

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event in ["Carregar Imagem", "-EFEITOS-", "-FATOR-", 'Contour']:
            ids = aplica_efeito(ids, value, window, False)


        filename = value["-FILE-"]

        if event == "Salvar a Imagem" and filename:
            save_image(filename)

        # if event == "Carregar Imagem":
        #     filename = value["-FILE-"]
        #     if os.path.exists(filename):
        #         carregarImagem(filename, window)

        if event == "-IMAGE-":
            x, y = value["-IMAGE-"]
            if not dragging:
                ponto_inicial = (x, y)
                dragging = True
            else:
                ponto_final = (x, y)
            if retangulo:
                window["-IMAGE-"].delete_figure(retangulo)
                # Arrumar
            if None not in (ponto_inicial, ponto_final):
                retangulo = window["-IMAGE-"].draw_rectangle(ponto_inicial, ponto_final, line_color='red')
        elif event.endswith('+UP'):
            dragging = False

        if event == "Cortar":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                crop_image(filename, (140, 61, 328, 383), "cropped.jpg")

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
            filename = value["-FILE-"]
            if os.path.exists(filename):
                filter(filename, event + ".jpg", event)
                # aplica_efeito(ids, value, window, False)
                ids = carregarImagem(ids, event + ".jpg", window)

        if event == "Preto e branco":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                muda_para_cinza(filename, "imagem_preto_branco.jpg")
                ids = carregarImagem(ids, "imagem_preto_branco.jpg", window)

        if event == "Resize":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                resize(filename, "resized.jpg", 300)
                ids = carregarImagem(ids, "resized.jpg", window)

        if event == "1" or event == "4" or event == "8" or event == "16" or event == "32" or event == "64" or event == "128":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                quantidade_cores(filename, "quantidade_cores.png", int(event))
                ids = carregarImagem(ids, "quantidade_cores.png", window)

        if event == "Mirror":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                mirror(filename, "mirrored.jpg")
                ids = carregarImagem(ids, "mirrored.jpg", window)

        
        if event == "90" or event == "-90":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                backup_rotate = rotate(filename, int(event), "rotated.jpg", backup_rotate)   
                ids = carregarImagem(ids, "rotated.jpg", window)   

        if event == "Serpia":
            filename = value["-FILE-"]
            if os.path.exists(filename):
                converte_sepia(filename, "serpia.png")
                ids = carregarImagem(ids, "serpia.png", window)  

        if event == "Criar Imagem":
            cria_imagem("CriarImagem.png", (100, 100))

        if event == "Save":
            # urllib.request.urlretrieve(filename, "teste")
            # image = Image.open("teste")
            # image.save("URL", format="PNG")
            filename = value["-FILE-"]
            if os.path.exists(filename):
                save_image(filename)

        if event == "Salvar Thumbnail":
            filename = value["-FILE-"]
            url = value["-URL-"]
            if filename:
                salvar_thumbnail(filename, True, True)
            if url:
                salvar_thumbnail(url, False, True)
            
        if event == "Qualidade Reduzida":
            filename = value["-FILE-"]

            if filename:
                image = Image.open(filename)
                image.save("qualidade.jpg", quality=5) 
                ids = carregarImagem(ids, "qualidade.jpg", window)  

        if event == "JPEG" or event == "GIF" or event == "PNG" or event == "BMP" or event == "PDF" or event == "SGV" or event == "WEBP":
            filename = value["-FILE-"]
            url = value["-URL-"]

            if filename:
                image = Image.open(filename)
                image.save("Imagem_Normal." + event, format=event)
            elif url:
                urllib.request.urlretrieve(url, "save_url")
                image = Image.open("save_url")
                image.save("Imagem_Url." + event, format=event)

        if event == "Carregar Endere??o (URL)":
            filename = value["-URL-"]

            if filename:
                ids = aplica_efeito(ids, value, window, True)
                
        if event == "Salvar URL":
            filename = value["-URL-"]

            if filename:
                salvar_url(filename)

    window.close()
    # os.remove("teste")
    # os.remove("thumbnailURL")

if __name__ == "__main__":
    main()