import requests
from sql import get_and_update_counter

def call_motor_1():
    # Dirección IP de la ESP32 (reemplázala con la IP que aparece en el monitor serie de tu ESP32)
    ESP32_IP = "http://90.163.205.199:80"  # Cambia esto por la IP asignada a tu ESP32
    x = get_and_update_counter()
    # Ruta para enviar la solicitud
    url = f"{ESP32_IP}/"

    # Parámetro necesario para activar el motor
    params = {
        "code": "1234",  
        "move": x
    }

    try:
        # Hacer una solicitud GET al servidor de la ESP32 con el parámetro
        response = requests.get(url, params=params)
        
        # Mostrar la respuesta del servidor
        if response.status_code == 200:
            print(f"Respuesta del servidor: {response.text}")
        else:
            print(f"Error: Código de estado {response.status_code} - {response.text}")
    except requests.ConnectionError:
        print("Error: No se pudo conectar con la ESP32")

    return True





