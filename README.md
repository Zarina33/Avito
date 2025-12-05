# Avito AI Demo - Text & Image Generation API

Демонстрационное приложение для работы с моделями Avibe (генерация текста) и Avision (анализ изображений).

---

## 📁 Структура проекта

```
Avito/
├── production_vibe/          # 🚀 Production-ready API (НОВОЕ)
│   ├── app_production.py     # Главное приложение
│   ├── config.py             # Конфигурация
│   ├── middleware.py         # Rate limiting, validation
│   ├── health.py             # Health checks, метрики
│   ├── deploy.sh             # Deployment скрипт
│   ├── requirements.txt      # Зависимости
│   ├── .env.example          # Шаблон конфигурации
│   ├── gunicorn_config.py    # Production server
│   ├── avito-ai.service      # Systemd service
│   ├── README.md             # Документация
│   ├── QUICKSTART.md         # Быстрый старт
│   └── ...                   # Другие файлы
│
├── app.py                    # 🔴 Оригинальное приложение
├── avibe.py                  # 🔴 Test script (Avibe)
├── avision.py                # 🔴 Test script (Avision)
│
├── templates/                # HTML шаблоны
│   ├── index.html
│   └── result_avibe.html
│
├── vibe/                     # Кеш моделей Avibe
│   └── models/
│       └── ...
│
├── vision/                   # Кеш моделей Avision
│   └── models/
│       └── ...
│
└── car5.jpeg                 # Тестовое изображение
```

---

## 🎯 Две версии

### 🔴 Оригинальная версия (app.py)

**Простое демо-приложение:**
- Запуск: `python app.py`
- Порт: 8085
- Функции: Web UI для текста и изображений
- Без production фич

**Когда использовать:**
- Быстрое тестирование моделей
- Локальная разработка
- Демонстрация возможностей

### 🚀 Production версия (production_vibe/)

**Enterprise-grade API:**
- Запуск: `cd production_vibe && ./deploy.sh production`
- Порт: 8085 (настраиваемый)
- Функции: Все из оригинальной + production features

**Дополнительные возможности:**
✅ Rate limiting (защита от перегрузки)
✅ Request tracing (уникальный ID)
✅ Health checks (3 endpoint)
✅ Метрики (system, GPU, application)
✅ Input validation (проверка данных)
✅ CORS support (cross-origin)
✅ Structured logging (контекст)
✅ JSON API (RESTful endpoints)
✅ Systemd integration (auto-restart)
✅ Graceful shutdown (корректное завершение)

**Когда использовать:**
- Production deployment
- API для других сервисов
- Мониторинг и метрики
- High-load scenarios

---

## 🚀 Быстрый старт

### Оригинальная версия

```bash
# 1. Перейти в корень проекта
cd /home/zarina/Work/BakaiMarket/Avito

# 2. Активировать окружение (если есть)
source venv/bin/activate

# 3. Запустить
python app.py

# Открыть: http://localhost:8085
```

### Production версия

```bash
# 1. Перейти в папку production
cd /home/zarina/Work/BakaiMarket/Avito/production_vibe

# 2. Запустить deployment
./deploy.sh production

# API готов: http://localhost:8085
# Health: http://localhost:8085/api/health
# Metrics: http://localhost:8085/api/metrics
```

Полная документация: [production_vibe/README.md](production_vibe/README.md)

---

## 📊 Сравнение версий

| Функция | app.py | production_vibe |
|---------|--------|-----------------|
| **Основные возможности** |
| Генерация текста (Avibe) | ✅ | ✅ |
| Анализ изображений (Avision) | ✅ | ✅ |
| Web интерфейс | ✅ | ✅ |
| GPU acceleration (H200) | ✅ | ✅ |
| **Production features** |
| Configuration управление | ❌ | ✅ через .env |
| Rate limiting | ❌ | ✅ настраиваемый |
| Health checks | ❌ | ✅ 3 endpoint |
| Метрики | Базовые | ✅ детальные |
| Request tracing | ❌ | ✅ с ID |
| Input validation | ❌ | ✅ |
| CORS support | ❌ | ✅ |
| JSON API | ❌ | ✅ RESTful |
| Error handling | Базовая | ✅ comprehensive |
| Structured logging | ❌ | ✅ |
| **Deployment** |
| Development server | Flask dev | Gunicorn |
| Systemd integration | ❌ | ✅ |
| Auto-deployment | ❌ | ✅ скрипт |
| Graceful shutdown | ❌ | ✅ |

---

## 🔧 Установка зависимостей

```bash
# Для оригинальной версии
pip install flask torch transformers pillow

# Для production версии (включает все + дополнительные)
cd production_vibe
pip install -r requirements.txt
```

---

## 📚 Документация

### Production версия (подробная)
- **[production_vibe/README.md](production_vibe/README.md)** - Главная документация
- **[production_vibe/QUICKSTART.md](production_vibe/QUICKSTART.md)** - Быстрый старт
- **[production_vibe/README_PRODUCTION.md](production_vibe/README_PRODUCTION.md)** - Полная документация
- **[production_vibe/SUMMARY.md](production_vibe/SUMMARY.md)** - Сравнение версий
- **[production_vibe/ARCHITECTURE.txt](production_vibe/ARCHITECTURE.txt)** - Архитектура

### Оригинальная версия
- Смотрите комментарии в коде `app.py`

---

## 🎯 Рекомендации

**Для разработки и тестирования:**
- Используйте `app.py` - проще и быстрее

**Для production использования:**
- Используйте `production_vibe/` - надежнее и функциональнее

**Миграция с app.py на production_vibe:**
1. Все существующие функции работают без изменений
2. Web интерфейс идентичен
3. Дополнительно получаете production features
4. Никаких breaking changes!

---

## 🔐 Безопасность

### Оригинальная версия
- Только для локального использования
- Нет защиты от перегрузки
- Хардкод настроек

### Production версия
- Rate limiting (защита от DDoS)
- Input validation (защита от bad input)
- CORS configuration (контроль доступа)
- Structured logging (аудит)
- Error sanitization (безопасные сообщения об ошибках)

---

## 📈 Метрики и мониторинг

### Оригинальная версия
- Базовые метрики в console (tokens/sec, время)

### Production версия
```bash
# Детальные метрики
curl http://localhost:8085/api/metrics

# Возвращает:
# - System metrics (CPU, RAM, Disk)
# - GPU metrics (Memory, Utilization)
# - Application metrics (Requests, Success rate, Response time)
```

---

## 🔄 Deployment

### Локальная разработка
```bash
# Оригинальная версия
python app.py

# Production версия (dev mode)
cd production_vibe && ./deploy.sh development
```

### Production server
```bash
# Только production_vibe
cd production_vibe && ./deploy.sh production

# Systemd service:
sudo systemctl start avito-ai
sudo systemctl status avito-ai
sudo journalctl -u avito-ai -f
```

---

## 🆘 Troubleshooting

### GPU не определяется

```bash
# Проверить CUDA
nvidia-smi

# Проверить в Python
python3 -c "import torch; print(torch.cuda.is_available())"

# Проверить переменную окружения
echo $CUDA_VISIBLE_DEVICES  # Должно быть "1"
```

### Порт 8085 занят

```bash
# Найти процесс
sudo lsof -i :8085

# Убить процесс
sudo kill -9 <PID>

# Или изменить порт в production_vibe/.env
PORT=8086
```

### Модели не загружаются

Проверьте пути к моделям:
- Vibe: `/mnt/data/avito/vibe/models`
- Vision: `/mnt/data/avito/vision/models/...`

Или настройте в `production_vibe/.env`:
```bash
VIBE_MODEL_DIR=/your/path/to/vibe/models
VISION_SNAPSHOT_DIR=/your/path/to/vision/snapshot
```

---

## 📞 Поддержка

**Быстрая проверка:**

```bash
# Оригинальная версия
curl http://localhost:8085/

# Production версия
curl http://localhost:8085/api/health
curl http://localhost:8085/api/metrics
```

**Логи:**

```bash
# Оригинальная версия - смотрите console

# Production версия
sudo journalctl -u avito-ai -f
```

---

## 🎉 Что дальше?

1. **Протестируйте обе версии:**
   ```bash
   # Оригинальная
   python app.py
   
   # Production
   cd production_vibe && ./deploy.sh development
   ```

2. **Выберите подходящую для ваших задач**

3. **Для production используйте production_vibe:**
   ```bash
   cd production_vibe && ./deploy.sh production
   ```

4. **Настройте мониторинг** (для production)

5. **Наслаждайтесь! 🚀**

---

## 📄 License

Internal use - Avito AI Demo Project

---

*Последнее обновление: 2025-11-28*


