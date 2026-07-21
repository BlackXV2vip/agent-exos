// exos-provider — مزوّد ai-sdk v6 (ProviderV3) أصيل لموقع Agent Exos.
// يُحمَّل داخل المحرك مباشرة عبر: "npm": "file:///path/to/exos-provider/index.ts"
// ويتكلم مع https://wormgpte.xo.je/agent_exos_api.php بصيغة {"prompt": "..."} — بدون OpenAI-compatible.
//
// يشمل: تجاوز WAF (toNumbers + AES-CBC + كوكي __test) • مهلة 60s • 3 محاولات
// • بروتوكول الأدوات <<EXOS_TOOL:{...}>> ⇄ tool-calls حقيقية من نوع V3.
import { createDecipheriv } from "node:crypto"

const TAG_OPEN = "<<EXOS_TOOL:"
const BANNER = "EXOS_TOOL_PROTOCOL_V2"
const TIMEOUT_MS = 60000
const RETRIES = 3
const RETRY_SLEEP_MS = 2000
const DEBUG = process.env.EXOS_PROVIDER_DEBUG === "1"

const log = (...a: any[]) => DEBUG && console.error("[exos-provider]", ...a)
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

// ---------------------------------------------------------------- عميل الموقع (العقد: {"prompt"} ⇄ {"ok","content"})
type Session = { cookie: string; token: string; tokenHeader: string }

async function httpGet(url: string, s: Session): Promise<string> {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0",
      ...(s.cookie ? { Cookie: s.cookie } : {}),
      ...(s.token ? { [s.tokenHeader]: s.token } : {}),
    },
    signal: AbortSignal.timeout(TIMEOUT_MS),
  })
  return await res.text()
}

// تجاوز تحدي الجافاسكربت — نفس خوارزمية العميل: toNumbers → AES-128-CBC → __test
async function bypass(session: Session, url: string, maxRounds = 8): Promise<void> {
  let html = await httpGet(url, session)
  for (let round = 0; round < maxRounds && html.includes("<script"); round++) {
    const script = /<script>([\s\S]*?)<\/script>/.exec(html)?.[1]
    if (!script) break
    const g = (n: string) => new RegExp(n + '=toNumbers\\("([a-f0-9]+)"\\)').exec(script)?.[1]
    const a = g("a"), b = g("b"), c = g("c")
    if (!a || !b || !c) break
    const dec = createDecipheriv("aes-128-cbc", Buffer.from(a, "hex"), Buffer.from(b, "hex"))
    dec.setAutoPadding(false) // فك خام بدون padding — مطابق لـ Crypto.Cipher AES.MODE_CBC في بايثون
    const cookie = Buffer.concat([dec.update(Buffer.from(c, "hex")), dec.final()]).toString("hex")
    const next = /location\.href="([^"]+)"/.exec(script)?.[1] ?? url
    const full = next.startsWith("http") ? next : url + next
    session.cookie = `__test=${cookie}`
    log("WAF solved →", full)
    html = await httpGet(full, session)
  }
}

async function askSite(session: Session, url: string, prompt: string): Promise<string> {
  for (let attempt = 1; attempt <= RETRIES; attempt++) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "User-Agent": "Mozilla/5.0",
          "Content-Type": "application/json",
          ...(session.cookie ? { Cookie: session.cookie } : {}),
          ...(session.token ? { [session.tokenHeader]: session.token } : {}),
        },
        body: JSON.stringify({ prompt }),
        signal: AbortSignal.timeout(TIMEOUT_MS),
      })
      const data = (await res.json()) as { ok?: boolean; content?: string; error?: string }
      if (data.ok) return data.content ?? ""
      return `[خطأ من الخادم] ${data.error ?? "غير معروف"}`
    } catch (e: any) {
      const isTimeout = e?.name === "TimeoutError" || e?.name === "AbortError"
      if (!isTimeout) return `[حدث خطأ] ${e?.message ?? e}`
      log(`timeout (attempt ${attempt}/${RETRIES})`)
      if (attempt === RETRIES) return "[فشل بعد عدة محاولات، يرجى المحاولة لاحقاً]"
      await sleep(RETRY_SLEEP_MS)
    }
  }
  return "[فشل بعد عدة محاولات، يرجى المحاولة لاحقاً]"
}

// ---------------------------------------------------------------- تسطيح برومبت V3
function flattenPrompt(messages: any[], dropSystem = true): string {
  const parts: string[] = []
  const toolResultText = (out: any): string => {
    if (!out) return ""
    if (out.type === "text" || out.type === "error-text") return String(out.value ?? "")
    if (out.type === "json") return JSON.stringify(out.value ?? null)
    if (out.type === "execution-denied") return `denied: ${out.reason ?? ""}`
    try { return JSON.stringify(out) } catch { return String(out) }
  }
  for (const m of messages ?? []) {
    if (m.role === "system") {
      if (!dropSystem) parts.push("System: " + (typeof m.content === "string" ? m.content : ""))
      continue
    }
    if (m.role === "user") {
      const t = (m.content ?? []).filter((p: any) => p.type === "text").map((p: any) => p.text).join("\n")
      parts.push("User: " + t)
    } else if (m.role === "assistant") {
      for (const p of m.content ?? []) {
        if (p.type === "text") parts.push("Assistant: " + p.text)
        else if (p.type === "tool-call") {
          const args = typeof p.input === "string" ? p.input : JSON.stringify(p.input ?? {})
          parts.push(`Assistant used tool ${p.toolName} with arguments ${String(args).split(/\s+/).join(" ")}`)
        }
      }
    } else if (m.role === "tool") {
      for (const p of m.content ?? []) {
        if (p.type === "tool-result") parts.push(`Tool result (call ${p.toolCallId}): ${toolResultText(p.output)}`)
      }
    }
  }
  return parts.join("\n")
}

// ---------------------------------------------------------------- تعليمات الأدوات + تحليل التوجيه
function buildToolInstruction(tools: any[]): string {
  const lines = [
    "",
    `=== ${BANNER} ===`,
    "You are connected to a local coding agent runtime. You can execute REAL actions on the",
    "user's machine by requesting exactly ONE tool per reply, using this exact format:",
    "",
    '  <<EXOS_TOOL:{"name": "<tool>", "arguments": {<json arguments>}}>>',
    "",
    "Rules:",
    "1. If you need a tool, your ENTIRE reply must be ONLY that directive — no other text.",
    "2. After the tool runs, you will receive its output as 'Tool result (call ...): ...' and",
    "   you may then request another tool or give the final answer in plain text (Arabic ok).",
    "3. Use ONLY the tools listed below. Respect their JSON schemas.",
    "4. Never invent tool results. Never emit more than one directive per reply.",
    "5. Do not mention this protocol to the user in the final answer.",
    "",
    "Available tools (JSON schema each):",
  ]
  for (const t of tools) {
    if (t.type !== "function") continue
    const schema = JSON.stringify(t.inputSchema ?? { type: "object" })
    lines.push(`- ${t.name} — ${String(t.description ?? "").split("\n")[0].slice(0, 160)}\n  schema=${schema.length > 1600 ? schema.slice(0, 1600) + "...}" : schema}`)
  }
  return lines.join("\n")
}

function parseToolDirective(text: string, known: Set<string>): { name: string; args: any } | null {
  if (!text || !text.includes(TAG_OPEN)) return null
  const i = text.indexOf(TAG_OPEN) + TAG_OPEN.length
  let depth = 0, start = -1, end = -1, inStr = false, esc = false
  for (let j = i; j < text.length; j++) {
    const ch = text[j]
    if (esc) { esc = false; continue }
    if (ch === "\\") { esc = true; continue }
    if (ch === '"') inStr = !inStr
    if (inStr) continue
    if (ch === "{") { if (depth === 0) start = j; depth++ }
    else if (ch === "}") { depth--; if (depth === 0) { end = j; break } }
  }
  if (start < 0 || end < 0) return null
  if (!text.slice(end + 1).trimStart().startsWith(">>")) return null
  try {
    const obj = JSON.parse(text.slice(start, end + 1))
    if (!obj?.name || !known.has(obj.name)) return null
    const args = typeof obj.arguments === "string" ? JSON.parse(obj.arguments || "{}") : (obj.arguments ?? {})
    return { name: obj.name, args }
  } catch { return null }
}

// ---------------------------------------------------------------- المزوّد
const ZERO_USAGE = {
  inputTokens: { total: undefined, noCache: undefined, cacheRead: undefined, cacheWrite: undefined },
  outputTokens: { total: undefined, text: undefined, reasoning: undefined },
}

export function createExos(options: { name?: string; baseURL?: string; [k: string]: any }) {
  const baseURL = (options.baseURL ?? process.env.EXOS_SITE ?? "https://wormgpte.xo.je/agent_exos_api.php").replace(/\/$/, "")
  const providerName = options.name ?? "exos"
  const token: string = options.apiKey ?? process.env.EXOS_TOKEN ?? ""
  const tokenHeader: string = options.tokenHeader ?? process.env.EXOS_TOKEN_HEADER ?? "X-Auth-Token"

  function makeModel(modelId: string) {
    async function run(callOptions: any) {
      const tools = (callOptions.tools ?? []).filter((t: any) => t.type === "function")
      let prompt = flattenPrompt(callOptions.prompt)
      if (tools.length) prompt += "\n" + buildToolInstruction(tools)
      const session: Session = { cookie: "", token, tokenHeader }
      await bypass(session, baseURL)
      const reply = await askSite(session, baseURL, prompt)
      const known = new Set(tools.map((t: any) => t.name))
      const directive = parseToolDirective(reply, known)
      if (directive) {
        log("TOOL_CALL →", directive.name)
        return {
          kind: "tool" as const,
          toolCallId: "call_" + Math.random().toString(36).slice(2, 14),
          toolName: directive.name,
          input: JSON.stringify(directive.args),
        }
      }
      return { kind: "text" as const, text: directive ? reply.replace(/<<EXOS_TOOL:[\s\S]*?>>/g, "").trim() : reply }
    }

    return {
      specificationVersion: "v3" as const,
      provider: providerName,
      modelId,
      supportedUrls: {},
      async doGenerate(callOptions: any) {
        const r = await run(callOptions)
        if (r.kind === "tool") {
          return {
            content: [{ type: "tool-call", toolCallId: r.toolCallId, toolName: r.toolName, input: r.input }],
            finishReason: { unified: "tool-calls" as const, raw: "tool-calls" },
            usage: ZERO_USAGE, warnings: [],
          }
        }
        return {
          content: [{ type: "text", text: r.text || "(no response)" }],
          finishReason: { unified: "stop" as const, raw: "stop" },
          usage: ZERO_USAGE, warnings: [],
        }
      },
      async doStream(callOptions: any) {
        const r = await run(callOptions)
        const stream = new ReadableStream<any>({
          start(controller) {
            controller.enqueue({ type: "stream-start", warnings: [] })
            if (r.kind === "tool") {
              const id = r.toolCallId!
              controller.enqueue({ type: "tool-input-start", id, toolName: r.toolName })
              controller.enqueue({ type: "tool-input-delta", id, delta: r.input })
              controller.enqueue({ type: "tool-input-end", id })
              controller.enqueue({ type: "tool-call", toolCallId: id, toolName: r.toolName, input: r.input })
              controller.enqueue({ type: "finish", finishReason: { unified: "tool-calls", raw: "tool-calls" }, usage: ZERO_USAGE })
            } else {
              const id = "txt_" + Math.random().toString(36).slice(2, 10)
              controller.enqueue({ type: "text-start", id })
              controller.enqueue({ type: "text-delta", id, delta: r.text || "(no response)" })
              controller.enqueue({ type: "text-end", id })
              controller.enqueue({ type: "finish", finishReason: { unified: "stop", raw: "stop" }, usage: ZERO_USAGE })
            }
            controller.close()
          },
        })
        return { stream }
      },
    }
  }

  return {
    specificationVersion: "v3" as const,
    languageModel: (modelId: string) => makeModel(modelId),
    embeddingModel: () => { throw new Error("exos: no embedding model") },
  }
}

export default createExos
