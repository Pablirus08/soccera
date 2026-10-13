import type { LucideIcon } from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"

/** Placeholder card for analyses that are planned but not built yet. */
export function ComingSoon({ icon: Icon, title, description }: { icon: LucideIcon; title: string; description: string }) {
  return (
    <Card className="border border-dashed bg-transparent ring-0">
      <CardContent className="flex items-start gap-3">
        <div className="rounded-md bg-muted p-2">
          <Icon className="size-4 text-muted-foreground" />
        </div>
        <div className="space-y-0.5">
          <p className="text-sm font-medium">{title}</p>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </CardContent>
    </Card>
  )
}
