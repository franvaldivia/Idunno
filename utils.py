import os
from io import BytesIO
from PIL import Image
import requests
import pandas as pd
import random

def read_value_from_file(file_name, default_value=0):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return int(file.read().strip())
    else:
        return default_value

def write_value_to_file(file_name, value):
    with open(file_name, 'w') as file:
        file.write(str(value))

def fetch_image_from_url(url):
    response = requests.get(url)
    print(response)
    return Image.open(BytesIO(response.content))

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def read_last_update_time(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return float(file.read().strip())
    else:
        return 0.0

def write_last_update_time(file_name, timestamp):
    write_value_to_file(file_name, timestamp)

def read_excel(excel):
    # Lee el archivo Excel y devuelve una lista de listas
    file = pd.read_excel(excel, header=None)
    all_values = []
    for i in range(len(file)):
        # Cada fila se convierte en una lista de preguntas y respuestas
        all_values.append(file.iloc[i].tolist())
    
    return all_values

def get_random_question_and_answer(question_list):
    random_index = random.randint(0, len(question_list) - 1)
    # Asume que cada pregunta y respuesta están en la misma fila
    question = question_list[random_index][0]  # Primera columna: pregunta
    answer = question_list[random_index][1]    # Segunda columna: respuesta
    return question, answer
