# Daftar prioritas model (jika satu sibuk, otomatis pakai berikutnya)
CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-flash"
]

def generate_with_fallback(client, contents, system_instruction=None, json_mode=False):
    """Mencoba model cadangan jika server Google sedang 503 atau limit."""
    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            cfg_params = {}
            if system_instruction:
                cfg_params["system_instruction"] = system_instruction
            if json_mode:
                cfg_params["response_mime_type"] = "application/json"
            else:
                cfg_params["temperature"] = 0.7

            config = types.GenerateContentConfig(**cfg_params)
            
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            last_error = e
            # Jika error 503 / 429 / 404, lanjut ke model cadangan berikutnya
            continue
    raise last_error
