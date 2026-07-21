interface ImportMetaEnv {
  readonly EXOS_AGENT_CHANNEL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module "virtual:exos-agent-server" {
  export namespace Server {
    export const listen: typeof import("../../../exos-agent/dist/types/src/node").Server.listen
    export type Listener = import("../../../exos-agent/dist/types/src/node").Server.Listener
  }
  export namespace Config {
    export const get: typeof import("../../../exos-agent/dist/types/src/node").Config.get
    export type Info = import("../../../exos-agent/dist/types/src/node").Config.Info
  }
  export const bootstrap: typeof import("../../../exos-agent/dist/types/src/node").bootstrap
}
