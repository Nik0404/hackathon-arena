# GPTHub

Единое мультимодальное ИИ-пространство на базе OpenWebUI для работы с текстом, файлами, изображениями, аудио и долгосрочной памятью в одном чате.

## Что реализовано

- текстовый чат
- анализ изображений
- ответы по PDF и другим файлам
- распознавание аудио
- ручной выбор модели
- автоматическая маршрутизация сценариев
- долгосрочная память между чатами

## Используемые модели

- `mws-gpt-alpha` — основной текстовый чат
- `qwen2.5-vl` — vision
- `cotype-pro-vl-32b` — vision
- `whisper-medium` — speech-to-text
- `bge-m3` — embeddings / retrieval
- `qwen-image-lightning` — image generation endpoint

## Быстрый запуск

### Требования

- Docker Desktop или Docker Engine с `docker compose`
- действующий ключ `MWS GPT` вида `sk-...`

### Шаг 1. Создать `.env`

Linux / macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
copy .env.example .env
```

### Шаг 2. Указать ключ MWS GPT

Откройте файл `.env` и заполните:

```text
OPENAI_API_KEY=sk-...
```

При необходимости можно также явно указать:

```text
OPENAI_API_BASE_URL=https://api.gpt.mws.ru/v1
RAG_OPENAI_API_BASE_URL=https://api.gpt.mws.ru/v1
AUDIO_STT_OPENAI_API_BASE_URL=https://api.gpt.mws.ru/v1
IMAGES_OPENAI_API_BASE_URL=https://api.gpt.mws.ru/v1
```

### Шаг 3. Запуск одной командой

```bash
docker compose up --build -d
```

После запуска интерфейс будет доступен по адресу:

```text
http://localhost:3000
```

## Что важно про запуск

- основной `docker-compose.yaml` настроен под `MWS GPT`
- `Ollama` для запуска решения не требуется
- данные OpenWebUI сохраняются в volume `open-webui`

## Что проверить после запуска

1. Открыть `http://localhost:3000`
2. Создать первого администратора
3. Открыть чат и проверить текстовый запрос
4. Загрузить изображение и спросить: `Что на этой картинке?`
5. Загрузить PDF и спросить: `О чем этот файл?`
6. Загрузить аудиофайл и спросить: `Что содержится в этом аудиофайле?`
7. Проверить память:
   - в одном чате написать `Меня зовут Никита`
   - создать новый чат
   - спросить `Как меня зовут?`

## Диагностика

Посмотреть состояние контейнеров:

```bash
docker compose ps
```

Посмотреть логи:

```bash
docker compose logs -f open-webui
```

Остановить проект:

```bash
docker compose down
```

## Примечание

Если сборка фронтенда падает по памяти Node.js, в `Dockerfile` уже увеличен heap size для этапа `npm run build`.
