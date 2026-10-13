# SoccerA

Plataforma de análisis y predicción en vivo para la Primera División de Costa Rica.

## Estructura

```
.
├── backend/    # Python: ingesta (Sofascore / API-Football), PostgreSQL, modelos, API FastAPI
└── frontend/   # Interfaz web (piloto, aún no conectado al backend)
```

Cada carpeta tiene su propio README con instrucciones de instalación.

## Inicio rápido (backend)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env   # completar API_FOOTBALL_KEY
```
