<!-- Banner -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:0f2027,100:203a43&height=120&section=header&text=Gay%20Of%20Day%20VK%20Bot&fontSize=40&fontColor=ffffff" alt="Gay Of Day VK Bot" />
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Быстрый%20старт-Запустить-0f172a?style=for-the-badge" alt="Быстрый старт" /></a>
  <a href="#commands"><img src="https://img.shields.io/badge/Команды-Посмотреть-1d4ed8?style=for-the-badge" alt="Команды" /></a>
  <a href="#troubleshooting"><img src="https://img.shields.io/badge/Диагностика-Починить-7f1d1d?style=for-the-badge" alt="Диагностика" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat" alt="Python" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat" alt="Docker Compose" />
  <img src="https://img.shields.io/badge/SQLite-Local%20DB-003B57?style=flat" alt="SQLite" />
  <img src="https://img.shields.io/badge/Groq-LLM-111827?style=flat" alt="Groq" />
  <img src="https://img.shields.io/badge/VK-Bot-4A76A8?style=flat" alt="VK" />
</p>

VK-бот сообщества, который выбирает «победителя дня» по истории чата. Работает на Groq LLM, хранит историю в SQLite, поддерживает расписание и управление настройками через команды.

---

## Возможности

- Ежедневный результат для каждого чата с сохранением итогов
- История сообщений и результатов в SQLite
- Интеграция с Groq и смена модели на лету
- Команды для сброса, списка моделей и расписания
- Docker Compose: запуск одной командой

<a id="quick-start"></a>
## Быстрый старт

1) Создай файл `.env` с ключами (см. «Настройка»)
2) Собери и запусти:

```bash
docker compose up -d --build
```

3) Посмотри логи:

```bash
docker compose logs -f
```

## Быстрый старт (Linux, одной командой)

Замените `VK_TOKEN_VALUE`, `GROQ_API_KEY_VALUE`, при необходимости модель и настройки промпта:

```bash
sudo apt-get update && sudo apt-get install -y git docker.io docker-compose-plugin && sudo systemctl enable --now docker && git clone https://github.com/zen2281488/gayOfDay.git && cd gayOfDay && printf 'VK_TOKEN=VK_TOKEN_VALUE\nGROQ_API_KEY=GROQ_API_KEY_VALUE\nGROQ_MODEL=llama-3.1-8b-instant\nGROQ_TEMPERATURE=0.9\nGAME_TITLE={{GAME_TITLE}} дня\nLEADERBOARD_TITLE=📊 Пидерборд\nUSER_PROMPT_TEMPLATE=Лог чата:\\n{{CHAT_LOG}}\\n\\nКто из них {{GAME_TITLE}}? Ответ — строго JSON.\n' > .env && docker compose up -d --build
```

## Быстрый старт (Windows, одной командой)

Замените `VK_TOKEN_VALUE`, `GROQ_API_KEY_VALUE`, при необходимости модель и настройки промпта:

```powershell
winget install -e --id Git.Git; winget install -e --id Docker.DockerDesktop; git clone https://github.com/zen2281488/gayOfDay.git; cd gayOfDay; @\"VK_TOKEN=VK_TOKEN_VALUE`nGROQ_API_KEY=GROQ_API_KEY_VALUE`nGROQ_MODEL=llama-3.1-8b-instant`nGROQ_TEMPERATURE=0.9`nGAME_TITLE={{GAME_TITLE}} дня`nLEADERBOARD_TITLE=📊 Пидерборд`nUSER_PROMPT_TEMPLATE=Лог чата:\n{{CHAT_LOG}}\n\nКто из них {{GAME_TITLE}}? Ответ — строго JSON.`n\"@ | Set-Content -Encoding UTF8 .env; docker compose up -d --build
```

<a id="configuration"></a>
## Настройка

Переменные окружения (`.env` или docker-compose):

- `VK_TOKEN` — токен сообщества VK с доступом к сообщениям
- `GROQ_API_KEY` — API ключ Groq (получить: https://console.groq.com/keys)
- `GROQ_MODEL` — ID модели (по умолчанию берется из кода, можно переопределить)
- `GROQ_TEMPERATURE` — температура генерации, например `0.7`
- `GAME_TITLE` — название игры в ответах (например, `{{GAME_TITLE}} дня`)
- `LEADERBOARD_TITLE` — заголовок таблицы лидеров
- `USER_PROMPT_TEMPLATE` — шаблон пользовательского промпта (подставляются `{{CHAT_LOG}}` и `{{GAME_TITLE}}`, переносы строк — через `\n`)
- `DB_PATH` — путь к SQLite (в Docker по умолчанию `/app/data/chat_history.db`)

Системный промпт зашит в коде и не задается через `.env`.

Пример `.env`:

```dotenv
VK_TOKEN=vk1.a.***
GROQ_API_KEY=gsk_***
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TEMPERATURE=0.9
GAME_TITLE=Самый модный парень на деревне
LEADERBOARD_TITLE=📊 Лидерборд
USER_PROMPT_TEMPLATE=Лог чата:\n{{CHAT_LOG}}\n\nКто из них {{GAME_TITLE}}? Выбери user_id и придумай причину, опираясь на стиль, уверенность и то, как человек подает себя. Обращайся к человеку по имени, а не по id. Используй цитаты из лога для обоснования. Вердикт — 4-6 предложений, с легкой иронией. Ответ — строго JSON.

```

<a id="commands"></a>
## Команды

Основные:

- `/кто` — запустить выбор
- `/сброс` — сбросить результат за сегодня
- `/время HH:MM` — установить авто-запуск
- `/сброс_времени` — удалить расписание
- `/настройки` — показать настройки
- `/список_моделей` — список моделей Groq (live)

Настройки модели/ключа:

- `/установить_модель <model_id>` — сменить модель
- `/установить_ключ <api_key>` — обновить ключ

<a id="data"></a>
## Хранилище данных

- SQLite хранится в `./data/chat_history.db`
- Сохраняются сообщения и результаты по каждому чату

<a id="troubleshooting"></a>
## Диагностика

- **Groq 400 / model_decommissioned** — посмотри `/список_моделей` и укажи рабочую модель через `/установить_модель <id>`
- **Ошибки JSON от Groq** — попробуй уменьшить `GROQ_TEMPERATURE` (например, `0.4`) и повторить
- **Бот молчит** — используй команду (например, `/кто`) и проверь права сообщества на сообщения
- **Docker engine error (Windows)** — убедись, что Docker Desktop запущен с Linux engine
- **Debian bullseye: 404 / bullseye-backports** — удали backports и установи Docker через get.docker.com:

```bash
sudo sed -i '/bullseye-backports/d' /etc/apt/sources.list /etc/apt/sources.list.d/*.list && sudo apt-get update && sudo apt-get install -y curl git && curl -fsSL https://get.docker.com | sh && sudo systemctl enable --now docker
```

## Примечания

- Сообщения сохраняются локально в SQLite для контекста
- Не коммить `.env` в репозиторий

## Лицензия

Проект распространяется по лицензии MIT. См. `LICENSE`.
