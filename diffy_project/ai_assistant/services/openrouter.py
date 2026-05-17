import requests
import json
from django.conf import settings

def call_openrouter_llm(system_prompt: str, user_prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"
    }
    
    payload = {
        "model": "deepseek/deepseek-chat", # было -r1 думает дольше
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=(5, 30))
    response.raise_for_status() # Выкинет ошибку, если статус не 200
    
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        # В идеале здесь логировать ошибку
        raise Exception(f"Ошибка API OpenRouter: {response.text}")