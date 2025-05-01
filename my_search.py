import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import faiss
import time
import google.api_core.exceptions  # Make sure this is imported
import pickle
import torch
from transformers import AutoTokenizer, AutoModel
from dotenv import load_dotenv
load_dotenv()


import google.generativeai as genai
# ========== SETUP ==========

# Load Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # <-- Replace with your key
model_gemini = genai.GenerativeModel("gemini-1.5-pro-latest")  # Or a more suitable model

# Load embedding model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
embedding_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
# Load FAISS index and chunks
index = faiss.read_index("chunk_index.faiss")
with open("chunk_texts.pkl", "rb") as f:
    chunks = pickle.load(f)

# ========== FUNCTIONS ==========

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = embedding_model(**inputs)
    embeddings = outputs.last_hidden_state
    input_mask_expanded = inputs['attention_mask'].unsqueeze(-1).expand(embeddings.size()).float()
    sum_embeddings = torch.sum(embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return (sum_embeddings / sum_mask).squeeze().numpy()

def query_faiss(query, top_k=2):
    query_vector = get_embedding(query).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    results = [chunks[i] for i in indices[0]]
    return results

import time
import google.api_core.exceptions  # Make sure this is imported

def get_answer_from_gemini(query, context_chunks, max_output_tokens=200, retries=3):
    context = "\n\n".join(context_chunks)
    prompt = f"""You are an assistant with access to the following context:\n\n{context}\n\nUser question: {query}\n\nPlease answer the question based only on the context above."""
    
    global model_gemini

    for attempt in range(retries):
        try:
            response = model_gemini.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_output_tokens
                )
            )
            return response.text

        except google.api_core.exceptions.DeadlineExceeded as e:
            print(f"[Attempt {attempt+1}] DeadlineExceeded: Retrying in 2s...")
            time.sleep(2)
        
        except Exception as e:
            print(f"[Attempt {attempt+1}] Other error: {e}")
            return f"Gemini error: {str(e)}"

    return "Gemini API timed out after multiple attempts. Try a shorter query or fewer context chunks."


def search_and_respond(user_query):
    try:
        top_chunks = query_faiss(user_query)  # ✅ removed max_output_tokens here
        response = get_answer_from_gemini(user_query, top_chunks, max_output_tokens=200)
        return response
    except Exception as e:
        return f"Failed to process query: {str(e)}"


# def search_and_respond(user_query,max_output_tokens=200):
#     try:
#         top_chunks = query_faiss(user_query)
#         response = get_answer_from_gemini(user_query, top_chunks,max_output_tokens=max_output_tokens)
#         return response
#     except Exception as e:
#         return f"Failed to process query: {str(e)}"
