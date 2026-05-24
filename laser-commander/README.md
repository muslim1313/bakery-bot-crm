# Universal AI Laser Commander

Phase 1: statik UI va modullar (uskuna profillari, material heuristikasi, Object→CAD stub).

Bu repozitoriy **Bakery Mini App bilan bog‘liq emas** — alohida GitHub loyiha sifatida ishlating.

## Loyiha tuzilishi

- `index.html` — asosiy interfeys
- `style.css` — stillar
- `laser-app.js` — marshrutlash va DOM
- `laser-modules/` — profillar, materiallar, aqlli parametrlar, masshtablash kontrakti

## Mahalliy ko‘rish

Statik server kerak (ES modules uchun):

```bash
npx --yes serve .
```

Brauzerda ochilgan URL ni oching.

## GitHub Pages

Repo **Root** yoki **`docs/`** papkasidan hosting qilinganda `index.html` ildizda bo‘lishi kerak.

## Keyingi bosqichlar

Backend inference, DXF chiqishi, CypCut / uskuna bridge — keyingi relizlar.
