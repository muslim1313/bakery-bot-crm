# Frontend UI uchun agent skilllar (qisqa qo‘llanma)

## Nega faqat “chiroyli prompt” yetmaydi?

Bitta UI/UX prompt **vizual tasavvur** beradi, lekin kod yozuvchi agent uchun **barqaror qoidalar** (tipografiya, spacing, rang mantig‘i, layout anti-slop, dark mode, reduced-motion va hokazo) odatda “bir martalik chat matni”da yo‘qoladi. Skill esa **har safar yuklanadigan instruksiya fayli** (`SKILL.md` va bog‘liq data/skriptlar) — agent bir xil standartda chiqaradi, qayta-qayta tushuntirish kamayadi: token, vaqt va “yana gradient/Inter” jarohati kamayadi.

**Amaliy qoida:** promptda *nimani* qurish kerakligini yozing + qaysi skill ustuvor ekanini ayting (masalan landing → `bexa-landing` + kerak bo‘lsa `design-taste-frontend`).

---

## Uchta manba (siz koʻrsatgan)

| Manba | Rol | O‘rnatish |
|--------|-----|-----------|
| **UI UX Pro Max** | Ko‘p platforma/stack bo‘yicha dizayn tizimi, qidiruv va reasoning (CSV data + Python skriptlar) | `npx uipro-cli init --ai cursor` — **loyiha ildizidan** (quyidagi “esloma”ni oʻqing) |
| **Taste Skill** | “Anti-slop” frontend: layout, type, motion, spacing; ko‘plab variantlar (minimalist, redesign, image→code va h.k.) | `npx skills add https://github.com/Leonxlnx/taste-skill -g --all` |
| **Bexa** | Professional, non-generic UI qoidalari (landing, dashboard, mobile, motion) | `npx skills add https://github.com/BekhruzTursunboev/Bexa-professional-frontend-design-skills-for-ai-agents -g --full-depth --all` |

**Agent Skills CLI** ( `npx skills …` ): [Vercel Labs agent-skills](https://github.com/vercel-labs/agent-skills).

---

## Muhim farqlar va tuzatishlar

1. **UI UX Pro Max** — README’dagi eski `uipro init … --global` bayrog‘i **hozirgi `uipro-cli`da yoʻq**. Global o‘xshash natija uchun CLI qayerda ishga tushsa, u yerda `.cursor/skills/` ochiladi — eng aniqi **shu loyiha papkasidan** `npx uipro-cli init --ai cursor -f`.
2. **`npx skills add` bilan `--full-depth`**: Bexa repoda bir nechta skill bor; `--full-depth` siz faqat bitta ildiz skill bilan cheklanishingiz mumkin. To‘liq to‘plam uchun: `-g --full-depth --all`.
3. **PowerShell**: ketma-ket buyruqlar uchun `&&` oʻrniga `;` ishlating.

---

## Bir martalik (global) oʻrnatish namunalari

```powershell
# Taste — barcha skill paketlari (12 ta), global
npx --yes skills add https://github.com/Leonxlnx/taste-skill -g --all

# Bexa — barcha skilllar (6 ta), global; full-depth majburiy
npx --yes skills add https://github.com/BekhruzTursunboev/Bexa-professional-frontend-design-skills-for-ai-agents -g --full-depth --all

# UI UX Pro Max — MUHIM: loyiha ildiziga oʻting, keyin:
cd "C:\path\to\your\project"
npx --yes uipro-cli init --ai cursor -f
```

Python 3.x UI UX Pro Max ichidagi qidiruv skriptlari uchun talab qilinadi (`python --version` tekshiring).

---

## O‘rnatilgan joylar (Windows, ushbu mashinada sinovdan oʻtgan)

- `npx skills add -g` → skill kontenti **`%USERPROFILE%\.agents\skills\`** ostida; Cursor ham universal symlink orqali ulangan.
- `uipro-cli init` **notoʻgʻri papkadan** ishlatilsa, **`%USERPROFILE%\.cursor\.cursor\skills\`** kabi ichki papka paydo boʻlishi mumkin — loyiha ildizidan qayta `init` qiling.

---

## Agentga bitta “baholash uchun” mini-instruksiya namunasi

Quyidagi blokni yangi frontend vazifasiga qoʻshing — skillnomlar agent mavjud skilllar roʻyxoriga mos ravishda yuklanadi:

```
Vazifa: bir sahifalik SaaS landing (hero + 3 ijtimoiy ishonch + pricing + FAQ).

Cheklovlar: React + Tailwind, WCAG AA kontrast, prefers-reduced-motion hurmat qilinadi.

Qoida paketlari (skill mazmuniga amal qil):
- UI UX Pro Max: mahsulot turiga mos dizayn tizimi va rang/tipografiya qarorlarini skill dagi jarayon boʻyicha chiqar.
- Bexa `bexa-landing`: markaziy “AI gradient hero” va generik uchta karta tuzilishidan qoch.
- Taste `design-taste-frontend`: spacing va tipografiya ierarxiyasini premium darajada tut.

Natija: kod + qisqa dizayn qarorlari roʻyxati (nimaga bunday rang/grid).
```

---

*Saqlangan: agentlar uchun UI skilllar va oʻrnatish eslatmalari.*
