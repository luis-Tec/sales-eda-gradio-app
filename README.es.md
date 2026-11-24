<div align="right">
  <a href="README.md">English</a> | <a href="README.es.md"><strong>Español</strong></a>
</div>

# Sistema Interactivo de EDA y Limpieza de Datos de Ventas (Python + Gradio)

Aplicación web modular desarrollada en **Python, Pandas, Matplotlib y Gradio** para automatizar el diagnóstico de calidad de datos, limpieza y estandarización, análisis exploratorio (EDA), detección de valores atípicos y registro validado de nuevas ventas.

---

## Funcionalidades Principales

1. **Diagnóstico de Calidad de Datos**
   - Inspección de tipos de datos, conteo de valores nulos, registros duplicados e identificadores repetidos.
   - Detección de inconsistencias lógicas (cantidades o precios negativos, textos sin estandarizar, fechas inválidas).

2. **Limpieza y Transformación Automatizada**
   - Eliminación de duplicados exactos y resolución de IDs repetidos.
   - Conversión de fechas al estándar internacional **ISO 8601** (`AAAA-MM-DD`).
   - Corrección de valores negativos mediante valor absoluto y normalización de texto.
   - Imputación de nulos numéricos con la mediana y categóricos con `"Desconocido"`.

3. **Análisis Comercial y Visualización (6 Gráficos en Matplotlib)**
   - Estadísticas descriptivas y filtrado dinámico en tiempo real.
   - Agrupaciones por categoría, producto, vendedor, región, método de pago y cliente frecuente.
   - Detección de transacciones atípicas (*outliers*) mediante **Rango Intercuartílico (IQR)**.
   - 6 gráficos analíticos: Ingresos por Categoría, Top 10 Productos, Tendencia Histórica, Métodos de Pago, Facturación por Región y Desempeño por Vendedor.

4. **Ingreso Validado y Exportación a CSV**
   - Formulario interactivo con validaciones (fechas, provincias, métodos de pago, montos) y generación automática de IDs consecutivos.
   - Descarga directa del CSV limpio y actualizado.

---

## Ejecución Local

```bash
git clone https://github.com/luis-Tec/sales-eda-gradio-app.git
cd sales-eda-gradio-app
pip install -r requirements.txt
python app.py
```

Abre el enlace local mostrado en consola (normalmente `http://127.0.0.1:7860`) y carga el archivo de prueba `data/ventas_tienda_tecnologia_ampliado.csv`.
