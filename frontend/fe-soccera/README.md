# SoccerA — Frontend

React + Vite + TypeScript, con Tailwind CSS v4 y componentes de [shadcn/ui](https://ui.shadcn.com).

## Correr en local

```powershell
cd frontend/fe-soccera
npm install
npm run dev        # http://localhost:3000
```

El puerto 3000 coincide con el CORS permitido por el backend (`backend/src/soccera/api/main.py`).

## Datos: modo demo vs. backend

Sin configuración, la app usa el snapshot de `src/mocks/` (tabla y partidos reales del
Apertura 2026 exportados de la base; jugadores inventados). Para usar la API FastAPI:

```powershell
copy .env.example .env.local   # y descomentar VITE_API_URL
```

Toda la comunicación con el backend está en `src/lib/api.ts`:

| Sección | Endpoint |
|---|---|
| Tabla, partidos (incl. próxima jornada), goles, disciplina | `/api/standings`, `/api/matches`, `/api/goals`, `/api/discipline` |
| Mejores jugadores | `/api/players?min_minutes=270` |
| Botón "Actualizar partidos" | `GET /api/sync/status` y, solo si algo está desactualizado, `POST /api/sync` |

El botón primero consulta `/api/sync/status`, que solo lee la base de datos. Si todo
está al día muestra "Todo está actualizado" sin llamar a Sofascore (con opción
"Forzar"); si no, `POST /api/sync` trae el calendario y el detalle de los partidos
pendientes (máximo 15 por llamada).

Para levantar ambos:

```powershell
# terminal 1
cd backend; .venv\Scripts\python.exe scripts\run_api.py
# terminal 2
cd frontend\fe-soccera; npm run dev
```

## Estructura

```
src/
├── pages/          # Inicio, Equipos, detalle de equipo, Análisis
├── components/     # piezas propias (tabla, próxima jornada, jugadores…)
│   └── ui/         # componentes shadcn (generados: npx shadcn@latest add <nombre>)
├── lib/
│   ├── api.ts          # capa de datos (mock o backend)
│   ├── league-data.tsx # estado global + acción de sincronizar
│   ├── football.ts     # cálculos: forma, puntos por jornada, local/visita…
│   └── types.ts        # tipos = esquemas Pydantic del backend
└── mocks/          # snapshot JSON + jugadores de ejemplo
```
