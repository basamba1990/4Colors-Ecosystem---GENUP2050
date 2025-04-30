def analyze_pitch(text):
    # Simple analyse des mots-clés
    keywords = ["marché", "solution", "problème", "client", "revenu", "scalabilité"]
    score = sum(1 for kw in keywords if kw in text.lower())
    feedback = "Bonne couverture des points clés." if score > 3 else "Essayez d'ajouter plus de détails sur votre marché et modèle économique."
    return {
        "score": score * 2,
        "feedback": feedback,
        "details": {kw: (kw in text.lower()) for kw in keywords}
    }
