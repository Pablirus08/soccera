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

Toda la comunicación con el backend está en `src/lib/api.ts`. Pendientes del backend:

| Necesidad del frontend | Estado |
|---|---|
| Tabla, partidos, goles, disciplina | ✅ `/api/standings`, `/api/matches`, `/api/goals`, `/api/discipline` |
| Próxima jornada | ❌ el adapter solo sincroniza partidos pasados (`events/last`); falta `events/next` |
| Botón "Actualizar partidos" | ❌ falta `POST /api/sync` (backfill + detalles de la temporada actual) |
| Mejores jugadores | ❌ no hay datos de jugadores todavía |

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
