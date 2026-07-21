# ⚡ Exos Agent — سجل إعادة التسمية (Rebrand Notes)

هذا المستودع مبني على سورس [opencode](https://github.com/anomalyco/opencode) v1.18.4 (رخصة MIT — ملف `LICENSE` الأصلي محفوظ كما هو كشرط قانوني).

## هوية البراند

| السياق | قبل | بعد |
|---|---|---|
| الأمر / lower-case | `opencode` | `exos-agent` |
| الاسم الظاهر | `OpenCode` | `Exos Agent` (نصوص) / `ExosAgent` (معرّفات) |
| متغيرات البيئة | `OPENCODE_*` | `EXOS_AGENT_*` |
| سكوب الحزم | `@opencode-ai/*` | `@exos-agent/*` |
| ملف الكونفيج | `opencode.json` | `exos-agent.json` |
| مجلد الكونفيج | `.opencode` | `.exos-agent` |
| الدومين (placeholder) | `opencode.ai` | `exos-agent.ai` ⚠️ غير موجود فعليًا |

## خط الأنابيب

1. **`tools/rebrand.py`** — استبدال واعٍ بحالة الأحرف لكل الملفات المتتبعة (~40 ألف موضع في 2,610 ملف) + إعادة تسمية 179 مسارًا. يدعم `--dry-run` وهو idempotent.
2. **إصلاح المعرّفات** (مرحلة يدوية موثقة في كومت `fb3ae2d`): اقتباس مفاتيح الكائنات `"exos-agent":`، وصول `ID["exos-agent"]`، والمعرّفات العارية → `exosAgent`.

## استثناءات محفوظة عن قصد

- **`LICENSE`** — حقوق MIT الأصلية (إلزامي).
- **حزم npm خارجية** ليست ملكنا: `opencode-gitlab-auth`، `opencode-poe-auth` (قائمة `PRESERVE` في `rebrand.py`).
- **الأصول الثنائية**: `packages/console/app/.../exos-agent-brand-assets.zip` + فيكسشر PNG — بداخلها لا يزال اسم opencode (TODO: استبدال يدوي بالبراند الجديد).

## حالة التحقق ✅

- أخطاء Parse في tsgo: **صفر** على مستوى الـ monorepo.
- `bun install` ناجح (4,708 حزمة).
- الـ CLI يقلع بشكل سليم (`--version` يعمل، أمر `run` يصل لمرحلة الاتصال بالبوابة).
- فحص الأنواع الكامل (typecheck semantics) لم يكتمل محليًا بسبب ذاكرة الـ sandbox (~2GB) — يُنصح بتشغيله في CI.

## TODO — الخطوات القادمة

1. **بوابة النماذج**: `defaultServer` في `packages/core/src/plugin/provider/exos-agent.ts` يشير إلى `https://console.exos-agent.ai` (placeholder) — وجّهه إلى بوابتك الفعلية.
2. **كتالوج النماذج**: بيانات models.dev تستخدم المفتاح `opencode` لمزوّد النماذج المجانية — إما تصفية التسمية عند الجلب أو تغيير المعرّف نهايةً لنهاية (قرار منتج).
3. **أسماء النماذج الظاهرة** (مثل big-pickle): تُشتق من الكتالوج — تُحسم مع نقطة (2).
4. **الأصول الثنائية للبراند** (zips/png).
5. عند الرفع محليًا: هوك `.husky/pre-push` يحتاج bun في PATH — أو استخدم `git push --no-verify`.
