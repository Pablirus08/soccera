import { FlaskConicalIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"

/** Marks sections that still run on invented data. */
export function MockBadge({ label = "Datos de ejemplo" }: { label?: string }) {
  return (
    <Badge variant="outline" className="gap-1 font-normal text-muted-foreground">
      <FlaskConicalIcon />
      {label}
    </Badge>
  )
}
