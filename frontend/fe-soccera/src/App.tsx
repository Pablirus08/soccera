import { BrowserRouter, Link, Route, Routes } from "react-router"

import { AppLayout } from "@/components/app-layout"
import { PageHeader } from "@/components/page-header"
import { ThemeProvider } from "@/components/theme-provider"
import { Button } from "@/components/ui/button"
import { Toaster } from "@/components/ui/sonner"
import { TooltipProvider } from "@/components/ui/tooltip"
import { LeagueDataProvider } from "@/lib/league-data"
import { AnalysisPage } from "@/pages/analysis"
import { ComparePage } from "@/pages/compare"
import { HomePage } from "@/pages/home"
import { MatchDetailPage } from "@/pages/match-detail"
import { TeamDetailPage } from "@/pages/team-detail"
import { TeamsPage } from "@/pages/teams"

function NotFound() {
  return (
    <div className="space-y-4">
      <PageHeader title="Página no encontrada" />
      <Button variant="outline" asChild>
        <Link to="/">Ir al inicio</Link>
      </Button>
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <TooltipProvider>
        <LeagueDataProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<AppLayout />}>
                <Route index element={<HomePage />} />
                <Route path="equipos" element={<TeamsPage />} />
                <Route path="equipos/:slug" element={<TeamDetailPage />} />
                <Route path="analisis" element={<AnalysisPage />} />
                <Route path="comparar" element={<ComparePage />} />
                <Route path="partidos/:sourceId" element={<MatchDetailPage />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </BrowserRouter>
          <Toaster richColors position="bottom-right" />
        </LeagueDataProvider>
      </TooltipProvider>
    </ThemeProvider>
  )
}
