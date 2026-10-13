import { Link } from "react-router"

import { TeamLogo } from "@/components/team-logo"
import { shortName, teamSlug } from "@/lib/football"
import { cn } from "@/lib/utils"

type TeamBadgeProps = {
  team: string
  size?: "sm" | "default" | "lg"
  short?: boolean
  link?: boolean
  className?: string
}

/** Team crest + name, optionally linking to the team page. */
export function TeamBadge({ team, size = "sm", short = false, link = true, className }: TeamBadgeProps) {
  const content = (
    <>
      <TeamLogo team={team} size={size} />
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
