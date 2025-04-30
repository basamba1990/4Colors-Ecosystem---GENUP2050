from supabase import create_client
from openai import OpenAI
import streamlit as st

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def suggest_profiles(keywords, user_id):
    """Suggère des profils similaires"""
    embedding = openai_client.embeddings.create(
        input=" ".join(keywords),
        model="text-embedding-3-small"
    ).data[0].embedding
    
    results = supabase.rpc('search_profiles', {
        'query_embedding': embedding,
        'similarity_threshold': 0.65,
        'current_user_id': user_id
    }).execute()
    
    return [{
        'id': item['id'],
        'name': item['name'],
        'similarity': item['similarity'],
        'keywords': item['keywords'][:5]
    } for item in results.data]
