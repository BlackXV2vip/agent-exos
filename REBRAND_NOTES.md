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
- ✅ **الأصول الثنائية (تمت)**: هوية بصرية جديدة مولّدة بالكامل (سداسية exoskeleton + صاعقة X، بنفسجي → سماوي). استُبدلت: حزمة البراند (16 ملف svg/png + 9 معاينات)، الـ zips الاثنان (بنية نظيفة باسم `Exos Agent Brand Assets`)، أيقونات المواقع الثلاثة (app/console/web: favicon.svg+ico، 96x96، apple-touch، manifest 192/512 ونسخ `-v3`)، كل SVG الشعارات في web/console/lander، أيقونات مزوّد الـ UI، أكثر من 150 أيقونة سطح مكتب (png/ico بكل المقاسات والمنصات)، صور social-share العشرة، لقطات التسويق (lander/web-homepage/help/screenshot-uk.png — حاليًا موك براندي، استبدلها لاحقًا بلقطات حقيقية)، شعارات البريد وVS Code، فيكسشر الـ 5MB (3.24MB ≈ حجم الأصل 3.9MB).
  - ⚠️ متبقٍ: `packages/desktop/icons/**`icon.icns` (3 ملفات — توليدها يحتاج macOS/png2icns).

## حالة التحقق ✅

- أخطاء Parse في tsgo: **صفر** على مستوى الـ monorepo.
- `bun install` ناجح (4,708 حزمة).
- الـ CLI يقلع بشكل سليم (`--version` يعمل، أمر `run` يصل لمرحلة الاتصال بالبوابة).
- فحص الأنواع الكامل (typecheck semantics) لم يكتمل محليًا بسبب ذاكرة الـ sandbox (~2GB) — يُنصح بتشغيله في CI.

## TODO — الخطوات القادمة

1. **بوابة النماذج**: `defaultServer` في `packages/core/src/plugin/provider/exos-agent.ts` يشير إلى `https://console.exos-agent.ai` (placeholder) — وجّهه إلى بوابتك الفعلية.
2. **كتالوج النماذج**: بيانات models.dev تستخدم المفتاح `opencode` لمزوّد النماذج المجانية — إما تصفية التسمية عند الجلب أو تغيير المعرّف نهايةً لنهاية (قرار منتج).
3. **أسماء النماذج الظاهرة** (مثل big-pickle): تُشتق من الكتالوج — تُحسم مع نقطة (2).
4. العلامات الفرعية **zen / go** (`go-ornate-*`, `zen-*` في الأصول والبريد) — تُحسم مع خطوة النماذج.
5. ملفات `.icns` (انظر الاستثناءات أعلاه).
6. عند الرفع محليًا: هوك `.husky/pre-push` يحتاج bun في PATH — أو استخدم `git push --no-verify`.
