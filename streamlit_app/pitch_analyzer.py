from openai import OpenAI
import xml.etree.ElementTree as ET
import json
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def process_xml(xml_file):
    """Extrait le texte d'un fichier XML"""
    try:
        tree = ET.parse(xml_file)
        return ' '.join([elem.text for elem in tree.iter() if elem.text])
    except Exception as e:
        st.error(f"Erreur XML : {str(e)}")
        raise

def analyze_pitch(content):
    """Analyse complète avec extraction de mots-clés"""
    prompt = f"""
    Analyse ce pitch selon :
    1. Structure logique
    2. Arguments clés
    3. Score/10
    4. 10 mots-clés (format JSON array)
    
    CONTENU : {content[:3000]}
    FORMAT JSON : {{"structure": "...", "score": ..., "keywords": [...]}}
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    analysis = json.loads(response.choices[0].message.content)
    analysis['keywords'] = list(set([k.lower().strip() for k in analysis.get('keywords', [])]))
    return analysis

def generate_variants(analysis, form_data):
    """Génère des variantes de script"""
    prompt = f"""
    Crée 3 variantes de pitch avec :
    - Ton : {form_data['tone']}
    - Métriques : {form_data['metrics']}
    - USP : {form_data['usp']}
    
    CONTEXTE : {analysis}
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return [choice.message.content for choice in response.choices]
