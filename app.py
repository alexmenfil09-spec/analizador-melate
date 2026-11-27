import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="Analizador Pro Melate", page_icon="🎱", layout="wide")
st.title("🎱 Analizador Matemático Pro: Melate, Revancha y Revanchita")

st.sidebar.header("⚙️ Filtros Matemáticos Avanzados")

ventana = st.sidebar.selectbox(
    "Rango de sorteos a estudiar:",
    ["Todo el historial", "Últimos 50 sorteos", "Últimos 100 sorteos", "Últimos 250 sorteos"]
)

usar_suma = st.sidebar.checkbox("Filtrar por Suma Total Óptima", value=True)
rango_suma = st.sidebar.slider("Rango de suma de los 6 números:", 60, 300, (125, 215))

balance_par = st.sidebar.selectbox(
    "Equilibrio Pares / Impares:",
    ["Cualquiera", "Equilibrado (3 Pares / 3 Impares)", "Flexible (2 a 4 Pares)"]
)

balance_alto_bajo = st.sidebar.selectbox(
    "Equilibrio Bajos (1-28) / Altos (29-56):",
    ["Cualquiera", "Equilibrado (3 Bajos / 3 Altos)", "Flexible (2 a 4 Bajos)"]
)

evitar_consecutivos = st.sidebar.checkbox("Evitar más de 2 números seguidos (ej. 14, 15, 16)", value=True)

juego = st.selectbox(
    "Selecciona la modalidad a analizar:",
    ["Melate (6 números + adicional)", "Revancha (6 números)", "Revanchita (6 números)"]
)

archivo = st.file_uploader(f"Sube el archivo CSV de {juego.split()[0]}", type=["csv"])

if archivo is not None:
    df_completo = pd.read_csv(archivo)
    
    if ventana == "Últimos 50 sorteos":
        df = df_completo.head(50).copy()
    elif ventana == "Últimos 100 sorteos":
        df = df_completo.head(100).copy()
    elif ventana == "Últimos 250 sorteos":
        df = df_completo.head(250).copy()
    else:
        df = df_completo.copy()

    df = df.reset_index(drop=True)
    cols_numeros = [c for c in df.columns if c.upper().startswith(('R', 'F', 'N')) and c[1:].isdigit()][:6]
    col_adicional = [c for c in df.columns if c.upper() in ('R7', 'F7', 'ADICIONAL')]

    if cols_numeros:
        todos = df[cols_numeros].values.flatten()
        frecuencias = pd.Series(todos).value_counts().reindex(range(1, 57), fill_value=0).sort_values(ascending=False)
        
        rezagos = {}
        for num in range(1, 57):
            apariciones = df[cols_numeros].isin([num]).any(axis=1)
            if apariciones.any():
                rezagos[num] = int(apariciones.idxmax())
            else:
                rezagos[num] = len(df)
        serie_rezagos = pd.Series(rezagos).sort_values(ascending=False)

        df['Suma_Historica'] = df[cols_numeros].sum(axis=1)
        suma_promedio = int(df['Suma_Historica'].mean())

        m1, m2, m3 = st.columns(3)
        m1.metric("Sorteos analizados", len(df))
        m2.metric("Suma promedio histórica", f"{suma_promedio} pts")
        m3.metric("Número más rezagado", f"#{serie_rezagos.index[0]} ({serie_rezagos.iloc[0]} sorteos sin salir)")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("🔥 **Top 12 Más Frecuentes**")
            st.dataframe(frecuencias.head(12).rename("Veces"), use_container_width=True)
        with c2:
            st.write("❄️ **Top 12 Menos Frecuentes**")
            st.dataframe(frecuencias.tail(12).rename("Veces"), use_container_width=True)
        with c3:
            st.write("⏳ **Top 12 Más Rezagados (Atraso)**")
            st.dataframe(serie_rezagos.head(12).rename("Sorteos sin salir"), use_container_width=True)

        st.divider()
        st.subheader("🎯 Generador con Filtros Matemáticos")
        
        estrategia = st.radio(
            "Base de selección de números:",
            [
                "Mixto Inteligente (2 Calientes + 2 Rezagados + 2 Aleatorios)",
                "Tendencia Caliente (Top 20 más frecuentes)",
                "Teoría del Rezago (Top 20 con más sorteos sin salir)",
                "Universo Completo (1 al 56 filtrado matemáticamente)"
            ]
        )

        cantidad_jugadas = st.number_input("¿Cuántas combinaciones quieres generar?", min_value=1, max_value=10, value=3)

        def cumple_filtros(comb):
            if usar_suma and not (rango_suma[0] <= sum(comb) <= rango_suma[1]):
                return False
            pares = sum(1 for x in comb if x % 2 == 0)
            if balance_par == "Equilibrado (3 Pares / 3 Impares)" and pares != 3:
                return False
            if balance_par == "Flexible (2 a 4 Pares)" and not (2 <= pares <= 4):
                return False
            bajos = sum(1 for x in comb if x <= 28)
            if balance_alto_bajo == "Equilibrado (3 Bajos / 3 Altos)" and bajos != 3:
                return False
            if balance_alto_bajo == "Flexible (2 a 4 Bajos)" and not (2 <= bajos <= 4):
                return False
            if evitar_consecutivos:
                seguidos = 1
                for i in range(1, len(comb)):
                    if comb[i] == comb[i-1] + 1:
                        seguidos += 1
                        if seguidos > 2:
                            return False
                    else:
                        seguidos = 1
            return True

        if st.button("🚀 Calcular Combinaciones Filtradas"):
            calientes = frecuencias.head(20).index.tolist()
            rezagados = serie_rezagos.head(20).index.tolist()
            
            resultados_validos = []
            intentos = 0
            
            while len(resultados_validos) < cantidad_jugadas and intentos < 15000:
                intentos += 1
                if "Mixto" in estrategia:
                    pool = set(random.sample(calientes, 2) + random.sample(rezagados, 2))
                    while len(pool) < 6:
                        pool.add(random.randint(1, 56))
                    candidata = sorted(list(pool))
                elif "Caliente" in estrategia:
                    candidata = sorted(random.sample(calientes, 6))
                elif "Rezago" in estrategia:
                    candidata = sorted(random.sample(rezagados, 6))
                else:
                    candidata = sorted(random.sample(range(1, 57), 6))
                
                if cumple_filtros(candidata) and candidata not in resultados_validos:
                    resultados_validos.append(candidata)

            if resultados_validos:
                for idx, jug in enumerate(resultados_validos, 1):
                    pares = sum(1 for x in jug if x % 2 == 0)
                    bajos = sum(1 for x in jug if x <= 28)
                    texto_extra = ""
                    if "Melate" in juego and col_adicional:
                        frec_ad = df[col_adicional[0]].value_counts()
                        adicional_sugerido = random.choice(frec_ad.head(10).index.tolist())
                        texto_extra = f" | Adicional sugerido: **{adicional_sugerido}**"
                    
                    st.success(f"**Jugada {idx}:** `{jug}` — Suma: **{sum(jug)}** | Pares/Impares: **{pares}/{6-pares}** | Bajos/Altos: **{bajos}/{6-bajos}**{texto_extra}")
            else:
                st.warning("⚠️ Los filtros seleccionados son muy estrictos para esa base. Intenta ampliar el rango de suma o cambiar el equilibrio a 'Flexible'.")
    else:
        st.error("No se detectaron columnas de números válidas en el CSV.")
else:
    st.info("👈 Ajusta tus filtros matemáticos en el panel izquierdo y sube tu archivo CSV arriba.")