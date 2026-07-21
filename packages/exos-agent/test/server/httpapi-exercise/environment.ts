import { Flag } from "@exos-agent/core/flag/flag"
import { Effect } from "effect"
import path from "path"

const preserveExerciseGlobalRoot = !!process.env.EXOS_AGENT_HTTPAPI_EXERCISE_GLOBAL
export const exerciseGlobalRoot =
  process.env.EXOS_AGENT_HTTPAPI_EXERCISE_GLOBAL ??
  path.join(process.env.TMPDIR ?? "/tmp", `exos-agent-httpapi-global-${process.pid}`)
process.env.XDG_DATA_HOME = path.join(exerciseGlobalRoot, "data")
process.env.XDG_CONFIG_HOME = path.join(exerciseGlobalRoot, "config")
process.env.XDG_STATE_HOME = path.join(exerciseGlobalRoot, "state")
process.env.XDG_CACHE_HOME = path.join(exerciseGlobalRoot, "cache")
process.env.EXOS_AGENT_DISABLE_SHARE = "true"
export const exerciseConfigDirectory = path.join(exerciseGlobalRoot, "config", "exos-agent")
export const exerciseDataDirectory = path.join(exerciseGlobalRoot, "data", "exos-agent")

const preserveExerciseDatabase = !!process.env.EXOS_AGENT_HTTPAPI_EXERCISE_DB
export const exerciseDatabasePath =
  process.env.EXOS_AGENT_HTTPAPI_EXERCISE_DB ??
  path.join(process.env.TMPDIR ?? "/tmp", `exos-agent-httpapi-exercise-${process.pid}.db`)
process.env.EXOS_AGENT_DB = exerciseDatabasePath
Flag.EXOS_AGENT_DB = exerciseDatabasePath

export const original = {
  EXOS_AGENT_SERVER_PASSWORD: Flag.EXOS_AGENT_SERVER_PASSWORD,
  EXOS_AGENT_SERVER_USERNAME: Flag.EXOS_AGENT_SERVER_USERNAME,
}

export const cleanupExercisePaths = Effect.promise(async () => {
  const fs = await import("fs/promises")
  if (!preserveExerciseDatabase) {
    await Promise.all(
      [exerciseDatabasePath, `${exerciseDatabasePath}-wal`, `${exerciseDatabasePath}-shm`].map((file) =>
        fs.rm(file, { force: true }).catch(() => undefined),
      ),
    )
  }
  if (!preserveExerciseGlobalRoot)
    await fs.rm(exerciseGlobalRoot, { recursive: true, force: true }).catch(() => undefined)
})
