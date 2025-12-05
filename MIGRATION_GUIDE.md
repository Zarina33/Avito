# 🔄 Руководство по миграции на production_vibe

## Что изменилось?

Все production файлы перемещены в отдельную папку `production_vibe/` для лучшей организации проекта.

---

## 📁 Старая структура ❌

```
Avito/
├── app.py
├── config.py              ⬅️ Было здесь
├── middleware.py          ⬅️ Было здесь
├── health.py              ⬅️ Было здесь
├── app_production.py      ⬅️ Было здесь
├── deploy.sh              ⬅️ Было здесь
├── README_PRODUCTION.md   ⬅️ Было здесь
└── ...
```

## 📁 Новая структура ✅

```
Avito/
├── README.md              ⬅️ Обновлен (описание обеих версий)
├── app.py                 ⬅️ Оригинальное приложение (без изменений)
├── avibe.py               ⬅️ Test scripts (без изменений)
├── avision.py             ⬅️ Test scripts (без изменений)
│
└── production_vibe/       ⬅️ ВСЯ PRODUCTION ВЕРСИЯ ЗДЕСЬ
    ├── START_HERE.txt     ⬅️ Начните отсюда!
    ├── README.md          ⬅️ Главная документация
    ├── QUICKSTART.md      ⬅️ Быстрый старт
    ├── app_production.py
    ├── config.py
    ├── middleware.py
    ├── health.py
    ├── deploy.sh          ⬅️ Deployment скрипт
    └── ...
```

---

## 🚀 Как использовать новую структуру

### Шаг 1: Перейти в папку production

```bash
cd /home/zarina/Work/BakaiMarket/Avito/production_vibe
```

### Шаг 2: Прочитать START_HERE.txt

```bash
cat START_HERE.txt
```

### Шаг 3: Запустить

```bash
# Development mode
./deploy.sh development

# ИЛИ Production mode
./deploy.sh production
```

---

## ⚠️ Важные изменения

### 1. Рабочая директория

**Было:**
```bash
cd /home/zarina/Work/BakaiMarket/Avito
python app_production.py
```

**Стало:**
```bash
cd /home/zarina/Work/BakaiMarket/Avito/production_vibe
./deploy.sh development
```

### 2. Systemd service

**Было:**
```bash
WorkingDirectory=/home/zarina/Work/BakaiMarket/Avito
```

**Стало:**
```bash
WorkingDirectory=/home/zarina/Work/BakaiMarket/Avito/production_vibe
```

Файл `avito-ai.service` уже обновлен!

### 3. Конфигурация (.env)

**Где искать:**
```bash
# Шаблон
/home/zarina/Work/BakaiMarket/Avito/production_vibe/.env.example

# Ваш файл (создать)
/home/zarina/Work/BakaiMarket/Avito/production_vibe/.env
```

### 4. Логи

**Без изменений, но теперь:**
```bash
sudo journalctl -u avito-ai -f
```

---

## 📊 Что осталось прежним

✅ Все API endpoints те же
✅ Web интерфейс тот же
✅ Порт по умолчанию: 8085
✅ Модели загружаются из тех же путей
✅ GPU использование: CUDA_VISIBLE_DEVICES=1
✅ Все функции работают идентично

**Изменилась только организация файлов!**

---

## 🔄 Переход с app.py

### Если использовали app.py

**app.py продолжает работать без изменений:**

```bash
cd /home/zarina/Work/BakaiMarket/Avito
python app.py
```

### Переход на production_vibe

1. **Остановите app.py** (Ctrl+C)

2. **Перейдите в production_vibe:**
   ```bash
   cd production_vibe
   ```

3. **Запустите:**
   ```bash
   ./deploy.sh development
   ```

4. **Проверьте:**
   ```bash
   curl http://localhost:8085/api/health
   ```

**Все работает точно так же, но с production features!**

---

## 🆕 Новые возможности

После миграции на production_vibe вы получаете:

✅ **Rate Limiting** - `/api/*` endpoints защищены
✅ **Health Checks** - `/api/health`, `/api/health/ready`, `/api/health/live`
✅ **Metrics** - `/api/metrics` с детальной статистикой
✅ **JSON API** - `/api/v1/text/generate` для интеграций
✅ **Request Tracing** - Каждый запрос имеет уникальный ID
✅ **Structured Logging** - Логи с контекстом
✅ **Input Validation** - Автоматическая проверка данных
✅ **Error Handling** - Профессиональная обработка ошибок
✅ **Configuration** - Управление через .env файл
✅ **Systemd Integration** - Auto-restart при падении

---

## 📝 Checklist миграции

- [ ] Прочитал START_HERE.txt
- [ ] Перешел в папку production_vibe
- [ ] Запустил `./deploy.sh development`
- [ ] Проверил Web UI: http://localhost:8085
- [ ] Проверил Health: http://localhost:8085/api/health
- [ ] Проверил Metrics: http://localhost:8085/api/metrics
- [ ] Протестировал существующие функции (текст/изображения)
- [ ] Все работает? ✅ Готово!
- [ ] Для production: `./deploy.sh production`

---

## 🆘 Проблемы?

### Не могу найти файлы

**Все production файлы в:**
```bash
/home/zarina/Work/BakaiMarket/Avito/production_vibe/
```

### deploy.sh не запускается

```bash
chmod +x /home/zarina/Work/BakaiMarket/Avito/production_vibe/deploy.sh
```

### Хочу вернуться к app.py

```bash
cd /home/zarina/Work/BakaiMarket/Avito
python app.py
```

**app.py никуда не делся и работает как раньше!**

---

## 📚 Документация

**В папке production_vibe:**

1. **START_HERE.txt** ⬅️ Начните здесь
2. **README.md** - Главная документация
3. **QUICKSTART.md** - Быстрый старт
4. **README_PRODUCTION.md** - Полная документация
5. **SUMMARY.md** - Сравнение версий
6. **ARCHITECTURE.txt** - Архитектура

---

## 🎯 Рекомендации

### Для разработки
- Используйте `app.py` - проще
- Или `production_vibe` в dev mode

### Для тестирования новых features
- `cd production_vibe && ./deploy.sh development`

### Для production
- `cd production_vibe && ./deploy.sh production`

---

## ✅ Готово!

Миграция завершена. Теперь у вас:

📁 **Чистая структура** - production код отделен от оригинального
🚀 **Production API** - готов к enterprise использованию
📖 **Полная документация** - в папке production_vibe
🔄 **Обратная совместимость** - app.py работает как раньше

---

**Следующий шаг:**

```bash
cd /home/zarina/Work/BakaiMarket/Avito/production_vibe
cat START_HERE.txt
./deploy.sh development
```

Удачи! 🎉
