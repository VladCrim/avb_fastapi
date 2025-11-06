from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import aiohttp
import asyncio

app = FastAPI()

# Временное хранилище для URL (в реальном проекте используйте БД)
url_db = {}
counter = 1  # Простой генератор ID (для демо)

# Модель для валидации входящего URL
class URLRequest(BaseModel):
    url: HttpUrl  # Автоматическая проверка валидности URL

# 1. Сокращение URL (POST /)
@app.post("/", status_code=status.HTTP_201_CREATED)
async def shorten_url(request: URLRequest):
    global counter
    short_id = str(counter)
    url_db[short_id] = str(request.url)  # Сохраняем оригинальный URL
    counter += 1
    return {"short_url": f"http://127.0.0.1:8080/{short_id}"}

# 2. Редирект по короткой ссылке (GET /<short_id>)
@app.get("/{short_id}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_original(short_id: str):
    if short_id not in url_db:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    return RedirectResponse(url=url_db[short_id], status_code=307)

# 3. Асинхронный запрос к внешнему сервису (GET /fetch-data)
@app.get("/fetch-data")
async def fetch_external_data():
    async with aiohttp.ClientSession() as session:
        # Пример: запрос к публичному API
        async with session.get("https://jsonplaceholder.typicode.com/todos/1") as response:
            if response.status != 200:
                raise HTTPException(status_code=502, detail="Ошибка внешнего сервиса")
            data = await response.json()
            return data

# Запуск сервера (для отладки)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
