/// <reference path="../markdown.d.ts" />

export * as SkillPlugin from "./skill"

import { define } from "./internal"
import { Effect } from "effect"
import { AbsolutePath } from "../schema"
import { SkillV2 } from "../skill"
import customizeExosAgentContent from "./skill/customize-exos-agent.md" with { type: "text" }

export const CustomizeExosAgentContent = customizeExosAgentContent

export const Plugin = define({
  id: "skill",
  effect: Effect.fn(function* (ctx) {
    yield* ctx.skill.transform((draft) => {
      draft.source(
        SkillV2.EmbeddedSource.make({
          type: "embedded",
          skill: SkillV2.Info.make({
            name: "customize-exos-agent",
            description:
              "Use ONLY when the user is editing or creating exos-agent's own configuration: exos-agent.json, exos-agent.jsonc, files under .exos-agent/, or files under ~/.config/exos-agent/. Also use when creating or fixing exos-agent agents, subagents, commands, skills, plugins, MCP servers, or permission rules. Do not use for the user's own application code, or for any project that is not configuring exos-agent itself.",
            location: AbsolutePath.make("/builtin/customize-exos-agent.md"),
            content: CustomizeExosAgentContent,
          }),
        }),
      )
    })
  }),
})
