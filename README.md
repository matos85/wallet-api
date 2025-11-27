# Wallet API — Конкурентобезопасный сервис кошельков

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-success)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

Конкурентобезопасное REST API для управления кошельками пользователей.  
Реализовано на **FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + Alembic + Docker Compose**.

Гарантируется отсутствие отрицательного баланса даже при тысячах одновременных списаний (SELECT FOR UPDATE).

## Функции

- POST `/api/v1/wallets` → создать кошелёк  
- GET  `/api/v1/wallets/{wallet_id}` → получить баланс  
- POST `/api/v1/wallets/{wallet_id}/operation` → пополнить / списать деньги  
- 100% защита от race condition  
- OpenAPI (Swagger) документация  
- Полный запуск одной командой через Docker  
- Автоматические миграции базы  
- Готовые тесты

## Быстрый старт (одной командой)

```bash
git clone https://github.com/твой_ник/wallet-api.git
cd wallet-api

# Запуск всего стека (PostgreSQL + API)
docker compose up --build
