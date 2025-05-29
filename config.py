import os
import pandas as pd
from google.oauth2 import service_account
from utils import read_excel

# Rutas de archivos

PREGUNTA_1 = read_excel("premio/Pregunta_1.xlsx")
PREGUNTA_2 = read_excel("premio/Pregunta_2.xlsx")
PREGUNTA_3 = read_excel("premio/Pregunta_3.xlsx")
PREGUNTA_4 = read_excel("premio/Pregunta_4.xlsx")
PUBLICIDAD_VALUE_FILE = 'publicidad_value.txt'
IMAGE_INDEX_FILE = 'image_index.txt'
LAST_UPDATE_FILE = 'last_update.txt'
IMAGES = ['blog-2.jpg', 'blog-3.jpg', 'blog-4.jpg']
MENSAJE2 = read_excel('premio/Descripcion.xlsx')
PRIVACY_POLICY_PATH = os.path.join('privacy_policy', 'privacy_policy.txt')

# Tokens
VERIFY_TOKEN = "EAAQdwZCXClGsBO6PuIIHZAcawQZCLtKGapCbZC2O75P8l13ZCa0ZCry2TGB4TCeV2N7u2cPZCsaBB5etyCDZCZCl9eiGkDxcYbZA5RERSFLpD7PnI5ZALSEVhNW1RBo1FBBIeEbR7sADoUaA8nS3LaXPP2novO2DrgJQaDg4ozQqK9xmI4ftMKEk5bl1ReO3g7cL8DnOqBJezntzp961lCjewZDZD"

# Google Cloud Vision API
CREDENTIALS_VISION = service_account.Credentials.from_service_account_file('Claves/idunno-434815-3ab84cd9b078.json')




