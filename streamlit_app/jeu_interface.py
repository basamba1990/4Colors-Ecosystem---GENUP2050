import streamlit as st
import json
from supabase_client import supabase, update_user_points

def show_jeu_dashboard():
    st.header("🌱 Jardin d'Échange Universel")
    
    # Section Solde et Historique
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Solde JEU", f"{st.session_state.user['jeu_points']} points")
    with col2:
        if st.button("📜 Voir l'historique"):
            show_transaction_history()

    # Liste des offres/demandes
    st.subheader("🔍 Offres & Demandes")
    offers = supabase.table('jeu_offers').select('*').execute().data
    for offer in offers:
        with st.expander(f"{offer['type'].capitalize()} : {offer['title']}"):
            st.markdown(f"**Description** : {offer['description']}")
            st.button("Proposer un échange", key=offer['id'],
                      on_click=initiate_exchange, args=(offer,))

def initiate_exchange(offer):
    st.session_state.current_offer = offer
    st.session_state.show_exchange_form = True

def exchange_form():
    with st.form("Proposition d'échange"):
        st.write(f"Vous proposez un échange avec {st.session_state.current_offer['title']}")
        duration = st.number_input("Durée (minutes)", min_value=15, step=15)
        description = st.text_area("Description de votre proposition")
        
        if st.form_submit_button("Envoyer la proposition"):
            supabase.table('jeu_transactions').insert({
                'from_user': st.session_state.user['id'],
                'to_user': st.session_state.current_offer['user_id'],
                'amount': duration,
                'description': description,
                'status': 'pending'
            }).execute()
            st.success("Proposition envoyée !")

def feedback_system(transaction_id):
    transaction = supabase.table('jeu_transactions').select('*').eq(
        'id', transaction_id).execute().data[0]
    
    with st.form(f"Feedback_{transaction_id}"):
        rating = st.slider("Évaluation (1-5)", 1, 5, 5)
        comment = st.text_area("Commentaire public")
        
        if st.form_submit_button("Soumettre"):
            supabase.table('jeu_transactions').update({
                'feedback': json.dumps({
                    'rating': rating,
                    'comment': comment
                })
            }).eq('id', transaction_id).execute()
            
            current_rating = supabase.table('users').select(
                'jeu_rating').eq('id', transaction['to_user']).execute().data[0]['jeu_rating']
            new_rating = (current_rating + rating) / 2
            supabase.table('users').update({
                'jeu_rating': new_rating
            }).eq('id', transaction['to_user']).execute()

def show_transaction_history():
    transactions = supabase.table('jeu_transactions').select('*').or_(
        f"from_user.eq.{st.session_state.user['id']},to_user.eq.{st.session_state.user['id']}"
    ).execute().data
    
    for t in transactions:
        st.markdown(f"""
        **Transaction {t['created_at'][:10]}**  
        - Statut: {t['status']}  
        - Montant: {t['amount']} points  
        - Description: {t['description']}
        """)
