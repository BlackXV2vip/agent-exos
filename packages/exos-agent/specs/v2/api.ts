// @ts-nocheck

import { ExosAgent } from "@exos-agent/core"
import { ReadTool } from "@exos-agent/core/tools"

const exos-agent = ExosAgent.make({})

exos-agent.tool.add(ReadTool)

exos-agent.tool.add({
  name: "bash",
  schema: {
    type: "object",
    properties: {
      command: {
        type: "string",
        description: "The command to run.",
      },
    },
    required: ["command"],
  },
  execute(input, ctx) {},
})

exos-agent.auth.add({
  provider: "openai",
  type: "api",
  value: process.env.OPENAI_API_KEY,
})

exos-agent.agent.add({
  name: "build",
  permissions: [],
  model: {
    id: "gpt-5-5",
    provider: "openai",
    variant: "xhigh",
  },
})

const sessionID = await exos-agent.session.create({
  agent: "build",
})

exos-agent.subscribe((event) => {
  console.log(event)
})

await exos-agent.session.prompt({
  sessionID,
  text: "hey what is up",
})

await exos-agent.session.prompt({
  sessionID,
  text: "what is up with this",
  files: [
    {
      mime: "image/png",
      uri: "data:image/png;base64,xxxx",
    },
  ],
})

await exos-agent.session.wait()

console.log(await exos-agent.session.messages(sessionID))
