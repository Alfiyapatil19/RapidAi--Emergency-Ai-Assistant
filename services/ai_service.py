"""
RapidAid - AI Service
Uses Hugging Face Hub Inference API
"""

import os
import json
import time
import logging
import base64
import re
from io import BytesIO

logger = logging.getLogger(__name__)

HF_TOKEN = os.environ.get("HF_TOKEN", "")

LANG_NAMES = {"en": "English", "hi": "Hindi", "mr": "Marathi"}

EMERGENCY_NAMES = {
    "burns":    "Burns (thermal/chemical)",
    "bleeding": "Severe Bleeding / Open Wound",
    "fracture": "Bone Fracture",
    "choking":  "Choking / Airway Obstruction",
    "heart":    "Heart Attack / Cardiac Arrest",
    "drowning": "Drowning / Near-Drowning",
}


# ============================================================
# IMAGE GENERATION helper
# ============================================================
def _generate_firstaid_image(emergency: str) -> str:
    """Generate a clean illustration for an emergency."""
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=HF_TOKEN)
        
        prompt = f"A highly realistic, professional, full-color medical photograph demonstrating clearly: {emergency}. Educational, instructional, high resolution, realistic lighting, safe for work."
        
        # Use FLUX for fast generation
        image = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
        
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        logger.error(f"Image gen failed: {e}")
        return ""

# ============================================================
# FIRST AID GUIDE (STRUCTURED JSON)
# ============================================================
def get_ai_firstaid(emergency: str, lang: str = "en", context: str = "") -> dict:
    if not HF_TOKEN:
        return {
            "success": False,
            "source":  "no_key",
            "message": "HF_TOKEN not configured.",
            "steps": [], "warning": ""
        }

    lang_name = LANG_NAMES.get(lang, "English")
    emer_name = EMERGENCY_NAMES.get(emergency, emergency.title())
    ctx_part  = f"\nAdditional context: {context}" if context else ""

    prompt = f"""You are an expert emergency first aid instructor.

A person urgently needs first aid guidance for: {emer_name}.{ctx_part}

Respond ONLY in {lang_name}.
Respond ONLY in JSON format (no extra text, no markdown backticks):

{{
  "title": "Short title",
  "steps": [
    {{"title": "Step 1", "detail": "Instruction"}},
    {{"title": "Step 2", "detail": "Instruction"}},
    {{"title": "Step 3", "detail": "Instruction"}}
  ],
  "warning": "Critical warning message"
}}
"""

    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=HF_TOKEN)

        models_to_try = [
            "Qwen/Qwen2.5-72B-Instruct",
            "meta-llama/Llama-3.2-3B-Instruct"
        ]

        for model_name in models_to_try:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model_name,
                    max_tokens=600
                )

                raw = chat_completion.choices[0].message.content.strip()
                # Remove markdown formatting if the model outputs it
                if raw.startswith("```json"):
                    raw = raw[7:]
                if raw.startswith("```"):
                    raw = raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()

                data = json.loads(raw)
                
                # Generate contextual image alongside steps
                image_b64 = _generate_firstaid_image(emer_name)

                return {
                    "success": True,
                    "source":  "hf_ai",
                    "title":   data.get("title", emer_name + " First Aid"),
                    "steps":   data.get("steps", []),
                    "warning": data.get("warning", "Call 108 immediately."),
                    "model":   model_name,
                    "lang":    lang,
                    "image_base64": image_b64
                }

            except Exception as model_err:
                err_str = str(model_err)
                logger.warning(f"{model_name} failed → {err_str[:100]}")

                if "429" in err_str or "Rate limit" in err_str:
                    time.sleep(2)
                    continue
                continue

        return {
            "success": False,
            "source": "api_error",
            "message": "All models failed or busy. Try again later.",
            "steps": [],
            "warning": ""
        }

    except Exception as e:
        logger.error(f"Hugging Face AI error: {e}")
        return {
            "success": False,
            "source": "api_error",
            "message": str(e),
            "steps": [],
            "warning": ""
        }


# ============================================================
# CHATBOT (FIXED CONTEXT ISSUE ✅)
# ============================================================
def get_ai_chat_response(user_message: str, emergency_context: str = "", lang: str = "en") -> dict:
    if not HF_TOKEN:
        return {
            "success": False,
            "message": "AI not configured.",
            "response": ""
        }

    lang_name = LANG_NAMES.get(lang, "English")

    ctx_part = ""
    if emergency_context and emergency_context.lower() in user_message.lower():
        ctx_part = f"The user is dealing with: {emergency_context}."

    prompt = f"""You are a calm expert first aid assistant.

{ctx_part}

IMPORTANT:
- If user asks about a NEW emergency, ignore previous context
- Answer only based on user question
- IF the user asks you to generate, show, or draw an image/picture, YOU MUST include this exact tag anywhere in your response: [GENERATE_IMAGE: <short description>]

Answer in {lang_name}.
Be short (2-4 sentences), clear, and medically helpful.
Always suggest calling 108/112 for serious conditions.

User: {user_message}
"""

    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=HF_TOKEN)

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="Qwen/Qwen2.5-72B-Instruct",
            max_tokens=300
        )

        response_text = chat_completion.choices[0].message.content.strip()

        image_base64 = ""
        # Check for image tag
        match = re.search(r'\[GENERATE_IMAGE:\s*(.*?)\]', response_text)
        if match:
            img_desc = match.group(1).strip()
            response_text = response_text.replace(match.group(0), "").strip()
            image_base64 = _generate_firstaid_image(img_desc)

        return {
            "success": True,
            "response": response_text,
            "image_base64": image_base64
        }

    except Exception as e:
        logger.error(f"Hugging Face Chat Error: {e}")
        return {
            "success": False,
            "message": str(e),
            "response": ""
        }