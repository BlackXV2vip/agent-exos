import { AgentV2 } from "@exos-agent/core/agent"
import { AISDK } from "@exos-agent/core/aisdk"
import { Catalog } from "@exos-agent/core/catalog"
import { CommandV2 } from "@exos-agent/core/command"
import { Credential } from "@exos-agent/core/credential"
import { AppNodeBuilder } from "@exos-agent/core/effect/app-node-builder"
import { LayerNodePlatform } from "@exos-agent/core/effect/app-node-platform"
import { LayerNode } from "@exos-agent/core/effect/layer-node"
import { EventV2 } from "@exos-agent/core/event"
import { FileSystem } from "@exos-agent/core/filesystem"
import { FSUtil } from "@exos-agent/core/fs-util"
import { Integration } from "@exos-agent/core/integration"
import { Location } from "@exos-agent/core/location"
import { Npm } from "@exos-agent/core/npm"
import { PluginV2 } from "@exos-agent/core/plugin"
import { Reference } from "@exos-agent/core/reference"
import { SkillV2 } from "@exos-agent/core/skill"
import { Effect, Layer } from "effect"
import { tempLocationLayer } from "../fixture/location"

const npmLayer = Layer.succeed(
  Npm.Service,
  Npm.Service.of({
    add: () => Effect.succeed({ directory: "", entrypoint: undefined }),
    install: () => Effect.void,
    which: () => Effect.succeed(undefined),
  }),
)

export const PluginTestLayer = AppNodeBuilder.build(
  LayerNode.group([
    FileSystem.node,
    FSUtil.node,
    Location.node,
    Npm.node,
    Credential.node,
    EventV2.node,
    LayerNodePlatform.httpClient,
    PluginV2.node,
    AgentV2.node,
    AISDK.node,
    Catalog.node,
    CommandV2.node,
    Integration.node,
    Reference.node,
    SkillV2.node,
  ]),
  [
    [Location.node, tempLocationLayer],
    [Npm.node, npmLayer],
  ],
)
