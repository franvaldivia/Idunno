from flask import Flask, render_template, jsonify, request, session
from datetime import date, datetime
import time
from PIL import Image
from flask_socketio import SocketIO, emit
from utils import read_value_from_file, write_value_to_file, read_last_update_time,read_excel, write_last_update_time,get_random_question_and_answer
from webhooks import  process_image_from_story_mention
from config import  IMAGE_INDEX_FILE, LAST_UPDATE_FILE, IMAGES,  PRIVACY_POLICY_PATH, VERIFY_TOKEN
from sql import get_all_messages,get_last_message,init_db,save_question_answer,get_question_answer,save_user_answer,delete_last_message, check_name_exists, get_first_message,insert_record,insert_game_result,get_all_game_results, clear_user_data
import os
from calls import call_motor_1
from reporting_logic import generate_report, generate_report_day
from send_message import enviar_email


app = Flask(__name__)

socketio = SocketIO(app)

current_question = None
current_answer = None
question_step = 1
timer_running = False  # Variable global para controlar si el temporizador está corriendo XD
processing = False 
processing_tail = False
count = 0
publicidad_empresa = None
play = None

init_db()



@app.route('/')
def index():
    return render_template("index.html")

# Manejamos la conexión al socket
@socketio.on('connect')
def handle_connect():
    print("Cliente conectado")
    emit('connected', {'message': 'Conexión establecida con el servidor'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Cliente desconectado")


@socketio.on('first_question')
def first_question():
    global current_question, current_answer, question_step, processing_tail

    PREGUNTA_1 = read_excel("premio/Pregunta_1.xlsx")
    current_question, current_answer = get_random_question_and_answer(PREGUNTA_1)
    save_question_answer(current_question, current_answer)
    question_step = 1
    if processing_tail == False:
        socketio.emit('first_question_2', {'value': current_question,'value2': current_answer})


@app.route('/webhook', methods=['GET', 'POST'])
def get_play():

    try:
        # Manejo del método POST
        if request.method == 'POST':
            data = request.json
            print('Hola')
            print (data)
            if 'object' in data and data['object'] == 'instagram':
                for entry in data.get('entry', []):
                    for messaging_event in entry.get('messaging', []):
                        if messaging_event.get('message'):
                            sender_id = messaging_event.get('sender', {}).get('id')
                            attachments = messaging_event['message'].get('attachments', [])
                            if attachments:
                                for attachment in attachments:
                                    if attachment.get("type") == 'story_mention':
                                        print(f'------------------------------------1----------------------------------------')
                                        con = process_image_from_story_mention(data)

                                        if con != False and con != None:
                                        
                                            k = insert_record(sender_id,con)
                                            handle_tail()
                                            
                                            if k == True:
                                                print(f'\n\nPaso 1. Hemos recibido un nuevo valor y añadido a la cola {con}\n\n')
                                                print(f'el estado de processing es {processing} en GET PLAY')
                                                if not processing:  # Si no estamos procesando, procesamos el siguiente
                                                    process_queue()
                                                return jsonify(value=con), 200
                                    if attachment.get("type") == 'image':
                                        print("Hola he recibido una imagen")
                                        process_image_from_story_mention(data)


            return '', 204  # No content si no hay nuevo mensaje

        # Manejo del método GET
        if request.method == 'GET':
            if request.args.get('hub.verify_token') == VERIFY_TOKEN:
                return request.args.get('hub.challenge'), 200
            return 'Token inválido', 403
        

    except Exception as e:
        return jsonify(error=str(e)), 500
    
def process_queue():
    global processing, processing_tail

    print(f'\n\nel estado de processing es {processing} en process_queue() \n\n')

    print(get_first_message())

    FM = get_first_message()[0] 

    if FM!= None and not processing:  # Solo procesar si no hay procesamiento en curso
        print('he entrado en el proces q')
        processing = True  # Indicamos que empezamos a procesar
        con2 = get_first_message()  # Tomamos el primer elemento de la cola

        print(f'{con2}---------------{con2[1]}')

        if con2[1] == "1" and processing_tail == False:
            processing_tail = True
            socketio.emit('newMessage', {'value': con2[2]})  # Emitimos el primer mensaje al cliente
            print(f'\n\nPaso 2. Hemos enviado el ultimo valor recibido de la cola {con2}\n\n')

        if con2[1] == "0" and processing_tail == False:
            processing_tail = True
            socketio.emit('newMessage2', {'value': con2[2]})  # Emitimos el primer mensaje al cliente
            delete_last_message(con2[0])
            for _ in range(9):  # Pausa 14 segundos de forma controlada
                socketio.sleep(1) 
            processing_tail = False



            
    else:
        processing = False  # Marcamos que hemos terminado si la cola está vacía
        print(f'\n\nPaso extra. Nos hemos quedado sin cola\n\n')
        

# En la función que maneja el webhook (get_play), al agregar un nuevo mensaje a la cola:


@socketio.on('messageProcessed')
def handle_message_processed():
    global processing, processing_tail

    processing = False  # Marcamos que ya no estamos procesando
    processing_tail = False

    if get_first_message():  # Si hay más mensajes en la cola
        process_queue()  # Procesamos el siguiente mensaje en la cola
    else:
        processing = False


@app.route('/question', methods=['POST'])
def question():
    global count, play
    if request.method == 'POST':
        count += 1
        print(f'EL valor del count en question 1 {count}')
        try:
            data = request.json

            if check_name_exists(get_last_message()) == True and count < 2 and play == 'a':

                user_answer = next(iter(data))  # Tomamos la clave del diccionario como la respuesta
                save_user_answer(user_answer)

                print(user_answer)
                print(f'\n\nPaso 5. La respuesta que hemos recibido del jugador es {user_answer}\n\n')

                # Procesar la respuesta cuando llegue
                process_user_answer(user_answer)
                print(f'EL valor del count en question 2 {count}')


            return jsonify(correct="Respuesta recibida y guardada correctamente"), 200

        except Exception as e:
            return jsonify(error=str(e)), 500


@socketio.on('submitAnswer')
def handle_submit_answer():
    global current_question, current_answer, question_step
    # Enviar la siguiente pregunta sin esperar la respuesta


    print(f'\n\nPaso 3. Nos ha llamado el HTML para que activemos el submitanswer\n\n')
    
    send_next_question()
    


def send_next_question():
    global current_question, current_answer, question_step, count

    # Leer las preguntas para el paso actual
    PREGUNTA_2 = read_excel("premio/Pregunta_2.xlsx")
    PREGUNTA_3 = read_excel("premio/Pregunta_3.xlsx")
    PREGUNTA_4 = read_excel("premio/Pregunta_4.xlsx")


    if question_step == 2:
        current_question, current_answer = get_random_question_and_answer(PREGUNTA_2)
        save_question_answer(current_question, current_answer)
    elif question_step == 3:
        current_question, current_answer = get_random_question_and_answer(PREGUNTA_3)
        save_question_answer(current_question, current_answer)
    elif question_step == 4:
        current_question, current_answer = get_random_question_and_answer(PREGUNTA_4)
        save_question_answer(current_question, current_answer)

    current_question, current_answer = get_question_answer()


    emit('QuestionResult', {'question': current_question, 'answer': current_answer })
    emit('timer',{'value': True})

    print(f'\n\nPaso 4. Estamos en el step {question_step} y hemos enviado la pregunta: \n{current_question}\n la respuesta ha esta pregunta es: \n {current_answer} \n\n')
    count = 0
    print(f'EL valor del count en send next question {count}')




def process_user_answer(user_answer):
    global current_answer, question_step, current_question, publicidad_empresa,count

    print(f'EL valor del count en process_user_answer {count}')

    # Verificar si la respuesta es correcta
    if str(user_answer) == str(current_answer):
        control_timer('b')

        question_step += 1
        
        count += 1

        socketio.emit('answerResult', {'correct': True})

        print(f'\n\nPaso 6. La respuesta del jugadro es correcta \n\n')

        if question_step > 4:
            

            P = get_first_message()[0]
            print(f'EL VALOR DEL DENSER ANTES DE BORRAR ES {P}')
            formatted_time = datetime.now().strftime('%H:%M:%S')
            question_step = question_step - 1 
            if P != -1:
                insert_game_result(date.today(), formatted_time, P, "SI", "NO", question_step, str(publicidad_empresa) )
            question_step = 1
            delete_last_message(P)
            handle_tail()
            print(f'\n\nPaso 7. EL jugador ha superado el juego \n\n')
            socketio.emit('first_question')

    else:
        count += 1
        control_timer('b')
        T = get_first_message()[0]
        formatted_time = datetime.now().strftime('%H:%M:%S')
        print(f'EL VALOR DEL DENSER ANTES DE BORRAR ES {T}')
        question_step = question_step - 1 
        if T != -1:
            insert_game_result(date.today(), formatted_time, T, "NO", "NO", question_step, str(publicidad_empresa))
        question_step = 1
        delete_last_message(T)
        socketio.emit('answerResult', {'correct': False})
        socketio.emit('timer', {'value': False})
        handle_tail()
        print(f'\n\nPaso 7.1. EL jugador no ha superado el juego \n\n')
        socketio.emit('first_question')



    # Después de procesar la respuesta, enviar la siguiente pregunta
    



@app.route('/get_image')
def get_image():
    global publicidad_empresa
    current_time = time.time()
    last_update_time = read_last_update_time(LAST_UPDATE_FILE)

    if current_time - last_update_time >= 30:
        current_index = read_value_from_file(IMAGE_INDEX_FILE)
        next_index = (current_index + 1) % len(IMAGES)
        write_value_to_file(IMAGE_INDEX_FILE, next_index)
        write_last_update_time(LAST_UPDATE_FILE, current_time)
    image_index = read_value_from_file(IMAGE_INDEX_FILE)
    index = image_index + 1
    publicidad_empresa = "Publicidad_" + str(index) 
    print(f'----------------{publicidad_empresa}------------------')

    return jsonify(image=IMAGES[image_index])


@socketio.on('tail_state')
def handle_tail():
    players = get_all_messages()  # Obtener el siguiente jugador
    print("Me han llamado al tailstate")
    socketio.emit('tail', {'value': players})  # Asignar el turno al nuevo jugador



@app.route('/privacy')
def privacy():
    try:
        with open(PRIVACY_POLICY_PATH, 'r') as file:
            privacy_text = file.read()
        return render_template('privacy.html', privacy_text=privacy_text)
    except Exception as e:
        return f"Error al cargar la política de privacidad: {e}", 500
    
@app.route('/reporting', methods=['GET', 'POST'])
def reporting():   
    return render_template('report.html',)

@app.route('/reporting/global', methods=['GET', 'POST'])
def reporting_global():
    # Valores por defecto
    default_values = {
        "start_date": "",
        "end_date": "",
        "agrupacion": "dias",
        "premiado": "-",
        "completo": "-",
        "publicidad": "-"
    }

    if request.method == 'POST':
        # Obtener filtros del formulario
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        agrupacion = request.form.get('agrupacion', 'dias')  # 'dias', 'semanas', 'meses'
        premiado = request.form.get('global_premiado', '-')
        completo = request.form.get('global_completo', '-')
        publicidad = request.form.get('global_publicidad', '-')

        # Actualizar valores por defecto con los recibidos en el formulario
        default_values.update({
            "start_date": start_date,
            "end_date": end_date,
            "agrupacion": agrupacion,
            "premiado": premiado,
            "completo": completo,
            "publicidad": publicidad
        })

        # Datos simulados (puedes reemplazarlo con una carga real)
        data_list = get_all_game_results()
        # Generar reporte y calcular estadísticas
        report_data = generate_report(
            data_list, start_date, end_date, agrupacion, premiado, completo, publicidad
        )

        # Renderizar con datos del reporte
        return render_template(
            'report.html',
            report_data=report_data,  # Pasamos todo el diccionario de datos
            **default_values  # Pasar valores actualizados al template
        )

    # Si es un GET, renderiza con valores por defecto
    return render_template('report.html', **default_values)

@app.route('/reporting/day', methods=['GET', 'POST'])
def reporting_day():
    # Valores por defecto
    default_values = {
        "date": "",
        "premiado": "-",
        "completo": "-",
        "publicidad": "-"
    }

    if request.method == 'POST':
        # Obtener filtros del formulario
        date = request.form.get('date')
        premiado = request.form.get('daily_premiado', '-')
        completo = request.form.get('daily_completo', '-')
        publicidad = request.form.get('daily_publicidad', '-')

        # Actualizar valores por defecto con los recibidos en el formulario
        default_values.update({
            "date": date,
            "premiado": premiado,
            "completo": completo,
            "publicidad": publicidad
        })

        # Datos simulados (puedes reemplazarlo con una carga real)
        data_list = get_all_game_results()
        # Generar reporte y calcular estadísticas
        report_data_day = generate_report_day(
            data_list, date, premiado, completo, publicidad
        )

        # Renderizar con datos del reporte
        return render_template(
            'report.html',
            report_data_day=report_data_day,  # Pasamos todo el diccionario de datos
            **default_values  # Pasar valores actualizados al template
        )

    # Si es un GET, renderiza con valores por defecto
    return render_template('report.html', **default_values)

@socketio.on('timer_2')   
def control_timer(data):
    global timer_running
    
    if data == 'a' and not timer_running:
        # Inicia el temporizador si no está corriendo
        timer_running = True
        socketio.start_background_task(start_timer)  # Lanza el temporizador como una tarea de fondo con Flask-SocketIO
    elif data == 'b' and timer_running:
        # Detiene el temporizador si está corriendo
        timer_running = False  # Actualiza la bandera para que el temporizador se detenga

def start_timer():
    global timer_running, count
    for _ in range(25):  # Pausa 20 segundos de forma controlada
        socketio.sleep(0.5)  # Pausa por 1 segundo en lugar de 20 para permitir la cancelación en el proceso
        if not timer_running:
            return  # Sale de la función si el temporizador se ha detenido
    if timer_running:
        process_user_answer("GH")  # Procesa la respuesta solo si el temporizador sigue corriendo
        print("---------- HEMOS EJECCUTADO GH --------------")
    timer_running = False  # Asegúrate de que se resetea el estado del temporizador después de la ejecución

@socketio.on('motor')   
def control_motor():
    call_motor_1()

@socketio.on('let_play')
def letplay(data):
    global play
    play = data

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'GET' or request.method == 'POST':
        try:
            # Llama a la función enviar_email y asume que retorna True si fue exitoso
            enviar_email()
            return jsonify({'success': True}), 200  # Retorna un JSON con un código HTTP 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # Maneja errores y retorna 500
    else:  # Si es un GET, retorna información o un mensaje
        return jsonify({'message': 'Use POST to send emails'}), 200


if __name__ == '__main__':

    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
