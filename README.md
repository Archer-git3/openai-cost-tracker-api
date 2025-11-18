# OpenAI Cost Tracker API

## Overview
**OpenAI Cost Tracker API** — це простий REST API для чат-бота на базі OpenAI.  
Він дозволяє:
- Спілкуватися з моделями OpenAI.
- Зберігати історію повідомлень.
- Відстежувати використання токенів та загальну вартість сесії.

Опційно можна запускати простий фронтенд через Streamlit для тестування чат-функціоналу.

---

## Setup

Проєкт використовує Python **3.13**.  

1. Створіть та активуйте віртуальне середовище:

Встановіть залежності:

```bash

pip install -r requirements.txt
```
Створіть файл .env у корені проєкту з наступними змінними:

.env
```
DATABASE_URL=postgresql+asyncpg://postgres:pasword@localhost:port/dbname
OPENAI_API_KEY=your_openai_api_key_here
```
Running the Project
1. Запуск FastAPI серверу
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```


2. Запуск Streamlit фронтенду
```bash
streamlit run ui/chatbot_ui.py
```
