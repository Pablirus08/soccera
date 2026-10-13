import { Link } from "react-router"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { shortName, teamInitials, teamSlug } from "@/lib/football"
import { cn } from "@/lib/utils"

type TeamBadgeProps = {
  team: string
  size?: "sm" | "default" | "lg"
  short?: boolean
  link?: boolean
  className?: string
}

/** Team crest placeholder (initials) + name. Swap the fallback for real crests later. */
export function TeamBadge({ team, size = "sm", short = false, link = true, className }: TeamBadgeProps) {
  const content = (
    <>
      <Avatar size={size}>
        <AvatarFallback className="text-[0.65rem] font-semibold">{teamInitials(team)}</AvatarFallback>
      </Avatar>
      <span className="truncate">{short ? shortName(team) : team}</span>
    </>
  )
  const classes = cn("flex min-w-0 items-center gap-2", className)

  return link ? (
    <Link to={`/equipos/${teamSlug(team)}`} className={cn(classes, "hover:underline underline-offset-4")}>
      {content}
    </Link>
  ) : (
    <span className={classes}>{content}</span>
  )
}
