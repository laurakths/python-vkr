import random
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_URL, MODEL
from theory_data import TASKS_BANK

used_tasks = {}


def call_openrouter(prompt, system_prompt="You are a helpful assistant."):
    if not OPENROUTER_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "PythonCompass"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return None


def mock_generate_task(topic, lang="ru"):
    if topic not in used_tasks:
        used_tasks[topic] = []

    tasks = TASKS_BANK.get(topic, {}).get(lang, [])

    available_tasks = [t for t in tasks if t not in used_tasks[topic]]

    if not available_tasks:
        used_tasks[topic] = []
        available_tasks = tasks

    task = random.choice(available_tasks)
    used_tasks[topic].append(task)

    return task


def mock_check_code(task, code, lang="ru"):
    code_lower = code.lower().strip()

    if "print(" in code_lower or "return" in code_lower:
        if lang == "ru":
            return "✅ Отлично! Задача решена верно."
        else:
            return "✅ Great! Task solved correctly."
    else:
        if lang == "ru":
            return "❌ Используйте print() для вывода."
        else:
            return "❌ Use print() to output."
