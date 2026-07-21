const stage = process.env.SST_STAGE || "dev"

export default {
  url: stage === "production" ? "https://exos-agent.ai" : `https://${stage}.exos-agent.ai`,
  console: stage === "production" ? "https://exos-agent.ai/auth" : `https://${stage}.exos-agent.ai/auth`,
  email: "help@anoma.ly",
  socialCard: "https://social-cards.sst.dev",
  github: "https://github.com/anomalyco/exos-agent",
  discord: "https://exos-agent.ai/discord",
  headerLinks: [
    { name: "app.header.home", url: "/" },
    { name: "app.header.docs", url: "/docs/" },
  ],
}
