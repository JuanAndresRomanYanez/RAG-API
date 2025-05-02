from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Asistente Legal (Leyes de Tránsito Bolivia) con RAG")

# Incluir las rutas de la API
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # Ejecutar el servidor en modo reload (ideal para desarrollo)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
