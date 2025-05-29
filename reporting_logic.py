import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import datetime


def generate_report(data_list, start_date, end_date, agrupacion, premiado, completo, publicidad):
    # Leer datos del CSV
    columns = ['fecha', 'hora', 'jugador', 'premiado', 'completo', 'publicidad', 'step']
    df = pd.DataFrame(data_list, columns=columns)

    # Convertir 'hora' a cadenas
    df['hora'] = df['hora'].apply(lambda x: x.strftime('%H:%M:%S') if isinstance(x, datetime.time) else str(x))

    # Convertir 'fecha' a datetime
    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')

    # Crear la columna 'fecha_hora'
    df['fecha_hora'] = pd.to_datetime(df['fecha'].dt.strftime('%Y-%m-%d') + ' ' + df['hora'], format='%Y-%m-%d %H:%M:%S')

    # Aplicar filtros
    filtered_df = df[(df['fecha'] >= pd.to_datetime(start_date)) & 
                     (df['fecha'] <= pd.to_datetime(end_date))]
    
    # Contar jugadores con valor "-1" en el periodo seleccionado
    count_jugador_menos_uno = filtered_df[filtered_df['jugador'] == "-1"].shape[0]

    if premiado != '-':
        filtered_df = filtered_df[filtered_df['premiado'] == premiado]
    if completo != '-':
        filtered_df = filtered_df[filtered_df['completo'] == completo]
    if publicidad != '-':
        filtered_df = filtered_df[filtered_df['publicidad'] == publicidad]

    # Gráficos de barras
    if agrupacion == 'dias':
        grouped = filtered_df.groupby(filtered_df['fecha'].dt.date)['jugador'].count()
    elif agrupacion == 'semanas':
        grouped = filtered_df.groupby(filtered_df['fecha'].dt.to_period('W'))['jugador'].count()
        grouped.index = grouped.index.to_timestamp()
    elif agrupacion == 'meses':
        grouped = filtered_df.groupby(filtered_df['fecha'].dt.to_period('M'))['jugador'].count()
        grouped.index = grouped.index.to_timestamp()

    max_value = grouped.max()
    min_value = grouped.min()

    fig, ax = plt.subplots(figsize=(10, 5))
    grouped.plot(kind='bar', ax=ax, color='blue', label='Número Total de Jugadores')
    ax.set_title('Jugadores por Periodo')
    ax.set_xlabel('Periodo')
    ax.set_ylabel('Número de Jugadores')
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    repeated_players_range = filtered_df['jugador'].value_counts()[filtered_df['jugador'].value_counts() > 1].count()
    unique_players_range = filtered_df['jugador'].nunique()
    total_players_range = filtered_df['jugador'].count()

    fig, ax = plt.subplots()
    ax.pie([repeated_players_range, unique_players_range - repeated_players_range], labels=['Repetidos', 'Únicos'],
           autopct='%1.1f%%', startangle=90)
    plt.title('Repetición de Jugadores (Rango de Fechas)')
    img_range = io.BytesIO()
    plt.savefig(img_range, format='png', bbox_inches='tight')
    img_range.seek(0)
    plot_range_url = base64.b64encode(img_range.getvalue()).decode()
    plt.close(fig)

    global_df = df.copy()
    if premiado != '-':
        global_df = global_df[global_df['premiado'] == premiado]
    if completo != '-':
        global_df = global_df[global_df['completo'] == completo]
    if publicidad != '-':
        global_df = global_df[global_df['publicidad'] == publicidad]

    repeated_players_global = global_df['jugador'].value_counts()[global_df['jugador'].value_counts() > 1].count()
    unique_players_global = global_df['jugador'].nunique()
    total_players_global = global_df['jugador'].count()

    percentage_repeated_range = (repeated_players_range / unique_players_range) * 100 if unique_players_range > 0 else 0
    percentage_repeated_global = (repeated_players_global / unique_players_global) * 100 if unique_players_global > 0 else 0

    mean_players = grouped.mean()

    # Calcular porcentajes para cada valor de step
    total_steps = filtered_df['step'].count()

    # Calcular porcentajes solo si hay datos
    if total_steps > 0:
        step_counts = filtered_df['step'].value_counts().sort_index()
        step1 = round((step_counts.loc[1] / total_steps) * 100, 2) if 1 in step_counts else 0
        step2 = round((step_counts.loc[2] / total_steps) * 100, 2) if 2 in step_counts else 0
        step3 = round((step_counts.loc[3] / total_steps) * 100, 2) if 3 in step_counts else 0
        step4 = round((step_counts.loc[4] / total_steps) * 100, 2) if 4 in step_counts else 0
    else:
        step1 = step2 = step3 = step4 = 0

    return {
        "bar_plot_url": plot_url,
        "pie_plot_range_url": plot_range_url,
        "mean_players": mean_players,
        "max_value": max_value,
        "min_value": min_value,
        "percentage_repeated_range": percentage_repeated_range,
        "percentage_repeated_global": percentage_repeated_global,
        "total_players_range": unique_players_range,
        "total_players_global_range": total_players_range,
        "total_players_global": total_players_global,
        "%step1": step1,
        "%step2": step2,
        "%step3": step3,
        "%step4": step4,
        "jugadores_menos_uno_periodo": count_jugador_menos_uno,

    }



def generate_report_day(data_list, date, premiado, completo, publicidad):
    # Crear el DataFrame a partir de la lista de datos
    columns = ['fecha', 'hora', 'jugador', 'premiado', 'completo', 'publicidad', 'step']
    df = pd.DataFrame(data_list, columns=columns)

    # Convertir 'fecha' y 'hora' a formato adecuado
    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.time

    # Filtrar los datos según la fecha proporcionada y los criterios adicionales
    filtered_df = df[df['fecha'] == pd.to_datetime(date)]
    if premiado != '-':
        filtered_df = filtered_df[filtered_df['premiado'] == premiado]
    if completo != '-':
        filtered_df = filtered_df[filtered_df['completo'] == completo]
    if publicidad != '-':
        filtered_df = filtered_df[filtered_df['publicidad'] == publicidad]

    # Crear una nueva columna 'hora_entera' para agrupar por horas
    filtered_df['hora_entera'] = filtered_df['hora'].apply(lambda x: x.strftime('%H:00'))

    # Contar el número de jugadores por hora
    jugadores_por_hora = filtered_df.groupby('hora_entera')['jugador'].count()

    # Calcular estadísticas
    mean_players = jugadores_por_hora.mean()
    max_value = jugadores_por_hora.max()
    min_value = jugadores_por_hora.min()
    total_players_day = jugadores_por_hora.sum()

    # Calcular porcentajes para cada valor de step
    total_steps = filtered_df['step'].count()
    step_percentages = (filtered_df['step'].value_counts(normalize=True) * 100).to_dict()

    # Asegurarnos de que existan todos los valores de step
    step1 = step_percentages.get(1, 0)
    step2 = step_percentages.get(2, 0)
    step3 = step_percentages.get(3, 0)
    step4 = step_percentages.get(4, 0)

    # Crear tabla con las horas y los valores
    table_data = jugadores_por_hora.reset_index()
    table_data.columns = ['Hora', 'Número de Jugadores']

    # Convertir tabla a un formato presentable
    print("Tabla de jugadores por hora:")
    print(table_data)

    # Generar el gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 5))
    jugadores_por_hora.plot(kind='bar', ax=ax, color='blue', label='Número de jugadores por hora')
    ax.set_title('Jugadores por Hora')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Número de Jugadores')
    ax.legend()

    # Guardar el gráfico en formato Base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    # Retornar resultados
    return {
        "table": table_data,
        "bar_plot_url": plot_url,
        "mean_players": mean_players,
        "max_value": max_value,
        "min_value": min_value,
        "total_players_day": total_players_day,
        "%step1": step1,
        "%step2": step2,
        "%step3": step3,
        "%step4": step4,
    }