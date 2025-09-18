import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO, BytesIO
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import base64
import tempfile
import os

# Configuración de la página
st.set_page_config(
    page_title="Visualizador MSA",
    page_icon="🧬",
    layout="wide"
)

# URL del backend (ajusta según tu configuración)
BACKEND_URL = "http://172.19.0.3:5000"  # Cambia esto por la URL de tu backend

# Esquemas de coloración para aminoácidos
COLOR_SCHEMES = {
    'Clustal': {
        'A': '#80a0f0', 'R': '#f01505', 'N': '#00ff00', 'D': '#c048c0',
        'C': '#f08080', 'Q': '#00ff00', 'E': '#c048c0', 'G': '#f09048',
        'H': '#15a4a4', 'I': '#80a0f0', 'L': '#80a0f0', 'K': '#f01505',
        'M': '#80a0f0', 'F': '#80a0f0', 'P': '#ffff00', 'S': '#00ff00',
        'T': '#00ff00', 'W': '#80a0f0', 'Y': '#15a4a4', 'V': '#80a0f0',
        '-': '#ffffff', 'X': '#ffffff'
    },
    'Hydrophobicity': {
        'A': '#ad0052', 'R': '#0000ff', 'N': '#0c00f3', 'D': '#0c00f3',
        'C': '#c2003d', 'Q': '#0c00f3', 'E': '#0c00f3', 'G': '#6a0095',
        'H': '#1500ea', 'I': '#ff0000', 'L': '#ea0015', 'K': '#0000ff',
        'M': '#b0004f', 'F': '#cb0034', 'P': '#4600b9', 'S': '#5e00a1',
        'T': '#61009e', 'W': '#4f00b0', 'Y': '#1500ea', 'V': '#f60009',
        '-': '#ffffff', 'X': '#ffffff'
    },
    'Chemistry': {
        'A': '#c8c8c8', 'R': '#145aff', 'N': '#00dcdc', 'D': '#e60a0a',
        'C': '#e6e600', 'Q': '#00dcdc', 'E': '#e60a0a', 'G': '#ebebeb',
        'H': '#8282d2', 'I': '#0f820f', 'L': '#0f820f', 'K': '#145aff',
        'M': '#e6e600', 'F': '#3232aa', 'P': '#dc9682', 'S': '#fa9600',
        'T': '#fa9600', 'W': '#b45ab4', 'Y': '#3232aa', 'V': '#0f820f',
        '-': '#ffffff', 'X': '#ffffff'
    }
}

class MSAAnalyzer:
    def __init__(self, sequences):
        self.sequences = sequences
        self.seq_names = list(sequences.keys())
        self.alignment_length = len(list(sequences.values())[0]) if sequences else 0
        
    def parse_fasta_file(self, file_content):
        """Parsea un archivo FASTA con múltiples secuencias"""
        sequences = {}
        current_name = None
        current_seq = []
        
        for line in file_content.strip().split('\n'):
            if line.startswith('>'):
                if current_name:
                    sequences[current_name] = ''.join(current_seq)
                # Extraer nombre más limpio
                current_name = line[1:].split('|')[-1].split('[')[0].strip()
                if not current_name:
                    current_name = line[1:].split()[0]
                current_seq = []
            else:
                current_seq.append(line.strip())
        
        if current_name:
            sequences[current_name] = ''.join(current_seq)
            
        return sequences
    
    def calculate_identity_matrix(self):
        """Calcula matriz de identidad por pares"""
        n_seqs = len(self.sequences)
        identity_matrix = np.zeros((n_seqs, n_seqs))
        
        seq_list = list(self.sequences.values())
        
        for i in range(n_seqs):
            for j in range(n_seqs):
                if i == j:
                    identity_matrix[i][j] = 100.0
                else:
                    seq1, seq2 = seq_list[i], seq_list[j]
                    matches = sum(1 for a, b in zip(seq1, seq2) if a == b and a != '-' and b != '-')
                    valid_positions = sum(1 for a, b in zip(seq1, seq2) if a != '-' or b != '-')
                    identity_matrix[i][j] = (matches / valid_positions * 100) if valid_positions > 0 else 0
        
        return identity_matrix
    
    def find_mutations(self, ref_seq_name=None):
        """Encuentra mutaciones comparando con secuencia de referencia"""
        if not ref_seq_name:
            ref_seq_name = self.seq_names[0]
        
        ref_seq = self.sequences[ref_seq_name]
        mutations = {}
        
        for name, seq in self.sequences.items():
            if name != ref_seq_name:
                seq_mutations = []
                for pos, (ref_aa, seq_aa) in enumerate(zip(ref_seq, seq)):
                    if ref_aa != seq_aa and ref_aa != '-' and seq_aa != '-':
                        seq_mutations.append({
                            'position': pos + 1,
                            'reference': ref_aa,
                            'mutant': seq_aa,
                            'change': f"{ref_aa}{pos+1}{seq_aa}"
                        })
                mutations[name] = seq_mutations
        
        return mutations
    
    def calculate_conservation(self):
        """Calcula el grado de conservación por posición"""
        conservation_scores = []
        
        for pos in range(self.alignment_length):
            column = [seq[pos] for seq in self.sequences.values()]
            # Excluir gaps para el cálculo
            amino_acids = [aa for aa in column if aa != '-']
            
            if amino_acids:
                # Calcular entropía de Shannon (inversa de conservación)
                counter = Counter(amino_acids)
                total = len(amino_acids)
                entropy = -sum((count/total) * np.log2(count/total) for count in counter.values())
                # Convertir a score de conservación (0-1)
                max_entropy = np.log2(min(20, len(set(amino_acids))))
                conservation = 1 - (entropy / max_entropy if max_entropy > 0 else 0)
            else:
                conservation = 0
            
            conservation_scores.append(conservation)
        
        return conservation_scores

def create_msa_visualization(sequences, color_scheme='Clustal', start_pos=0, end_pos=100):
    """Crea visualización del MSA"""
    colors = COLOR_SCHEMES[color_scheme]
    
    fig, ax = plt.subplots(figsize=(max(15, (end_pos-start_pos)*0.15), len(sequences)*0.5))
    
    seq_names = list(sequences.keys())
    y_positions = range(len(seq_names))
    
    # Crear matriz de colores
    for i, (name, seq) in enumerate(sequences.items()):
        subseq = seq[start_pos:end_pos]
        for j, aa in enumerate(subseq):
            color = colors.get(aa.upper(), '#ffffff')
            rect = plt.Rectangle((j, len(seq_names)-i-1), 1, 1, 
                               facecolor=color, edgecolor='black', linewidth=0.1)
            ax.add_patch(rect)
            
            # Añadir texto del aminoácido
            ax.text(j+0.5, len(seq_names)-i-0.5, aa, 
                   ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Configurar ejes
    ax.set_xlim(0, end_pos-start_pos)
    ax.set_ylim(0, len(seq_names))
    ax.set_yticks([i+0.5 for i in range(len(seq_names))])
    ax.set_yticklabels(reversed(seq_names))
    ax.set_xlabel('Posición en el alineamiento')
    ax.set_title(f'Alineamiento Múltiple de Secuencias ({color_scheme})')
    
    # Añadir números de posición
    step = max(1, (end_pos-start_pos)//20)
    ax.set_xticks(range(0, end_pos-start_pos, step))
    ax.set_xticklabels(range(start_pos, end_pos, step))
    
    plt.tight_layout()
    return fig

def send_to_backend(uploaded_file):
    """Envía archivo al backend para alineamiento"""
    try:
        files = {"file": uploaded_file}
        response = requests.post(f"{BACKEND_URL}/align", files=files, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error del servidor: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def decode_fasta_content(data):
    """Retorna directamente el contenido FASTA en texto plano"""
    return data


def render_analysis_tab(sequences, tab_name, color_scheme):
    """Renderiza una pestaña de análisis completo"""
    analyzer = MSAAnalyzer(sequences)
    
    if not sequences:
        st.error("No se pudieron procesar las secuencias.")
        return
    
    st.subheader(f"📊 Análisis - {tab_name}")
    
    # Información general
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Número de secuencias", len(sequences))
    with col2:
        st.metric("Longitud del alineamiento", analyzer.alignment_length)
    with col3:
        avg_length = np.mean([len(seq.replace('-', '')) for seq in sequences.values()])
        st.metric("Longitud promedio (sin gaps)", f"{avg_length:.0f}")
    
    # Lista de secuencias
    st.write("🔍 **Secuencias en el alineamiento:**")
    for i, name in enumerate(sequences.keys(), 1):
        st.write(f"{i}. {name}")
    
    # VISUALIZACIÓN MSA
    st.subheader("🎨 Visualización del Alineamiento")
    
    # Controles de rango
    col1, col2 = st.columns(2)
    with col1:
        start_pos = st.number_input(f"Posición inicial ({tab_name}):", 
                                  min_value=0, 
                                  max_value=analyzer.alignment_length-1, 
                                  value=0,
                                  key=f"start_{tab_name}")
    with col2:
        end_pos = st.number_input(f"Posición final ({tab_name}):", 
                                min_value=start_pos+1, 
                                max_value=analyzer.alignment_length, 
                                value=min(100, analyzer.alignment_length),
                                key=f"end_{tab_name}")
    
    # Crear y mostrar visualización
    msa_fig = create_msa_visualization(sequences, color_scheme, start_pos, end_pos)
    st.pyplot(msa_fig)
    
    # MATRIZ DE IDENTIDAD
    st.subheader("🔢 Análisis de Identidad por Pares")
    
    identity_matrix = analyzer.calculate_identity_matrix()
    
    # Crear heatmap con plotly
    fig_identity = go.Figure(data=go.Heatmap(
        z=identity_matrix,
        x=analyzer.seq_names,
        y=analyzer.seq_names,
        colorscale='RdYlBu_r',
        text=np.round(identity_matrix, 1),
        texttemplate="%{text}%",
        textfont={"size": 10},
        colorbar=dict(title="Identidad (%)")
    ))
    
    fig_identity.update_layout(
        title="Matriz de Identidad por Pares",
        xaxis_title="Secuencias",
        yaxis_title="Secuencias",
        width=700,
        height=600
    )
    
    st.plotly_chart(fig_identity, use_container_width=True)
    
    # ANÁLISIS DE MUTACIONES
    st.subheader("🧬 Análisis de Mutaciones")
    
    # Seleccionar secuencia de referencia
    ref_seq = st.selectbox(f"Selecciona secuencia de referencia ({tab_name}):", 
                          analyzer.seq_names,
                          key=f"ref_{tab_name}")
    
    mutations = analyzer.find_mutations(ref_seq)
    
    if mutations:
        # Resumen de mutaciones
        total_mutations = sum(len(muts) for muts in mutations.values())
        st.write(f"**Total de mutaciones encontradas:** {total_mutations}")
        
        # Mostrar mutaciones por secuencia
        for seq_name, seq_mutations in mutations.items():
            if seq_mutations:
                st.write(f"**Mutaciones en {seq_name}:**")
                mut_df = pd.DataFrame(seq_mutations)
                st.dataframe(mut_df)
    
    # ANÁLISIS DE CONSERVACIÓN
    st.subheader("📈 Análisis de Conservación")
    
    conservation_scores = analyzer.calculate_conservation()
    
    # Gráfico de conservación
    fig_cons = px.line(x=range(1, len(conservation_scores)+1), 
                     y=conservation_scores,
                     title=f"Grado de Conservación por Posición - {tab_name}")
    fig_cons.update_xaxes(title="Posición")
    fig_cons.update_yaxes(title="Score de Conservación (0-1)")
    fig_cons.add_hline(y=0.8, line_dash="dash", line_color="red", 
                     annotation_text="Altamente conservado (>0.8)")
    st.plotly_chart(fig_cons, use_container_width=True)
    
    # Estadísticas de conservación
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Conservación promedio", f"{np.mean(conservation_scores):.3f}")
    with col2:
        highly_conserved = sum(1 for score in conservation_scores if score > 0.8)
        st.metric("Posiciones altamente conservadas", f"{highly_conserved}")
    with col3:
        variable_positions = sum(1 for score in conservation_scores if score < 0.5)
        st.metric("Posiciones variables", f"{variable_positions}")

# INTERFAZ PRINCIPAL
st.title("🧬 Visualizador MSA - Alineamiento Múltiple de Secuencias")
st.markdown("**Sube secuencias sin alinear y obtén análisis completo de ambos algoritmos**")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Configuraciones")
color_scheme = st.sidebar.selectbox("Esquema de colores:", list(COLOR_SCHEMES.keys()))

# Configuración del backend
st.sidebar.subheader("🔗 Configuración Backend")
backend_url = st.sidebar.text_input("URL del Backend:", value=BACKEND_URL)
BACKEND_URL = backend_url

# Carga de archivo
st.header("📁 Cargar Archivo FASTA (Sin Alinear)")
st.info("💡 Sube un archivo FASTA con secuencias sin alinear. El sistema las procesará automáticamente.")

uploaded_file = st.file_uploader(
    "Sube tu archivo FASTA:", 
    type=['fasta', 'fa', 'txt'],
    help="Archivo FASTA con múltiples secuencias SIN alinear"
)

# Mostrar historial de alineamientos
st.header("📜 Historial de Alineamientos")

try:
    history_response = requests.get(f"{BACKEND_URL}/alignments")
    if history_response.status_code == 200:
        alignments = history_response.json()
        if alignments:
            for aln in alignments:
                st.write(f"📂 {aln['filename']} - ⏰ {aln['created_at']}")

                if st.button(f"🔍 Ver {aln['filename']}", key=f"view_{aln['id']}"):
                    # cargar alineamiento específico
                    detail = requests.get(f"{BACKEND_URL}/alignment/{aln['id']}")
                    if detail.status_code == 200:
                        data = detail.json()
                        st.session_state['muscle_content'] = data['muscle_content']
                        st.session_state['msa_content'] = data['msa_content']
                        analyzer = MSAAnalyzer({})
                        st.session_state['muscle_sequences'] = analyzer.parse_fasta_file(data['muscle_content'])
                        st.session_state['msa_sequences'] = analyzer.parse_fasta_file(data['msa_content'])
                        st.session_state['alignments_ready'] = True
                        st.success(f"✅ Alineamiento {aln['filename']} cargado desde historial")
        else:
            st.info("No hay alineamientos guardados todavía.")
    else:
        st.warning("⚠️ No se pudo obtener el historial")
except Exception as e:
    st.error(f"Error al consultar historial: {str(e)}")

if uploaded_file is not None:
    # Mostrar información del archivo
    st.success(f"✅ Archivo cargado: {uploaded_file.name}")
    
    # Botón para procesar
    if st.button("🚀 Procesar Alineamiento", type="primary"):
        with st.spinner("Enviando archivo al servidor para alineamiento..."):
            # Resetear el puntero del archivo
            uploaded_file.seek(0)
            
            # Enviar al backend
            result = send_to_backend(uploaded_file)
            
            if result:
                st.success("✅ Alineamiento completado exitosamente!")
                            
                # Usar directamente el texto
                muscle_content = decode_fasta_content(result["aligned_muscle.fasta"])
                msa_content = decode_fasta_content(result["aligned_msa.fasta"])

                            
                if muscle_content and msa_content:
                    # Parsear ambos alineamientos
                    analyzer = MSAAnalyzer({})
                    muscle_sequences = analyzer.parse_fasta_file(muscle_content)
                    msa_sequences = analyzer.parse_fasta_file(msa_content)
                                
                    # Guardar en session state para persistencia
                    st.session_state['muscle_sequences'] = muscle_sequences
                    st.session_state['msa_sequences'] = msa_sequences
                    st.session_state['muscle_content'] = muscle_content
                    st.session_state['msa_content'] = msa_content
                    st.session_state['alignments_ready'] = True

                    # Guardar en la base de datos a través del backend
                    save_payload = {
                        "filename": uploaded_file.name,
                        "muscle_content": st.session_state['muscle_content'],
                        "msa_content": st.session_state['msa_content']
                    }
                    save_response = requests.post(f"{BACKEND_URL}/save", json=save_payload)

                    if save_response.status_code == 200:
                        st.success("🗄️ Alineamiento guardado en la base de datos!")
                    else:
                        st.warning("⚠️ No se pudo guardar el alineamiento en la base de datos")

# Mostrar resultados si están disponibles
if st.session_state.get('alignments_ready', False):
    st.header("📊 Resultados del Alineamiento")
    
    # Botones de descarga
    st.subheader("💾 Descargar Alineamientos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Descargar MUSCLE (.fasta)",
            data=st.session_state['muscle_content'],
            file_name="alignment_muscle.fasta",
            mime="text/plain"
        )
    
    with col2:
        st.download_button(
            label="📥 Descargar MSA (.fasta)",
            data=st.session_state['msa_content'],
            file_name="alignment_msa.fasta",
            mime="text/plain"
        )
    
    # Pestañas para análisis
    tab1, tab2 = st.tabs(["🔬 MUSCLE", "🧬 MSA"])
    
    with tab1:
        render_analysis_tab(st.session_state['muscle_sequences'], "MUSCLE", color_scheme)
    
    with tab2:
        render_analysis_tab(st.session_state['msa_sequences'], "MSA", color_scheme)

else:
    st.info("👆 Sube un archivo FASTA con secuencias sin alinear para comenzar el análisis.")

# Footer
st.markdown("---")
st.markdown("🧬 **Visualizador MSA** - Análisis completo de alineamientos múltiples de secuencias con backend integrado")