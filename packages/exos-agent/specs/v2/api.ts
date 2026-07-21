// @ts-nocheck

import { ExosAgent } from "@exos-agent/core"
import { ReadTool } from "@exos-agent/core/tools"

const exosAgent = ExosAgent.make({})

exosAgent.tool.add(ReadTool)

exosAgent.tool.add({
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

exosAgent.auth.add({
  provider: "openai",
  type: "api",
  value: process.env.OPENAI_API_KEY,
})

exosAgent.agent.add({
  name: "build",
  permissions: [],
  model: {
    id: "gpt-5-5",
    provider: "openai",
    variant: "xhigh",
  },
})

const sessionID = await exosAgent.session.create({
  agent: "build",
})

exosAgent.subscribe((event) => {
  console.log(event)
})

await exosAgent.session.prompt({
  sessionID,
  text: "hey what is up",
})

await exosAgent.session.prompt({
  sessionID,
  text: "what is up with this",
  files: [
    {
      mime: "image/png",
      uri: "data:image/png;base64,xxxx",
    },
  ],
})

await exosAgent.session.wait()

console.log(await exosAgent.session.messages(sessionID))
