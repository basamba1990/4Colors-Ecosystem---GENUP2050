import stripe
import streamlit as st

stripe.api_key = st.secrets["STRIPE_API_KEY"]

def create_payment_link(pitch_id, amount):
    """Crée un lien de paiement Stripe"""
    try:
        product = stripe.Product.create(name=f"Pitch {pitch_id[:6]}")
        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount*100,
            currency="eur"
        )
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price.id, 'quantity': 1}],
            mode='payment',
            success_url=st.secrets["STRIPE_SUCCESS_URL"],
            cancel_url=st.secrets["STRIPE_CANCEL_URL"]
        )
        return session.url
    except Exception as e:
        st.error(f"Erreur de paiement : {str(e)}")
        return None
