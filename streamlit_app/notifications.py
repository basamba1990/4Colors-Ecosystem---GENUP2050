import streamlit as st
from supabase_client import supabase

def check_notifications():
    if not st.session_state.user:
        return
    
    notifications = supabase.table('jeu_transactions').select('*').eq(
        'to_user', st.session_state.user['id']
    ).eq('status', 'pending').execute().data
    
    if notifications:
        st.sidebar.markdown(f"🔔 {len(notifications)} notifications")
        for notif in notifications:
            with st.sidebar.expander(f"Nouvelle proposition de {notif['from_user']}"):
                st.write(notif['description'])
                if st.button("Accepter", key=f"accept_{notif['id']}"):
                    handle_transaction_response(notif['id'], 'accepted')
                if st.button("Refuser", key=f"reject_{notif['id']}"):
                    handle_transaction_response(notif['id'], 'rejected')

def handle_transaction_response(transaction_id, response):
    supabase.table('jeu_transactions').update({
        'status': response
    }).eq('id', transaction_id).execute()
    
    if response == 'accepted':
        transaction = supabase.table('jeu_transactions').select('*').eq(
            'id', transaction_id).execute().data[0]
        
        supabase.rpc('update_jeu_points', {
            'user_id': transaction['from_user'],
            'points': -transaction['amount']
        }).execute()
        
        supabase.rpc('update_jeu_points', {
            'user_id': transaction['to_user'],
            'points': transaction['amount']
        }).execute()
