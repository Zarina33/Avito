# 🚀 Quick Start Guide - Production API

## Быстрый старт (3 минуты)

### 1. Установка

```bash
# Клонируйте репозиторий (если еще не сделано)
cd /home/zarina/Work/BakaiMarket/Avito

# Создайте конфигурацию
cp .env.example .env
# Отредактируйте .env если нужно (по умолчанию все настроено)

# Запустите автоматическую установку и деплой
chmod +x deploy.sh
./deploy.sh production
```

Готово! API запущен на http://localhost:8085

---

## Основные команды

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

# Логи (в реальном времени)
sudo journalctl -u avito-ai -f
```

### Разработка

```bash
# Режим разработки (без systemd)
./deploy.sh development

# Или напрямую
python3 app_production.py
```

---

## Проверка работоспособности

```bash
# 1. Health check
curl http://localhost:8085/api/health

# 2. Readiness check (проверяет GPU)
curl http://localhost:8085/api/health/ready

# 3. Метрики
curl http://localhost:8085/api/metrics | jq

# 4. Тест текстовой генерации
curl -X POST http://localhost:8085/api/v1/text/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Привет! Как дела?"}'
```

---

## Структура проекта

### Production файлы (новые)

```
config.py              # ⚙️  Конфигурация (environment variables)
middleware.py          # 🛡️  Middleware (rate limiting, validation, errors)
health.py             # 🏥 Health checks и метрики
app_production.py     # 🚀 Main production app
deploy.sh             # 📦 Deployment script
gunicorn_config.py    # 🔧 Gunicorn config
avito-ai.service      # 🔄 Systemd service
.env.example          # 📝 Environment template
requirements.txt      # 📚 Dependencies
README_PRODUCTION.md  # 📖 Full documentation
QUICKSTART.md         # ⚡ This file
```

### Legacy файлы (старые)

```
app.py                # 🔴 Старый Flask app (можно удалить после тестирования)
avibe.py              # 🔴 Test script (можно оставить для тестов)
avision.py            # 🔴 Test script (можно оставить для тестов)
```

---

## Основные улучшения

| Функция | Описание | Эндпоинт/Настройка |
|---------|----------|-------------------|
| 🔐 **Rate Limiting** | Защита от перегрузки | `RATE_LIMIT_PER_MINUTE=10` в .env |
| 🆔 **Request Tracing** | Уникальный ID каждого запроса | Автоматически в логах |
| 🏥 **Health Checks** | 3 типа проверок | `/api/health`, `/api/health/ready`, `/api/health/live` |
| 📊 **Metrics** | Система, GPU, статистика | `/api/metrics` |
| ✅ **Validation** | Проверка входных данных | Автоматически |
| 🌐 **CORS** | Cross-origin requests | `ALLOWED_ORIGINS=*` в .env |
| 📝 **Structured Logs** | Логи с контекстом | Request ID в каждой записи |
| 🔄 **Graceful Shutdown** | Корректное завершение | SIGTERM/SIGINT handlers |
| 🌍 **JSON API** | RESTful эндпоинты | `/api/v1/text/generate` |
| ⚙️ **Environment Config** | Настройка через .env | Все параметры |

---

## Мониторинг

### Системные метрики

```bash
# Полные метрики
curl -s http://localhost:8085/api/metrics | jq

# Только использование GPU
curl -s http://localhost:8085/api/metrics | jq '.gpu'

# Статистика запросов
curl -s http://localhost:8085/api/metrics | jq '.application'
```

### Логи

```bash
# Все логи (последние 50 строк)
sudo journalctl -u avito-ai -n 50

# В реальном времени
sudo journalctl -u avito-ai -f

# Только ошибки
sudo journalctl -u avito-ai -p err

# По времени
sudo journalctl -u avito-ai --since "10 minutes ago"

# Поиск по request ID
sudo journalctl -u avito-ai | grep "a1b2c3d4-"
```

---

## Настройка производительности

### В файле .env:

```bash
# Уменьшить количество токенов = быстрее
MAX_TOKENS_AVIBE=128
MAX_TOKENS_AVISION=100

# Увеличить temperature = более случайные ответы
TEMPERATURE=0.8

# Строже rate limits
RATE_LIMIT_PER_MINUTE=5
RATE_LIMIT_PER_HOUR=50

# Увеличить максимальную длину промпта
MAX_PROMPT_LENGTH=5000
```

После изменений:

```bash
sudo systemctl restart avito-ai
```

---

## Безопасность

### Production настройки

В `.env` для production:

```bash
# Разрешить только определенные домены
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Строгие лимиты
RATE_LIMIT_PER_MINUTE=5
RATE_LIMIT_PER_HOUR=100

# Логи в файл
LOG_FILE=/var/log/avito-ai/app.log

# Не забудьте настроить файрвол
# sudo ufw allow 8085/tcp
```

---

## Troubleshooting

### Проблема: GPU не доступен

```bash
# Проверка
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"

# Проверьте CUDA_VISIBLE_DEVICES
echo $CUDA_VISIBLE_DEVICES
# Должно быть "1"
```

### Проблема: Сервис не запускается

```bash
# Смотрим логи
sudo journalctl -u avito-ai -n 100 --no-pager

# Проверяем конфигурацию
python3 -c "from config import config; print(config.environment)"

# Тест импортов
python3 -c "import torch, transformers, flask; print('OK')"
```

### Проблема: Rate limit срабатывает слишком часто

Увеличьте лимиты в `.env`:

```bash
RATE_LIMIT_PER_MINUTE=50
RATE_LIMIT_PER_HOUR=500
```

Перезапустите:

```bash
sudo systemctl restart avito-ai
```

---

## API Examples

### Текстовая генерация

```bash
curl -X POST http://localhost:8085/api/v1/text/generate \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: my-custom-id" \
  -d '{
    "prompt": "Напиши короткое стихотворение про осень",
    "max_tokens": 200,
    "temperature": 0.8
  }'
```

### Web интерфейс

Откройте браузер: http://localhost:8085

### Health check (для мониторинга)

```bash
# Добавьте в cron для периодической проверки
*/5 * * * * curl -f http://localhost:8085/api/health || echo "API down!"
```

---

## Обновление

```bash
# 1. Получить новый код
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

## Полная документация

См. [README_PRODUCTION.md](README_PRODUCTION.md) для:
- Детальное описание всех эндпоинтов
- Расширенная настройка
- Docker deployment
- Production checklist
- Мониторинг и алертинг
- И многое другое

---

## Поддержка

**Важные файлы для отладки:**

1. Логи: `sudo journalctl -u avito-ai -f`
2. Метрики: `http://localhost:8085/api/metrics`
3. Конфигурация: `.env`
4. Статус: `sudo systemctl status avito-ai`

**Quick Health Check:**

```bash
# Все ли работает?
curl -s http://localhost:8085/api/health | jq
curl -s http://localhost:8085/api/health/ready | jq
curl -s http://localhost:8085/api/metrics | jq '.application'
```

---

**Готово! Ваш production API запущен! 🚀**

