export * from "./client.js"
export * from "./server.js"

import { createExosAgentClient } from "./client.js"
import { createExosAgentServer } from "./server.js"
import type { ServerOptions } from "./server.js"

export * as data from "./data.js"

export async function createExosAgent(options?: ServerOptions) {
  const server = await createExosAgentServer({
    ...options,
  })

  const client = createExosAgentClient({
    baseUrl: server.url,
  })

  return {
    client,
    server,
  }
}
