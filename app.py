from datetime import datetime
import re
from typing import Optional
import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd


#README
"""
# Sistema de Análisis
Aplicación interactiva desarrollada en Python con Gradio y Pandas para realizar el diagnóstico, limpieza, análisis estadístico y visualización gráfica.

## Estructura del Proyecto
El sistema está diseñado de forma modular:

1. **Diagnóstico de Calidad de Datos:**
   * Detección de tipos de datos, conteo de celdas vacías y localización de registros o identificadores duplicados.
   * Identificación de inconsistencias lógicas como cantidades o precios negativos y textos no estandarizados.

2. **Limpieza y Transformación:**
   * Eliminación de duplicados exactos y resolución de valores duplicados en identificadores de venta.
   * Conversión de fechas al estándar internacional ISO 8601 (`AAAA-MM-DD`).
   * Corrección de valores negativos y ceros mediante valor absoluto.
   * Normalización de textos, unificación estricta de cliente frecuente (`Sí` / `No`) e imputación de valores nulos con la mediana para números y `Desconocido` para textos.

3. **Análisis Comercial y Visualización:**
   * Estadísticas descriptivas de precios, cantidades e ingresos con detección de valores más frecuentes por columna.
   * Consultas y filtrado dinámico en tiempo real sobre cualquier columna del conjunto de datos.
   * Agrupaciones por categoría, producto, vendedor, región, método de pago y cliente frecuente.
   * Representación gráfica de ingresos, productos líderes, series temporales mensuales, métodos de pago, desempeño por región y ventas por vendedor.
   * Detección de transacciones atípicas (outliers) mediante el modelo de Rango Intercuartílico (IQR).

4. **Ingreso y Persistencia de Nuevos Registros:**
   * Formulario interactivo con validación de fechas, provincias, métodos de pago, precios y cantidades.
   * Asignación automática de identificadores consecutivos.
   * Visualización de registros nuevos y exportación a un archivo.

## Requisitos e Instalación
Para ejecutar la aplicación se requiere Python 3.10 o superior y las siguientes librerías:

pip install pandas gradio matplotlib

## Ejecución del Proyecto
Para iniciar la aplicación en el navegador, hay que ejecutar el comando en la terminal dentro de la carpeta del proyecto:

python Proyecto.py

Una vez iniciada, hay que abrir el enlace local que aparece en la terminal (usualmente `http://127.0.0.1:7860`) en cualquier navegador web.
"""

# SECCION DE CONSTANTES Y CONFIGURACION GENERAL DEL SISTEMA

# OPCION PARA SALIR DEL MENU PRINCIPAL
OPCION_SALIR = "14. Salir"

# OPCIONES DEL MENU PRINCIPAL
OPCIONES_MENU = [
    "1. Mostrar información del conjunto de datos",
    "2. Mostrar primeras y últimas filas",
    "3. Analizar tipos de datos",
    "4. Analizar datos nulos",
    "5. Analizar datos duplicados",
    "6. Analizar datos inconsistentes",
    "7. Limpiar datos",
    "8. Obtener estadísticas descriptivas",
    "9. Filtrar o consultar datos",
    "10. Realizar agrupaciones y operaciones",
    "11. Generar representaciones gráficas",
    "12. Realizar análisis adicional",
    "13. Ingresar nuevos datos",
    OPCION_SALIR,
]

# OPCIONES DEL MENU PRINCIPAL QUE REQUIEREN LIMPIEZA DE DATOS
OPCIONES_REQUIEREN_LIMPIEZA = [
    "8. Obtener estadísticas descriptivas",
    "10. Realizar agrupaciones y operaciones",
    "11. Generar representaciones gráficas",
    "12. Realizar análisis adicional",
    "13. Ingresar nuevos datos",
]

# OPCIONES DE GRAFICOS
OPCIONES_GRAFICOS = [
    "Ingresos por Categoría",
    "Top 10 Productos con Mayor Recaudación",
    "Tendencia Histórica de Ventas",
    "Distribución por Método de Pago",
    "Facturación por Región",
    "Desempeño Comercial por Vendedor",
]

# OPCIONES DEL SUBMENU DE INGRESO DE NUEVOS DATOS
OPCIONES_SUBMENU_INGRESO = [
    "Ingresar un nuevo registro",
    "Mostrar registros ingresados",
    "Guardar los nuevos datos",
    "Regresar al menú principal",
]

# VALORES PREDETERMINADOS PARA LAS REGIONES
OPCIONES_REGIONES_DEFAULT = [
    "San José",
    "Alajuela",
    "Cartago",
    "Heredia",
    "Guanacaste",
    "Puntarenas",
    "Limón",
]

# VALORES PREDETERMINADOS PARA LOS METODOS DE PAGO
OPCIONES_METODOS_PAGO_DEFAULT = [
    "Sinpe Móvil",
    "Tarjeta",
    "Transferencia",
    "Efectivo",
]

# VALORES PREDETERMINADOS PARA LAS CATEGORIAS
OPCIONES_CATEGORIAS_DEFAULT = [
    "Celulares",
    "Laptops",
    "Accesorios",
    "Audio",
    "Monitores",
]

# SEÑAL PARA INDICAR QUE LOS DATOS ESTAN SUCIOS
SEÑAL_DATOS_SUCIOS = (
    "<div style='text-align: center; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; "
    "background-color: #fef3c7; color: #92400e; margin-bottom: 12px; border: 1px solid #fde68a;'>"
    "Estado: Datos Sin procesar"
    "</div>"
)

# SEÑAL PARA INDICAR QUE LOS DATOS ESTAN LIMPIOS
SEÑAL_DATOS_LIMPIOS = (
    "<div style='text-align: center; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; "
    "background-color: #dcfce7; color: #166534; margin-bottom: 12px; border: 1px solid #bbf7d0;'>"
    "Estado: Datos Limpios"
    "</div>"
)

# ESTABLECE EL FONDO Y TIPOGRAFIAS DE LA APLICACION
TEMA_APLICACION = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "-apple-system", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
)

# ESTILOS PARA LA APLICACION
CSS_APLICACION = """
#cargador_archivo {
    min-height: 520px !important;
}
#cargador_archivo [data-testid="dropzone"], #cargador_archivo .upload-container, #cargador_archivo > div {
    min-height: 470px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
}
"""


# SECCION DE FUNCIONES PARA EL ANALISIS, LIMPIEZA DE DATOS Y GENERACION DE GRAFICOS

# Aplica formato visual a las columnas de dinero y cantidades para mostrarlas ordenadas
def formatear_tabla(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    temp = df.copy()
    for col in temp.columns:
        if col in ["precio_unitario", "total_venta", "Monto por encima del límite"]:
            temp[col] = pd.to_numeric(temp[col], errors="coerce").map(
                lambda x: f"{x:,.2f}" if pd.notna(x) else ""
            )
        elif col == "cantidad":
            temp[col] = pd.to_numeric(temp[col], errors="coerce").map(
                lambda x: f"{int(x):,}" if pd.notna(x) else ""
            )
    return temp


# Retorna una tabla cuando un analisis no encuentra problemas
def crear_tabla_vacia(n_cols: int, mensaje: str) -> pd.DataFrame:
    return pd.DataFrame({"Estado": [mensaje],"Columnas Evaluadas": [n_cols],})


# Registra una fila en el resumen de operaciones de limpieza realizadas
def agregar_operacion(lista: list, etapa: str, col: str, n: int, detalle: str):
    lista.append({"Etapa / Transformación": etapa, "Columna Afectada": col, "Registros Tratados": n, "Estrategia Aplicada": detalle})


# Registra una fila con el detalle de una inconsistencia encontrada
def agregar_inconsistencia(lista: list, col: str, tipo: str, n: int):
    lista.append({"Columna": col, "Tipo de Inconsistencia": tipo, "Registros Afectados": n})


# Revisa los tipos de datos de cada columna
def analizar_tipos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    n_cols = len(df.columns)
    detalle = []
    conteo_tipos = {}

    for col in df.columns:
        dtype_str = str(df[col].dtype)
        if pd.api.types.is_integer_dtype(df[col]):
            tipo_semantico = "Entero"
        elif pd.api.types.is_float_dtype(df[col]):
            tipo_semantico = "Decimal"
        elif pd.api.types.is_datetime64_any_dtype(df[col]) or "fecha" in col.lower():
            tipo_semantico = "Fecha"
        elif pd.api.types.is_bool_dtype(df[col]):
            tipo_semantico = "Booleano"
        else:
            tipo_semantico = "Texto"

        conteo_tipos[tipo_semantico] = conteo_tipos.get(tipo_semantico, 0) + 1
        ejemplo = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "N/A"
        detalle.append({"Columna": col, "Tipo Técnico": dtype_str, "Tipo Semántico": tipo_semantico, "Ejemplo": ejemplo})

    resumen = pd.DataFrame([{"Tipo de Dato": tipo, "Cantidad de Columnas": cantidad} for tipo, cantidad in conteo_tipos.items()])
    df_detalle = pd.DataFrame(detalle)

    partes = [f"{cantidad} {'columna' if cantidad == 1 else 'columnas'} de tipo {tipo}" for tipo, cantidad in conteo_tipos.items()]
    conclusion = (
        f"Como resultado del análisis se evaluaron {n_cols} columnas en el conjunto de datos, "
        f"identificando {', '.join(partes)}. ")

    return resumen, df_detalle, conclusion


# Busca celdas vacias en el dataset y muestra las columnas y filas afectadas 
def analizar_nulos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    n_filas = len(df)
    nulos_col = df.isna().sum()
    total_nulos = int(nulos_col.sum())
    cols_con_nulos = nulos_col[nulos_col > 0]

    if total_nulos == 0:
        return (
            crear_tabla_vacia(len(df.columns), "Sin valores nulos"),
            pd.DataFrame(columns=df.columns),
            "No se encontraron valores nulos en el conjunto de datos. Todas las columnas tienen sus registros completos.",)

    tabla_nulos = pd.DataFrame([{"Columna": col, "Valores Nulos": cant} for col, cant in cols_con_nulos.items()])
    filas_nulas = df[df.isna().any(axis=1)]
    total_afectadas = len(filas_nulas)

    detalles = [f"la columna '{col}' tiene {cant} {'valor nulo' if cant == 1 else 'valores nulos'}" for col, cant in cols_con_nulos.items()]
    txt_nulos = "valor nulo" if total_nulos == 1 else "valores nulos"
    txt_filas = "fila" if total_afectadas == 1 else "filas"

    conclusion = (
        f"Como resultado del análisis se encontraron un total de {total_nulos} {txt_nulos} "
        f"los cuales afectaron a {total_afectadas} {txt_filas} de un total de {n_filas:,} registros, en donde {', '.join(detalles)}.")

    return tabla_nulos, filas_nulas, conclusion


# Detecta filas repetidas exactas y ventas con el mismo id_venta
def analizar_duplicados(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    n_filas = len(df)
    col_id = "id_venta" if "id_venta" in df.columns else (
        next((c for c in df.columns if "id" in c.lower()), df.columns[0]) if len(df.columns) > 0 else None)

    exactos = int(df.duplicated().sum())
    filas_exactas = int(df.duplicated(keep=False).sum())
    datos_stats = [{
        "Criterio de Duplicado": "Duplicados Exactos (Fila completa)",
        "Registros Redundantes": exactos,
        "Filas Involucradas": filas_exactas}]

    dups_id = 0
    filas_id = 0
    unicos_id = 0
    if col_id:
        dups_id = int(df.duplicated(subset=[col_id]).sum())
        filas_id = int(df.duplicated(subset=[col_id], keep=False).sum())
        unicos_id = df[df.duplicated(subset=[col_id], keep=False)][col_id].nunique()
        datos_stats.append({
            "Criterio de Duplicado": f"Duplicados por Identificador ({col_id})",
            "Registros Redundantes": dups_id,
            "Filas Involucradas": filas_id,})

    tabla_stats = pd.DataFrame(datos_stats)

    if col_id and dups_id > 0:
        tabla_filas = df[df.duplicated(subset=[col_id], keep=False)].sort_values(by=col_id)
    elif exactos > 0:
        tabla_filas = df[df.duplicated(keep=False)].sort_values(by=list(df.columns))
    else:
        tabla_filas = pd.DataFrame(columns=df.columns)

    if exactos == 0 and (not col_id or dups_id == 0):
        return (
            crear_tabla_vacia(len(df.columns), "Sin duplicados detectados"),
            tabla_filas,
            "No se encontraron registros duplicados ni colisiones de identificador en el conjunto de datos. Todos los registros son únicos.")

    detalles = []
    if exactos > 0:
        detalles.append(f"{exactos} registros duplicados exactos abarcando {filas_exactas} filas")
    if col_id and dups_id > 0:
        detalles.append(f"{dups_id} duplicados por identificador '{col_id}' afectando a {unicos_id} IDs en {filas_id} filas")

    total_afectadas = len(tabla_filas)
    unidad_filas = "fila" if total_afectadas == 1 else "filas"
    conclusion = f"Como resultado del análisis se detectaron {' y '.join(detalles)} afectando a {total_afectadas} {unidad_filas} de un total de {n_filas:,} registros."

    return tabla_stats, tabla_filas, conclusion


# Revisa fechas, numeros negativos y textos 
def analizar_inconsistencias(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    n_filas = len(df)
    datos_stats = []
    mask_filas = pd.Series(False, index=df.index)
    motivos = pd.Series("", index=df.index)

    # Fechas con barras
    if "fecha" in df.columns:
        mask_fechas = df["fecha"].dropna().astype(str).str.contains(r"/", regex=True)
        if mask_fechas.sum() > 0:
            cant = int(mask_fechas.sum())
            agregar_inconsistencia(datos_stats, "fecha", "Fecha con formato de barras", cant)
            mask_filas |= mask_fechas
            motivos = motivos.where(~mask_fechas, motivos + " [Fecha con formato de barras]")

    # Cantidades negativas o cero
    if "cantidad" in df.columns and pd.api.types.is_numeric_dtype(df["cantidad"]):
        mask_cant = (df["cantidad"] <= 0) & df["cantidad"].notna()
        if mask_cant.sum() > 0:
            cant = int(mask_cant.sum())
            agregar_inconsistencia(datos_stats, "cantidad", "Cantidad negativa o cero", cant)
            mask_filas |= mask_cant
            motivos = motivos.where(~mask_cant, motivos + " [Cantidad negativa o cero]")

    # Precios negativos o cero
    if "precio_unitario" in df.columns and pd.api.types.is_numeric_dtype(df["precio_unitario"]):
        mask_precio = (df["precio_unitario"] <= 0) & df["precio_unitario"].notna()
        if mask_precio.sum() > 0:
            cant = int(mask_precio.sum())
            agregar_inconsistencia(datos_stats, "precio_unitario", "Precio negativo o cero", cant)
            mask_filas |= mask_precio
            motivos = motivos.where(~mask_precio, motivos + " [Precio negativo o cero]")

    # Textos con espacios en blanco o problemas de mayúsculas
    cols_texto = [c for c in ["vendedor", "categoria", "cliente_frecuente", "region", "metodo_pago", "producto"] if c in df.columns]
    for col in cols_texto:
        serie = df[col].dropna().astype(str)
        mask_espacios = serie.str.strip() != serie
        unicos_orig = serie.nunique()
        unicos_est = serie.str.strip().str.title().nunique()

        if col == "cliente_frecuente":
            mask_cf = ~serie.isin(["Sí", "No"])
            cant = int(mask_cf.sum())
            if cant > 0:
                agregar_inconsistencia(datos_stats, col, "Texto no estandarizado", cant)
                mask_filas |= mask_cf
                motivos = motivos.where(~mask_cf, motivos + f" [Texto no estandarizado en '{col}']")
        else:
            if unicos_orig > unicos_est or mask_espacios.sum() > 0:
                serie_est = serie.str.strip().str.title()
                mask_texto = (serie != serie_est) | mask_espacios
                cant = int(mask_texto.sum())
                if cant > 0:
                    agregar_inconsistencia(datos_stats, col, "Texto no estandarizado", cant)
                    mask_filas |= mask_texto
                    motivos = motivos.where(~mask_texto, motivos + f" [Texto no estandarizado en '{col}']")

    if not datos_stats:
        return (
            crear_tabla_vacia(len(df.columns), "Sin inconsistencias detectadas"),
            pd.DataFrame(columns=df.columns),
            "No se detectaron inconsistencias lógicas, de formato o tipográficas en el conjunto de datos.")

    tabla_stats = pd.DataFrame(datos_stats)
    tabla_filas = df[mask_filas].copy()
    tabla_filas.insert(0, "Motivo_Inconsistencia", motivos[mask_filas].str.strip())

    total_afectadas = len(tabla_filas)
    unidad_filas = "fila" if total_afectadas == 1 else "filas"
    resumen = [f"{fila['Registros Afectados']} en la columna '{fila['Columna']}' ({fila['Tipo de Inconsistencia']})" for _, fila in tabla_stats.iterrows()]
    conclusion = f"Como resultado del análisis se identificaron {len(tabla_stats)} tipos de inconsistencias que afectan a un total de {total_afectadas:,} {unidad_filas} de un total de {n_filas:,} registros, en donde: {', '.join(resumen)}."

    return tabla_stats, tabla_filas, conclusion


# Se aplica la limpieza de datos, donde se quitan los registros duplicados, se estandariza fechas, se corrigen numeros y se corrigen textos
def limpiar_datos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str, pd.DataFrame]:
    total_inicial = len(df)
    df_limpio = df.copy()
    operaciones = []

    # Eliminación de duplicados exactos
    n_duplicados = int(df_limpio.duplicated().sum())
    if n_duplicados > 0:
        df_limpio = df_limpio.drop_duplicates().copy()
        agregar_operacion(operaciones, "Eliminación de Duplicados Exactos", "Todas las columnas", n_duplicados, "Eliminación de filas 100% idénticas")

    # ID's duplicados
    col_id = "id_venta" if "id_venta" in df_limpio.columns else next((c for c in df_limpio.columns if "id" in c.lower()), None)
    if col_id:
        dups_id = int(df_limpio.duplicated(subset=[col_id]).sum())
        if dups_id > 0:
            df_limpio = df_limpio.drop_duplicates(subset=[col_id], keep="first").copy()
            agregar_operacion(operaciones, "Eliminacion por ID duplicado", col_id, dups_id, "Se mantiene el registro valido, se elimina el resto")

    # Estandarización de formato de fecha a AAAA-MM-DD
    if "fecha" in df_limpio.columns:
        mask_fechas = df_limpio["fecha"].dropna().astype(str).str.contains(r"/")
        if mask_fechas.sum() > 0:
            cant = int(mask_fechas.sum())
            df_limpio["fecha"] = pd.to_datetime(df_limpio["fecha"], format="mixed", dayfirst=True).dt.strftime("%Y-%m-%d")
            agregar_operacion(operaciones, "Estandarización de Fechas", "fecha", cant, "Conversión al formato estándar ISO 8601 (AAAA-MM-DD)")

    # Corrección de cantidades negativas o en cero
    if "cantidad" in df_limpio.columns and pd.api.types.is_numeric_dtype(df_limpio["cantidad"]):
        mask_cant = (df_limpio["cantidad"] <= 0) & df_limpio["cantidad"].notna()
        if mask_cant.sum() > 0:
            cant = int(mask_cant.sum())
            df_limpio["cantidad"] = df_limpio["cantidad"].abs().replace(0, 1)
            agregar_operacion(operaciones, "Corrección de números negativos y en cero", "cantidad", cant, "Se reemplazan los números negativos y en cero por su valor absoluto")

    # Corrección de precios negativos o en cero
    if "precio_unitario" in df_limpio.columns and pd.api.types.is_numeric_dtype(df_limpio["precio_unitario"]):
        mask_precio = (df_limpio["precio_unitario"] <= 0) & df_limpio["precio_unitario"].notna()
        if mask_precio.sum() > 0:
            cant = int(mask_precio.sum())
            df_limpio["precio_unitario"] = df_limpio["precio_unitario"].abs().replace(0, 1.0)
            agregar_operacion(operaciones, "Corrección de números negativos y en cero", "precio_unitario", cant, "Se reemplazan los números negativos y en cero por su valor absoluto")

    # Normalización de texto y eliminación de espacios
    cols_texto = ["vendedor", "categoria", "region", "metodo_pago", "producto"]
    for col in cols_texto:
        if col in df_limpio.columns:
            serie = df_limpio[col].dropna().astype(str)
            serie_est = serie.str.strip().str.title()
            modificados = int((serie != serie_est).sum())
            if modificados > 0:
                df_limpio[col] = serie_est
                agregar_operacion(operaciones, f"Normalización de Texto ({col})", col, modificados, "Se eliminaron espacios en blanco y se estandarizó a formato título")

    # Estandarización de cliente frecuente a estrictamente 'Sí' y 'No'
    if "cliente_frecuente" in df_limpio.columns:
        serie_cf = df_limpio["cliente_frecuente"].dropna().astype(str).str.strip().str.lower()
        cf_est = serie_cf.apply(lambda s: "Sí" if s.startswith("s") or s in ["true", "1"] else "No")
        modificados = int((df_limpio["cliente_frecuente"] != cf_est).sum())
        if modificados > 0:
            df_limpio["cliente_frecuente"] = cf_est
            agregar_operacion(operaciones, "Estandarización de Cliente Frecuente", "cliente_frecuente", modificados, "Se unificaron las respuestas estrictamente a 'Sí' y 'No'")

    # Valores nulos
    nulos_restantes = df_limpio.isna().sum()
    for col, cant in nulos_restantes[nulos_restantes > 0].items():
        if pd.api.types.is_numeric_dtype(df_limpio[col]):
            mediana = df_limpio[col].median()
            df_limpio[col] = df_limpio[col].fillna(mediana)
            agregar_operacion(operaciones, "Corrección de valores nulos", col, int(cant), f"Se reemplazaron los valores nulos con la mediana ({mediana:,.2f})")
        else:
            valor_imputacion = "Desconocido"
            df_limpio[col] = df_limpio[col].fillna(valor_imputacion)
            agregar_operacion(operaciones, "Corrección de valores nulos", col, int(cant), f"Se reemplazaron los valores nulos con '{valor_imputacion}'")

    if not operaciones:
        agregar_operacion(operaciones, "Inspección de Datos", "Todas", 0, "No se requirieron transformaciones adicionales")

    tabla_limpieza = pd.DataFrame(operaciones)
    total_final = len(df_limpio)
    filas_eliminadas = total_inicial - total_final

    conclusion = (
        f"Se limpiaron los datos correctamente, dejando un total de {total_final:,} registros listos para trabajar y eliminando {filas_eliminadas} filas repetidas. "
        "A continuación se detalla el método específico utilizado para cada caso:\n\n"
        "Duplicados: Se utilizó el método drop_duplicates() por fila completa y por la columna id_venta manteniendo el primer registro para eliminar transacciones repetidas y no inflar las ventas.\n\n"
        "Fechas: Se utilizó pd.to_datetime() y dt.strftime('%Y-%m-%d') para transformar las fechas con barras al formato estándar internacional ISO 8601 (AAAA-MM-DD), permitiendo ordenarlas y agruparlas por fecha sin fallos.\n\n"
        "Cantidades y precios negativos o en cero: Se aplicó la función de valor absoluto .abs() y .replace(0, 1) para corregir errores de signo, ya que las venta requiere cantidades y precios positivos.\n\n"
        "Textos desordenados: Se utilizaron los métodos de texto .str.strip() y .str.title() para quitar espacios sobrantes y unificar mayúsculas en productos, categorías y vendedores, y se unificó cliente frecuente estrictamente a 'Sí' y 'No'.\n\n"
        "Valores vacíos (nulos): Se utilizó el método .fillna() con la mediana para los números esto porque es más robusta y no se afecta por datos extremos, y se asignó 'Desconocido' en textos y regiones para evitar tener que eliminar filas útiles.\n\n"
    )

    return tabla_limpieza, df_limpio, conclusion, df_limpio


# Calcula promedios, medianas, totales y frecuencias de las ventas
def analizar_estadisticas(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    n_filas = len(df)
    temp = df.copy()
    if "cantidad" in temp.columns and "precio_unitario" in temp.columns:
        temp["total_venta"] = temp["cantidad"] * temp["precio_unitario"]

    filas_num = []
    config_num = [
        ("cantidad", "Cantidad de Artículos", "{:.2f}", "{:.0f}", "{:.2f}", "{:.0f}", "{:.0f}", lambda s: f"{int(s.sum()):,}"),
        ("precio_unitario", "Precio Unitario", "{:,.2f}", "{:,.2f}", "{:,.2f}", "{:,.2f}", "{:,.2f}", lambda _: "-"),
        ("total_venta", "Total por Venta (Ingresos)", "{:,.2f}", "{:,.2f}", "{:,.2f}", "{:,.2f}", "{:,.2f}", lambda s: f"{s.sum():,.2f}")]
    for col, label, f_avg, f_med, f_std, f_min, f_max, f_tot in config_num:
        if col in temp.columns:
            s = temp[col].dropna()
            filas_num.append({
                "Variable": label,
                "Promedio": f_avg.format(s.mean()),
                "Mediana": f_med.format(s.median()),
                "Desv. Estándar": f_std.format(s.std()),
                "Mínimo": f_min.format(s.min()),
                "Máximo": f_max.format(s.max()),
                "Total Acumulado": f_tot(s)})
    tabla_num = pd.DataFrame(filas_num)

    config_cat = [
        ("producto", "Producto"),
        ("categoria", "Categoría"),
        ("vendedor", "Vendedor"),
        ("region", "Región"),
        ("metodo_pago", "Método de Pago"),
        ("cliente_frecuente", "Cliente Frecuente")]
    filas_cat = []
    modas = {}
    for col_key, col_label in config_cat:
        if col_key in temp.columns:
            s = temp[col_key].dropna().astype(str)
            unicos = s.nunique()
            vc = s.value_counts()
            if len(vc) > 0:
                top1 = vc.index[0]
                freq1 = int(vc.iloc[0])
                pct1 = f"{(freq1 / n_filas) * 100:.1f}%"
                modas[col_key] = (top1, pct1)
                top2 = f"{vc.index[1]} ({int(vc.iloc[1]):,})" if len(vc) > 1 else "-"
            else:
                top1, freq1, pct1, top2 = "N/A", 0, "0.0%", "-"

            filas_cat.append({
                "Dimensión Comercial": col_label,
                "Cantidad": unicos,
                "Moda": top1,
                "Frecuencia Líder": f"{freq1:,}",
                "Participación Líder": pct1,
                "Segundo Lugar": top2})
    tabla_cat = pd.DataFrame(filas_cat)

    val_total = temp["total_venta"].sum() if "total_venta" in temp.columns else 0
    val_media = temp["total_venta"].mean() if "total_venta" in temp.columns else 0
    val_cant = temp["cantidad"].sum() if "cantidad" in temp.columns else 0

    prod_estrella = modas.get("producto", ("N/A", ""))[0]
    cat_lider = modas.get("categoria", ("N/A", ""))[0]
    region_lider = modas.get("region", ("N/A", ""))[0]
    pago_lider = modas.get("metodo_pago", ("N/A", ""))[0]

    conclusion = (
        f"El análisis descriptivo revela un ingreso acumulado total de {val_total:,.2f} con un ticket promedio de {val_media:,.2f} por transacción, "
        f"acumulando un total de {int(val_cant):,} unidades vendidas en {n_filas:,} transacciones. "
        f"La categoría dominante es {cat_lider}, el producto con mayor frecuencia es {prod_estrella}, "
        f"la zona geográfica con mayor actividad comercial es {region_lider} y el método de pago predilecto por los clientes es {pago_lider}.")

    return tabla_num, tabla_cat, conclusion


# Encuentra compras inusualmente altas usando el modelo de rango intercuartilico IQR para el analisis adicional
def analizar_outliers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    temp = df.copy()
    if "cantidad" in temp.columns and "precio_unitario" in temp.columns:
        temp["total_venta"] = temp["cantidad"] * temp["precio_unitario"]
    elif "total_venta" not in temp.columns:
        temp["total_venta"] = 0

    n_filas = len(temp)
    s = temp["total_venta"].dropna()

    q1 = s.quantile(0.25)
    q2 = s.quantile(0.50)
    q3 = s.quantile(0.75)
    iqr = q3 - q1

    limite_inferior = max(0.0, q1 - 1.5 * iqr)
    limite_superior = q3 + 1.5 * iqr

    df_outliers = temp[(temp["total_venta"] < limite_inferior) | (temp["total_venta"] > limite_superior)].copy()
    n_outliers = len(df_outliers)
    monto_outliers = df_outliers["total_venta"].sum() if n_outliers > 0 else 0
    monto_total = s.sum() if n_filas > 0 else 0

    tabla_parametros = pd.DataFrame([
        {"Métrica del Modelo IQR": "Primer Cuartil (Q1 - Percentil 25%)", "Valor Estadístico": f"{q1:,.2f}"},
        {"Métrica del Modelo IQR": "Mediana / Segundo Cuartil (Q2 - 50%)", "Valor Estadístico": f"{q2:,.2f}"},
        {"Métrica del Modelo IQR": "Tercer Cuartil (Q3 - Percentil 75%)", "Valor Estadístico": f"{q3:,.2f}"},
        {"Métrica del Modelo IQR": "Rango Intercuartílico (IQR = Q3 - Q1)", "Valor Estadístico": f"{iqr:,.2f}"},
        {"Métrica del Modelo IQR": "Límite Inferior (Q1 - 1.5 * IQR)", "Valor Estadístico": f"{limite_inferior:,.2f}"},
        {"Métrica del Modelo IQR": "Límite Superior (Q3 + 1.5 * IQR)", "Valor Estadístico": f"{limite_superior:,.2f}"},
    ])

    if n_outliers == 0:
        tabla_detalle = crear_tabla_vacia(len(temp.columns), "Sin valores atípicos")
        conclusion = (
            f"El análisis de valores atípicos mediante el modelo IQR no detectó transacciones fuera de los umbrales estadísticos "
            f"[{limite_inferior:,.2f} - {limite_superior:,.2f}]. El comportamiento de compra es homogéneo en toda la muestra."
        )
    else:
        df_outliers["Monto por encima del límite"] = df_outliers["total_venta"] - limite_superior
        tabla_ordenada = df_outliers.sort_values(by="total_venta", ascending=False)
        top_out = tabla_ordenada.iloc[0]
        prod_top = top_out.get("producto", "N/A")
        val_top = top_out.get("total_venta", 0)

        tabla_detalle = tabla_ordenada.copy()
        if "precio_unitario" in tabla_detalle.columns:
            tabla_detalle["precio_unitario"] = tabla_detalle["precio_unitario"].map(lambda x: f"{x:,.2f}" if pd.notna(x) else "")
        if "total_venta" in tabla_detalle.columns:
            tabla_detalle["total_venta"] = tabla_detalle["total_venta"].map(lambda x: f"{x:,.2f}" if pd.notna(x) else "")
        tabla_detalle["Monto por encima del límite"] = tabla_detalle["Monto por encima del límite"].map(lambda x: f"{x:,.2f}" if pd.notna(x) else "")

        conclusion = (
            f"El modelo IQR identificó {n_outliers:,} transacciones con montos inusualmente altos superiores a {limite_superior:,.2f}, "
            f"las cuales concentran {monto_outliers:,.2f} de los ingresos globales. "
            f"La transacción atípica más alta correspondió al producto '{prod_top}' con una venta individual de {val_top:,.2f}. "
            f"Estas compras podrían corresponder a ventas institucionales o corporativas debido a su alto valor."
        )

    return tabla_parametros, tabla_detalle, conclusion


# Valida los datos del formulario y agrega la venta con su ID consecutivo
def agregar_registro_nuevo(
    df: Optional[pd.DataFrame],
    cola: list,
    fecha: str,
    categoria: str,
    producto: str,
    precio: float,
    cantidad: int,
    metodo_pago: str,
    region: str,
    vendedor: str,
    cliente_frecuente: str):
    fecha_limpia = str(fecha).strip() if fecha else ""
    producto_limpio = str(producto).strip() if producto else ""
    vendedor_limpio = str(vendedor).strip() if vendedor else ""
    categoria_limpia = str(categoria).strip() if categoria else ""
    metodo_limpio = str(metodo_pago).strip() if metodo_pago else ""
    region_limpia = str(region).strip() if region else ""
    frecuente_limpio = str(cliente_frecuente).strip().title() if cliente_frecuente else "No"

    if not producto_limpio:
        gr.Warning("El nombre del producto no puede estar vacío.")
        return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: El nombre del producto es obligatorio.</div>", producto, vendedor

    if not vendedor_limpio:
        gr.Warning("El nombre del vendedor no puede estar vacío.")
        return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: El nombre del vendedor es obligatorio.</div>", producto, vendedor

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_limpia):
        gr.Warning("La fecha debe tener el formato estricto AAAA-MM-DD (Ejemplo: 2025-08-15).")
        return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: Formato de fecha inválido. Utilice AAAA-MM-DD.</div>", producto, vendedor

    try:
        dt = datetime.strptime(fecha_limpia, "%Y-%m-%d")
        if dt.year < 2000 or dt.year > 2050:
            raise ValueError("Año fuera de rango razonable.")
    except ValueError:
        gr.Warning("La fecha ingresada no corresponde a una fecha real del calendario (AAAA-MM-DD).")
        return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: Fecha de calendario inválida.</div>", producto, vendedor

    try:
        val_precio = float(precio)
        if val_precio <= 0:
            gr.Warning("El precio unitario debe ser un valor positivo mayor a 0.")
            return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: Precio unitario debe ser mayor a cero.</div>", producto, vendedor
    except (ValueError, TypeError):
        gr.Warning("El precio unitario ingresado no es un número válido.")
        return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: Precio no numérico.</div>", producto, vendedor

    try:
        val_cantidad = int(cantidad)
        if val_cantidad <= 0:
            gr.Warning("La cantidad debe ser un número entero mayor a 0.")
            return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: Cantidad debe ser mayor a cero.</div>", producto, vendedor
    except (ValueError, TypeError):
        gr.Warning("La cantidad ingresada no es un número entero válido.")
        return cola, pd.DataFrame(cola), "<div style='color: #ef4444;'>Error: Cantidad no entera.</div>", producto, vendedor

    total_venta = round(val_precio * val_cantidad, 2)

    max_id = 0
    if df is not None and not df.empty:
        col_id = "id_venta" if "id_venta" in df.columns else next((c for c in df.columns if "id" in c.lower()), None)
        if col_id:
            try:
                val_max = pd.to_numeric(df[col_id], errors="coerce").max()
                if pd.notna(val_max):
                    max_id = int(val_max)
            except Exception:
                max_id = len(df)
        else:
            max_id = len(df)

    siguiente_id = max_id + len(cola) + 1

    nuevo = {
        "id_venta": siguiente_id,
        "fecha": fecha_limpia,
        "producto": producto_limpio.title(),
        "categoria": categoria_limpia.title(),
        "precio_unitario": val_precio,
        "cantidad": val_cantidad,
        "metodo_pago": metodo_limpio.title(),
        "region": region_limpia.title(),
        "vendedor": vendedor_limpio.title(),
        "cliente_frecuente": frecuente_limpio,
    }

    cola_actualizada = list(cola) + [nuevo]
    gr.Info(f"Registro agregado con éxito (ID: {siguiente_id}). Total agregados: {len(cola_actualizada)}")
    df_cola = formatear_tabla(pd.DataFrame(cola_actualizada))
    msg_ok = f"<div style='color: #22c55e; font-weight: bold;'>Registro agregado correctamente (ID: {siguiente_id}). Total agregados: {len(cola_actualizada)}</div>"

    return cola_actualizada, df_cola, msg_ok, "", ""


# Elimina todos los registros nuevos ingresados
def limpiar_cola_registros():
    gr.Info("Registros eliminados.")
    return [], pd.DataFrame(), pd.DataFrame(), "<div style='text-align: center; color: #94a3b8; font-weight: 500;'>No hay registros ingresados todavía.</div>"


# Guarda las nuevas ventas en el dataset principal y genera el archivo CSV actualizado
def guardar_nuevos_registros(df: Optional[pd.DataFrame], cola: list):
    if not cola:
        gr.Warning("No hay nuevos registros para guardar.")
        return df, cola, pd.DataFrame(), pd.DataFrame(), gr.update(visible=False), SEÑAL_DATOS_LIMPIOS

    df_nuevos = pd.DataFrame(cola)
    if df is not None and not df.empty:
        df_consolidado = pd.concat([df, df_nuevos], ignore_index=True)
    else:
        df_consolidado = df_nuevos

    ruta_descarga = "ventas_actualizadas.csv"
    df_consolidado.to_csv(ruta_descarga, index=False, encoding="utf-8")

    total = len(cola)
    gr.Info(f"Se guardaron {total} registro(s) exitosamente. Total en dataset: {len(df_consolidado):,} filas.")

    return df_consolidado, [], pd.DataFrame(), pd.DataFrame(), gr.update(value=ruta_descarga, visible=True), SEÑAL_DATOS_LIMPIOS


# Controla las pantallas del submenu para el ingreso de nuevos datos y guardado
def cambiar_subvista_ingreso(subopcion: str, cola: list):
    df_cola = formatear_tabla(pd.DataFrame(cola))
    msg_cola = (
        f"<div style='text-align: center; color: #38bdf8; font-weight: 600;'>Registros pendientes de guardar: {len(cola)}</div>"
        if cola else "<div style='text-align: center; color: #94a3b8; font-weight: 500;'>No hay registros ingresados todavía.</div>")

    if subopcion == "Ingresar un nuevo registro":
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(visible=False),
            gr.update(),
            gr.update(visible=True),
            gr.update(visible=False))
    elif subopcion == "Mostrar registros ingresados":
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=df_cola),
            gr.update(value=df_cola),
            gr.update(value=msg_cola),
            gr.update(visible=False),
            gr.update(),
            gr.update(visible=True),
            gr.update(visible=False))
    elif subopcion == "Guardar los nuevos datos":
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(value=df_cola),
            gr.update(value=df_cola),
            gr.update(),
            gr.update(visible=False),
            gr.update(),
            gr.update(visible=True),
            gr.update(visible=False))
    elif subopcion == "Regresar al menú principal":
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(visible=False),
            None,
            gr.update(visible=False),
            gr.update(visible=True))
    return (
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(visible=False),
        gr.update(),
        gr.update(visible=True),
        gr.update(visible=False))


# Busca coincidencias de texto en una columna especifica o en toda la tabla
def filtrar_datos(df: Optional[pd.DataFrame], columna: Optional[str], texto: Optional[str]) -> tuple[pd.DataFrame, str]:
    if df is None or df.empty:
        return pd.DataFrame(), "<div style='text-align: center; color: #94a3b8;'>No hay datos cargados para filtrar.</div>"

    query = str(texto).strip().lower() if texto else ""
    if not query:
        return formatear_tabla(df), f"<div style='text-align: center; color: white; font-weight: 500;'>Mostrando todos los registros ({len(df):,} filas)</div>"

    col_target = str(columna).strip() if columna else "Todas las columnas"

    if col_target == "Todas las columnas" or col_target not in df.columns:
        mascara = pd.Series(False, index=df.index)
        for col in df.columns:
            mascara |= df[col].astype(str).str.lower().str.contains(query, regex=False, na=False)
        resultado = df[mascara]
        total_coincidencias = len(resultado)
        msg = f"<div style='text-align: center; color: #38bdf8; font-weight: 600;'>Se encontraron {total_coincidencias:,} coincidencias de '{query}' en todas las columnas (de {len(df):,} registros).</div>"
    else:
        mascara = df[col_target].astype(str).str.lower().str.contains(query, regex=False, na=False)
        resultado = df[mascara]
        total_coincidencias = len(resultado)
        msg = f"<div style='text-align: center; color: #38bdf8; font-weight: 600;'>Se encontraron {total_coincidencias:,} coincidencias de '{query}' en la columna '{col_target}'.</div>"

    if len(resultado) == 0:
        msg = f"<div style='text-align: center; color: #f87171; font-weight: 600;'>No se encontraron registros que coincidan con '{query}' en '{col_target}'.</div>"

    return formatear_tabla(resultado), msg


# Limpia la busqueda y vuelve a mostrar todos los registros del dataset
def restablecer_filtro(df: Optional[pd.DataFrame]) -> tuple[str, str, pd.DataFrame, str]:
    if df is None:
        return "Todas las columnas", "", pd.DataFrame(), ""
    return (
        "Todas las columnas",
        "",
        formatear_tabla(df),
        f"<div style='text-align: center; color: white; font-weight: 500;'>Mostrando todos los registros ({len(df):,} filas)</div>")


# Agrupa las ventas por columna seleccionada y calcula totales e ingresos
def agrupar_datos(df: Optional[pd.DataFrame], dimension: Optional[str]) -> tuple[pd.DataFrame, str]:
    if df is None or df.empty:
        return pd.DataFrame(), "No hay datos cargados."

    mapa_cols = {
        "Categoría": "categoria",
        "Producto": "producto",
        "Vendedor": "vendedor",
        "Región": "region",
        "Método de Pago": "metodo_pago",
        "Cliente Frecuente": "cliente_frecuente"}
    dim_col = mapa_cols.get(dimension, "categoria")
    if dim_col not in df.columns:
        dim_col = df.select_dtypes(include=["object", "string", "category"]).columns[0]
        dim_nombre = dim_col.capitalize()
    else:
        dim_nombre = dimension if dimension in mapa_cols else dim_col.capitalize()

    temp = df.copy()
    if "cantidad" in temp.columns and "precio_unitario" in temp.columns:
        temp["total_venta"] = temp["cantidad"] * temp["precio_unitario"]
    elif "total_venta" not in temp.columns:
        temp["total_venta"] = 0

    agrupado = temp.groupby(dim_col, as_index=False).agg(
        Transacciones=("total_venta", "count"),
        Unidades_Vendidas=("cantidad", "sum") if "cantidad" in temp.columns else ("total_venta", "count"),
        Ingreso_Total=("total_venta", "sum"),
        Ticket_Promedio=("total_venta", "mean"))

    total_ingresos = agrupado["Ingreso_Total"].sum()
    agrupado["Participacion_Num"] = (agrupado["Ingreso_Total"] / total_ingresos * 100) if total_ingresos > 0 else 0
    agrupado = agrupado.sort_values(by="Ingreso_Total", ascending=False).reset_index(drop=True)

    lider_ingreso = agrupado.iloc[0]
    lider_unidades = agrupado.sort_values(by="Unidades_Vendidas", ascending=False).iloc[0]
    lider_ticket = agrupado.sort_values(by="Ticket_Promedio", ascending=False).iloc[0]

    tabla_mostrar = pd.DataFrame({
        dim_nombre: agrupado[dim_col],
        "Transacciones": agrupado["Transacciones"].map(lambda x: f"{int(x):,}"),
        "Unidades Vendidas": agrupado["Unidades_Vendidas"].map(lambda x: f"{int(x):,}"),
        "Ingreso Total": agrupado["Ingreso_Total"].map(lambda x: f"{x:,.2f}"),
        "Ticket Promedio": agrupado["Ticket_Promedio"].map(lambda x: f"{x:,.2f}"),
        "Participación": agrupado["Participacion_Num"].map(lambda x: f"{x:.1f}%")})

    ing_val = lider_ingreso["Ingreso_Total"]
    pct_val = lider_ingreso["Participacion_Num"]
    unid_val = int(lider_unidades["Unidades_Vendidas"])
    tkt_val = lider_ticket["Ticket_Promedio"]
    nom_ing = lider_ingreso[dim_col]
    nom_unid = lider_unidades[dim_col]
    nom_tkt = lider_ticket[dim_col]

    if nom_ing == nom_unid == nom_tkt:
        conclusion = (
            f"Al agrupar el conjunto de datos por '{dim_nombre}', '{nom_ing}' lidera las ventas "
            f"con {ing_val:,.2f} en facturación ({pct_val:.1f}% del total), {unid_val:,} unidades vendidas "
            f"y el ticket promedio más alto con {tkt_val:,.2f} por transacción."
        )
    elif nom_ing == nom_unid:
        conclusion = (
            f"Al agrupar el conjunto de datos por '{dim_nombre}', '{nom_ing}' lidera tanto la facturación "
            f"con {ing_val:,.2f} ({pct_val:.1f}% del total) como la cantidad de unidades vendidas con {unid_val:,} unidades, "
            f"mientras que '{nom_tkt}' presentó el ticket promedio más alto con {tkt_val:,.2f} por transacción."
        )
    elif nom_ing == nom_tkt:
        conclusion = (
            f"Al agrupar el conjunto de datos por '{dim_nombre}', '{nom_ing}' lidera la facturación "
            f"con {ing_val:,.2f} ({pct_val:.1f}% del total) y el ticket promedio más alto con {tkt_val:,.2f} por transacción, "
            f"mientras que '{nom_unid}' registró la mayor cantidad de ventas con {unid_val:,} unidades."
        )
    else:
        conclusion = (
            f"Al agrupar el conjunto de datos por '{dim_nombre}', '{nom_ing}' lidera la facturación "
            f"con {ing_val:,.2f} ({pct_val:.1f}% del total). "
            f"En cantidad de unidades vendidas, '{nom_unid}' ocupa el primer lugar con {unid_val:,} unidades, "
            f"mientras que '{nom_tkt}' presentó el ticket promedio más alto con {tkt_val:,.2f} por transacción."
        )

    return tabla_mostrar, conclusion


# Dibuja graficos de barras horizontales o verticales con formato en millones
def _dibujar_barras(ax, serie: pd.Series, titulo: str, xlabel: str, ylabel: str, color: str, edgecolor: str, rot: int = 0, horizontal: bool = False):
    vals = serie.values / 1e6
    if horizontal:
        bars = ax.barh(serie.index, vals, color=color, edgecolor=edgecolor)
        ax.set_xlabel(xlabel, fontsize=11)
    else:
        bars = ax.bar(serie.index, vals, color=color, edgecolor=edgecolor)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_xlabel(xlabel, fontsize=11)
        if rot:
            plt.xticks(rotation=rot)
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=12)
    ax.bar_label(bars, fmt="%.1fM", padding=3, color="white", fontsize=9)


# Crea el grafico seleccionado con Matplotlib y conclusion
def generar_grafico(df: Optional[pd.DataFrame], tipo_grafico: Optional[str]) -> tuple[Optional[plt.Figure], str]:
    if df is None or df.empty:
        return None, "No hay datos cargados para generar la visualización gráfica."

    temp = df.copy()
    if "cantidad" in temp.columns and "precio_unitario" in temp.columns:
        temp["total_venta"] = temp["cantidad"] * temp["precio_unitario"]
    elif "total_venta" not in temp.columns:
        temp["total_venta"] = 0

    plt.close("all")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor("#1e293b")
    ax.set_facecolor("#0f172a")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.grid(color="#334155", linestyle="--", alpha=0.5)

    if tipo_grafico == "Ingresos por Categoría":
        grp = temp.groupby("categoria")["total_venta"].sum().sort_values(ascending=False)
        _dibujar_barras(ax, grp, "Ingresos Totales por Categoría en Millones", "Categoría", "Ingreso Total Millones", "#38bdf8", "#0284c7")
        top_cat, top_val = grp.index[0], grp.iloc[0]
        pct_top = (top_val / grp.sum()) * 100
        segunda_cat = grp.index[1] if len(grp) > 1 else ""
        conclusion = (
            f"La categoría de '{top_cat}' se consolida como la fuente de ingresos principal de la tienda, generando "
            f"{top_val:,.2f} ({pct_top:.1f}% del total). "
            f"Los datos muestran que la mayor parte del flujo de caja proviene de equipos de alto valor, "
            f"mientras que opciones como '{segunda_cat}' y accesorios funcionan como complementos clave para impulsar las ventas.")

    elif tipo_grafico == "Top 10 Productos con Mayor Recaudación":
        grp = temp.groupby("producto")["total_venta"].sum().sort_values(ascending=True).tail(10)
        _dibujar_barras(ax, grp, "Top 10 Productos con Mayor Facturación en Millones", "Ingreso Total Millones", "", "#818cf8", "#4f46e5", horizontal=True)
        top_prod, top_prod_val = grp.index[-1], grp.iloc[-1]
        segundo_prod = grp.index[-2] if len(grp) > 1 else ""
        conclusion = (
            f"El producto estrella de la tienda es '{top_prod}' con {top_prod_val:,.2f} en facturación acumulada, "
            f"seguido por '{segundo_prod}'. "
            f"El análisis nos cuenta que pocos artículos de gama alta generan la mayor parte de la rentabilidad del negocio "
            f"y aunque se vendan menos unidades en comparación con cables o accesorios pequeños, su alto valor compensa el bajo volumen.")

    elif tipo_grafico == "Tendencia Histórica de Ventas":
        temp["mes_anio"] = pd.to_datetime(temp["fecha"], errors="coerce").dt.to_period("M").astype(str)
        grp = temp.groupby("mes_anio")["total_venta"].sum()
        ax.plot(grp.index, grp.values / 1e6, marker="o", color="#34d399", linewidth=2.5, markersize=6)
        ax.set_title("Evolución Mensual de Ventas en Millones", fontsize=13, fontweight="bold", pad=12)
        ax.set_ylabel("Ingreso Total Millones", fontsize=11)
        ax.set_xlabel("Mes", fontsize=11)
        plt.xticks(rotation=45)
        mes_max, val_max = grp.idxmax(), grp.max()
        mes_min, val_min = grp.idxmin(), grp.min()
        conclusion = (
            f"La evolución temporal muestra que el pico más alto de ventas ocurrió en '{mes_max}' con {val_max:,.2f}, "
            f"mientras que el mes con menor actividad fue '{mes_min}' ({val_min:,.2f}). "
            f"Esta curva refleja un estancamiento del mercado tecnológico, donde se aprecian momentos de compras fuertes "
            f"seguidos de meses de estabilización.")

    elif tipo_grafico == "Distribución por Método de Pago":
        grp = temp.groupby("metodo_pago")["total_venta"].sum()
        colores = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171"]
        _wedges, _texts, autotexts = ax.pie(  # type: ignore[misc]
            grp.values,
            labels=grp.index,
            autopct="%1.1f%%",
            startangle=140,
            colors=colores[:len(grp)],
            wedgeprops={"edgecolor": "#0f172a", "linewidth": 2},
            textprops={"color": "white", "fontsize": 10})
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")
        ax.set_title("Distribución de Ingresos por Método de Pago", fontsize=13, fontweight="bold", pad=12)
        top_pago = grp.idxmax()
        pct_pago = (grp.max() / grp.sum()) * 100
        segundo_pago = grp.sort_values(ascending=False).index[1] if len(grp) > 1 else ""
        conclusion = (
            f"El método de pago con mayor recaudación es '{top_pago}' con el {pct_pago:.1f}% de los ingresos, "
            f"seguido de cerca por '{segundo_pago}'. "
            f"La preferencia de los clientes demuestra la preferencia por pagos en efectivo y la agilidad de los medios digitales "
            f"que facilitan que los compradores realicen compras tecnológicas de alto valor.")

    elif tipo_grafico == "Facturación por Región":
        grp = temp.groupby("region")["total_venta"].sum().sort_values(ascending=False)
        _dibujar_barras(ax, grp, "Facturación Total por Región en Millones", "Región", "Ingreso Total Millones", "#fbbf24", "#d97706", rot=45)
        top_reg, val_reg = grp.index[0], grp.iloc[0]
        pct_reg = (val_reg / grp.sum()) * 100
        segunda_reg = grp.index[1] if len(grp) > 1 else ""
        conclusion = (
            f"En el mapa geográfico, la provincia de '{top_reg}' lidera la facturación con {val_reg:,.2f} ({pct_reg:.1f}% de los ingresos), "
            f"acompañada por '{segunda_reg}'. "
            f"Este comportamiento muestra una alta concentración de clientes en zonas con gran actividad, "
            f"marcando a '{top_reg}' como un punto estratégico para asegurar buen stock de productos y agilizar entregas.")

    elif tipo_grafico == "Desempeño Comercial por Vendedor":
        grp = temp.groupby("vendedor")["total_venta"].sum().sort_values(ascending=False)
        _dibujar_barras(ax, grp, "Facturación Total por Vendedor en Millones", "Vendedor", "Ingreso Total Millones", "#f472b6", "#db2777", rot=45)
        top_vend, val_vend = grp.index[0], grp.iloc[0]
        pct_vend = (val_vend / grp.sum()) * 100
        segundo_vend = grp.index[1] if len(grp) > 1 else ""
        conclusion = (
            f"En el equipo comercial, '{top_vend}' encabeza las ventas con {val_vend:,.2f} recaudados ({pct_vend:.1f}% del total), "
            f"seguida por '{segundo_vend}'. "
            f"El éxito del equipo refleja que el asesoramiento técnico y personalizado marca la diferencia al vender tecnología de gama alta, "
            f"logrando concretar pedidos de mayor valor y fidelizar tanto a clientes frecuentes como a compras empresariales.")
    else:
        conclusion = "Seleccione un gráfico válido de la lista."

    fig.tight_layout()
    return fig, conclusion


# SECCION QUE CONTROLA EL ESTADO Y LAS VISTAS

# Comprueba que el dataset no tenga nulos, duplicados o inconsistencias
def verificar_datos_limpios(df: Optional[pd.DataFrame]) -> bool:
    if df is None or df.empty:
        return False

    col_id = "id_venta" if "id_venta" in df.columns else next((c for c in df.columns if "id" in c.lower()), None)
    return not (
        df.isna().any().any()
        or df.duplicated().any()
        or (bool(col_id) and df.duplicated(subset=[col_id]).any())
        or ("fecha" in df.columns and df["fecha"].dropna().astype(str).str.contains(r"/").any())
        or ("cantidad" in df.columns and pd.api.types.is_numeric_dtype(df["cantidad"]) and (df["cantidad"] <= 0).any())
        or ("cliente_frecuente" in df.columns and (~df["cliente_frecuente"].dropna().astype(str).isin(["Sí", "No"])).any())
    )


# Lee el archivo CSV subido y valida su contenido y muestra el menu
def cargar_archivo(archivo):
    if not archivo:
        return (
            gr.update(visible=False),
            gr.update(value=None, visible=True),
            None,
            gr.update(visible=False),
            SEÑAL_DATOS_SUCIOS,
        )

    try:
        ruta = archivo.name if hasattr(archivo, "name") else str(archivo)
        try:
            df = pd.read_csv(ruta, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(ruta, encoding="latin1")

        if df.empty or len(df.columns) == 0:
            gr.Warning("El archivo CSV cargado está vacío o no contiene datos válidos.")
            return (
                gr.update(visible=False),
                gr.update(value=None, visible=True),
                None,
                gr.update(visible=False),
                SEÑAL_DATOS_SUCIOS,
            )

        gr.Info(f"Archivo cargado exitosamente: {len(df):,} filas y {len(df.columns)} columnas.")
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            df,
            gr.update(visible=True),
            SEÑAL_DATOS_SUCIOS,
        )
    except Exception as error:
        gr.Warning(f"Error al intentar leer el archivo CSV: {str(error)}")
        return (
            gr.update(visible=False),
            gr.update(value=None, visible=True),
            None,
            gr.update(visible=False),
            SEÑAL_DATOS_SUCIOS,
        )


# Genera la configuracion inicial de la interfaz con todos los paneles ocultos
def _salida_base(df: Optional[pd.DataFrame]) -> list:
    return [
        df,
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value=""),
        gr.update(value=None),
        gr.update(visible=False),
        gr.update(value=""),
        gr.update(value=None),
        gr.update(value=""),
        gr.update(value=None),
        gr.update(value=""),
        gr.update(visible=False),
        gr.update(choices=["Todas las columnas"], value="Todas las columnas"),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=None),
        gr.update(visible=False),
        gr.update(value="Categoría"),
        gr.update(value=None),
        gr.update(value=""),
        gr.update(visible=False),
        gr.update(value="Ingresos por Categoría"),
        gr.update(value=None),
        gr.update(value=""),
        gr.update(visible=False, value=""),
        gr.update(visible=False),
        gr.update(),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
    ]


# Oculta todos los paneles visibles del area central
def ocultar_paneles(df: Optional[pd.DataFrame]):
    return tuple(_salida_base(df))


# Muestra la vista con una sola tabla para consultar datos o primeras y ultimas filas
def mostrar_vista_simple(df: pd.DataFrame, titulo: str, datos: pd.DataFrame):
    salida = _salida_base(df)
    salida[2] = gr.update(visible=True)
    salida[3] = gr.update(value=titulo)
    salida[4] = gr.update(value=formatear_tabla(datos))
    return tuple(salida)


# Despliega la vista universal con tabla, detalle y conclusion
def mostrar_tres_paneles(df: pd.DataFrame, t1: str, tab1: pd.DataFrame, t2: str, tab2: pd.DataFrame, conclusion: str):
    salida = _salida_base(df)
    salida[5] = gr.update(visible=True)
    salida[6] = gr.update(value=f"<h3 style='text-align: center;'>{t1}</h3>")
    salida[7] = gr.update(value=formatear_tabla(tab1))
    salida[8] = gr.update(value=f"<h3 style='text-align: center;'>{t2}</h3>")
    salida[9] = gr.update(value=formatear_tabla(tab2))
    salida[10] = gr.update(value=conclusion)
    return tuple(salida)


# Abre el panel con buscador y selector de columnas para filtrar
def mostrar_filtrado(df: pd.DataFrame):
    salida = _salida_base(df)
    salida[11] = gr.update(visible=True)
    salida[12] = gr.update(choices=["Todas las columnas"] + list(df.columns), value="Todas las columnas")
    salida[14] = gr.update(value=f"<div style='text-align: center; color: white; font-weight: 500;'>Mostrando todos los registros ({len(df):,} filas)</div>")
    salida[15] = gr.update(value=formatear_tabla(df))
    return tuple(salida)


# Abre el panel para agrupar ventas por diferentes columnas
def mostrar_agrupaciones(df: pd.DataFrame):
    tabla_ini, conc_ini = agrupar_datos(df, "Categoría")
    salida = _salida_base(df)
    salida[16] = gr.update(visible=True)
    salida[17] = gr.update(value="Categoría")
    salida[18] = gr.update(value=tabla_ini)
    salida[19] = gr.update(value=conc_ini)
    return tuple(salida)


# Abre el panel de visualizaciones graficas y conclusiones
def mostrar_graficos(df: pd.DataFrame):
    fig_ini, conc_ini = generar_grafico(df, "Ingresos por Categoría")
    salida = _salida_base(df)
    salida[20] = gr.update(visible=True)
    salida[21] = gr.update(value="Ingresos por Categoría")
    salida[22] = gr.update(value=fig_ini)
    salida[23] = gr.update(value=conc_ini)
    return tuple(salida)


# Crea una tarjeta con texto centrado
def formatear_mensaje_panel_central(mensaje: str) -> str:
    parrafos = mensaje.strip().split("\n\n")
    html_parrafos = "".join(
        f"<p style='margin: 12px 0; font-size: 1.15rem; line-height: 1.6; color: #f1f5f9;'>{p.replace('\n', '<br>')}</p>"
        for p in parrafos if p.strip()
    )
    return (
        f"<div style='display: flex; flex-direction: column; justify-content: center; align-items: center; "
        f"min-height: 520px; height: 100%; text-align: center; padding: 40px 24px; border-radius: 12px; "
        f"background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); box-sizing: border-box;'>"
        f"<div style='max-width: 620px; font-weight: 500;'>"
        f"{html_parrafos}"
        f"</div>"
        f"</div>"
    )


# Muestra un mensaje informativo o de advertencia centrado en la pantalla
def mostrar_notificacion(df: Optional[pd.DataFrame], mensaje: str):
    salida = _salida_base(df)
    salida[24] = gr.update(visible=True, value=formatear_mensaje_panel_central(mensaje))
    return tuple(salida)


# Despliega el submenu y el formulario para registrar nuevas ventas
def mostrar_ingreso_datos(df: pd.DataFrame):
    salida = _salida_base(df)
    salida[25] = gr.update(visible=True)
    salida[26] = gr.update(value="Ingresar un nuevo registro")
    salida[27] = gr.update(visible=True)
    return tuple(salida)


# Muestra u oculta los botones de confirmacion para limpiar datos o salir
def gestionar_confirmacion(opcion: Optional[str]):
    if opcion == "7. Limpiar datos":
        return gr.update(visible=True), gr.update(visible=False)
    elif opcion == OPCION_SALIR:
        return gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False)


# Ejecuta la limpieza de datos tras la confirmacion del usuario y actualiza la vista
def confirmar_limpieza(df: Optional[pd.DataFrame]):
    if df is None:
        return (gr.update(visible=False), SEÑAL_DATOS_SUCIOS, *ocultar_paneles(df))

    tabla_stats, tabla_limpia, conclusion, df_limpio = limpiar_datos(df)
    return (
        gr.update(visible=False),
        SEÑAL_DATOS_LIMPIOS,
        *mostrar_tres_paneles(
            df_limpio,
            "Estadísticas de Limpieza de Datos",
            tabla_stats,
            "Conjunto de Datos Limpio",
            tabla_limpia,
            conclusion))


# Cancela la operacion de limpieza y desmarca la opcion en el menu
def cancelar_limpieza():
    return gr.update(visible=False), None, gr.update(visible=False, value="")


# Recibe la opcion elegida en el menu y ejecuta la vista o analisis correspondiente
def menu(df: Optional[pd.DataFrame], opcion: Optional[str]):
    if df is None:
        return ocultar_paneles(df)

    if not opcion:
        salida = _salida_base(df)
        salida[1] = gr.update(visible=True)
        return tuple(salida)

    if opcion == OPCION_SALIR:
        return mostrar_notificacion(
            df,
            "Por favor, confirme si desea salir haciendo clic en el botón 'Salir' ubicado debajo del menú lateral, "
            "o haga clic en 'Cancelar' para continuar trabajando con el conjunto de datos.")

    if opcion in OPCIONES_REQUIEREN_LIMPIEZA and not verificar_datos_limpios(df):
        gr.Warning("Los datos contienen anomalías. Debes ejecutar primero la opción '7. Limpiar datos'.")
        mensaje = (
            f"Para utilizar la opción '{opcion}', es obligatorio que el conjunto de datos se encuentre limpio y estandarizado.\n\n"
            f"Actualmente el dataset contiene valores nulos, duplicados o inconsistencias pendientes de corrección.\n\n"
            f"Por favor, selecciona primero la opción '7. Limpiar datos' en el menú lateral.")
        return mostrar_notificacion(df, mensaje)

    match opcion:
        case "1. Mostrar información del conjunto de datos":
            return mostrar_vista_simple(df, "<h3 style='text-align: center;'>Conjunto de Datos Completo</h3>", df)

        case "2. Mostrar primeras y últimas filas":
            return mostrar_vista_simple(df, "<h3 style='text-align: center;'>Primeras y Últimas Filas</h3>", pd.concat([df.head(2), df.tail(2)]))

        case "3. Analizar tipos de datos":
            resumen, detalle, conclusion = analizar_tipos(df)
            return mostrar_tres_paneles(df, "Resumen de Tipos de Datos", resumen, "Detalle de Tipos por Columna", detalle, conclusion)

        case "4. Analizar datos nulos":
            stats, filas, conclusion = analizar_nulos(df)
            return mostrar_tres_paneles(df, "Estadísticas de Valores Nulos", stats, "Registros con Valores Nulos", filas, conclusion)

        case "5. Analizar datos duplicados":
            stats, filas, conclusion = analizar_duplicados(df)
            return mostrar_tres_paneles(df, "Estadísticas de Duplicados", stats, "Registros Duplicados", filas, conclusion)

        case "6. Analizar datos inconsistentes":
            stats, filas, conclusion = analizar_inconsistencias(df)
            return mostrar_tres_paneles(df, "Estadísticas de Inconsistencias", stats, "Registros con Inconsistencias", filas, conclusion)

        case "7. Limpiar datos":
            return mostrar_notificacion(
                df,
                "Se ha solicitado la limpieza del conjunto de datos.\n\n"
                "Por favor, confirme la operación haciendo clic en el botón 'Limpiar' que aparece debajo del menú lateral, "
                "o haga clic en 'Cancelar' para continuar sin realizar cambios.")

        case "8. Obtener estadísticas descriptivas":
            stats_num, stats_cat, conclusion = analizar_estadisticas(df)
            return mostrar_tres_paneles(df, "Resumen de estadísticas (precios, cantidades e ingresos)", stats_num, "Valores más frecuentes por columna", stats_cat, conclusion)

        case "9. Filtrar o consultar datos":
            return mostrar_filtrado(df)

        case "10. Realizar agrupaciones y operaciones":
            return mostrar_agrupaciones(df)

        case "11. Generar representaciones gráficas":
            return mostrar_graficos(df)

        case "12. Realizar análisis adicional":
            params, detalle, conclusion = analizar_outliers(df)
            return mostrar_tres_paneles(df, "Detección de Valores Atípicos (Modelo IQR)", params, "Detalle de Transacciones Atípicas Detectadas", detalle, conclusion)

        case "13. Ingresar nuevos datos":
            return mostrar_ingreso_datos(df)


# Reinicia la aplicacion y regresa a la pantalla inicial para cargar un nuevo archivo
def confirmar_salida():
    salida = _salida_base(None)
    salida[26] = gr.update(value="Ingresar un nuevo registro")
    return (
        gr.update(value=None, visible=True),
        None,
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        salida[0],
        *salida[1:25],
        SEÑAL_DATOS_SUCIOS,
        *salida[25:30],[])


# Cancela la salida
def cancelar_salida():
    return gr.update(visible=False), None, gr.update(visible=False, value="")


# SECCION QUE DEFINE LA INTERFAZ GRAFICA

# Define todos los componentes de la vista y gestiona los eventos
def crear_interfaz() -> gr.Blocks:
    with gr.Blocks(title="Panel de Análisis de Datos") as aplicacion:

        with gr.Group():
            gr.Markdown("<h1 style='text-align: center;'>Panel de Análisis de Datos</h1>\n")

        df_estado = gr.State()
        cola_estado = gr.State([])

        with gr.Row():
            with gr.Column(scale=1, min_width=290, visible=False) as panel_lateral:
                with gr.Group():
                    gr.Markdown("<h2 style='text-align: center;'>Menú</h2>")
                    badge_estado = gr.Markdown(SEÑAL_DATOS_SUCIOS)
                    menu_opciones = gr.Radio(choices=OPCIONES_MENU, show_label=False)

                with gr.Group(visible=False) as grupo_limpieza:
                    gr.Markdown("**¿Desea ejecutar la limpieza de datos?**")
                    with gr.Row():
                        btn_confirmar_limpieza = gr.Button("Limpiar", variant="primary", size="sm")
                        btn_cancelar_limpieza = gr.Button("Cancelar", variant="secondary", size="sm")

                with gr.Group(visible=False) as grupo_salida:
                    gr.Markdown("**¿Desea salir de la sesión actual?**")
                    with gr.Row():
                        btn_confirmar_salida = gr.Button("Salir", variant="stop", size="sm")
                        btn_cancelar_salida = gr.Button("Cancelar", variant="secondary", size="sm")

            with gr.Column(scale=4):

                input_archivo = gr.File(
                    label="Cargar archivo CSV",
                    file_types=[".csv"],
                    type="filepath",
                    height=520,
                    elem_id="cargador_archivo")

                with gr.Column(visible=False) as panel_inicial:
                    gr.Markdown(
                        formatear_mensaje_panel_central(
                            "Archivo cargado correctamente.\n\n"
                            "Por favor, seleccione una opción del menú lateral para comenzar a explorar, limpiar y analizar los datos."))

                with gr.Column(visible=False) as panel_simple:
                    with gr.Group():
                        titulo_simple = gr.Markdown()
                        tabla_simple = gr.Dataframe(interactive=False)

                with gr.Column(visible=False) as panel_tres:
                    with gr.Group():
                        titulo_1 = gr.Markdown()
                        tabla_1 = gr.Dataframe(interactive=False)

                    with gr.Group():
                        titulo_2 = gr.Markdown()
                        tabla_2 = gr.Dataframe(interactive=False)

                    with gr.Group():
                        gr.Markdown("<h3 style='text-align: center;'>Conclusión</h3>")
                        txt_conclusion = gr.Markdown()

                with gr.Column(visible=False) as panel_filtro:
                    with gr.Group():
                        gr.Markdown("<h3 style='text-align: center;'>Herramienta de Filtrado y Consulta</h3>")
                        with gr.Row():
                            dropdown_col_filtro = gr.Dropdown(
                                choices=["Todas las columnas"],
                                value="Todas las columnas",
                                label="Columna a filtrar",
                            )
                            input_filtro = gr.Textbox(
                                label="Término de búsqueda",
                                placeholder="Escriba el valor a buscar...",
                            )
                        with gr.Row():
                            btn_reset_filtro = gr.Button("Restablecer Filtro", variant="secondary", size="sm")

                    with gr.Group():
                        info_filtro = gr.Markdown("<div style='text-align: center; color: white;'>Mostrando todos los registros</div>")
                        tabla_filtro = gr.Dataframe(interactive=False)

                with gr.Column(visible=False) as panel_agrupado:
                    with gr.Group():
                        gr.Markdown("<h3 style='text-align: center;'>Agrupaciones y Operaciones por Dimensión</h3>")
                        dropdown_dim_agrupado = gr.Dropdown(
                            choices=["Categoría", "Producto", "Vendedor", "Región", "Método de Pago", "Cliente Frecuente"],
                            value="Categoría",
                            show_label=False,
                        )

                    with gr.Group():
                        tabla_agrupado = gr.Dataframe(interactive=False)

                    with gr.Group():
                        gr.Markdown("<h3 style='text-align: center;'>Conclusión</h3>")
                        info_agrupado = gr.Markdown()

                with gr.Column(visible=False) as panel_grafico:
                    with gr.Group():
                        gr.Markdown("<h3 style='text-align: center;'>Representaciones Gráficas</h3>")
                        dropdown_grafico = gr.Dropdown(
                            choices=OPCIONES_GRAFICOS,
                            value="Ingresos por Categoría",
                            show_label=False)

                    with gr.Group():
                        plot_figura = gr.Plot(show_label=False)

                    with gr.Group():
                        gr.Markdown("<h3 style='text-align: center;'>Conclusión</h3>")
                        info_grafico = gr.Markdown()

                with gr.Column(visible=False) as panel_ingreso:
                    with gr.Group():
                        gr.Markdown("<h3 style='text-align: center;'>Ingresar y Gestionar Nuevos Datos</h3>")
                        sub_menu_ingreso = gr.Radio(
                            choices=OPCIONES_SUBMENU_INGRESO,
                            value="Ingresar un nuevo registro",
                            show_label=False)

                    with gr.Group(visible=True) as form_ingreso:
                        gr.Markdown("<h4 style='text-align: center;'>Formulario de Captura de Registro</h4>")
                        with gr.Row():
                            in_fecha = gr.Textbox(
                                label="Fecha (AAAA-MM-DD)",
                                placeholder="Ej: 2025-08-15",
                                value=pd.Timestamp.now().strftime("%Y-%m-%d"))
                            in_categoria = gr.Dropdown(
                                label="Categoría",
                                choices=OPCIONES_CATEGORIAS_DEFAULT,
                                value="Celulares",
                                allow_custom_value=True)
                            in_producto = gr.Textbox(
                                label="Producto",
                                placeholder="Ej: Smartphone Samsung S24")
                        with gr.Row():
                            in_precio = gr.Number(
                                label="Precio Unitario ($)",
                                value=500.0,
                                minimum=0.01)
                            in_cantidad = gr.Number(
                                label="Cantidad",
                                value=1,
                                precision=0,
                                minimum=1)
                            in_metodo_pago = gr.Dropdown(
                                label="Método de Pago",
                                choices=OPCIONES_METODOS_PAGO_DEFAULT,
                                value="Sinpe Móvil",
                                allow_custom_value=True)
                        with gr.Row():
                            in_region = gr.Dropdown(
                                label="Región / Provincia",
                                choices=OPCIONES_REGIONES_DEFAULT,
                                value="San José",
                                allow_custom_value=True)
                            in_vendedor = gr.Textbox(
                                label="Vendedor",
                                placeholder="Ej: Carlos Gómez")
                            in_cliente_frecuente = gr.Dropdown(
                                label="Cliente Frecuente",
                                choices=["Sí", "No"],
                                value="No")
                        with gr.Row():
                            btn_agregar = gr.Button("Agregar Registro", variant="primary")
                        info_registro = gr.Markdown()
                    with gr.Group(visible=False) as tabla_cola_vista:
                        gr.Markdown("<h4 style='text-align: center;'>Registros Ingresados</h4>")
                        info_cola = gr.Markdown("<div style='text-align: center; color: #94a3b8; font-weight: 500;'>No hay registros ingresados todavía.</div>")
                        tabla_cola = gr.Dataframe(interactive=False)
                        with gr.Row():
                            btn_vaciar_cola = gr.Button("Vaciar Registros", variant="secondary", size="sm")

                    with gr.Group(visible=False) as guardar_vista:
                        gr.Markdown("<h4 style='text-align: center;'>Guardar Nuevos Datos</h4>")
                        tabla_guardar = gr.Dataframe(interactive=False)
                        with gr.Row():
                            btn_guardar = gr.Button("Guardar", variant="primary")
                            btn_descargar = gr.DownloadButton("Descargar CSV Actualizado", visible=False, variant="secondary")

                panel_notificacion = gr.Markdown(visible=False)

        input_archivo.change(
            fn=cargar_archivo,
            inputs=[input_archivo],
            outputs=[
                panel_lateral,
                input_archivo,
                df_estado,
                panel_inicial,
                badge_estado,])

        salidas_analisis = [
            df_estado,
            panel_inicial,
            panel_simple,
            titulo_simple,
            tabla_simple,
            panel_tres,
            titulo_1,
            tabla_1,
            titulo_2,
            tabla_2,
            txt_conclusion,
            panel_filtro,
            dropdown_col_filtro,
            input_filtro,
            info_filtro,
            tabla_filtro,
            panel_agrupado,
            dropdown_dim_agrupado,
            tabla_agrupado,
            info_agrupado,
            panel_grafico,
            dropdown_grafico,
            plot_figura,
            info_grafico,
            panel_notificacion,
            panel_ingreso,
            sub_menu_ingreso,
            form_ingreso,
            tabla_cola_vista,
            guardar_vista]

        menu_opciones.change(
            fn=menu,
            inputs=[df_estado, menu_opciones],
            outputs=salidas_analisis)

        menu_opciones.change(
            fn=gestionar_confirmacion,
            inputs=[menu_opciones],
            outputs=[grupo_limpieza, grupo_salida])

        btn_confirmar_limpieza.click(
            fn=confirmar_limpieza,
            inputs=[df_estado],
            outputs=[grupo_limpieza, badge_estado, *salidas_analisis])

        btn_cancelar_limpieza.click(
            fn=cancelar_limpieza,
            outputs=[grupo_limpieza, menu_opciones, panel_notificacion])

        dropdown_col_filtro.change(
            fn=filtrar_datos,
            inputs=[df_estado, dropdown_col_filtro, input_filtro],
            outputs=[tabla_filtro, info_filtro])

        input_filtro.change(
            fn=filtrar_datos,
            inputs=[df_estado, dropdown_col_filtro, input_filtro],
            outputs=[tabla_filtro, info_filtro])

        btn_reset_filtro.click(
            fn=restablecer_filtro,
            inputs=[df_estado],
            outputs=[dropdown_col_filtro, input_filtro, tabla_filtro, info_filtro])

        dropdown_dim_agrupado.change(
            fn=agrupar_datos,
            inputs=[df_estado, dropdown_dim_agrupado],
            outputs=[tabla_agrupado, info_agrupado])

        dropdown_grafico.change(
            fn=generar_grafico,
            inputs=[df_estado, dropdown_grafico],
            outputs=[plot_figura, info_grafico])

        sub_menu_ingreso.change(
            fn=cambiar_subvista_ingreso,
            inputs=[sub_menu_ingreso, cola_estado],
            outputs=[
                form_ingreso,
                tabla_cola_vista,
                guardar_vista,
                tabla_cola,
                tabla_guardar,
                info_cola,
                btn_descargar,
                menu_opciones,
                panel_ingreso,
                panel_inicial,])

        btn_agregar.click(
            fn=agregar_registro_nuevo,
            inputs=[
                df_estado,
                cola_estado,
                in_fecha,
                in_categoria,
                in_producto,
                in_precio,
                in_cantidad,
                in_metodo_pago,
                in_region,
                in_vendedor,
                in_cliente_frecuente],
            outputs=[
                cola_estado,
                tabla_cola,
                info_registro,
                in_producto,
                in_vendedor])

        btn_vaciar_cola.click(
            fn=limpiar_cola_registros,
            outputs=[
                cola_estado,
                tabla_cola,
                tabla_guardar,
                info_cola])

        btn_guardar.click(
            fn=guardar_nuevos_registros,
            inputs=[df_estado, cola_estado],
            outputs=[
                df_estado,
                cola_estado,
                tabla_cola,
                tabla_guardar,
                btn_descargar,
                badge_estado])

        btn_confirmar_salida.click(
            fn=confirmar_salida,
            outputs=[
                input_archivo,
                menu_opciones,
                panel_lateral,
                grupo_limpieza,
                grupo_salida,
                *salidas_analisis[:25],
                badge_estado,
                *salidas_analisis[25:],
                cola_estado])

        btn_cancelar_salida.click(
            fn=cancelar_salida,
            outputs=[grupo_salida, menu_opciones, panel_notificacion])

    return aplicacion


# INICIALIZACION Y EJECUCION DE LA APLICACION

demo = crear_interfaz()

if __name__ == "__main__":
    demo.launch(theme=TEMA_APLICACION, css=CSS_APLICACION)