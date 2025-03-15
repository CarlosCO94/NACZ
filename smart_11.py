import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Jugadores - Liga Peruana",
    page_icon="⚽",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #1E88E5;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1E88E5;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        border-radius: 5px;
        background-color: #e3f2fd;
    }
    .metric-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .select-container {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .results-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Diccionario de posiciones con sus patrones
POSICIONES = {
    "Portero": "GK",
    "Defensa Central": "CB|RCB|LCB",
    "Lateral Izquierdo": "LB|LWB",
    "Lateral Derecho": "RB|RWB",
    "Mediocentro Defensivo": "DMF|CDM",
    "Mediocentro": "RCMF|LCMF|CM",
    "Extremo": "RW|RWF|LW|LWF",
    "Delantero": "CF|ST"
}

# Perfiles disponibles para cada posición
PERFILES = {
    "Portero": ["Portero Bueno con los Pies", "Portero con Muchas paradas"],
    "Defensa Central": ["Central ganador de Duelos", "Central Rapido", "Central Tecnico"],
    "Lateral Izquierdo": ["Lateral Defensivo", "Lateral Ofensivo"],
    "Lateral Derecho": ["Lateral Defensivo", "Lateral Ofensivo"],
    "Mediocentro Defensivo": ["Mediocentro Defensivo (Fisico)", "Mediocentro BoxToBox", "Mediocentro Creador"],
    "Mediocentro": ["Mediocentro BoxToBox", "Mediocentro Creador"],
    "Extremo": ["Extremo Regateador", "Extremo centrador", "Extremo Goleador"],
    "Delantero": ["Delantero Cabeceador", "Delantero Killer", "Delantero Asociativo"]
}

# Métricas y ponderaciones por perfil
METRICAS_PERFILES = {
    'Portero Bueno con los Pies': {
        'metricas': [
            'Pases recibidos /90',
            'Pases/90',
            'Precisión pases, %',
            'Pases hacia adelante/90',
            'Precisión pases hacia adelante, %',
            'Pases laterales/90',
            'Precisión pases laterales, %',
            'Pases cortos / medios /90',
            'Precisión pases cortos / medios, %',
            'Pases largos/90',
            'Precisión pases largos, %',
            'Goles recibidos/90',
            'Remates en contra/90',
            'xG en contra/90',
            'Goles evitados/90',
            'Salidas/90',
            'Duelos aéreos en los 90',
            'Paradas, %',
            'Porterías imbatidas en los 90'
        ],
        'ponderaciones': [
            0.075,  # Pases recibidos /90
            0.1,    # Pases/90
            0.1251, # Precisión pases, % (Ajustado)
            0.05,   # Pases hacia adelante/90
            0.075,  # Precisión pases hacia adelante, %
            0.05,   # Pases laterales/90
            0.075,  # Precisión pases laterales, %
            0.05,   # Pases cortos / medios /90
            0.075,  # Precisión pases cortos / medios, %
            0.05,   # Pases largos/90
            0.075,  # Precisión pases largos, %
            -0.1,   # Goles recibidos/90
            -0.075, # Remates en contra/90
            -0.05,  # xG en contra/90
            0.1,    # Goles evitados/90
            0.05,   # Salidas/90
            0.075,  # Duelos aéreos en los 90
            0.1,    # Paradas, %
            0.1     # Porterías imbatidas en los 90
        ]
    },
    'Portero con Muchas paradas': {
        'metricas': [
            'Goles recibidos/90',
            'Remates en contra/90',
            'xG en contra/90',
            'Goles evitados/90',
            'Salidas/90',
            'Duelos aéreos en los 90',
            'Paradas, %',
            'Porterías imbatidas en los 90'
        ],
        'ponderaciones': [
            -0.5,   # Goles recibidos/90
            -0.373, # Remates en contra/90
            -0.25,  # xG en contra/90
            0.5,    # Goles evitados/90
            0.25,   # Salidas/90
            0.373,  # Duelos aéreos en los 90
            0.5,    # Paradas, %
            0.5     # Porterías imbatidas en los 90
        ]
    },
    'Lateral Defensivo': {
        'metricas': [
            'Duelos ganados, %',
            'Acciones defensivas realizadas/90',
            'Duelos defensivos/90',
            'Duelos defensivos ganados, %',
            'Duelos aéreos ganados, %',
            'Interceptaciones/90',
            'Pases/90',
            'Precisión pases, %',
            'Pases hacia adelante/90',
            'Precisión pases hacia adelante, %'
        ],
        'ponderaciones': [
            0.1209,  # Duelos ganados, %
            0.0909,  # Acciones defensivas realizadas/90
            0.0909,  # Duelos defensivos/90
            0.1209,  # Duelos defensivos ganados, %
            0.0909,  # Duelos aéreos ganados, %
            0.1518,  # Interceptaciones/90
            0.0609,  # Pases/90
            0.1209,  # Precisión pases, %
            0.0609,  # Pases hacia adelante/90
            0.0909   # Precisión pases hacia adelante, %
        ]
    },
    'Lateral Ofensivo': {
        'metricas': [
            'Duelos ganados, %',
            'Acciones defensivas realizadas/90',
            'Duelos defensivos/90',
            'Duelos defensivos ganados, %',
            'Duelos aéreos ganados, %',
            'Interceptaciones/90',
            'Pases/90',
            'Precisión pases, %',
            'Pases hacia adelante/90',
            'Precisión pases hacia adelante, %',
            'Acciones de ataque exitosas/90',
            'Centros al área pequeña/90',
            'Duelos atacantes ganados, %',
            'Carreras en progresión/90',
            'Aceleraciones/90',
            'Pases recibidos /90',
            'Third assists/90',
            'Precisión pases en el último tercio, %',
            'Pases hacía el área pequeña, %',
            'Precisión pases en profundidad, %',
            'Centros desde el último tercio/90',
            'Precisión pases progresivos, %'
        ],
        'ponderaciones': [
            0.0758,  # Duelos ganados, %
            0.0568,  # Acciones defensivas realizadas/90
            0.0568,  # Duelos defensivos/90
            0.0758,  # Duelos defensivos ganados, %
            0.0568,  # Duelos aéreos ganados, %
            0.0947,  # Interceptaciones/90
            0.0379,  # Pases/90
            0.0758,  # Precisión pases, %
            0.0379,  # Pases hacia adelante/90
            0.0568,  # Precisión pases hacia adelante, %
            0.0313,  # Acciones de ataque exitosas/90 (valor inicial para métricas faltantes)
            0.0313,  # Centros al área pequeña/90
            0.0313,  # Duelos atacantes ganados, %
            0.0313,  # Carreras en progresión/90
            0.0313,  # Aceleraciones/90
            0.0313,  # Pases recibidos /90
            0.0313,  # Third assists/90
            0.0313,  # Precisión pases en el último tercio, %
            0.0313,  # Pases hacía el área pequeña, %
            0.0313,  # Precisión pases en profundidad, %
            0.0313,  # Centros desde el último tercio/90
            0.0313   # Precisión pases progresivos, % 
        ]
    },
    'Central ganador de Duelos': {
        'metricas': [
            'Duelos/90',
            'Duelos ganados, %',
            'Duelos defensivos/90',
            'Duelos defensivos ganados, %',
            'Duelos aéreos en los 90',
            'Duelos aéreos ganados, %'
        ],
        'ponderaciones': [
            0.1579,  # Duelos/90
            0.2105,  # Duelos ganados, %
            0.1053,  # Duelos defensivos/90
            0.2632,  # Duelos defensivos ganados, %
            0.1053,  # Duelos aéreos en los 90
            0.1579   # Duelos aéreos ganados, %
        ]
    },
    'Central Rapido': {
        'metricas': [
            'Aceleraciones/90',
            'Carreras en progresión/90',
            'Interceptaciones/90',
            'Duelos defensivos/90',
            'Posesión conquistada después de una interceptación',
            'Entradas/90'
        ],
        'ponderaciones': [
            0.16,  # Aceleraciones/90
            0.12,  # Carreras en progresión/90
            0.2,   # Interceptaciones/90
            0.08,  # Duelos defensivos/90
            0.16,  # Posesión conquistada después de una interceptación
            0.28   # Entradas/90
        ]
    },
    'Central Tecnico': {
        'metricas': [
            'Pases/90',
            'Precisión pases, %',
            'Pases cortos / medios /90',
            'Precisión pases cortos / medios, %',
            'Pases largos/90',
            'Precisión pases largos, %',
            'Pases hacia adelante/90',
            'Precisión pases hacia adelante, %',
            'Pases hacia atrás/90',
            'Precision pases hacia atrás, %',
            'Pases laterales/90',
            'Precisión pases laterales, %',
            'Jugadas claves/90',
            'Pases en el último tercio/90',
            'Precisión pases en el último tercio, %'
        ],
        'ponderaciones': [
            0.0755,  # Pases/90
            0.0943,  # Precisión pases, %
            0.0566,  # Pases cortos / medios /90
            0.0755,  # Precisión pases cortos / medios, %
            0.0566,  # Pases largos/90
            0.0755,  # Precisión pases largos, %
            0.0566,  # Pases hacia adelante/90
            0.0755,  # Precisión pases hacia adelante, %
            0.0377,  # Pases hacia atrás/90
            0.0566,  # Precision pases hacia atrás, %
            0.0377,  # Pases laterales/90
            0.0566,  # Precisión pases laterales, %
            0.0755,  # Jugadas claves/90
            0.0943,  # Pases en el último tercio/90
            0.0755   # Precisión pases en el último tercio, %
        ]
    },
    'Mediocentro Defensivo (Fisico)': {
        'metricas': [
            'Duelos/90',
            'Duelos ganados, %',
            'Duelos defensivos/90',
            'Duelos defensivos ganados, %',
            'Interceptaciones/90',
            'Entradas/90',
            'Faltas/90',
            'Posesión conquistada después de una entrada',
            'Posesión conquistada después de una interceptación'
        ],
        'ponderaciones': [
            0.129,  # Duelos/90
            0.1613, # Duelos ganados, %
            0.129,  # Duelos defensivos/90
            0.1613, # Duelos defensivos ganados, %
            0.129,  # Interceptaciones/90
            0.129,  # Entradas/90
            -0.0968,# Faltas/90 (Se resta debido a que es una métrica negativa para un mediocentro defensivo)
            0.129,  # Posesión conquistada después de una entrada
            0.129   # Posesión conquistada después de una interceptación
        ]
    },
    'Mediocentro BoxToBox': {
        'metricas': [
            'Duelos/90',
            'Duelos ganados, %',
            'Pases/90',
            'Precisión pases, %',
            'Interceptaciones/90',
            'Carreras en progresión/90',
            'Aceleraciones/90',
            'Remates/90',
            'Goles/90',
            'Asistencias/90',
            'Toques en el área de penalti/90',
            'xG/90',
            'Pases al área de penalti/90'
        ],
        'ponderaciones': [
            0.07,  # Duelos/90
            0.09,  # Duelos ganados, %
            0.07,  # Pases/90
            0.08,  # Precisión pases, %
            0.07,  # Interceptaciones/90
            0.09,  # Carreras en progresión/90
            0.07,  # Aceleraciones/90
            0.07,  # Remates/90
            0.06,  # Goles/90
            0.07,  # Asistencias/90
            0.07,  # Toques en el área de penalti/90
            0.06,  # xG/90
            0.06   # Pases al área de penalti/90
        ]
    },
    'Mediocentro Creador': {
        'metricas': [
            'Asistencias/90',
            'xA/90',
            'Acciones de ataque exitosas/90',
            'Goles/90',
            'Duelos/90',
            'Duelos ganados, %',
            'Entradas/90',
            'Interceptaciones/90',
            'Regates/90',
            'Precisión pases, %',
            'Precisión pases hacia adelante, %',
            'Jugadas claves/90',
            'Pases en el último tercio/90',
            'Precisión pases en el último tercio, %',
            'Centros/90',
            'Precisión centros, %',
            'Desmarques/90'
        ],
        'ponderaciones': [
            0.12,  # Asistencias/90
            0.12,  # xA/90
            0.10,  # Acciones de ataque exitosas/90
            0.07,  # Goles/90
            0.07,  # Duelos/90
            0.07,  # Duelos ganados, %
            0.01,  # Entradas/90
            0.06,  # Interceptaciones/90
            0.07,  # Regates/90
            0.05,  # Precisión en los pases/90
            0.05,  # Precisión en los pases hacia adelante/90
            0.04,  # Jugadas claves/90
            0.04,  # Pases en el último tercio/90
            0.04,  # Precisión en los pases en el último tercio/90
            0.03,  # Centros/90
            0.03,  # Precisión en los centros/90
            0.03   # Desmarques/90
        ]
    },
    'Extremo Regateador': {
        'metricas': [
            'Regates/90',
            'Regates realizados, %',
            'Duelos atacantes/90',
            'Duelos atacantes ganados, %',
            'Aceleraciones/90',
            'Remates/90',
            'Asistencias/90',
            'Jugadas claves/90',
            'Toques en el área de penalti/90',
            'Centros/90',
            'Precisión centros, %'
        ],
        'ponderaciones': [
            0.15,  # Regates/90
            0.08,  # Regates realizados, %
            0.08,  # Duelos atacantes/90
            0.10,  # Duelos atacantes ganados, %
            0.08,  # Aceleraciones/90
            0.08,  # Remates/90
            0.08,  # Asistencias/90
            0.08,  # Jugadas claves/90
            0.09,  # Toques en el área de penalti/90
            0.08,  # Centros/90
            0.10   # Precisión centros, %
        ]
    },
    'Extremo centrador': {
        'metricas': [
            'Centros/90',
            'Precisión centros, %',
            'Jugadas claves/90',
            'Asistencias/90',
            'Pases en el último tercio/90',
            'Precisión pases en el último tercio, %',
            'Toques en el área de penalti/90',
            'Pases al área de penalti/90',
            'Regates/90',
            'Aceleraciones/90',
            'xA/90'
        ],
        'ponderaciones': [
            0.15,  # Centros/90
            0.09,  # Precisión centros, %
            0.1,   # Jugadas claves/90
            0.1,   # Asistencias/90
            0.07,  # Pases en el último tercio/90
            0.09,  # Precisión pases en el último tercio, %
            0.05,  # Toques en el área de penalti/90
            0.09,  # Pases al área de penalti/90
            0.08,  # Regates/90
            0.09,  # Aceleraciones/90
            0.09   # xA/90
        ]
    },
    'Extremo Goleador': {
        'metricas': [
            'Goles/90',
            'Remates/90',
            'xG/90',
            'Goles de cabeza/90',
            'Tiros a la portería, %',
            'Asistencias/90',
            'Jugadas claves/90',
            'Toques en el área de penalti/90',
            'Goles hechos, %'
        ],
        'ponderaciones': [
            0.1,   # Goles/90
            0.13,  # Remates/90
            0.11,  # xG/90
            0.13,  # Goles de cabeza/90
            0.13,  # Tiros a la portería, %
            0.06,  # Asistencias/90
            0.1,   # Jugadas claves/90
            0.1,   # Toques en el área de penalti/90
            0.08   # Goles hechos, %
        ]
    },
    'Delantero Cabeceador': {
        'metricas': [
            'Goles de cabeza',
            'Goles de cabeza/90',
            'Duelos aéreos en los 90',
            'Duelos aéreos ganados, %',
            'Remates/90',
            'Goles/90',
            'xG/90',
            'Toques en el área de penalti/90'
        ],
        'ponderaciones': [
            0.2,   # Goles de cabeza
            0.1,   # Goles de cabeza/90
            0.14,  # Duelos aéreos en los 90
            0.15,  # Duelos aéreos ganados, %
            0.08,  # Remates/90
            0.08,  # Goles/90
            0.08,  # xG/90
            0.10   # Toques en el área de penalti/90
        ]
    },
    'Delantero Killer': {
        'metricas': [
            'Goles/90',
            'xG/90',
            'Remates/90',
            'Tiros a la portería, %',
            'Goles hechos, %',
            'Asistencias/90',
            'Jugadas claves/90',
            'Toques en el área de penalti/90',
            'Duelos ganados, %',
            'Pases al área de penalti/90',
            'Goles (excepto los penaltis)',
            'Goles, excepto los penaltis/90'
        ],
        'ponderaciones': [
            0.13,  # Goles/90
            0.1,   # xG/90
            0.1,   # Remates/90
            0.1,   # Tiros a la portería, %
            0.1,   # Goles hechos, %
            0.02,  # Asistencias/90
            0.05,  # Jugadas claves/90
            0.05,  # Toques en el área de penalti/90
            0.06,  # Duelos ganados, %
            0.06,  # Pases al área de penalti/90
            0.07,  # Goles (excepto los penaltis)
            0.07   # Goles, excepto los penaltis/90
        ]
    },
    'Delantero Asociativo': {
        'metricas': [
            'Asistencias/90',
            'Jugadas claves/90',
            'Pases/90',
            'Precisión pases, %',
            'Duelos ganados, %',
            'Toques en el área de penalti/90',
            'Remates/90',
            'xG/90',
            'Goles/90',
            'Pases en el último tercio/90',
            'Precisión pases en el último tercio, %',
            'Pases al área de penalti/90'
        ],
        'ponderaciones': [
            0.09,  # Asistencias/90
            0.1,   # Jugadas claves/90
            0.09,  # Pases/90
            0.09,  # Precisión pases, %
            0.09,  # Duelos ganados, %
            0.1,   # Toques en el área de penalti/90
            0.08,  # Remates/90
            0.08,  # xG/90
            0.08,  # Goles/90
            0.08,  # Pases en el último tercio/90
            0.04,  # Precisión pases en el último tercio, %
            0.08   # Pases al área de penalti/90
        ]
    }
}

# Descripciones de perfiles
DESCRIPCIONES = {
    'Portero Bueno con los Pies': "Arquero con capacidad para iniciar jugadas, distribuir el balón y jugar con los pies bajo presión.",
    'Portero con Muchas paradas': "Arquero especializado en paradas y con gran capacidad para evitar goles en situaciones difíciles.",
    'Lateral Defensivo': "Lateral que prioriza el trabajo defensivo, ganador de duelos e interceptaciones.",
    'Lateral Ofensivo': "Lateral con vocación ofensiva, capaz de llegar a línea de fondo y centrar con precisión.",
    'Central ganador de Duelos': "Defensa central dominante en los duelos aéreos y terrestres.",
    'Central Rapido': "Defensa central con buena velocidad, ideal para equipos con línea alta.",
    'Central Tecnico': "Defensa central con buena técnica y capacidad para iniciar el juego desde atrás.",
    'Mediocentro Defensivo (Fisico)': "Mediocentro físico especializado en recuperación y cobertura defensiva.",
    'Mediocentro BoxToBox': "Mediocentro con capacidad para participar tanto en defensa como en ataque.",
    'Mediocentro Creador': "Mediocentro técnico especializado en la creación de juego y asistencias.",
    'Extremo Regateador': "Extremo habilidoso con capacidad para superar rivales en el uno contra uno.",
    'Extremo centrador': "Extremo especializado en llegar a línea de fondo y centrar con precisión.",
    'Extremo Goleador': "Extremo con alta capacidad goleadora que tiende a finalizar jugadas.",
    'Delantero Cabeceador': "Delantero especializado en el juego aéreo y remate de cabeza.",
    'Delantero Killer': "Delantero definidor con alto porcentaje de conversión de ocasiones.",
    'Delantero Asociativo': "Delantero que participa en el juego combinativo y crea ocasiones para sus compañeros."
}

# Función para cargar datos
def cargar_datos(archivo):
    try:
        df = pd.read_excel(archivo)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Función para filtrar jugadores por posición
def filtrar_jugadores(df, patron):
    if 'Posición específica' not in df.columns:
        st.error("No se encontró la columna 'Posición específica'")
        return pd.DataFrame()
    
    # Filtrar por patrón de posición
    mask = df['Posición específica'].str.contains(patron, regex=True, na=False)
    return df[mask]

# Reemplazar la función calcular_puntaje con esta versión corregida:

def calcular_puntaje(df, perfil):
    if perfil not in METRICAS_PERFILES:
        st.error(f"Perfil {perfil} no encontrado en la configuración")
        return pd.DataFrame()
    
    metricas = METRICAS_PERFILES[perfil]['metricas']
    ponderaciones = METRICAS_PERFILES[perfil]['ponderaciones']
    
    df_puntaje = df.copy()
    df_puntaje['Puntaje'] = 0
    
    # Verificar las métricas disponibles
    metricas_disponibles = []
    ponderaciones_disponibles = []
    metricas_faltantes = []
    
    for i, metrica in enumerate(metricas):
        if metrica in df.columns:
            metricas_disponibles.append(metrica)
            ponderaciones_disponibles.append(ponderaciones[i])
        else:
            metricas_faltantes.append(metrica)
    
    # Calcular puntaje con métricas disponibles
    for i, metrica in enumerate(metricas_disponibles):
        # Convertir a numérico asegurándose de que no hay NaN
        df_puntaje[metrica] = pd.to_numeric(df_puntaje[metrica], errors='coerce').fillna(0)
        
        # Obtener el peso para esta métrica
        peso = ponderaciones_disponibles[i]
        
        # Normalizar valores (min-max scaling)
        max_val = df_puntaje[metrica].max()
        min_val = df_puntaje[metrica].min()
        
        # Solo normalizar si hay un rango válido
        if max_val > min_val:
            # Para métricas con peso positivo, mayor es mejor
            # Para métricas con peso negativo, menor es mejor
            if peso >= 0:
                df_puntaje[f'{metrica}_norm'] = (df_puntaje[metrica] - min_val) / (max_val - min_val)
            else:
                # Para métricas negativas, invertimos la normalización
                df_puntaje[f'{metrica}_norm'] = 1 - (df_puntaje[metrica] - min_val) / (max_val - min_val)
                # Convertimos el peso a positivo para la suma
                peso = abs(peso)
        else:
            df_puntaje[f'{metrica}_norm'] = 0.5  # Valor por defecto si todos son iguales
        
        # Aplicar ponderación (siempre positiva ahora)
        df_puntaje['Puntaje'] += df_puntaje[f'{metrica}_norm'] * peso
    
    # Escalar el puntaje al rango 0-10 pero sin re-normalizar basado en min/max
    # Calculamos el máximo puntaje teórico posible (si todas las métricas fueran perfectas)
    max_puntaje_teorico = sum(abs(p) for p in ponderaciones_disponibles)
    
    # Escalamos los puntajes para que estén en el rango 0-10
    if max_puntaje_teorico > 0:
        df_puntaje['Puntaje'] = (df_puntaje['Puntaje'] / max_puntaje_teorico) * 10
    
    # Preparar DataFrame de salida
    columnas_salida = ['Jugador', 'Equipo', 'Edad', 'Puntaje']
    resultado = pd.DataFrame()
    
    # Jugador
    if 'Jugador' in df_puntaje.columns:
        resultado['Jugador'] = df_puntaje['Jugador']
    else:
        resultado['Jugador'] = [f"Jugador {i+1}" for i in range(len(df_puntaje))]
    
    # Equipo
    if 'Equipo durante el período seleccionado' in df_puntaje.columns:
        resultado['Equipo'] = df_puntaje['Equipo durante el período seleccionado']
    elif 'Equipo' in df_puntaje.columns:
        resultado['Equipo'] = df_puntaje['Equipo']
    else:
        resultado['Equipo'] = "Sin equipo"
    
    # Edad
    if 'Edad' in df_puntaje.columns:
        resultado['Edad'] = df_puntaje['Edad']
    else:
        resultado['Edad'] = 0
    
    # Puntaje (redondeado a 2 decimales)
    resultado['Puntaje'] = df_puntaje['Puntaje'].round(2)
    
    # Añadir métricas originales para referencia
    for metrica in metricas_disponibles:
        resultado[metrica] = df_puntaje[metrica]
    
    return resultado, metricas_disponibles, metricas_faltantes

# Función para generar colores para equipos
def generar_colores_equipos(equipos):
    colores_base = {
        'Universitario': '#E30613',  # Rojo
        'Alianza Lima': '#0032A0',   # Azul
        'Sporting Cristal': '#00BFFF',  # Celeste
        'Cienciano': '#8B0000',   # Rojo oscuro
        'Melgar': '#FF4500',   # Rojo-naranja
        'Sport Boys': '#FF69B4'   # Rosa
    }
    
    colores_equipos = {}
    colores_disponibles = px.colors.qualitative.Plotly
    
    for i, equipo in enumerate(equipos):
        if equipo in colores_base:
            colores_equipos[equipo] = colores_base[equipo]
        else:
            colores_equipos[equipo] = colores_disponibles[i % len(colores_disponibles)]
    
    return colores_equipos

# Título principal
st.markdown('<h1 class="main-header">⚽ Análisis de Jugadores - Liga Peruana</h1>', unsafe_allow_html=True)

# Carga de archivo
archivo_subido = st.file_uploader("Cargar archivo Excel con datos de jugadores", type=["xlsx", "xls"])

# Si hay archivo cargado
if archivo_subido is not None:
    # Cargar datos
    datos = cargar_datos(archivo_subido)
    
    if datos is not None:
        st.write(f"Total de jugadores en el archivo: {len(datos)}")
        
        # Reemplaza todo el bloque de filtros con este código:

        # Filtros básicos en expander
        with st.expander("Filtros adicionales"):
            datos_filtrados = datos.copy()
            
            # Filtros en columnas
            col1, col2, col3 = st.columns(3)
            
            # Filtro de edad
            with col1:
                if "Edad" in datos.columns:
                    edad_min = int(datos["Edad"].min()) if not pd.isna(datos["Edad"].min()) else 15
                    edad_max = int(datos["Edad"].max()) if not pd.isna(datos["Edad"].max()) else 45
                    
                    edad_rango = st.slider(
                        "📅 Rango de edad:",
                        min_value=edad_min,
                        max_value=edad_max,
                        value=(edad_min, edad_max)
                    )
                    
                    datos_filtrados = datos_filtrados[(datos_filtrados["Edad"] >= edad_rango[0]) & 
                                                    (datos_filtrados["Edad"] <= edad_rango[1])]
            
            # Filtro de minutos jugados
            with col2:
                if "Minutos jugados" in datos.columns:
                    min_jugados_min = int(datos["Minutos jugados"].min()) if not pd.isna(datos["Minutos jugados"].min()) else 0
                    min_jugados_max = int(datos["Minutos jugados"].max()) if not pd.isna(datos["Minutos jugados"].max()) else 3000
                    
                    min_jugados_rango = st.slider(
                        "⏱️ Minutos jugados:",
                        min_value=min_jugados_min,
                        max_value=min_jugados_max,
                        value=(min_jugados_min, min_jugados_max)
                    )
                    
                    datos_filtrados = datos_filtrados[(datos_filtrados["Minutos jugados"] >= min_jugados_rango[0]) & 
                                                    (datos_filtrados["Minutos jugados"] <= min_jugados_rango[1])]
            
            # Filtro de nacionalidad
            with col3:
                if "Pasaporte" in datos.columns:
                    nacionalidad_busqueda = st.text_input(
                        "🌎 Buscar por nacionalidad:",
                        placeholder="Ej: Argentina, Perú, etc."
                    )
                    
                    if nacionalidad_busqueda:
                        # Convertir a minúscula para búsqueda insensible a mayúsculas
                        busqueda_lower = nacionalidad_busqueda.lower()
                        
                        # Filtrar jugadores que contengan la nacionalidad buscada
                        datos_filtrados = datos_filtrados[
                            datos_filtrados["Pasaporte"].str.lower().str.contains(busqueda_lower, na=False)
                        ]
                        
                        # Mostrar un resumen de las nacionalidades encontradas
                        if len(datos_filtrados) > 0:
                            encontradas = datos_filtrados["Pasaporte"].unique()
                            st.success(f"Encontrados jugadores con pasaportes: {', '.join(encontradas)}")
                        else:
                            st.warning(f"No se encontraron jugadores con '{nacionalidad_busqueda}' en su pasaporte.")
            
            # Mostrar todas las nacionalidades como texto normal (fuera de col3)
            if "Pasaporte" in datos.columns:
                if st.checkbox("Ver todas las nacionalidades disponibles"):
                    nacionalidades = sorted(datos["Pasaporte"].dropna().unique().tolist())
                    st.text_area("Nacionalidades disponibles:", value=", ".join(nacionalidades), height=100, disabled=True)
        
        # Actualizar datos con filtros
        datos = datos_filtrados
        st.write(f"Jugadores después de aplicar filtros: {len(datos)}")
        
        # SECCIÓN DE SELECCIÓN DE POSICIÓN Y PERFIL
        st.markdown('<h2 class="section-header">🔍 Selecciona posición y perfil</h2>', unsafe_allow_html=True)
        
        # Contenedor con estilo para los selectores
        st.markdown('<div class="select-container">', unsafe_allow_html=True)
        
        # Usar dos columnas para los selectores
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de posición con iconos
            posicion = st.selectbox(
                "Posición:",
                list(POSICIONES.keys()),
                format_func=lambda x: {
                    "Portero": "🧤 Portero",
                    "Defensa Central": "🛡️ Defensa Central",
                    "Lateral Izquierdo": "⬅️ Lateral Izquierdo",
                    "Lateral Derecho": "➡️ Lateral Derecho",
                    "Mediocentro Defensivo": "💪 Mediocentro Defensivo",
                    "Mediocentro": "🔄 Mediocentro",
                    "Extremo": "🚀 Extremo",
                    "Delantero": "⚽ Delantero"
                }.get(x, x)
            )
        
        # Selector de perfil si aplica
        if posicion in PERFILES:
            with col2:
                # Selector de perfil
                perfil = st.selectbox(
                    "Perfil específico:",
                    PERFILES[posicion],
                    format_func=lambda x: f"📊 {x}"
                )
        else:
            perfil = posicion  # Usar la posición como perfil si no hay perfiles específicos
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mostrar descripción del perfil
        if perfil in DESCRIPCIONES:
            st.info(f"ℹ️ **{perfil}**: {DESCRIPCIONES[perfil]}")
        
        # SECCIÓN DE RESULTADOS Y ANÁLISIS
        st.markdown(f'<h2 class="section-header">📊 Top 10 Jugadores: {perfil}</h2>', unsafe_allow_html=True)
        
        # Contenedor con estilo para resultados
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        
        # Filtrar jugadores por posición seleccionada
        patron = POSICIONES[posicion]
        jugadores_filtrados = filtrar_jugadores(datos, patron)
        
        if len(jugadores_filtrados) == 0:
            st.warning(f"⚠️ No se encontraron jugadores para la posición {posicion}")
        else:
            st.write(f"📋 Jugadores encontrados: {len(jugadores_filtrados)}")
            
            # Verificar si hay métricas definidas para el perfil seleccionado
            if perfil in METRICAS_PERFILES:
                # Calcular puntajes
                resultados, metricas_disponibles, metricas_faltantes = calcular_puntaje(jugadores_filtrados, perfil)
                
                if len(metricas_faltantes) > 0:
                    st.warning(f"⚠️ Algunas métricas no están disponibles: {', '.join(metricas_faltantes[:3])}{'...' if len(metricas_faltantes) > 3 else ''}")
                
                if len(metricas_disponibles) < 3:
                    st.error("❌ No hay suficientes métricas disponibles para hacer una evaluación adecuada")
                else:
                    # Mostrar métricas principales disponibles
                    st.markdown('<h3 style="color:#1E88E5;">Métricas principales utilizadas</h3>', unsafe_allow_html=True)
                    
                    # Tomar hasta 5 métricas para mostrar
                    metricas_mostrar = metricas_disponibles[:min(5, len(metricas_disponibles))]
                    
                    # Crear tarjetas para métricas principales
                    cols_metricas = st.columns(len(metricas_mostrar))
                    for i, metrica in enumerate(metricas_mostrar):
                        with cols_metricas[i]:
                            # Buscar el índice de la métrica en la lista original
                            idx = METRICAS_PERFILES[perfil]['metricas'].index(metrica)
                            peso = METRICAS_PERFILES[perfil]['ponderaciones'][idx]
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <p style="font-weight:bold; color:#1E88E5;">{metrica}</p>
                                <p style="font-size:1.2rem;">📈</p>
                                <p style="color:#4CAF50; font-size:0.9rem;">Peso: {abs(peso):.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Ordenar jugadores por puntaje y obtener top 10
                    top10 = resultados.sort_values(by='Puntaje', ascending=False).head(10)
                    
                    # Crear pestañas para diferentes visualizaciones
                    tab1, tab2, tab3 = st.tabs(["📋 Tabla de Datos", "📊 Gráficos", "🔍 Métricas Detalladas"])
                    
                    with tab1:
                        # Formatear el dataframe para mostrar
                        df_display = top10.copy()
                        
                        # Formatear el puntaje a 2 decimales
                        df_display['Puntaje'] = df_display['Puntaje'].map(lambda x: f"{x:.2f}")
                        
                        # Añadir iconos al nombre de los jugadores (Top 3)
                        if len(df_display) > 0:
                            df_display.iloc[0, df_display.columns.get_loc('Jugador')] = f"🥇 {df_display.iloc[0]['Jugador']}"
                        if len(df_display) > 1:
                            df_display.iloc[1, df_display.columns.get_loc('Jugador')] = f"🥈 {df_display.iloc[1]['Jugador']}"
                        if len(df_display) > 2:
                            df_display.iloc[2, df_display.columns.get_loc('Jugador')] = f"🥉 {df_display.iloc[2]['Jugador']}"
                        
                        # Mostrar tabla estilizada
                        st.dataframe(
                            df_display.reset_index(drop=True),
                            use_container_width=True,
                            height=400
                        )
                    
                    with tab2:
                        # Opciones de visualización
                        viz_col1, viz_col2 = st.columns([1, 3])
                        
                        with viz_col1:
                            # Selector de tipo de gráfico
                            tipo_grafico = st.radio(
                                "Tipo de gráfico:",
                                ["Barras", "Radar", "Dispersión"],
                                index=0
                            )
                            
                            # Opciones adicionales según el gráfico
                            if tipo_grafico == "Barras":
                                color_by = st.radio(
                                    "Colorear por:",
                                    ["Equipo", "Puntaje"],
                                    index=0
                                )
                            
                            elif tipo_grafico == "Radar":
                                num_jugadores = st.slider(
                                    "Jugadores a mostrar:",
                                    min_value=2,
                                    max_value=min(5, len(top10)),
                                    value=min(4, len(top10))
                                )
                            
                            elif tipo_grafico == "Dispersión":
                                # Seleccionar dos métricas para el gráfico de dispersión
                                if len(metricas_disponibles) >= 2:
                                    metrica_x = st.selectbox(
                                        "Métrica X:",
                                        metricas_disponibles,
                                        index=0
                                    )
                                    
                                    metrica_y = st.selectbox(
                                        "Métrica Y:",
                                        [m for m in metricas_disponibles if m != metrica_x],
                                        index=0
                                    )
                        
                        with viz_col2:
                            # Crear gráfico según la selección
                            if tipo_grafico == "Barras":
                                # Asignar colores por equipo o puntaje
                                if color_by == "Equipo":
                                    equipos = top10['Equipo'].unique()
                                    colores_equipos = generar_colores_equipos(equipos)
                                    
                                    fig = px.bar(
                                        top10, 
                                        x='Jugador', 
                                        y='Puntaje',
                                        color='Equipo',
                                        color_discrete_map=colores_equipos,
                                        title=f"Top 10 {perfil} por puntaje",
                                        height=500
                                    )
                                else:
                                    fig = px.bar(
                                        top10, 
                                        x='Jugador', 
                                        y='Puntaje',
                                        color='Puntaje',
                                        color_continuous_scale='Viridis',
                                        title=f"Top 10 {perfil} por puntaje",
                                        height=500
                                    )
                                
                                fig.update_layout(
                                    xaxis_tickangle=-45,
                                    xaxis_title="Jugador",
                                    yaxis_title="Puntaje",
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    margin=dict(l=0, r=0, t=50, b=0)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Añadir texto explicativo
                                st.markdown("""
                                <div style="background-color:#f9f9f9; padding:10px; border-radius:5px; font-size:0.9rem;">
                                    📊 El gráfico de barras muestra el puntaje calculado para cada jugador según las métricas
                                    del perfil seleccionado. Un puntaje más alto indica mejor rendimiento en las métricas
                                    priorizadas para este perfil.
                                </div>
                                """, unsafe_allow_html=True)
                            
                            elif tipo_grafico == "Radar":
                                # Gráfico radar para los top jugadores seleccionados
                                top_n = top10.head(num_jugadores)
                                
                                # Preparar datos para radar (máximo 8 métricas)
                                metricas_radar = metricas_disponibles[:min(8, len(metricas_disponibles))]
                                
                                # Crear figura radar
                                fig = go.Figure()
                                
                                # Normalizar valores
                                radar_data = {}
                                for metrica in metricas_radar:
                                    if metrica in top_n.columns:
                                        max_val = top_n[metrica].max()
                                        min_val = top_n[metrica].min()
                                        
                                        if max_val > min_val:
                                            radar_data[metrica] = (top_n[metrica] - min_val) / (max_val - min_val)
                                        else:
                                            radar_data[metrica] = top_n[metrica] * 0 + 0.5
                                
                                # Colores para cada jugador
                                colores_jugadores = px.colors.qualitative.Plotly[:num_jugadores]
                                
                                # Agregar cada jugador
                                for i, jugador in top_n.iterrows():
                                    valores = [radar_data[metrica][i] for metrica in metricas_radar]
                                    
                                    # Cerrar polígono
                                    valores.append(valores[0])
                                    etiquetas = metricas_radar + [metricas_radar[0]]
                                    
                                    fig.add_trace(go.Scatterpolar(
                                        r=valores,
                                        theta=etiquetas,
                                        fill='toself',
                                        name=f"{jugador['Jugador']} ({jugador['Equipo']})",
                                        line_color=colores_jugadores[i % len(colores_jugadores)]
                                    ))
                                
                                # Configurar layout
                                fig.update_layout(
                                    polar=dict(
                                        radialaxis=dict(
                                            visible=True,
                                            range=[0, 1]
                                        )
                                    ),
                                    title=f"Comparativa de métricas - Top {num_jugadores} {perfil}",
                                    height=600,
                                    margin=dict(l=80, r=80, t=100, b=80)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Añadir texto explicativo
                                st.markdown("""
                                <div style="background-color:#f9f9f9; padding:10px; border-radius:5px; font-size:0.9rem;">
                                    📊 El gráfico radar muestra el rendimiento relativo de cada jugador en las métricas principales.
                                    Cada eje representa una métrica distinta, y el área cubierta indica el rendimiento global.
                                    Los valores están normalizados para facilitar la comparación.
                                </div>
                                """, unsafe_allow_html=True)
                            
                            elif tipo_grafico == "Dispersión":
                                if len(metricas_disponibles) >= 2 and 'metrica_x' in locals() and 'metrica_y' in locals():
                                    # Gráfico de dispersión con las métricas seleccionadas
                                    fig = px.scatter(
                                        top10,
                                        x=metrica_x,
                                        y=metrica_y,
                                        color='Equipo',
                                        size='Puntaje',
                                        hover_name='Jugador',
                                        title=f"Relación entre {metrica_x} y {metrica_y}",
                                        height=500
                                    )
                                    
                                    fig.update_layout(
                                        xaxis_title=metrica_x,
                                        yaxis_title=metrica_y,
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        margin=dict(l=0, r=0, t=50, b=0)
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Calcular correlación
                                    corr = top10[metrica_x].corr(top10[metrica_y])
                                    
                                    # Añadir texto explicativo
                                    st.markdown(f"""
                                    <div style="background-color:#f9f9f9; padding:10px; border-radius:5px; font-size:0.9rem;">
                                        📊 El gráfico de dispersión muestra la relación entre {metrica_x} y {metrica_y}.
                                        Cada punto representa un jugador, el tamaño indica su puntaje general.
                                        Correlación: {corr:.2f} ({
                                        "fuerte positiva" if corr > 0.7 else
                                        "moderada positiva" if corr > 0.3 else
                                        "débil positiva" if corr > 0 else
                                        "fuerte negativa" if corr < -0.7 else
                                        "moderada negativa" if corr < -0.3 else
                                        "débil negativa"})
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.warning("No hay suficientes métricas disponibles para el gráfico de dispersión")
                    
                    with tab3:
                        # Mostrar todas las métricas utilizadas en la evaluación
                        st.markdown("### 📊 Métricas completas utilizadas en la evaluación")
                        
                        # Categorizar métricas para visualización
                        categorias = {
                            "Ofensivas": ["Goles", "xG", "Remates", "Asistencias", "Toques", "Centros", "xA", "Tiros"],
                            "Defensivas": ["Duelos defensivos", "Interceptaciones", "Acciones defensivas", "Entrada", "Duelos aéreos", "Recuperaciones"],
                            "Pases": ["Pases", "Precisión pases", "Pases progresivos", "Pases al área", "Pases en el último tercio"],
                            "Portería": ["Paradas", "Goles evitados", "Porterías imbatidas", "Goles recibidos"]
                        }
                        
                        # Clasificar las métricas por categoría
                        metricas_por_categoria = {categoria: [] for categoria in categorias}
                        otras_metricas = []
                        
                        for metrica in metricas_disponibles:
                            categorizada = False
                            for categoria, palabras_clave in categorias.items():
                                if any(palabra in metrica for palabra in palabras_clave):
                                    metricas_por_categoria[categoria].append(metrica)
                                    categorizada = True
                                    break
                            if not categorizada:
                                otras_metricas.append(metrica)
                        
                        # Determinar número de columnas basado en categorías con métricas
                        categorias_con_metricas = [cat for cat, met in metricas_por_categoria.items() if met]
                        if otras_metricas:
                            categorias_con_metricas.append("Otras")
                        
                        num_cols = min(4, len(categorias_con_metricas))
                        cols = st.columns(num_cols)
                        
                        # Distribuir categorías entre columnas
                        for i, categoria in enumerate(categorias_con_metricas):
                            col_index = i % num_cols
                            with cols[col_index]:
                                if categoria == "Otras":
                                    st.markdown(f"#### Otras Métricas")
                                    metricas_lista = otras_metricas
                                else:
                                    st.markdown(f"#### {categoria}")
                                    metricas_lista = metricas_por_categoria[categoria]
                                
                                for metrica in sorted(metricas_lista):
                                    # Obtener el índice y peso de la métrica
                                    try:
                                        idx = METRICAS_PERFILES[perfil]['metricas'].index(metrica)
                                        peso = METRICAS_PERFILES[perfil]['ponderaciones'][idx]
                                        signo = "+" if peso >= 0 else "-"
                                        st.markdown(f"**{metrica}** ({signo}{abs(peso):.2f})")
                                        st.progress(abs(peso))
                                    except:
                                        st.markdown(f"**{metrica}**")
                                        st.progress(0.5)  # Valor por defecto
            else:
                st.error(f"❌ No se encontraron métricas definidas para el perfil {perfil}")
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("👆 Sube un archivo Excel para comenzar el análisis")
    
    # Información sobre el formato esperado
    st.markdown('<h2 class="section-header">Formato esperado del archivo</h2>', unsafe_allow_html=True)
    
    # Usar columnas para mostrar la información
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        ### Columnas necesarias:
        
        - **Jugador**: Nombre del jugador
        - **Posición específica**: Códigos de posición (GK, CB, LB, etc.)
        - **Equipo** o **Equipo durante el período seleccionado**
        - **Edad**: Edad del jugador
        
        ### Columnas de métricas:
        El archivo debe incluir métricas relevantes para cada posición como:
        - Goles/90, xG/90, Asistencias/90
        - Duelos defensivos ganados, %
        - Interceptaciones/90
        - Precisión pases, %
        - Y otras métricas específicas
        """)
    
    with info_col2:
        st.markdown("""
        ### Ejemplos de posiciones:
        
        | Posición | Códigos |
        |----------|---------|
        | Portero | GK |
        | Defensa Central | CB, RCB, LCB |
        | Lateral | LB, RB, LWB, RWB |
        | Mediocentro Defensivo | DMF, CDM |
        | Mediocentro | CM, RCMF, LCMF |
        | Extremo | RW, LW, RWF, LWF |
        | Delantero | CF, ST |
        """)

# Pie de página
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Desarrollado para análisis de jugadores de la Liga Peruana ⚽</p>
</div>
""", unsafe_allow_html=True)