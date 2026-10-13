import type { Match, Position } from "@/lib/types"

export type Result = "W" | "D" | "L"

export const POSITION_LABELS: Record<Position, string> = {
  GK: "Porteros",
  DEF: "Defensas",
  MID: "Mediocampistas",
  FWD: "Delanteros",
}

export const POSITION_SHORT: Record<Position, string> = {
  GK: "POR",
  DEF: "DEF",
  MID: "MED",
  FWD: "DEL",
}

// Short display names; anything missing falls back to the full name.
const SHORT_NAMES: Record<string, string> = {
  "Deportivo Saprissa": "Saprissa",
  "LD Alajuelense": "Alajuelense",
  "CS Cartaginés": "Cartaginés",
  "Municipal Pérez Zeledón": "Pérez Zeledón",
  "CD Escorpiones Belen": "Escorpiones",
  "Puntarenas FC": "Puntarenas",
  "Sporting FC": "Sporting",
  "Municipal Liberia": "Liberia",
}

export const shortName = (team: string) => SHORT_NAMES[team] ?? team

export const teamSlug = (team: string) =>
  team
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")

/** "Pérez Zeledón" → "PZ", "Saprissa" → "Sa" (two letters so one-word names don't collide). */
export const teamInitials = (team: string) => {
  const words = shortName(team).split(/\s+/)
  return words.length > 1 ? (words[0][0] + words[1][0]).toUpperCase() : words[0].slice(0, 2)
}

export const isPlayed = (m: Match) =>
  m.status === "FINISHED" && m.home_score !== null && m.away_score !== null

const byDate = (a: Match, b: Match) => a.match_date.localeCompare(b.match_date)

export function teamMatches(team: string, matches: Match[]) {
  return matches.filter((m) => m.home_team === team || m.away_team === team).sort(byDate)
}

export function resultFor(team: string, m: Match): Result | null {
  if (!isPlayed(m)) return null
  const [own, other] =
    m.home_team === team ? [m.home_score!, m.away_score!] : [m.away_score!, m.home_score!]
  return own > other ? "W" : own < other ? "L" : "D"
}

export function recentForm(team: string, matches: Match[], n = 5): Result[] {
  return teamMatches(team, matches)
    .map((m) => resultFor(team, m))
    .filter((r): r is Result => r !== null)
    .slice(-n)
}

export function lastPlayedRound(matches: Match[]) {
  return Math.max(0, ...matches.filter(isPlayed).map((m) => Number(m.round ?? 0)))
}

/** Cumulative points after each round the team played. */
export function pointsProgression(team: string, matches: Match[]) {
  let points = 0
  return teamMatches(team, matches)
    .filter(isPlayed)
    .map((m) => {
      const r = resultFor(team, m)
      points += r === "W" ? 3 : r === "D" ? 1 : 0
      return { round: `J${m.round}`, points }
    })
}

/** Goals scored/conceded per played match. */
export function goalsPerMatch(team: string, matches: Match[]) {
  return teamMatches(team, matches)
    .filter(isPlayed)
    .map((m) => {
      const home = m.home_team === team
      return {
        round: `J${m.round}`,
        rival: shortName(home ? m.away_team : m.home_team),
        favor: home ? m.home_score! : m.away_score!,
        contra: home ? m.away_score! : m.home_score!,
      }
    })
}

export function homeAwaySplit(team: string, matches: Match[]) {
  const empty = () => ({ played: 0, won: 0, drawn: 0, lost: 0, gf: 0, ga: 0, points: 0 })
  const split = { home: empty(), away: empty() }
  for (const m of teamMatches(team, matches).filter(isPlayed)) {
    const side = m.home_team === team ? split.home : split.away
    const r = resultFor(team, m)
    side.played++
    side.gf += m.home_team === team ? m.home_score! : m.away_score!
    side.ga += m.home_team === team ? m.away_score! : m.home_score!
    if (r === "W") {
      side.won++
      side.points += 3
    } else if (r === "D") {
      side.drawn++
      side.points++
    } else {
      side.lost++
    }
  }
  return split
}

export function goalsByRound(matches: Match[]) {
  const totals = new Map<number, number>()
  for (const m of matches.filter(isPlayed)) {
    const round = Number(m.round)
    totals.set(round, (totals.get(round) ?? 0) + m.home_score! + m.away_score!)
  }
  return [...totals.entries()]
    .sort(([a], [b]) => a - b)
    .map(([round, goals]) => ({ round: `J${round}`, goals }))
}

const CR_TZ = "America/Costa_Rica"

export const formatMatchDay = (iso: string) =>
  new Intl.DateTimeFormat("es-CR", {
    timeZone: CR_TZ,
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date(iso))

export const formatMatchTime = (iso: string) =>
  new Intl.DateTimeFormat("es-CR", {
    timeZone: CR_TZ,
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(iso))

export const formatShortDate = (iso: string) =>
  new Intl.DateTimeFormat("es-CR", { timeZone: CR_TZ, day: "numeric", month: "short" }).format(
    new Date(iso),
  )

export const formatDateTime = (iso: string) =>
  new Intl.DateTimeFormat("es-CR", {
    timeZone: CR_TZ,
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(iso))
