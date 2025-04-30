import openai

def retrieve_and_generate_response(prompt, vector_store, top_k=3):
    # Cette fonction simule un appel RAG avec OpenAI et une base vectorielle
    docs = vector_store.similarity_search(prompt, k=top_k)
    context = "\n".join([doc.page_content for doc in docs])
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Vous êtes un assistant utile pour les entrepreneurs."},
            {"role": "user", "content": f"{context}\n\nQuestion: {prompt}"}
        ]
    )
    return response.choices[0].message["content"]
