import { $ } from "bun"

await $`bun ./scripts/copy-icons.ts ${process.env.EXOS_AGENT_CHANNEL ?? "dev"}`

await $`cd ../exos-agent && bun script/build-node.ts`
