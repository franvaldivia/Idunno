import os
import psycopg2
from datetime import datetime, timedelta

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.environ.get('DATABASE_URL')

# Función para conectar a la base de datos
def connect_db():
    return psycopg2.connect(DATABASE_URL)

# Inicializar las tablas en PostgreSQL
def init_db():
    conn = connect_db()
    c = conn.cursor()

    # Crear tablas
    c.execute('''
        CREATE TABLE IF NOT EXISTS publicidad_message (
            id SERIAL PRIMARY KEY,
            value TEXT NOT NULL,
            rep TEXT DEFAULT NULL,
            name TEXT DEFAULT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_state (
            id SERIAL PRIMARY KEY,
            question TEXT,
            answer TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            id SERIAL PRIMARY KEY,
            answer TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS player (
            number TEXT NOT NULL,
            hora TEXT NOT NULL,
            fecha TEXT NOT NULL
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS game_results (
            id SERIAL PRIMARY KEY,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            jugador TEXT NOT NULL,
            premiado TEXT  NOT NULL,
            completo TEXT NOT NULL,
            publicidad TEXT DEFAULT NULL,
            step TEXT NOT NULL
        );
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS counter (
            id SERIAL PRIMARY KEY,
            value INTEGER NOT NULL
        );
    ''')

    # Insertar valor inicial solo si no existe
    c.execute('SELECT COUNT(*) FROM counter')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO counter (value) VALUES (0)')


    conn.commit()
    conn.close()

# Agregar un mensaje a la base de datos
def add_message(value, rep, name):
    conn = connect_db()
    c = conn.cursor()
    c.execute('INSERT INTO publicidad_message (value, rep, name) VALUES (%s, %s, %s)', (value, rep, name))
    conn.commit()
    conn.close()

# Obtener el último mensaje
def get_last_message():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT value FROM publicidad_message ORDER BY id DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Obtener el primer mensaje
def get_first_message():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT value, rep, name FROM publicidad_message ORDER BY id ASC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result if result else (None, None, None)

# Obtener todos los mensajes
def get_all_messages():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT name FROM publicidad_message')
    result = c.fetchall()
    conn.close()
    return result

# Eliminar el mensaje más antiguo con un valor específico
def delete_last_message(value):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT id FROM publicidad_message WHERE value = %s ORDER BY id ASC LIMIT 1', (value,))
    oldest_entry = c.fetchone()
    if oldest_entry:
        c.execute('DELETE FROM publicidad_message WHERE id = %s', (oldest_entry[0],))
        conn.commit()
    conn.close()

# Comprobar si existe un nombre en la base de datos
def check_name_exists(name):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT 1 FROM publicidad_message WHERE value = %s', (name,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Guardar el estado del cuestionario para un usuario
def save_question_answer(question, answer):
    conn = connect_db()
    c = conn.cursor()
    c.execute('INSERT INTO user_state (question, answer) VALUES (%s, %s)', (question, answer))
    conn.commit()
    conn.close()

# Obtener el estado más reciente guardado en la tabla
def get_question_answer():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT question, answer FROM user_state ORDER BY id DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result if result else None

def delete_all_records():

    conn = connect_db()
    c = conn.cursor()
    c.execute('DELETE FROM user_state')  # Elimina todos los registros
    conn.commit()  # Confirma los cambios
    conn.close()   # Cierra la conexión



# Guardar la respuesta del usuario
def save_user_answer(user_answer):
    conn = connect_db()
    c = conn.cursor()
    c.execute('INSERT INTO user_answers (answer) VALUES (%s)', (user_answer,))
    conn.commit()
    conn.close()

# Obtener la última respuesta del usuario
def get_last_user_answer():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT answer FROM user_answers ORDER BY id DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Insertar o actualizar registros en la tabla player

def insert_record(number, name):
    conn = connect_db()
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_datetime = datetime.now()

    # Verificar si el registro ya existe en `sender`
    cursor.execute('SELECT hora, fecha FROM player WHERE number = %s', (number,))
    record = cursor.fetchone()

    if record:
        # Si el registro existe, calcular la diferencia de tiempo
        record_datetime = datetime.strptime(f"{record[1]} {record[0]}", "%Y-%m-%d %H:%M:%S")
        time_difference = (current_datetime - record_datetime).total_seconds()

        if time_difference >= 86400:
            # Si ha pasado más de un dia actualizar el registro
            cursor.execute('''
                UPDATE player
                SET hora = %s, fecha = %s
                WHERE number = %s
            ''', (current_time, current_date, number))
            conn.commit()
            add_message(number, 1, name)
            print(f'Dejamos al jugador {number} jugar porque ha pasado más de 1 dia.')
            print('...................................................................')
            print(get_last_completo_by_jugador(number))
            if get_last_completo_by_jugador(number) == True:
                name = name + " BONUS"
                add_message(-1, 1, name)
                return True
            return True
        else:
            conn.commit()
            add_message(number, 0, name)
            print(f'No dejamos al jugador {number} jugar porque NO ha pasado más de 1 dia.')
            return True
    else:
        # Si no existe el registro, insertar uno nuevo
        cursor.execute('''
            INSERT INTO player (number, hora, fecha)
            VALUES (%s, %s, %s)
        ''', (number, current_time, current_date))
        conn.commit()
        add_message(number, 1, name)
        print(f'Dejamos al jugador {number} jugar porque no existía.')
        return True

    # Cerrar la conexión
    cursor.close()
    conn.close()


def insert_game_result(fecha, hora, jugador, premiado, completo, step, publicidad=None):

    try:
        conn = connect_db()
        c = conn.cursor()

        query = '''
            INSERT INTO game_results (fecha, hora, jugador, premiado, completo, publicidad, step)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        c.execute(query, (fecha, hora, jugador, premiado, completo, publicidad, step))
        conn.commit()
        print("Registro insertado exitosamente.")
    except Exception as e:
        print(f"Error al insertar el registro: {e}")
    finally:
        if conn:
            conn.close()

def get_all_game_results():
    try:
        conn = connect_db()
        c = conn.cursor()

        query = "SELECT fecha, hora, jugador, premiado, completo, publicidad, step FROM game_results"
        c.execute(query)

        results = c.fetchall()
        return results
    except Exception as e:
        print(f"Error al obtener los registros: {e}")
        return []
    finally:
        if conn:
            conn.close()
    


def update_completo_if_recent(sender):

    # Conexión a la base de datos
    conn = connect_db() 
    cursor = conn.cursor()

    try:
        # Buscar el último registro del jugador
        cursor.execute("""
            SELECT id, fecha, hora
            FROM game_results
            WHERE jugador = %s
            ORDER BY fecha DESC, hora DESC
            LIMIT 1
        """, (sender,))
        result = cursor.fetchone()

        if result:
            registro_id, fecha, hora = result
            # Combinar fecha y hora en un objeto datetime
            registro_datetime = datetime.combine(fecha, hora)
            
            # Calcular si han pasado menos de 1 dia
            ahora = datetime.now()
            if timedelta(hours=14) < ahora - registro_datetime < timedelta(hours=24):

                # Actualizar la columna 'completo' a 'SI'
                cursor.execute("""
                    UPDATE game_results
                    SET completo = 'SI'
                    WHERE id = %s
                """, (registro_id,))
                conn.commit()
                print(f"Registro actualizado para el jugador {sender}.")
            else:
                print("El registro tiene más de 1 dia, no se actualiza.")
        else:
            print(f"No se encontraron registros para el jugador {sender}.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


def get_last_completo_by_jugador(jugador):
    """
    Obtiene el valor de la columna 'completo' correspondiente al último registro
    insertado del jugador especificado en la tabla 'game_results'.

    Args:
        jugador (str): El nombre del jugador.

    Returns:
        str: El valor de la columna 'completo' o None si no se encuentra.
    """
    try:
        # Conectar a la base de datos
        conn = connect_db()
        c = conn.cursor()

        # Consulta para obtener el último registro basado en el jugador
        c.execute('''
            SELECT completo
            FROM game_results
            WHERE jugador = %s
            ORDER BY id DESC
            LIMIT 1
        ''', (jugador,))

        # Obtener el resultado
        result = c.fetchone()

        # Cerrar la conexión

        if result[0] == 'SI':
            return True
        else:
            return False

    except psycopg2.Error as e:
        print("Error al consultar la base de datos:", e)
        return None

def clear_user_data():
    try:
        # Conectar a la base de datos
        conn = connect_db()
        c = conn.cursor()

        # Borrar registros de las tablas
        c.execute('DELETE FROM user_answers;')
        c.execute('DELETE FROM user_state;')

        # Confirmar cambios
        conn.commit()

        print("Registros de 'user_answers' y 'user_state' eliminados exitosamente.")
    except Exception as e:
        print(f"Error al borrar registros: {e}")
    finally:
        # Cerrar conexión
        if conn:
            conn.close()

def get_and_update_counter():
    conn = connect_db()
    c = conn.cursor()

    # Obtener el valor actual
    c.execute('SELECT value FROM counter WHERE id = 1')
    current = c.fetchone()[0]

    # Calcular el siguiente valor
    next_value = 0 if current >= 118 else current + 1

    # Actualizar la tabla
    c.execute('UPDATE counter SET value = %s WHERE id = 1', (next_value,))
    conn.commit()
    conn.close()

    return current
