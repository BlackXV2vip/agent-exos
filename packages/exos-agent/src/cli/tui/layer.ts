import { run as runTui, type TuiInput } from "@exos-agent/tui"
import { Global } from "@exos-agent/core/global"
import { AppNodeBuilder } from "@exos-agent/core/effect/app-node-builder"
import { Effect } from "effect"

export function run(input: TuiInput) {
  return runTui(input).pipe(Effect.provide(AppNodeBuilder.build(Global.node)))
}
