# backend/utils/download_hf_models.py
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSequenceClassification
import os

models = {
    "conversational": "microsoft/DialoGPT-small",
    "emotion": "j-hartmann/emotion-english-distilroberta-base",
    "sentiment": "nlptown/bert-base-multilingual-uncased-sentiment"
}

base_dir = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(base_dir, exist_ok=True)

for key, repo in models.items():
    out = os.path.join(base_dir, key)
    os.makedirs(out, exist_ok=True)
    print(f"Downloading {repo} → {out}")
    if key == "conversational":
        tokenizer = AutoTokenizer.from_pretrained(repo)
        model = AutoModelForCausalLM.from_pretrained(repo)
        tokenizer.save_pretrained(out)
        model.save_pretrained(out)
    else:
        # Use pipeline to ensure model files are cached/saved
        p = pipeline("text-classification" if key=="emotion" else "sentiment-analysis", model=repo)
        # Save underlying model/tokenizer
        tokenizer = p.tokenizer
        model = p.model
        tokenizer.save_pretrained(out)
        model.save_pretrained(out)
    print("Saved:", out)
