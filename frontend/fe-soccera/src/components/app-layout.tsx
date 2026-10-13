import { CircleAlertIcon } from "lucide-react"
import { Outlet } from "react-router"

import { AppSidebar } from "@/components/app-sidebar"
import { SyncButton } from "@/components/sync-button"
import { ThemeToggle } from "@/components/theme-toggle"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDateTime } from "@/lib/football"
import { useLeagueData } from "@/lib/league-data"

export function AppLayout() {
  const { data, error, loading } = useLeagueData()

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b bg-background/95 px-4 backdrop-blur">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-1 data-[orientation=vertical]:h-4" />
          <span className="hidden truncate text-xs text-muted-foreground sm:inline">
            {data
              ? data.updatedAt
                ? `Actualizado ${formatDateTime(data.updatedAt)}`
                : "Sin sincronizar"
              : "Cargando…"}
          </span>
          <div className="ml-auto flex items-center gap-1">
            <ThemeToggle />
            <SyncButton />
          </div>
        </header>

        <main className="mx-auto w-full min-w-0 max-w-7xl flex-1 p-4 md:p-6">
          {error ? (
            <div className="flex items-center gap-2 rounded-lg border border-destructive/40 p-4 text-sm text-destructive">
              <CircleAlertIcon className="size-4" /> No se pudieron cargar los datos: {error}
            </div>
          ) : loading || !data ? (
            <div className="space-y-4">
              <Skeleton className="h-8 w-64" />
              <div className="grid gap-4 lg:grid-cols-3">
                <Skeleton className="h-96 lg:col-span-2" />
                <Skeleton className="h-96" />
              </div>
            </div>
          ) : (
            <Outlet />
          )}
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
