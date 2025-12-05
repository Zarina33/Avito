import os
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Устанавливаем свои директории для кеша
# Например:
root_cache_dir = "/home/zarina/Work/BakaiMarket/Avito/vision"
models_cache_dir = os.path.join(root_cache_dir, "models")
hub_cache_dir = os.path.join(root_cache_dir, "hub")
datasets_cache_dir = os.path.join(root_cache_dir, "datasets")

os.makedirs(models_cache_dir, exist_ok=True)
os.makedirs(hub_cache_dir, exist_ok=True)
os.makedirs(datasets_cache_dir, exist_ok=True)

# Устанавливаем переменные окружения, чтобы Transformers / hub использовали наши директории
os.environ["HF_HOME"] = root_cache_dir
os.environ["TRANSFORMERS_CACHE"] = models_cache_dir
os.environ["HF_DATASETS_CACHE"] = datasets_cache_dir

# --- Настройка модели и устройства ---
model_id = "AvitoTech/avision"
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"✅ Модель будет работать на устройстве: {device}")

# Путь к изображению
local_image_path = "/home/zarina/Work/BakaiMarket/Avito/car5.jpeg"

# --- Загрузка модели и процессора (с указанием cache_dir) ---
print(f"\n⬇️ Скачивание и загрузка модели {model_id} в {models_cache_dir} ...")
processor = AutoProcessor.from_pretrained(model_id, cache_dir=models_cache_dir, local_files_only=False)

model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    torch_dtype="auto",
    cache_dir=models_cache_dir,
    local_files_only=False
)
model.to(device)
print("🚀 Модель успешно загружена.")

# --- Загрузка локального изображения ---
if not os.path.exists(local_image_path):
    print(f"❌ Ошибка: файл не найден по пути: {local_image_path}")
    img = Image.new('RGB', (400, 300), color='red')
else:
    try:
        img = Image.open(local_image_path).convert('RGB')
        print(f"🖼️ Загружено изображение: {local_image_path}")
    except Exception as e:
        print(f"❌ Ошибка при открытии файла: {e}")
        img = Image.new('RGB', (400, 300), color='red')

# --- Подготовка мультимодального запроса (ОБНОВЛЁННЫЙ БЛОК) ---
prompt_text = "Опиши изображение подробно и скажи, что здесь можно продать."

# 1. Форматирование сообщения: создаем структуру, необходимую для apply_chat_template
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": img},
            {"type": "text", "text": prompt_text}
        ],
    }
]

# 2. ВРУЧНУЮ преобразуем сообщения в чат-строку, которую ожидает токенизатор
chat_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


# 3. Вызываем процессор, передавая ТОЛЬКО готовую строку 'chat_text' и объект изображения.
# Это обходит проблему с аргументом `messages`.
inputs = processor(
    text=[chat_text],  # <--- Передаем готовую строку
    images=img,        # <--- Передаем объект PIL.Image
    return_tensors="pt",
    padding=True
)
inputs = inputs.to(device)

# --- Генерация ответа ---
print("\n⚙️ Генерация ответа...")
generated_ids = model.generate(
    **inputs,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7
)

# Удаляем токены исходного промпта из ответа (для чистоты)
input_ids_len = inputs.input_ids.shape[1]
generated_text_ids = generated_ids[:, input_ids_len:]
response = processor.batch_decode(generated_text_ids, skip_special_tokens=True)[0]

# --- Вывод результата ---
print("\n--- Результат ---")
print(f"Запрос: {prompt_text}")
print(f"Ответ: \n{response}")

# Очистка модели и кеши памяти
del model
del processor
if torch.cuda.is_available():
    torch.cuda.empty_cache()
