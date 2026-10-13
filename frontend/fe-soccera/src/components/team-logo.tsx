import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { teamInitials, teamLogoUrl } from "@/lib/football"
import { cn } from "@/lib/utils"

type TeamLogoProps = {
  team: string
  size?: "sm" | "default" | "lg"
  className?: string
}

/** Club crest, shown whole (no circular crop or ring); initials if there's no crest. */
export function TeamLogo({ team, size = "default", className }: TeamLogoProps) {
  const src = teamLogoUrl(team)
  return (
    <Avatar size={size} className={cn("has-[img]:rounded-none has-[img]:after:hidden", className)}>
      {src && <AvatarImage src={src} alt={team} className="rounded-none object-contain" />}
      <AvatarFallback className="text-[0.6rem] font-semibold">{teamInitials(team)}</AvatarFallback>
    </Avatar>
  )
}
