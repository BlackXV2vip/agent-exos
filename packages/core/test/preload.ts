import path from "path"

process.env.EXOS_AGENT_DB = ":memory:"
process.env.EXOS_AGENT_MODELS_PATH = path.join(import.meta.dir, "plugin", "fixtures", "models-dev.json")
process.env.EXOS_AGENT_DISABLE_MODELS_FETCH = "true"
