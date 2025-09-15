# 🎨 API Threads Carousel Generator

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)

> **Мощный API для автоматической генерации визуальных каруселей для социальных сетей с поддержкой ИИ-дизайна**

## 🚀 Особенности

- **🤖 ИИ-генерация конфигураций** - Автоматический подбор стилей по описанию
- **🎨 Гибкая настройка дизайна** - Полный контроль над цветами, шрифтами, отступами
- **📱 Оптимизация для соцсетей** - Поддержка форматов Instagram, LinkedIn, TikTok
- **⚡ Высокая производительность** - Асинхронная обработка больших запросов
- **🔤 Поддержка эмодзи** - Noto Color Emoji для ярких визуалов
- **📊 Множественные слайды** - До 20 слайдов в одной карусели
- **🛠️ REST API** - Простая интеграция с любыми сервисами

## 📖 Быстрый старт

### Установка

```bash
git clone https://github.com/alexrexby/api-threads-carousel.git
cd api-threads-carousel
pip install -r requirements.txt
```

### Запуск

```bash
python app.py
```

API будет доступен по адресу: `http://localhost:5000`

### Первый запрос

```bash
curl -X POST http://localhost:5000/generate-carousel \
  -H "Content-Type: application/json" \
  -d '{
    "text": "**Заголовок слайда 1**\nКонтент первого слайда\n\n========\n\n**Заголовок слайда 2**\nКонтент второго слайда",
    "config": {
      "background_color": "#667eea",
      "text_color": "#ffffff",
      "font_size": 44,
      "padding": 90
    }
  }'
```

## 🔌 API Эндпоинты

### `POST /generate-carousel`
Генерация карусели из текста с разделителями

**Параметры:**
- `text` (string) - Текст с разделителями `========`
- `config` (object) - Конфигурация дизайна

### `POST /generate-config` 
ИИ-генерация конфигурации дизайна

**Параметры:**
- `description` (string) - Описание желаемого стиля

### `GET /health`
Проверка состояния сервиса

## 🎨 Примеры конфигураций

### Корпоративный стиль
```json
{
  "background_color": "#1e3d59",
  "text_color": "#ffffff",
  "font_size": 48,
  "title_font_size": 60,
  "padding": 80,
  "corner_radius": 20,
  "add_logo_text": true,
  "logo_text": "@company"
}
```

### Яркий креативный
```json
{
  "background_color": "#ff6b6b",
  "text_color": "#ffffff",
  "font_size": 44,
  "title_font_size": 56,
  "padding": 90,
  "corner_radius": 30,
  "add_page_numbers": true
}
```

## 📱 Поддерживаемые форматы

| Платформа | Размер | Формат |
|-----------|--------|--------|
| Instagram Post | 1080×1080 | 1:1 |
| Instagram Story | 1080×1920 | 9:16 |
| LinkedIn | 1080×1080 | 1:1 |
| TikTok | 1080×1350 | 4:5 |

## 🛠️ Конфигурация

### Переменные окружения

```bash
# .env
FLASK_ENV=production
FLASK_DEBUG=False
API_HOST=0.0.0.0
API_PORT=5000
OPENAI_API_KEY=your_openai_key
MAX_SLIDES=20
DEFAULT_FONT_SIZE=44
```

### Docker

```bash
docker build -t carousel-api .
docker run -p 5000:5000 carousel-api
```

## 📊 Мониторинг и логи

API предоставляет метрики для мониторинга:
- Время генерации изображений
- Количество обработанных запросов
- Ошибки и исключения

## 🤝 Интеграции

### n8n Workflow
```json
{
  "node": "HTTP Request",
  "method": "POST",
  "url": "http://your-api.com/generate-carousel",
  "body": "{{$json.carousel_data}}"
}
```

### Zapier Integration
Подключите через Webhooks для автоматизации создания контента.

## 📚 Документация

- [API Reference](docs/api-reference.md)
- [Configuration Guide](docs/configuration.md)
- [Integration Examples](docs/integrations.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🧪 Тестирование

```bash
# Запуск тестов
python -m pytest tests/

# Проверка покрытия
python -m pytest --cov=app tests/
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - подробности в файле [LICENSE](LICENSE).

## 🎯 Roadmap

- [ ] Поддержка видео в каруселях
- [ ] Интеграция с базами данных
- [ ] GraphQL API
- [ ] Кеширование результатов
- [ ] Batch обработка
- [ ] Аналитика использования

## 📞 Поддержка

- 📧 Email: support@apithreads.ru
- 💬 Telegram: [@apithreads](https://t.me/apithreads)
- 🐛 Issues: [GitHub Issues](https://github.com/alexrexby/api-threads-carousel/issues)

---

**Сделано с ❤️ командой APIThreads**
