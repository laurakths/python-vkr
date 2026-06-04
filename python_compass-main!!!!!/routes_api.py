import os
import sys
import tempfile
import subprocess
from flask import Blueprint, request, jsonify
from flask_login import login_required
from config import OPENROUTER_API_KEY
from theory_data import THEORY, THEORY_RU, TOPICS_ORDER
from ai_utils import call_openrouter, mock_generate_task, mock_check_code

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/theory')
@login_required
def get_theory():
    lang = request.args.get('lang', 'ru')
    theory = THEORY.get(lang, THEORY_RU)
    topics_list = []
    for topic in TOPICS_ORDER:
        if topic in theory:
            topics_list.append({
                "key": topic,
                "title": theory[topic]["title"],
                "content": theory[topic]["content"]
            })
    return jsonify(topics_list)


@api_bp.route('/api/topics')
@login_required
def get_topics():
    lang = request.args.get('lang', 'ru')
    theory = THEORY.get(lang, THEORY_RU)
    topics = []
    for topic in TOPICS_ORDER:
        if topic in theory:
            topics.append({"key": topic, "title": theory[topic]["title"]})
    return jsonify(topics)


@api_bp.route('/api/generate_task', methods=['POST'])
@login_required
def generate_task():
    data = request.json
    topic = data.get('topic', 'fun')
    lang = data.get('lang', 'ru')

    topic_title = THEORY.get(lang, THEORY_RU).get(topic, {}).get('title', topic)

    if lang == "ru":
        prompt = f"Сгенерируй короткую задачу по Python для темы '{topic_title}'. Верни ТОЛЬКО текст задачи."
    else:
        prompt = f"Generate a short Python task for topic '{topic_title}'. Return ONLY task text."

    result = call_openrouter(prompt, "Ты — преподаватель Python.")

    if not result:
        result = mock_generate_task(topic, lang)

    return jsonify({"task": result})


@api_bp.route('/api/check_code', methods=['POST'])
@login_required
def check_code():
    data = request.json
    task = data.get('task', '')
    code = data.get('code', '')
    lang = data.get('lang', 'ru')

    if lang == "ru":
        prompt = f"Проверь решение. Задача: '{task}'. Код: {code}. Если верно — '✅ Отлично!'. Если ошибка — кратко объясни."
    else:
        prompt = f"Check solution. Task: '{task}'. Code: {code}. If correct — '✅ Great!'. If error — briefly explain."

    result = call_openrouter(prompt, "Ты — учитель Python.")

    if not result:
        result = mock_check_code(task, code, lang)

    return jsonify({"feedback": result})


@api_bp.route('/api/run_code', methods=['POST'])
@login_required
def run_code():
    data = request.json
    code = data.get('code', '')
    input_data = data.get('input_data', '')
    lang = data.get('lang', 'ru')

    if not code.strip():
        return jsonify({"output": "", "error": "No code to execute"})

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            f.flush()
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=10
        )

        os.unlink(tmp_path)

        error = result.stderr
        eof_error = False

        if 'EOFError' in error:
            eof_error = True
            if lang == 'ru':
                error = '⛔ Программа ожидает ввод данных. Пожалуйста, напишите входные данные в поле «Ввод данных».'
            else:
                error = '⛔ The program expects input. Please enter the input data in the "Input" field.'

        return jsonify({
            "output": result.stdout,
            "error": error,
            "eof_error": eof_error
        })

    except subprocess.TimeoutExpired:
        os.unlink(tmp_path)
        return jsonify({"output": "", "error": "Execution timed out (10s limit)"})
    except Exception as e:
        try:
            os.unlink(tmp_path)
        except:
            pass
        return jsonify({"output": "", "error": str(e)})
