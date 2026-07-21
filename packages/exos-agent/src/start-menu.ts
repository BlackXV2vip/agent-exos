#!/usr/bin/env node
import { spawn, spawnSync } from "child_process"
import fs from "fs"
import path from "path"
import os from "os"

console.log("╔══════════════════════════════════════╗")
console.log("║  EXOS AGENT — BLACKXV2VIP EDITION     ║")
console.log("╚══════════════════════════════════════╝")
console.log("")
console.log("Agent 👨🏻‍💻: مرحباً! اختر طريقة التشغيل:")
console.log("  [1] الطرفية التفاعلية (Terminal Interactive)")
console.log("  [2] تليجرام بوت (Telegram Bot)")
console.log("")

const readline = require("readline").createInterface({
  input: process.stdin,
  output: process.stdout,
})

readline.question("You👤: اختر الرقم (1 أو 2): ", (answer: string) => {
  readline.close()
  const choice = answer.trim()
  if (choice === "1") {
    console.log("Agent 👨🏻‍💻: تشغيل الوضع التفاعلي...")
    const child = spawn("bun", ["run", "--cwd", "packages/exos-agent", "dev"], {
      stdio: "inherit",
      cwd: process.cwd(),
    })
  } else if (choice === "2") {
    console.log("Agent 👨🏻‍💻: تشغيل البوت التليجرامي...")
    console.log("You👤: أدخل توكن البوت (من @BotFather):")
    const readline2 = require("readline").createInterface({ input: process.stdin, output: process.stdout })
    readline2.question("> ", (token: string) => {
      readline2.close()
      console.log("Agent 👨🏻‍💻: البوت متصل — اكتب رسالتك في تليجرام")
      spawn("bash", ["telegram-bot.sh"], { stdio: "inherit", env: { ...process.env, BOT_TOKEN: token.trim() } })
    })
  } else {
    console.log("Agent 👨🏻‍💻: اختيار غير صحيح — افتراضي: الوضع التفاعلي (1)")
    const child = spawn("bun", ["run", "--cwd", "packages/exos-agent", "dev"], { stdio: "inherit", cwd: process.cwd() })
  }
})
