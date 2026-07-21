/**
 * Application-wide constants and configuration
 */
export const config = {
  // Base URL
  baseUrl: "https://exos-agent.ai",

  // GitHub
  github: {
    repoUrl: "https://github.com/anomalyco/exos-agent",
    starsFormatted: {
      compact: "160K",
      full: "160,000",
    },
  },

  // Social links
  social: {
    twitter: "https://x.com/exos-agent",
    discord: "https://discord.gg/exos-agent",
  },

  // Static stats (used on landing page)
  stats: {
    contributors: "900",
    commits: "13,000",
    monthlyUsers: "7.5M",
  },
} as const
