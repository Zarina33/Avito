import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# —————————————————————————————————————
# Указываем свои директории для кешей / хранения
root_cache_dir = "/home/zarina/Work/BakaiMarket/Avito/vibe"        # корневая папка кешей
models_cache_dir = os.path.join(root_cache_dir, "models")     # для моделей
tokenizer_cache_dir = os.path.join(root_cache_dir, "tokenizers")  # для токенизаторов
os.makedirs(models_cache_dir, exist_ok=True)
os.makedirs(tokenizer_cache_dir, exist_ok=True)

# Устанавливаем переменные окружения, чтобы библиотека использовала наши директории
os.environ["HF_HOME"] = root_cache_dir
os.environ["TRANSFORMERS_CACHE"] = models_cache_dir
os.environ["HF_TOKENIZERS_CACHE"] = tokenizer_cache_dir

# —————————————————————————————————————
# 1. Определение названия модели
model_name = "AvitoTech/avibe"

# 2. Загрузка токенизатора (с указанием cache_dir)
print(f"Загрузка токенизатора {model_name} в {tokenizer_cache_dir} ...")
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    cache_dir=tokenizer_cache_dir,
    local_files_only=False  # если есть локально, будет использовано; иначе скачивает
)
print("Токенизатор загружен.")

# 3. Загрузка модели
print(f"Загрузка модели {model_name} в {models_cache_dir} ...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    cache_dir=models_cache_dir,
    torch_dtype="auto",
    device_map="auto",
    local_files_only=False
)
print("Модель загружена.")

# 4. Подготовка запроса
prompt = "Привет, подскажи рецепт борща"

# Формирование сообщений / чат-формата
messages = [
    {"role": "user", "content": prompt}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

# 5. Токенизация и генерация
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=1024,
    do_sample=True,
    temperature=0.7
)

input_ids_len = model_inputs.input_ids.shape[1]
generated_text_ids = generated_ids[:, input_ids_len:]
response = tokenizer.decode(generated_text_ids[0], skip_special_tokens=True)

# 6. Вывод результата
print("\n--- Запрос ---")
print(prompt)
print("\n--- Ответ A-vibe ---")
print(response)

# Очистка памяти
del model
del tokenizer
if torch.cuda.is_available():
    torch.cuda.empty_cache()

