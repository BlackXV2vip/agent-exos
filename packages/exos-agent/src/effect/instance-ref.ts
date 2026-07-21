import { Context } from "effect"
import type { InstanceContext } from "@/project/instance-context"
import type { WorkspaceV2 } from "@exos-agent/core/workspace"

export const InstanceRef = Context.Reference<InstanceContext | undefined>("~exos-agent/InstanceRef", {
  defaultValue: () => undefined,
})

export const WorkspaceRef = Context.Reference<WorkspaceV2.ID | undefined>("~exos-agent/WorkspaceRef", {
  defaultValue: () => undefined,
})
