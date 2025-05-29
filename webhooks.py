from flask import jsonify
from utils import fetch_image_from_url, read_value_from_file, read_excel
from vision_api import detect_texts, image_to_vision_image
from PIL import Image
from config import VERIFY_TOKEN, IMAGES, MENSAJE2,PUBLICIDAD_VALUE_FILE, PREGUNTA_1,PREGUNTA_2,PREGUNTA_3,PREGUNTA_4
import re
from sql import update_completo_if_recent

publicidad2_message = None  



def process_image_from_story_mention(data):


    if 'object' in data and data['object'] == 'instagram':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event.get('sender', {}).get('id')
                    attachments = messaging_event['message'].get('attachments', [])
                    if attachments:
                        for attachment in attachments:
                            if attachment.get("type") == 'story_mention':
                                print(f'----------------------------------2------------------------------------------')

                                URL = attachment.get("payload").get('url')

                                screen_text =['Mención','@Idunno','Nombre','GIdunno','market','@Idunno_market','@idunno_market','Principal']

                                print(URL)

                                remote_image = fetch_image_from_url(URL)
                                print(remote_image)
                                remote_texts = detect_texts(image_to_vision_image(remote_image))

                                print(remote_texts)


                                common_texts = [word for word in screen_text if word in remote_texts]

                                print(common_texts)


                                if  len(screen_text)*0.2<len(common_texts):

                                    nombre = procesar_texto(remote_texts[0])


                                    return nombre
                                    
                                
                                
                            if attachment.get("type") == 'image':

                                URL = attachment.get("payload").get('url')

                                screen_text =['Mención','Principal','@Idunno','Nombre','GIdunno','market','@Idunno_market','@idunno_market','Your','story', 'Tu','tu','historia','Historia','Añade','min','minutos','un','comentario','h','H','Horas', 'horas']


                                remote_image = fetch_image_from_url(URL)
                                remote_texts = detect_texts(image_to_vision_image(remote_image))

                                print(remote_texts)

                                common_texts = [word for word in screen_text if word in remote_texts]

                                print(common_texts)


                                if  len(screen_text)*0.15<len(common_texts):

                                    print('entro en el Len')

                                    tiempo = encontrar_valor_tiempo(remote_texts[0])

                                    if int(tiempo) > 14:

                                        print(f'el tiempo encontrado es {tiempo}')
                                        update_completo_if_recent(sender_id)
                                    
                                    else:

                                        print('No hemos encontrado tiempo')


def procesar_texto(texto):
    # Paso 1: Eliminar los saltos de línea
    texto_limpio = texto.replace("\n", " ")

    # Lista de palabras a eliminar
    palabras_a_eliminar = ['Principal', '@Idunno', 'Nombre', 'GIdunno', 'Shop', '@Idunno_Shop', '@idunno_shop']

    # Paso 2: Eliminar las palabras de la lista
    for palabra in palabras_a_eliminar:
        texto_limpio = texto_limpio.replace(palabra, "")

    # Eliminar dobles espacios generados al remover palabras
    texto_limpio = ' '.join(texto_limpio.split())

    # Paso 3: Obtener la palabra después de "Nombre"
    texto_original = texto.replace("\n", " ")
    palabras = texto_original.split()
    
    if 'Nombre' in palabras:
        indice_nombre = palabras.index('Nombre')
        if indice_nombre + 1 < len(palabras):
            return palabras[indice_nombre + 1]
        else:
            return "No hay palabra después de 'Nombre'"
    else:
        return "No se encontró 'Nombre' en el texto"

def encontrar_valor_tiempo(texto):
    # Limpiar el texto
    texto_limpio = texto.replace("\n", " ")
    print('El texto limpio es: ')
    print(texto_limpio)

    # Buscar patrones de tiempo como "17h", "17 h", "17Horas", etc.
    coincidencia = re.search(r'(\d{1,2})\s*(h|H|horas|Horas)\b', texto_limpio)
    if coincidencia:
        return int(coincidencia.group(1))  # devuelve solo el número como entero

    return False


# def process_attachments(attachments):
#     """Procesa los attachments y retorna el valor de publicidad si aplica."""
#     for attachment in attachments:
#         if attachment.get("type") == 'story_mention':
#             con = process_image_from_story_mention(attachment)
#             if con:
#                 return con
#     return None