# 🚀 Avito AI Production API

Production-ready implementation of Avito AI API with Avibe (text generation) and Avision (image analysis) models.

---

## 📁 Структура папки

```
production_vibe/
├── app_production.py       # Главное приложение
├── config.py               # Управление конфигурацией
├── middleware.py           # Rate limiting, validation, errors
├── health.py               # Health checks и метрики
├── requirements.txt        # Python зависимости
├── .env.example            # Шаблон конфигурации
├── gunicorn_config.py      # Production server config
├── avito-ai.service        # Systemd service file
├── deploy.sh               # Deployment automation script
├── README.md               # Этот файл
├── README_PRODUCTION.md    # Полная документация
├── QUICKSTART.md           # Быстрый старт (3 минуты)
├── SUMMARY.md              # Сравнение old vs new
└── ARCHITECTURE.txt        # Архитектура системы
```

---

## ⚡ Быстрый старт

### 1. Переход в папку

```bash
cd /home/zarina/Work/BakaiMarket/Avito/production_vibe
```

### 2. Конфигурация

```bash
# Создать .env из шаблона
cp .env.example .env

# Отредактировать при необходимости (пути к моделям уже настроены)
nano .env
```

### 3. Запуск

**Development mode:**
```bash
./deploy.sh development
```

**Production mode (с systemd):**
```bash
./deploy.sh production
```

Готово! API запущен на http://localhost:8085

---

## 🎯 Основные возможности

✅ **Configuration Management** - Все настройки через .env файл
✅ **Rate Limiting** - Защита от перегрузки (настраиваемо)
✅ **Request Tracing** - Уникальный ID для каждого запроса
✅ **Health Checks** - 3 endpoint для мониторинга
✅ **Metrics** - Детальная статистика (system, GPU, application)
✅ **Input Validation** - Проверка всех входных данных
✅ **CORS Support** - Настраиваемый cross-origin access
✅ **Structured Logging** - Логи с контекстом и request ID
✅ **Graceful Shutdown** - Корректное завершение работы
✅ **JSON API** - RESTful endpoints для интеграций
✅ **Production Server** - Gunicorn с оптимизациями
✅ **Systemd Integration** - Auto-start и auto-restart

---

## 📊 API Endpoints

### Web Interface
- `GET /` - Главная страница с формами

### AI Endpoints (Forms)
- `POST /avibe` - Генерация текста (form data)
- `POST /avision` - Анализ изображений (multipart form)

### AI Endpoints (JSON)
- `POST /api/v1/text/generate` - Генерация текста (JSON)

### Health & Monitoring
- `GET /api/health` - Basic health check
- `GET /api/health/ready` - Readiness probe (проверяет GPU)
- `GET /api/health/live` - Liveness probe
- `GET /api/metrics` - Детальные метрики

---

## 🔧 Основные команды

### Управление сервисом

```bash
# Запуск
sudo systemctl start avito-ai

# Остановка
sudo systemctl stop avito-ai

# Перезапуск
sudo systemctl restart avito-ai

# Статус
sudo systemctl status avito-ai

# Логи в реальном времени
sudo journalctl -u avito-ai -f
```

### Проверка работоспособности

```bash
# Health check
curl http://localhost:8085/api/health

# Readiness (проверяет GPU)
curl http://localhost:8085/api/health/ready

# Метрики
curl http://localhost:8085/api/metrics

# Тест генерации текста
curl -X POST http://localhost:8085/api/v1/text/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Привет!"}'
```

---

## ⚙️ Конфигурация

Все настройки в файле `.env`:

```bash
# Security
RATE_LIMIT_PER_MINUTE=10      # Запросов в минуту на IP
RATE_LIMIT_PER_HOUR=100       # Запросов в час на IP
ALLOWED_ORIGINS=*             # CORS origins (разделены запятыми)
MAX_PROMPT_LENGTH=2000        # Макс. длина промпта

# Performance
MAX_TOKENS_AVIBE=256          # Макс. токенов для текста
MAX_TOKENS_AVISION=200        # Макс. токенов для изображений
TEMPERATURE=0.7               # Температура генерации (0-2)

# Model Paths
VIBE_MODEL_DIR=/mnt/data/avito/vibe/models
VIBE_TOKENIZER_DIR=/mnt/data/avito/vibe/tokenizers
VISION_SNAPSHOT_DIR=/mnt/data/avito/vision/models/.../

# Logging
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
LOG_FILE=/var/log/avito-ai/app.log  # Опционально
```

После изменений:
```bash
sudo systemctl restart avito-ai
```

---

## 📚 Документация

- **[QUICKSTART.md](QUICKSTART.md)** - Быстрый старт (3-5 минут)
- **[README_PRODUCTION.md](README_PRODUCTION.md)** - Полная документация
- **[SUMMARY.md](SUMMARY.md)** - Сравнение old vs new
- **[ARCHITECTURE.txt](ARCHITECTURE.txt)** - Архитектура системы

---

## 🔍 Мониторинг

### Метрики

```bash
curl http://localhost:8085/api/metrics
```

Возвращает:
- **System**: CPU, RAM, Disk usage
- **GPU**: Memory, utilization
- **Application**: Requests, success rate, response time, tokens

### Логи

```bash
# Последние 50 строк
sudo journalctl -u avito-ai -n 50

# В реальном времени
sudo journalctl -u avito-ai -f

# Только ошибки
sudo journalctl -u avito-ai -p err

# За последние 10 минут
sudo journalctl -u avito-ai --since "10 minutes ago"
```

---

## 🐛 Troubleshooting

### GPU не доступен
```bash
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Сервис не запускается
```bash
sudo journalctl -u avito-ai -n 100 --no-pager
python3 -c "from config import config; print(config.environment)"
```

### Rate limit срабатывает часто
Увеличьте в `.env`:
```bash
RATE_LIMIT_PER_MINUTE=50
RATE_LIMIT_PER_HOUR=500
```

---

## 🔄 Обновление

```bash
cd /home/zarina/Work/BakaiMarket/Avito/production_vibe

# 1. Обновить код (если из git)
git pull

# 2. Обновить зависимости
source venv/bin/activate
pip install -r requirements.txt

# 3. Перезапустить
sudo systemctl restart avito-ai

# 4. Проверить
curl http://localhost:8085/api/health
```

---

## 📈 Production Checklist

Для production deployment:

- [ ] Настроить `.env` (не использовать `.env.example`)
- [ ] Установить `ALLOWED_ORIGINS` (не `*`)
- [ ] Настроить `LOG_FILE` для постоянных логов
- [ ] Настроить log rotation (logrotate)
- [ ] Настроить firewall (ufw/iptables)
- [ ] Настроить SSL/TLS (nginx reverse proxy)
- [ ] Настроить мониторинг (Prometheus, Grafana)
- [ ] Настроить алерты (email, Slack)
- [ ] Протестировать graceful shutdown
- [ ] Настроить автоматические бэкапы

---

## 🎉 Пример использования

### Web Interface

Откройте в браузере: http://localhost:8085

### JSON API

```bash
# Генерация текста
curl -X POST http://localhost:8085/api/v1/text/generate \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: my-request-123" \
  -d '{
    "prompt": "Напиши короткое стихотворение про осень",
    "max_tokens": 200,
    "temperature": 0.8
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "text": "Осень красками играет...",
    "generated_tokens": 87,
    "input_tokens": 12
  },
  "metrics": {
    "generation_time": 1.234,
    "total_time": 1.250,
    "tokens_per_second": 70.45
  },
  "request_id": "my-request-123"
}
```

---

## 🚀 Deployment

### Local Development
```bash
./deploy.sh development
```

### Production Server
```bash
./deploy.sh production
```

### Docker (опционально)
```bash
# В разработке - см. README_PRODUCTION.md
```

---

## 📞 Поддержка

**Быстрая диагностика:**

```bash
# Все ли работает?
curl http://localhost:8085/api/health
curl http://localhost:8085/api/health/ready
curl http://localhost:8085/api/metrics

# Статус сервиса
sudo systemctl status avito-ai

# Логи
sudo journalctl -u avito-ai -f
```

**Важные файлы:**
- Конфигурация: `.env`
- Логи: `/var/log/avito-ai/app.log` или `journalctl`
- Метрики: http://localhost:8085/api/metrics

---

## 📊 Сравнение с оригинальным app.py

| Функция | app.py | production_vibe |
|---------|--------|-----------------|
| Конфигурация | Хардкод | Environment vars |
| Обработка ошибок | Базовая | Professional |
| Rate Limiting | ❌ | ✅ |
| Request Tracing | ❌ | ✅ |
| Health Checks | ❌ | ✅ (3 типа) |
| Метрики | Базовые | Детальные |
| Валидация | ❌ | ✅ |
| CORS | ❌ | ✅ |
| Production Server | Flask dev | Gunicorn |
| Systemd | ❌ | ✅ |

**Все существующие функции работают без изменений!**

---

## 📄 License

Internal use - Avito AI Demo Project

---

**Готово к production использованию! 🚀**

*Последнее обновление: 2025-11-28*


