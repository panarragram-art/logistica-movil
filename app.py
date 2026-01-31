import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Logística Inter-Almacenes", layout="wide")

st.title("📦 Sistema de Petición entre Almacenes")

# --- CARGA DE DATOS ---
# En una fase real, aquí subirías tu Excel de catálogo
@st.cache_data
def load_data():
    data = {
        'EAN': ['8401', '8402', '8403', '8404', '8501', '8502'],
        'Referencia': ['POLO-01', 'POLO-01', 'POLO-01', 'POLO-01', 'JEAN-99', 'JEAN-99'],
        'Nombre': ['Polo Piqué', 'Polo Piqué', 'Polo Piqué', 'Polo Piqué', 'Jean Slim', 'Jean Slim'],
        'Talla': ['S', 'M', 'L', 'XL', '32', '34'],
        'Color': ['Azul', 'Azul', 'Azul', 'Azul', 'Negro', 'Negro'],
        'Colección': ['V24', 'V24', 'V24', 'V24', 'ESS', 'ESS']
    }
    return pd.DataFrame(data)

df_catalogo = load_data()

# --- ESTADO DE LA APP ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- SIDEBAR (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("Datos del Pedido")
    ref_pedido = st.text_input("Referencia Pedido", "PED-001")
    alm_origen = st.text_input("Almacén Origen", "ALM-PRINCIPAL")
    alm_destino = st.text_input("Almacén Destino", "TIENDA-SUR")
    
    if st.button("🗑️ Vaciar Carrito"):
        st.session_state.carrito = []
        st.rerun()

# --- CUERPO PRINCIPAL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Selección de Productos")
    ref_busqueda = st.selectbox("Buscar Referencia", df_catalogo['Referencia'].unique())
    
    # Filtrar variantes
    variantes = df_catalogo[df_catalogo['Referencia'] == ref_busqueda]
    
    st.write(f"Variantes para: **{ref_busqueda}**")
    
    cantidades = {}
    for _, row in variantes.iterrows():
        label = f"{row['Talla']} - {row['Color']} (EAN: {row['EAN']})"
        cantidades[row['EAN']] = st.number_input(label, min_value=0, step=1, key=row['EAN'])

    if st.button("➕ Añadir al Pedido"):
        for ean, cant in cantidades.items():
            if cant > 0:
                st.session_state.carrito.append({
                    'EAN': ean,
                    'Origen': alm_origen,
                    'Destino': alm_destino,
                    'Ref_Pedido': ref_pedido,
                    'Cantidad': cant
                })
        st.success("Añadido correctamente")

with col2:
    st.subheader("2. Resumen y Exportación")
    if st.session_state.carrito:
        df_pedido = pd.DataFrame(st.session_state.carrito)
        st.table(df_pedido)
        
        # Generar Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_pedido.to_excel(writer, index=False, sheet_name='Pedido')
        
        st.download_button(
            label="📥 Descargar Excel para ERP",
            data=output.getvalue(),
            file_name=f"{ref_pedido}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("El pedido está vacío.")
      
