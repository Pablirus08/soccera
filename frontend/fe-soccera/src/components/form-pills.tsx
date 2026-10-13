import type { Result } from "@/lib/football"
import { cn } from "@/lib/utils"

const STYLES: Record<Result, { label: string; title: string; className: string }> = {
  W: { label: "G", title: "Ganado", className: "bg-[#0ca30c] text-white" },
  D: { label: "E", title: "Empate", className: "bg-muted-foreground/60 text-white" },
  L: { label: "P", title: "Perdido", className: "bg-[#d03b3b] text-white" },
}

/** Last-N results. Letter + color, so the result never relies on color alone. */
export function FormPills({ form, className }: { form: Result[]; className?: string }) {
  return (
    <div className={cn("flex gap-1", className)} aria-label="Forma reciente">
      {form.map((r, i) => (
        <span
          key={i}
          title={STYLES[r].title}
          className={cn(
            "flex size-5 items-center justify-center rounded-sm text-[0.65rem] font-semibold",
            STYLES[r].className,
          )}
        >
          {STYLES[r].label}
        </span>
      ))}
    </div>
  )
}
