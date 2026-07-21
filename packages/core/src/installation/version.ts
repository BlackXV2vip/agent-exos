declare global {
  const EXOS_AGENT_VERSION: string
  const EXOS_AGENT_CHANNEL: string
}

export const InstallationVersion = typeof EXOS_AGENT_VERSION === "string" ? EXOS_AGENT_VERSION : "local"
export const InstallationChannel = typeof EXOS_AGENT_CHANNEL === "string" ? EXOS_AGENT_CHANNEL : "local"
export const InstallationLocal = InstallationChannel === "local"
