# backend/services/chatbot_service.py
import os
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import threading
from typing import Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, Conversation
import torch
from config.settings import settings


class ChatbotService:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.ready = False
        self._loading = False
        self.error: Optional[str] = None
        # device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Defer heavy loading to background
        self.conv_tokenizer = None
        self.conv_model = None
        self.conv_pipe = None
        self.emotion_pipe = None
        self.sentiment_pipe = None

        # runtime state
        self.histories = {}  # type: Dict[str, torch.Tensor]
        self.conversations = {}  # type: Dict[str, Conversation]
        # persona prefix to make chatbot sound "manually-trained"/empathetic
        self.persona = (
            "You are Sathi, a calm, frank, empathetic mental-health assistant. "
            "You speak gently but directly, validate feelings, and ask useful follow-up questions when needed."
        )

    @classmethod
    def get(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = ChatbotService()
        return cls._instance

    def _load_models(self):
        try:
            # conversational model (DialoGPT)
            conv_dir = settings.CHATBOT_MODEL_DIR
            self.conv_tokenizer = AutoTokenizer.from_pretrained(conv_dir, local_files_only=True)
            self.conv_model = AutoModelForCausalLM.from_pretrained(conv_dir, local_files_only=True).to(self.device)
            self.conv_model.eval()

            # conversational pipeline for multi-turn coherence
            self.conv_pipe = pipeline(
                'conversational',
                model=self.conv_model,
                tokenizer=self.conv_tokenizer,
                device=0 if self.device.type == "cuda" else -1,
                framework='pt',
            )

            # emotion classifier
            emo_dir = settings.EMOTION_MODEL_DIR
            self.emotion_pipe = pipeline(
                "text-classification",
                model=emo_dir,
                tokenizer=emo_dir,
                device=0 if self.device.type == "cuda" else -1,
                top_k=None,
                framework="pt",
            )

            # sentiment classifier
            sent_dir = settings.SENTIMENT_MODEL_DIR
            self.sentiment_pipe = pipeline(
                "sentiment-analysis",
                model=sent_dir,
                tokenizer=sent_dir,
                device=0 if self.device.type == "cuda" else -1,
                framework="pt",
            )
            self.ready = True
            self.error = None
        except Exception as e:
            self.error = f"Chatbot model load failed: {e}"
        finally:
            self._loading = False

    def ensure_loading(self):
        if self.ready or self._loading:
            return
        self._loading = True
        threading.Thread(target=self._load_models, daemon=True).start()

    def analyze_emotion(self, text):
        res = self.emotion_pipe(text, top_k=None)
        # pipeline for this model returns list of dicts; pick top
        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return {"label": "neutral", "score": 0.0}

    def analyze_sentiment(self, text):
        res = self.sentiment_pipe(text)
        if isinstance(res, list) and len(res)>0:
            return res[0]
        return {"label": "NEUTRAL", "score": 0.0}

    def generate_reply(self, session_id, user_text, max_new_tokens=150):
        if not self.ready:
            self.ensure_loading()
            return ("The chat service is warming up. Please try again in a few seconds.", False)
        # safety check: suicidal keywords
        lowered = user_text.lower()
        suicidal_triggers = ["suicide", "kill myself", "end my life", "i want to die", "hurt myself"]
        for term in suicidal_triggers:
            if term in lowered:
                return ("I'm really sorry you're feeling that way. "
                        
                        "I’m not able to handle crises. If you're in immediate danger, please call local emergency services now. "
                        "Would you like me to provide some immediate support numbers or connect you to a counselor?"), True

        # Use transformers conversational pipeline with per-session state
        conv = self.conversations.get(session_id)
        if conv is None:
            # Seed first turn; persona is better handled in instruction-tuned models, but include as light priming
            conv = Conversation(user_input=user_text)
            self.conversations[session_id] = conv
        else:
            conv.add_user_input(user_text)

        gen_kwargs = dict(
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.8,
            repetition_penalty=1.15,
            no_repeat_ngram_size=3,
            pad_token_id=self.conv_tokenizer.eos_token_id,
        )
        try:
            self.conv_pipe(conv, **gen_kwargs)
            reply = conv.generated_responses[-1] if conv.generated_responses else ""
        except Exception:
            reply = "I’m here and listening. Could you share a bit more about what you’re experiencing?"
        return reply, False

    def health_status(self):
        # trigger load if not started yet
        if not self.ready and not self._loading and not self.error:
            self.ensure_loading()
        return {"ready": self.ready, "loading": self._loading, "error": self.error}

# create singleton for import
chatbot = ChatbotService.get()
