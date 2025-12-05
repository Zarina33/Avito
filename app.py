import os
import io
import torch
import logging
from datetime import datetime
import time

# ⚡ ВАЖНО: Устанавливаем использование только GPU 1 (NVIDIA H200)
# Это должно быть ДО импорта других библиотек, использующих CUDA
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

from flask import Flask, request, render_template_string
from PIL import Image
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoModelForImageTextToText
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

# Пути к локальным моделям и процессорам / токенизаторам
vibe_model_dir = "/mnt/data/avito/vibe/models"
vibe_tokenizer_dir = "/mnt/data/avito/vibe/tokenizers"

vision_snapshot_dir = "/mnt/data/avito/vision/models/models--AvitoTech--avision/snapshots/def8375a2aa67643348ffd93143691410576663f"

logging.info("="*70)
logging.info("🚀 Запуск Avito AI Demo")
logging.info("="*70)
logging.info(f"🎯 Используем GPU: {torch.cuda.get_device_name(0)}")
logging.info(f"💾 Доступная память GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# Загрузка Avibe (текстовая модель) с оптимизациями
logging.info("📥 Загрузка Avibe (текстовая модель)...")
start_time = time.time()
tokenizer_avibe = AutoTokenizer.from_pretrained(
    "AvitoTech/avibe",
    cache_dir=vibe_tokenizer_dir,
    local_files_only=True
)
model_avibe = AutoModelForCausalLM.from_pretrained(
    "AvitoTech/avibe",
    cache_dir=vibe_model_dir,
    torch_dtype=torch.float16,  # Явно используем float16 для ускорения
    device_map="cuda:0",  # Используем единственную доступную GPU (H200)
    local_files_only=True,
    low_cpu_mem_usage=True,
)
logging.info(f"✅ Avibe загружен за {time.time() - start_time:.2f} сек")

# Загрузка Avision (мультимодальный процессор + модель) с оптимизациями
logging.info("📥 Загрузка Avision (мультимодальная модель)...")
start_time = time.time()
processor_avision = AutoProcessor.from_pretrained(
    vision_snapshot_dir,
    local_files_only=True
)
model_avision = AutoModelForImageTextToText.from_pretrained(
    vision_snapshot_dir,
    torch_dtype=torch.float16,  # Явно используем float16 для ускорения
    device_map="cuda:0",  # Используем единственную доступную GPU (H200)
    local_files_only=True,
    low_cpu_mem_usage=True,
)
logging.info(f"✅ Avision загружен за {time.time() - start_time:.2f} сек")
logging.info("="*70)
logging.info("🎉 Все модели загружены! Сервер готов к работе")
logging.info("="*70)

HTML = """
<!doctype html>
<html>
<head>
  <title>Avibe + Avision | AI Demo</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 40px 20px;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    h1 {
      text-align: center;
      color: white;
      font-size: 2.5em;
      margin-bottom: 50px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .cards-wrapper {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
      gap: 30px;
      margin-bottom: 40px;
    }
    
    .card {
      background: white;
      border-radius: 20px;
      padding: 35px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0 15px 50px rgba(0,0,0,0.3);
    }
    
    .card h2 {
      color: #667eea;
      font-size: 1.8em;
      margin-bottom: 25px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .card h2 .emoji {
      font-size: 1.2em;
    }
    
    textarea, input[type=text] {
      width: 100%;
      padding: 15px;
      border: 2px solid #e0e0e0;
      border-radius: 10px;
      font-size: 16px;
      font-family: inherit;
      transition: border-color 0.3s ease;
      resize: vertical;
    }
    
    textarea:focus, input[type=text]:focus {
      outline: none;
      border-color: #667eea;
    }
    
    input[type=file] {
      width: 100%;
      padding: 15px;
      border: 2px dashed #e0e0e0;
      border-radius: 10px;
      font-size: 16px;
      cursor: pointer;
      transition: border-color 0.3s ease, background-color 0.3s ease;
    }
    
    input[type=file]:hover {
      border-color: #667eea;
      background-color: #f8f9ff;
    }
    
    button {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      padding: 15px 40px;
      border-radius: 25px;
      font-size: 18px;
      font-weight: bold;
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      margin-top: 20px;
      width: 100%;
    }
    
    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    button:active {
      transform: translateY(0);
    }
    
    .result-card {
      background: white;
      border-radius: 20px;
      padding: 35px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
      animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .result-card h2 {
      color: #764ba2;
      font-size: 1.8em;
      margin-bottom: 20px;
    }
    
    .result-card pre {
      background: #f8f9ff;
      padding: 20px;
      border-radius: 10px;
      border-left: 4px solid #667eea;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: 'Courier New', monospace;
      line-height: 1.6;
      color: #333;
      margin-bottom: 20px;
    }
    
    .result-card img {
      max-width: 100%;
      border-radius: 15px;
      box-shadow: 0 5px 20px rgba(0,0,0,0.15);
      margin-top: 20px;
    }
    
    .form-group {
      margin-bottom: 20px;
    }
    
    .form-label {
      display: block;
      margin-bottom: 8px;
      color: #555;
      font-weight: 600;
      font-size: 14px;
    }
    
    /* Metrics panel styles */
    .metrics-panel {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 25px;
      padding: 20px;
      background: linear-gradient(135deg, #f8f9ff 0%, #e8ebff 100%);
      border-radius: 12px;
      border: 2px solid #667eea;
    }
    
    .metric-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .metric-icon {
      font-size: 2em;
      line-height: 1;
    }
    
    .metric-content {
      flex: 1;
    }
    
    .metric-label {
      font-size: 0.85em;
      color: #666;
      font-weight: 600;
      margin-bottom: 4px;
    }
    
    .metric-value {
      font-size: 1.2em;
      color: #667eea;
      font-weight: bold;
    }
    
    @media (max-width: 768px) {
      h1 {
        font-size: 2em;
      }
      
      .cards-wrapper {
        grid-template-columns: 1fr;
      }
      
      .card {
        padding: 25px;
      }
      
      .metrics-panel {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        padding: 15px;
        gap: 10px;
      }
      
      .metric-item {
        padding: 10px;
        flex-direction: column;
        text-align: center;
      }
      
      .metric-icon {
        font-size: 1.5em;
      }
      
      .metric-value {
        font-size: 1em;
      }
    }
    
    /* Loader styles */
    .loader-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.7);
      z-index: 9999;
      justify-content: center;
      align-items: center;
      backdrop-filter: blur(5px);
    }
    
    .loader-overlay.active {
      display: flex;
    }
    
    .loader-content {
      text-align: center;
    }
    
    .spinner {
      width: 80px;
      height: 80px;
      border: 8px solid rgba(255, 255, 255, 0.3);
      border-top: 8px solid #ffffff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .loader-text {
      color: white;
      font-size: 1.3em;
      font-weight: 600;
      animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    
    .loader-subtext {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.9em;
      margin-top: 10px;
    }
  </style>
  <script>
    function showLoader(message) {
      const loader = document.getElementById('loader');
      const loaderText = document.getElementById('loader-text');
      loaderText.textContent = message;
      loader.classList.add('active');
    }
    
    function hideLoader() {
      const loader = document.getElementById('loader');
      loader.classList.remove('active');
    }
    
    // Скрыть loader при загрузке страницы (если вернулись с результатом)
    window.addEventListener('load', function() {
      hideLoader();
    });
  </script>
</head>
<body>
  <!-- Loader overlay -->
  <div id="loader" class="loader-overlay">
    <div class="loader-content">
      <div class="spinner"></div>
      <div id="loader-text" class="loader-text">Обработка запроса...</div>
      <div class="loader-subtext">Пожалуйста, подождите</div>
    </div>
  </div>

  <div class="container">
    <h1>🤖 Avibe & Avision Demo</h1>
    
    <div class="cards-wrapper">
      <div class="card">
        <h2><span class="emoji">🗣</span> Avibe (текстовый чат)</h2>
        <form method="post" action="/avibe" onsubmit="showLoader('🤖 Генерация ответа...')">
          <div class="form-group">
            <label class="form-label">Введите ваш вопрос:</label>
            <textarea name="prompt" rows="5" placeholder="Привет, подскажи рецепт борща">Привет, подскажи рецепт борща</textarea>
          </div>
          <button type="submit">✨ Отправить</button>
        </form>
      </div>
      
      <div class="card">
        <h2><span class="emoji">🖼</span> Avision (анализ изображений)</h2>
        <form method="post" action="/avision" enctype="multipart/form-data" onsubmit="showLoader('🔍 Анализ изображения...')">
          <div class="form-group">
            <label class="form-label">Выберите изображение:</label>
            <input type="file" name="image" accept="image/*">
          </div>
          <div class="form-group">
            <label class="form-label">Вопрос об изображении:</label>
            <input type="text" name="prompt2" value="Опиши изображение подробно и скажи, что здесь можно продать" placeholder="Что вы хотите узнать об изображении?">
          </div>
          <button type="submit">🔍 Анализировать</button>
        </form>
      </div>
    </div>

    {% if result %}
      <div class="result-card">
        <h2>📋 Результат:</h2>
        
        {% if metrics %}
        <div class="metrics-panel">
          <div class="metric-item">
            <span class="metric-icon">⚡</span>
            <div class="metric-content">
              <div class="metric-label">Скорость генерации</div>
              <div class="metric-value">{{ metrics.tokens_per_sec }} токенов/сек</div>
            </div>
          </div>
          <div class="metric-item">
            <span class="metric-icon">🕐</span>
            <div class="metric-content">
              <div class="metric-label">Время генерации</div>
              <div class="metric-value">{{ metrics.gen_time }} сек</div>
            </div>
          </div>
          <div class="metric-item">
            <span class="metric-icon">📊</span>
            <div class="metric-content">
              <div class="metric-label">Сгенерировано токенов</div>
              <div class="metric-value">{{ metrics.generated_tokens }}</div>
            </div>
          </div>
          <div class="metric-item">
            <span class="metric-icon">⏱</span>
            <div class="metric-content">
              <div class="metric-label">Общее время</div>
              <div class="metric-value">{{ metrics.total_time }} сек</div>
            </div>
          </div>
        </div>
        {% endif %}
        
        <pre>{{ result }}</pre>
        {% if image_data %}
          <img src="data:image/png;base64,{{ image_data }}" alt="Uploaded image" />
        {% endif %}
      </div>
    {% endif %}
  </div>
</body>
</html>
"""

from base64 import b64encode

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/avibe", methods=["POST"])
def route_avibe():
    start_time = time.time()
    prompt = request.form.get("prompt", "")
    
    logging.info("┌" + "─"*68 + "┐")
    logging.info("│ 🗣  AVIBE REQUEST (текстовый чат)                                 │")
    logging.info("├" + "─"*68 + "┤")
    logging.info(f"│ Промпт: {prompt[:50]}{'...' if len(prompt) > 50 else '':<14}│")
    
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer_avibe.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer_avibe([text], return_tensors="pt").to(model_avibe.device)
    
    logging.info(f"│ Входных токенов: {inputs.input_ids.shape[1]:<49}│")
    logging.info("│ ⏳ Генерация ответа...                                           │")
    
    gen_start = time.time()
    # Оптимизированная генерация
    generated_ids = model_avibe.generate(
        **inputs,
        max_new_tokens=256,  # Уменьшено с 512 для ускорения
        do_sample=True,
        temperature=0.7,
        top_p=0.9,  # Nucleus sampling для ускорения
        repetition_penalty=1.1,
        pad_token_id=tokenizer_avibe.eos_token_id,
        use_cache=True,  # Важно для скорости!
    )
    gen_time = time.time() - gen_start
    
    input_len = inputs.input_ids.shape[1]
    gen_ids = generated_ids[:, input_len:]
    generated_tokens = gen_ids.shape[1]
    tokens_per_sec = generated_tokens / gen_time
    
    response = tokenizer_avibe.decode(gen_ids[0], skip_special_tokens=True)
    total_time = time.time() - start_time
    
    logging.info(f"│ ✅ Сгенерировано токенов: {generated_tokens:<42}│")
    logging.info(f"│ ⚡ Скорость: {tokens_per_sec:.2f} токенов/сек{' '*(38-len(f'{tokens_per_sec:.2f}'))}│")
    logging.info(f"│ ⏱  Время генерации: {gen_time:.2f} сек{' '*(42-len(f'{gen_time:.2f}'))}│")
    logging.info(f"│ 🕐 Общее время: {total_time:.2f} сек{' '*(46-len(f'{total_time:.2f}'))}│")
    logging.info(f"│ 📝 Ответ: {response[:50]}{'...' if len(response) > 50 else '':<12}│")
    logging.info("└" + "─"*68 + "┘")
    
    # Формируем метрики для отображения пользователю
    metrics = {
        'tokens_per_sec': f"{tokens_per_sec:.2f}",
        'gen_time': f"{gen_time:.2f}",
        'generated_tokens': generated_tokens,
        'total_time': f"{total_time:.2f}"
    }
    
    return render_template_string(HTML, result=response, image_data=None, metrics=metrics)

@app.route("/avision", methods=["POST"])
def route_avision():
    start_time = time.time()
    prompt2 = request.form.get("prompt2", "")
    file = request.files.get("image")
    
    logging.info("┌" + "─"*68 + "┐")
    logging.info("│ 🖼  AVISION REQUEST (анализ изображения)                          │")
    logging.info("├" + "─"*68 + "┤")
    
    if not file:
        logging.warning("│ ⚠️  Изображение не загружено!                                    │")
        logging.info("└" + "─"*68 + "┘")
        return render_template_string(HTML, result="No image uploaded", image_data=None)
    
    logging.info(f"│ Файл: {file.filename[:55]:<56}│")
    logging.info(f"│ Промпт: {prompt2[:50]}{'...' if len(prompt2) > 50 else '':<14}│")
    
    image_bytes = file.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    logging.info(f"│ Размер изображения: {img.size[0]}x{img.size[1]}{' '*(43-len(f'{img.size[0]}x{img.size[1]}'))}│")
    
    # ИСПРАВЛЕННЫЙ БЛОК: используем тот же подход, что и в рабочем коде
    # 1. Создаем структуру сообщений для apply_chat_template
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": img},
                {"type": "text", "text": prompt2}
            ],
        }
    ]
    
    # 2. Применяем chat template для получения правильно отформатированного текста
    chat_text = processor_avision.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # 3. Обрабатываем с помощью процессора, передавая готовую строку и изображение
    inputs = processor_avision(
        text=[chat_text],  # Передаем готовую строку чата
        images=img,        # Передаем объект PIL.Image
        return_tensors="pt",
        padding=True
    ).to(model_avision.device)
    
    logging.info(f"│ Входных токенов: {inputs.input_ids.shape[1]:<49}│")
    logging.info("│ ⏳ Генерация ответа...                                           │")
    
    gen_start = time.time()
    # Оптимизированная генерация
    generated_ids = model_avision.generate(
        **inputs,
        max_new_tokens=200,  # Уменьшено с 256 для ускорения
        do_sample=True,
        temperature=0.7,
        top_p=0.9,  # Nucleus sampling для ускорения
        repetition_penalty=1.1,
        use_cache=True,  # Важно для скорости!
    )
    gen_time = time.time() - gen_start
    
    # Удаляем токены исходного промпта из ответа
    input_ids_len = inputs.input_ids.shape[1]
    generated_text_ids = generated_ids[:, input_ids_len:]
    generated_tokens = generated_text_ids.shape[1]
    tokens_per_sec = generated_tokens / gen_time
    
    response = processor_avision.batch_decode(generated_text_ids, skip_special_tokens=True)[0]
    total_time = time.time() - start_time
    
    logging.info(f"│ ✅ Сгенерировано токенов: {generated_tokens:<42}│")
    logging.info(f"│ ⚡ Скорость: {tokens_per_sec:.2f} токенов/сек{' '*(38-len(f'{tokens_per_sec:.2f}'))}│")
    logging.info(f"│ ⏱  Время генерации: {gen_time:.2f} сек{' '*(42-len(f'{gen_time:.2f}'))}│")
    logging.info(f"│ 🕐 Общее время: {total_time:.2f} сек{' '*(46-len(f'{total_time:.2f}'))}│")
    logging.info(f"│ 📝 Ответ: {response[:50]}{'...' if len(response) > 50 else '':<12}│")
    logging.info("└" + "─"*68 + "┘")
    
    # Формируем метрики для отображения пользователю
    metrics = {
        'tokens_per_sec': f"{tokens_per_sec:.2f}",
        'gen_time': f"{gen_time:.2f}",
        'generated_tokens': generated_tokens,
        'total_time': f"{total_time:.2f}"
    }
    
    img_data = b64encode(image_bytes).decode('utf-8')
    return render_template_string(HTML, result=response, image_data=img_data, metrics=metrics)

if __name__ == "__main__":
    logging.info("\n" + "🌐 Запуск Flask сервера...")
    logging.info(f"📍 Адрес: http://0.0.0.0:8085")
    logging.info(f"📍 Локальный доступ: http://localhost:8085")
    logging.info("Press CTRL+C to quit\n")
    app.run(host="0.0.0.0", port=8085)
