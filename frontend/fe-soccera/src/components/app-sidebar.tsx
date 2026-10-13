import { ChartColumnIcon, HouseIcon, ShieldIcon, TrophyIcon } from "lucide-react"
import { Link, useLocation } from "react-router"

import { TeamLogo } from "@/components/team-logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSkeleton,
  SidebarRail,
} from "@/components/ui/sidebar"
import { isMock, LEAGUE } from "@/lib/api"
import { shortName, teamSlug } from "@/lib/football"
import { useLeagueData } from "@/lib/league-data"

const NAV = [
  { to: "/", label: "Inicio", icon: HouseIcon },
  { to: "/equipos", label: "Equipos", icon: ShieldIcon },
  { to: "/analisis", label: "Análisis", icon: ChartColumnIcon },
]

export function AppSidebar() {
  const { pathname } = useLocation()
  const { data, loading } = useLeagueData()
  const teams =
    data?.standings.rows
      .map((r) => r.team_name)
      .sort((a, b) => shortName(a).localeCompare(shortName(b), "es")) ?? []

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <TrophyIcon className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">SoccerA</span>
                  <span className="truncate text-xs text-muted-foreground">
                    {LEAGUE.name} · {LEAGUE.tournament}
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>General</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV.map(({ to, label, icon: Icon }) => (
                <SidebarMenuItem key={to}>
                  <SidebarMenuButton
                    asChild
                    tooltip={label}
                    isActive={to === "/" ? pathname === "/" : pathname === to}
                  >
                    <Link to={to}>
                      <Icon />
                      <span>{label}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Equipos</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {loading
                ? Array.from({ length: 6 }, (_, i) => (
                    <SidebarMenuItem key={i}>
                      <SidebarMenuSkeleton showIcon />
                    </SidebarMenuItem>
                  ))
                : teams.map((team) => {
                    const to = `/equipos/${teamSlug(team)}`
                    return (
                      <SidebarMenuItem key={team}>
                        <SidebarMenuButton asChild tooltip={team} isActive={pathname === to}>
                          <Link to={to}>
                            <TeamLogo team={team} size="sm" />
                            <span>{shortName(team)}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    )
                  })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <p className="px-2 text-xs text-muted-foreground group-data-[collapsible=icon]:hidden">
          {isMock ? "Modo demo · sin backend" : "Conectado al backend"}
        </p>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
