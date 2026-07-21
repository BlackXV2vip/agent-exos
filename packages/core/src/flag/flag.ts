import { Config } from "effect"

export function truthy(key: string) {
  const value = process.env[key]?.toLowerCase()
  return value === "true" || value === "1"
}

const copy = process.env["EXOS_AGENT_EXPERIMENTAL_DISABLE_COPY_ON_SELECT"]
const fff = process.env["EXOS_AGENT_DISABLE_FFF"]

function enabledByExperimental(key: string) {
  return process.env[key] === undefined ? truthy("EXOS_AGENT_EXPERIMENTAL") : truthy(key)
}

export const Flag = {
  OTEL_EXPORTER_OTLP_ENDPOINT: process.env["OTEL_EXPORTER_OTLP_ENDPOINT"],
  OTEL_EXPORTER_OTLP_HEADERS: process.env["OTEL_EXPORTER_OTLP_HEADERS"],

  EXOS_AGENT_AUTO_HEAP_SNAPSHOT: truthy("EXOS_AGENT_AUTO_HEAP_SNAPSHOT"),
  EXOS_AGENT_GIT_BASH_PATH: process.env["EXOS_AGENT_GIT_BASH_PATH"],
  EXOS_AGENT_CONFIG: process.env["EXOS_AGENT_CONFIG"],
  EXOS_AGENT_CONFIG_CONTENT: process.env["EXOS_AGENT_CONFIG_CONTENT"],
  EXOS_AGENT_DISABLE_AUTOUPDATE: truthy("EXOS_AGENT_DISABLE_AUTOUPDATE"),
  EXOS_AGENT_ALWAYS_NOTIFY_UPDATE: truthy("EXOS_AGENT_ALWAYS_NOTIFY_UPDATE"),
  EXOS_AGENT_DISABLE_PRUNE: truthy("EXOS_AGENT_DISABLE_PRUNE"),
  EXOS_AGENT_DISABLE_TERMINAL_TITLE: truthy("EXOS_AGENT_DISABLE_TERMINAL_TITLE"),
  EXOS_AGENT_SHOW_TTFD: truthy("EXOS_AGENT_SHOW_TTFD"),
  EXOS_AGENT_DISABLE_AUTOCOMPACT: truthy("EXOS_AGENT_DISABLE_AUTOCOMPACT"),
  EXOS_AGENT_DISABLE_MODELS_FETCH: truthy("EXOS_AGENT_DISABLE_MODELS_FETCH"),
  EXOS_AGENT_DISABLE_MOUSE: truthy("EXOS_AGENT_DISABLE_MOUSE"),
  EXOS_AGENT_FAKE_VCS: process.env["EXOS_AGENT_FAKE_VCS"],
  EXOS_AGENT_SERVER_PASSWORD: process.env["EXOS_AGENT_SERVER_PASSWORD"],
  EXOS_AGENT_SERVER_USERNAME: process.env["EXOS_AGENT_SERVER_USERNAME"],
  EXOS_AGENT_DISABLE_FFF: fff === undefined ? process.platform === "win32" : truthy("EXOS_AGENT_DISABLE_FFF"),

  // Experimental
  EXOS_AGENT_EXPERIMENTAL_FILEWATCHER: Config.boolean("EXOS_AGENT_EXPERIMENTAL_FILEWATCHER").pipe(
    Config.withDefault(false),
  ),
  EXOS_AGENT_EXPERIMENTAL_DISABLE_FILEWATCHER: Config.boolean("EXOS_AGENT_EXPERIMENTAL_DISABLE_FILEWATCHER").pipe(
    Config.withDefault(false),
  ),
  EXOS_AGENT_EXPERIMENTAL_DISABLE_COPY_ON_SELECT:
    copy === undefined ? process.platform === "win32" : truthy("EXOS_AGENT_EXPERIMENTAL_DISABLE_COPY_ON_SELECT"),
  EXOS_AGENT_MODELS_URL: process.env["EXOS_AGENT_MODELS_URL"],
  EXOS_AGENT_MODELS_PATH: process.env["EXOS_AGENT_MODELS_PATH"],
  EXOS_AGENT_DB: process.env["EXOS_AGENT_DB"],

  EXOS_AGENT_WORKSPACE_ID: process.env["EXOS_AGENT_WORKSPACE_ID"],
  EXOS_AGENT_EXPERIMENTAL_WORKSPACES: enabledByExperimental("EXOS_AGENT_EXPERIMENTAL_WORKSPACES"),

  // Evaluated at access time (not module load) because tests, the CLI, and
  // external tooling set these env vars at runtime.
  get EXOS_AGENT_DISABLE_PROJECT_CONFIG() {
    return truthy("EXOS_AGENT_DISABLE_PROJECT_CONFIG")
  },
  get EXOS_AGENT_EXPERIMENTAL_REFERENCES() {
    return enabledByExperimental("EXOS_AGENT_EXPERIMENTAL_REFERENCES")
  },
  get EXOS_AGENT_TUI_CONFIG() {
    return process.env["EXOS_AGENT_TUI_CONFIG"]
  },
  get EXOS_AGENT_CONFIG_DIR() {
    return process.env["EXOS_AGENT_CONFIG_DIR"]
  },
  get EXOS_AGENT_PURE() {
    return truthy("EXOS_AGENT_PURE")
  },
  get EXOS_AGENT_PERMISSION() {
    return process.env["EXOS_AGENT_PERMISSION"]
  },
  get EXOS_AGENT_PLUGIN_META_FILE() {
    return process.env["EXOS_AGENT_PLUGIN_META_FILE"]
  },
  get EXOS_AGENT_CLIENT() {
    return process.env["EXOS_AGENT_CLIENT"] ?? "cli"
  },
}
