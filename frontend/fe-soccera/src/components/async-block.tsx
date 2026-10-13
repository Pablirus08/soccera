import { CircleAlertIcon, ServerOffIcon } from "lucide-react"
import type { ReactNode } from "react"

import { Skeleton } from "@/components/ui/skeleton"
import { DemoModeError } from "@/lib/api"

type AsyncBlockProps<T> = {
  data: T | null
  error: Error | null
  loading: boolean
  children: (data: T) => ReactNode
  skeletonClassName?: string
}

/** Loading / error / demo-mode states for data fetched on demand. */
export function AsyncBlock<T>({ data, error, loading, children, skeletonClassName = "h-64" }: AsyncBlockProps<T>) {
  if (loading) return <Skeleton className={`w-full ${skeletonClassName}`} />
  if (error instanceof DemoModeError)
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <ServerOffIcon className="size-4" /> {error.message}.
      </p>
    )
  if (error)
    return (
      <p className="flex items-center gap-2 text-sm text-destructive">
        <CircleAlertIcon className="size-4" /> {error.message}
      </p>
    )
  return data ? <>{children(data)}</> : null
}
