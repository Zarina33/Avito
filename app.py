import os
import io
import torch
from flask import Flask, request, render_template_string
from PIL import Image
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoModelForImageTextToText
)

app = Flask(__name__)

# Пути к локальным моделям и процессорам / токенизаторам
vibe_model_dir = "/mnt/data/avito/vibe/models"
vibe_tokenizer_dir = "/mnt/data/avito/vibe/tokenizers"

vision_snapshot_dir = "/mnt/data/avito/vision/models/models--AvitoTech--avision/snapshots/def8375a2aa67643348ffd93143691410576663f"

# Загрузка Avibe (текстовая модель)
tokenizer_avibe = AutoTokenizer.from_pretrained(
    "AvitoTech/avibe",
    cache_dir=vibe_tokenizer_dir,
    local_files_only=True
)
model_avibe = AutoModelForCausalLM.from_pretrained(
    "AvitoTech/avibe",
    cache_dir=vibe_model_dir,
    torch_dtype="auto",
    device_map="auto",
    local_files_only=True
)

# Загрузка Avision (мультимодальный процессор + модель)
processor_avision = AutoProcessor.from_pretrained(
    vision_snapshot_dir,
    local_files_only=True
)
model_avision = AutoModelForImageTextToText.from_pretrained(
    vision_snapshot_dir,
    torch_dtype="auto",
    device_map="auto",
    local_files_only=True
)

HTML = """
<!doctype html>
<html>
<head>
  <title>Avibe + Avision</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    .section { margin-bottom: 40px; }
    textarea, input[type=text] { width: 60%; }
  </style>
</head>
<body>
  <h1>Avibe & Avision Demo</h1>
  
  <div class="section">
    <h2>🗣 Avibe (текстовый чат)</h2>
    <form method="post" action="/avibe">
      <textarea name="prompt" rows="4" cols="60">Привет, подскажи рецепт борща</textarea><br><br>
      <button type="submit">Отправить</button>
    </form>
  </div>
  
  <div class="section">
    <h2>🖼 Avision (изображение + анализ)</h2>
    <form method="post" action="/avision" enctype="multipart/form-data">
      <input type="file" name="image" accept="image/*"><br><br>
      <input type="text" name="prompt2" value="Опиши изображение подробно и скажи, что здесь можно продать"><br><br>
      <button type="submit">Анализировать</button>
    </form>
  </div>

  {% if result %}
    <div class="section">
      <h2>Результат:</h2>
      <pre>{{ result }}</pre>
      {% if image_data %}
        <img src="data:image/png;base64,{{ image_data }}" alt="Uploaded image" style="max-width:400px;" />
      {% endif %}
    </div>
  {% endif %}
  
</body>
</html>
"""

from base64 import b64encode

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/avibe", methods=["POST"])
def route_avibe():
    prompt = request.form.get("prompt", "")
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer_avibe.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer_avibe([text], return_tensors="pt").to(model_avibe.device)
    generated_ids = model_avibe.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7
    )
    input_len = inputs.input_ids.shape[1]
    gen_ids = generated_ids[:, input_len:]
    response = tokenizer_avibe.decode(gen_ids[0], skip_special_tokens=True)
    return render_template_string(HTML, result=response, image_data=None)

@app.route("/avision", methods=["POST"])
def route_avision():
    prompt2 = request.form.get("prompt2", "")
    file = request.files.get("image")
    if not file:
        return render_template_string(HTML, result="No image uploaded", image_data=None)
    
    image_bytes = file.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
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
    
    generated_ids = model_avision.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7
    )
    
    # Удаляем токены исходного промпта из ответа
    input_ids_len = inputs.input_ids.shape[1]
    generated_text_ids = generated_ids[:, input_ids_len:]
    response = processor_avision.batch_decode(generated_text_ids, skip_special_tokens=True)[0]
    
    img_data = b64encode(image_bytes).decode('utf-8')
    return render_template_string(HTML, result=response, image_data=img_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)
