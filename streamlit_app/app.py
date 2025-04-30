import streamlit as st
import tempfile
from streamlit_tags import st_tags
from supabase_client import supabase, get_rag_context, suggest_profiles
from rag_utils import generate_coaching_response
from whisper_utils import transcribe_audio
from pitch_analyzer import process_xml, analyze_pitch, generate_variants
from pdf_generator import generate_pdf
from jeu_interface import show_jeu_dashboard
from notifications import check_notifications
from payment import create_payment_link

# Configuration de la page
st.set_page_config(
    page_title="4Colors Pro - GENUP2050",
    page_icon="🚀",
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
        'user': {'id': 'test_user'},  # Simulation utilisateur
        'analysis': None
    })

# Sidebar
with st.sidebar:
    menu = st.selectbox("Menu", ["🏠 Accueil", "🎤 Pitch", "🌱 JEU", "💳 Paiements"])
    check_notifications()

# Page principale
if menu == "🌱 JEU":
    show_jeu_dashboard()
elif menu == "🎤 Pitch":
    st.title("🚀 Optimisation de Pitch")
    
    # Upload de fichiers
    uploaded_files = st.file_uploader("Télécharger fichiers", type=["mp4", "xml", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        try:
            for file in uploaded_files:
                ext = file.name.split('.')[-1].lower()
                st.session_state.files[ext] = file
            
            # Traitement XML/Transcription
            if 'xml' in st.session_state.files:
                with st.status("Analyse XML..."):
                    transcription = process_xml(st.session_state.files['xml'])
            else:
                with st.status("Transcription audio..."):
                    with tempfile.NamedTemporaryFile() as tmp_file:
                        tmp_file.write(st.session_state.files['mp4'].getbuffer())
                        transcription = transcribe_audio(tmp_file.name)
            
            # Analyse du pitch
            with st.status("Analyse IA..."):
                analysis = analyze_pitch(transcription)
                st.session_state.analysis = analysis
                st.session_state.analysis['id'] = "pitch_" + str(hash(transcription))  # ID unique

            # Section mots-clés
            with st.expander("🔑 Mots-clés générés", expanded=True):
                keywords = st.session_state.analysis.get('keywords', [])
                edited_keywords = st_tags(
                    label="Affiner les mots-clés:",
                    value=keywords,
                    suggestions=suggest_additional_keywords(keywords),
                    maxtags=15
                )
                st.session_state.analysis['keywords'] = edited_keywords

            # Suggestions de profils
            st.subheader("👥 Profils similaires")
            if st.session_state.analysis['keywords']:
                profiles = suggest_profiles(st.session_state.analysis['keywords'], st.session_state.user['id'])
                for p in profiles:
                    with st.container(border=True):
                        st.markdown(f"**{p['name']}** (Similarité: {p['similarity']*100:.1f}%)")
                        st.caption(f"Mots-clés : {', '.join(p['keywords'])}")
            
            # Génération de variantes
            with st.expander("🔧 Personnalisation"):
                form_data = {
                    'problem': st.text_area("Problème clé"),
                    'solution': st.text_area("Solution"),
                    'usp': st.text_input("USP"),
                    'metrics': st.text_input("Métriques"),
                    'tone': st.selectbox("Ton", ["Convaincant", "Inspirant", "Urgent"])
                }
                if st.button("Générer"):
                    st.session_state.variants = generate_variants(st.session_state.analysis, form_data)

            # Résultats et monétisation
            if st.session_state.variants:
                selected = st.radio("Choisir une version", st.session_state.variants)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Script**\n\n{selected}")
                with col2:
                    if st.button("📤 Générer PDF"):
                        pdf_path = generate_pdf(selected, st.session_state.files.get('png'), st.session_state.analysis)
                        with open(pdf_path, "rb") as f:
                            st.download_button("Télécharger", f, file_name="pitch.pdf")
                    if st.button("💰 Monétiser (5€)"):
                        payment_link = create_payment_link(st.session_state.analysis['id'], 5)
                        st.markdown(f"[Lien de paiement]({payment_link})")

        except Exception as e:
            st.error(f"Erreur : {str(e)}")
elif menu == "💳 Paiements":
    st.title("💳 Gestion des Paiements")
    # ... (interface de gestion des paiements)

def suggest_additional_keywords(keywords):
    """Génère des suggestions de mots-clés supplémentaires"""
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"Suggère 20 mots-clés liés à : {', '.join(keywords)}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return [k.strip() for k in response.choices[0].message.content.split(",")]
