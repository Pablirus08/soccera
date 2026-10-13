import type { PlayerStat } from "@/lib/types"

// Fictional players — the backend has no player data yet. Teams are real so
// links to team pages work; names and numbers are invented.
export const playersMock: PlayerStat[] = [
  // Porteros
  { id: "gk1", name: "Andrés Mora", team_name: "Deportivo Saprissa", position: "GK", rating: 7.6, matches: 10, stats: [{ label: "Vallas invictas", value: 5 }, { label: "Atajadas", value: 31 }] },
  { id: "gk2", name: "Kevin Chaves", team_name: "Sporting FC", position: "GK", rating: 7.3, matches: 10, stats: [{ label: "Vallas invictas", value: 4 }, { label: "Atajadas", value: 27 }] },
  { id: "gk3", name: "Luis Quesada", team_name: "LD Alajuelense", position: "GK", rating: 7.1, matches: 9, stats: [{ label: "Vallas invictas", value: 3 }, { label: "Atajadas", value: 22 }] },
  { id: "gk4", name: "Daniel Arias", team_name: "CS Cartaginés", position: "GK", rating: 7.0, matches: 10, stats: [{ label: "Vallas invictas", value: 3 }, { label: "Atajadas", value: 35 }] },
  { id: "gk5", name: "Esteban Calderón", team_name: "San Carlos", position: "GK", rating: 6.9, matches: 10, stats: [{ label: "Vallas invictas", value: 2 }, { label: "Atajadas", value: 29 }] },
  // Defensas
  { id: "df1", name: "José Ulate", team_name: "Deportivo Saprissa", position: "DEF", rating: 7.4, matches: 10, stats: [{ label: "Despejes", value: 48 }, { label: "Intercepciones", value: 17 }] },
  { id: "df2", name: "Mauricio Brenes", team_name: "Herediano", position: "DEF", rating: 7.2, matches: 10, stats: [{ label: "Despejes", value: 41 }, { label: "Intercepciones", value: 14 }] },
  { id: "df3", name: "Carlos Solís", team_name: "Sporting FC", position: "DEF", rating: 7.1, matches: 9, stats: [{ label: "Despejes", value: 37 }, { label: "Intercepciones", value: 19 }] },
  { id: "df4", name: "Fabián Rojas", team_name: "LD Alajuelense", position: "DEF", rating: 7.0, matches: 10, stats: [{ label: "Despejes", value: 33 }, { label: "Intercepciones", value: 12 }] },
  { id: "df5", name: "Diego Vargas", team_name: "Inter San Carlos", position: "DEF", rating: 6.9, matches: 10, stats: [{ label: "Despejes", value: 52 }, { label: "Intercepciones", value: 11 }] },
  // Mediocampistas
  { id: "mf1", name: "Jefferson Mena", team_name: "Deportivo Saprissa", position: "MID", rating: 7.7, matches: 10, stats: [{ label: "Asistencias", value: 5 }, { label: "Pases clave", value: 24 }] },
  { id: "mf2", name: "Bryan Jiménez", team_name: "CS Cartaginés", position: "MID", rating: 7.5, matches: 10, stats: [{ label: "Asistencias", value: 4 }, { label: "Pases clave", value: 21 }] },
  { id: "mf3", name: "Allan Castro", team_name: "San Carlos", position: "MID", rating: 7.2, matches: 10, stats: [{ label: "Asistencias", value: 3 }, { label: "Pases clave", value: 19 }] },
  { id: "mf4", name: "Randall Soto", team_name: "Puntarenas FC", position: "MID", rating: 7.1, matches: 9, stats: [{ label: "Asistencias", value: 3 }, { label: "Pases clave", value: 16 }] },
  { id: "mf5", name: "Christian Pérez", team_name: "Herediano", position: "MID", rating: 7.0, matches: 10, stats: [{ label: "Asistencias", value: 2 }, { label: "Pases clave", value: 18 }] },
  // Delanteros
  { id: "fw1", name: "Marco Araya", team_name: "Deportivo Saprissa", position: "FWD", rating: 7.9, matches: 10, stats: [{ label: "Goles", value: 8 }, { label: "Tiros al arco", value: 19 }] },
  { id: "fw2", name: "Johan Salazar", team_name: "Sporting FC", position: "FWD", rating: 7.6, matches: 10, stats: [{ label: "Goles", value: 7 }, { label: "Tiros al arco", value: 16 }] },
  { id: "fw3", name: "Alonso Méndez", team_name: "CS Cartaginés", position: "FWD", rating: 7.4, matches: 10, stats: [{ label: "Goles", value: 6 }, { label: "Tiros al arco", value: 15 }] },
  { id: "fw4", name: "Kendall Monge", team_name: "Municipal Pérez Zeledón", position: "FWD", rating: 7.2, matches: 10, stats: [{ label: "Goles", value: 5 }, { label: "Tiros al arco", value: 13 }] },
  { id: "fw5", name: "Ronald Picado", team_name: "LD Alajuelense", position: "FWD", rating: 7.0, matches: 8, stats: [{ label: "Goles", value: 4 }, { label: "Tiros al arco", value: 12 }] },
]
