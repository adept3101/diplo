# Дипломная работа
## Разработка web-приложения для коттировки валют на финансовом рынке с нейросетевой коррекцикй
## Стэк

* Backend:
    * Python 3.13
    * FastAPI
    * PostgreSQL
    * SQLalchemy
    * Pydantic 
    * JWT
    * Alembic
    * Docker

* ML: 
    * TensorFlow
    * Keras

* Frontend:
    * JavaScript
    * React 

Данные берутся из API Центрального Банка Российской Федерации (в XML формате...).
Нейросеть обучается на старых данных, глубиной 3 года, т.е. с 2022 по 2025 год.

Авторизация реализована с помощью JWT-токенов.

## Quick start 
```bash
// Клонируем репозиторий
git clone https://github.com/adept3101/diplo

// Создаем образ и запускаем
docker build -t app .
docker run app

// Для запуска фронта
npm run dev

```
