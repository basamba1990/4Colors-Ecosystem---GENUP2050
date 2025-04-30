import streamlit as st
import tempfile
import time
from supabase_client import supabase, get_rag_context
from rag_utils import generate_coaching_response
from whisper_utils import transcribe_audio
from pitch_analyzer import process_xml, analyze_pitch, generate_variants
from pdf_generator import generate_pdf
from jeu_interface import show_jeu_dashboard
from notifications import check_notifications

# Configuration de la page
st.set_page_config(
    page_title="4Colors Ecosystem - GENUP2050",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialisation de session
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [],
        'profile': None,
        'variants': None,
        'files': {},
        'user': None  # Ajout pour le système JEU
    })

# Sidebar pour l'upload et navigation
with st.sidebar:
    # Menu principal
    menu = st.selectbox(
        "Menu Principal",
        ["🏠 Accueil", "🎤 Optimisation Pitch", "🌱 JEU"],
        index=0
    )
    
    # Vérifier les notifications
    if st.session_state.user:
        check_notifications()

    # Section upload (seulement pour le module Pitch)
    if menu == "🎤 Optimisation Pitch":
        st.header("📤 Téléchargement des fichiers")
        with st.expander("ℹ️ Instructions", expanded=True):
            st.markdown("""
            1. Téléchargez vidéo (MP4) + transcription (XML) + vignette (PNG)
            2. Analyse automatique par IA
            3. Formulaire d'amélioration
            4. Génération du script final
            """)

        uploaded_files = st.file_uploader(
            "Glissez vos fichiers ici",
            type=["mp4", "xml", "png"],
            accept_multiple_files=True,
            help="Formats acceptés : MP4 (vidéo), XML (transcription), PNG (vignette)"
        )

        if uploaded_files:
            try:
                for file in uploaded_files:
                    ext = file.name.split('.')[-1].lower()
                    st.session_state.files[ext] = file

                if 'xml' in st.session_state.files:
                    with st.status("📝 Analyse de la transcription..."):
                        transcription = process_xml(st.session_state.files['xml'])
                else:
                    with st.status("🎤 Transcription audio..."):
                        video_file = st.session_state.files['mp4']
                        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                            tmp_file.write(video_file.getbuffer())
                            transcription = transcribe_audio(tmp_file.name)

                with st.status("🤖 Analyse stratégique..."):
                    analysis = analyze_pitch(transcription)
                    st.session_state.analysis = analysis

                st.success("Prêt pour l'étape suivante !")

            except Exception as e:
                st.error(f"**Erreur de traitement :**\n{str(e)}")

# Interface principale
st.title("🌐 4Colors Ecosystem")
check_notifications()  # Double vérification des notifications

# Navigation selon le menu
if menu == "🌱 JEU":
    show_jeu_dashboard()
elif menu == "🎤 Optimisation Pitch":
    if 'analysis' in st.session_state:
        with st.expander("🔧 Personnalisation avancée", expanded=True):
            form_data = {
                'problem': st.text_area("Problème clé à résoudre", max_chars=200),
                'solution': st.text_area("Solution innovante", max_chars=200),
                'usp': st.text_input("Avantage unique (USP)", max_chars=50),
                'metrics': st.text_input("Chiffres clés (séparés par des virgules)"),
                'tone': st.selectbox("Ton souhaité", ["Convaincant", "Inspirant", "Urgent"])
            }

            if st.button("✨ Générer les variantes"):
                with st.spinner("Création des versions améliorées..."):
                    variants = generate_variants(st.session_state.analysis, form_data)
                    st.session_state.variants = variants

    if st.session_state.variants:
        st.header("📄 Versions optimisées")
        selected = st.radio("Choisissez votre version préférée :", 
                          st.session_state.variants,
                          index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Votre script")
            st.markdown(f"> {selected}")
        
        with col2:
            st.markdown("### Exportation")
            if st.button("📤 Générer PDF"):
                pdf_path = generate_pdf(
                    selected,
                    st.session_state.files.get('png'),
                    st.session_state.analysis
                )
                with open(pdf_path, "rb") as f:
                    st.download_button("Télécharger", f, file_name="pitch_pro.pdf")
else:
    st.write("Bienvenue dans l'écosystème 4Colors !")
