# Design System — PixelVault

---

## 1. Color Palette

PixelVault uses a dark, cyberpunk-inspired color scheme with purple/indigo primary accents.

| Token | Value | Usage |
|---|---|---|
| Background | `#0f172a` (slate-900) | Page background |
| Surface (glass) | `rgba(255,255,255,0.05)` | Card/panel background |
| Surface border | `rgba(255,255,255,0.08)` | Card borders |
| Primary | Purple → Indigo → Fuchsia gradient | CTAs, active states |
| Text primary | `#f8fafc` (slate-50) | Body text |
| Text muted | `#94a3b8` (slate-400) | Subtext, labels |
| Text dimmed | `#64748b` (slate-500) | Placeholder text |
| Success | `#10b981` (emerald-500) | Positive states, toasts |
| Warning | `#f59e0b` (amber-500) | Medium risk alerts |
| Danger | `#ef4444` (red-500) | Critical alerts, errors |
| Accent purple | `#7c3aed` (violet-600) | Interactive elements |
| Accent cyan | `#06b6d4` (cyan-500) | Notes section |

---

## 2. Primary Gradient (Nebula Grad)

```css
.nebula-grad {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #c026d3 100%);
}
```

Applied to: primary CTA buttons, active badges, score rings.

---

## 3. Typography

- **Font family:** `Outfit` (Google Fonts) — weights 300, 400, 600, 700
- **Fallback:** `sans-serif`
- **Heading sizes:** Tailwind `text-xl` through `text-4xl`
- **Body:** `text-sm` to `text-base`
- **Labels:** `text-xs`, `uppercase`, `tracking-widest`, `font-bold`
- **Monospace (passwords):** `font-mono`, `text-xs`

---

## 4. Glass Morphism

```css
.glass {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
```

Used on: all card containers, modals, nav bars, overlay panels.

---

## 5. Spacing

- Container padding: `p-6` to `p-8`
- Card gap: `gap-4` to `gap-6`
- Section margin: `mb-8` to `mb-12`
- Input padding: `px-4 py-2` to `px-4 py-3`
- Button padding: `px-6 py-3` to `px-8 py-4`

---

## 6. Components

### Navbar
- Fixed-position, glass background, `backdrop-filter: blur`
- Left: PixelVault logo/wordmark
- Right: navigation links (text-sm, hover: text-white) + Logout button
- Logout: `bg-slate-800`, hover: `bg-slate-700`, rounded-lg

### Cards / Panels
- Class: `glass p-6 rounded-2xl`
- Top color accent border for credential health: `border-t-2 border-green-500/50` or `border-red-500/50`
- Hover: `card-hover` (subtle scale + border glow)

### Primary Button (CTA)
- Class: `nebula-grad py-3 px-6 rounded-xl font-bold shadow-lg shadow-purple-500/20`
- Hover: slight brightness increase via Tailwind hover utilities

### Secondary Button
- Class: `bg-slate-800 hover:bg-slate-700 rounded-xl font-bold`

### Form Inputs
```css
background: #0f172a (slate-950 / dark surface)
border: 1px solid #334155 (slate-700)
border-radius: rounded-xl
focus: border-purple-500, outline-none
```

### Modal Overlay
- Full-screen `fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center`
- Modal panel: `glass p-8 rounded-3xl max-w-md w-full`
- Toggled with `classList.toggle('hidden')` / `classList.toggle('flex')`

### Toast Notifications
- Fixed `bottom:20px right:20px`, `z-index:9999`, flex column, `gap:10px`
- Inline styles (not Tailwind) for dynamic color
- Success: `rgba(16,185,129,0.15)` bg + `rgba(16,185,129,0.4)` border
- Error: `rgba(239,68,68,0.15)` bg + `rgba(239,68,68,0.4)` border
- Animation: opacity + translateY transition on `requestAnimationFrame`, auto-remove after 3s

### Tables
- `w-full text-left text-sm`
- Header: `text-xs uppercase tracking-widest text-gray-500 border-b border-white/10`
- Rows: `hover:bg-white/5 transition-colors divide-y divide-white/5`

### Lock Overlay
- Full-page overlay on vault/notes/audit pages before unlock
- Centered card with master-password input + unlock button
- `DOMContentLoaded` auto-removes overlay if session is valid

---

## 7. Password Strength Checklist (Registration)

Shown on `index.html` in register mode only.

```html
<ul id="pwd-checklist">
  <li class="pwd-rule" id="rule-length">8+ characters</li>
  <li class="pwd-rule" id="rule-upper">Uppercase letter</li>
  <li class="pwd-rule" id="rule-lower">Lowercase letter</li>
  <li class="pwd-rule" id="rule-number">Number</li>
  <li class="pwd-rule" id="rule-special">Special character</li>
</ul>
```

Rules get `.met` class applied via `classList.toggle('met', regex.test(v))` on `input` event.

---

## 8. Mode Selector (Stego page)

Tab-style mode switcher:
```javascript
// Active state
document.getElementById(`mode-${mode}`).classList.add('active', 'text-white');
// Inactive
btn.classList.remove('active', 'text-white');
```

---

## 9. Animations

- **Page transitions:** None (MPA — full page load per route)
- **Toast:** opacity + translateY enter/exit with 300ms transition
- **Card hover:** `.card-hover` — `transition-all`, subtle border glow
- **Score ring:** CSS `conic-gradient` updated dynamically via `style.setProperty('background', ...)`
- **Loading state:** `animate-pulse` class applied to result box during extraction

---

## 10. Responsive Rules

The design is desktop-first but includes basic responsive adjustments:
- Grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` on credential/feature grids
- Navbar: horizontal nav hidden on small screens (no mobile menu implemented)
- Modals: `max-w-md w-full mx-4` for small screens
- Stat badges: `sm:w-16 sm:h-16` responsive sizing

> **Note:** Mobile experience is incomplete. No hamburger menu or mobile navigation.
