# BaseNama Design Direction

## Product
BaseNama is a creator-owned catalog for custom Clash of Clans base-name artwork. Its purpose is to help visitors browse real designs, understand prices, and contact Mujib through WhatsApp.

## Identity
- Visual identity: Clash of Clans fantasy, with a dark night-world foundation and restrained purple/magenta accents that are already part of the brand.
- The fantasy tone comes from the actual artwork, naming, and typography, not from adding unrelated ornaments to every component.
- Keep the existing brand assets and recognizable look. Anti-Slop is a quality filter, not permission to rebrand the product.

## Audience and priorities
1. Browse real base-name designs quickly, especially on Android phones.
2. Filter and inspect gallery entries without losing context.
3. Understand the existing price tiers and order process.
4. Reach the existing WhatsApp contact path easily.

## Layout and interaction
- Mobile-first. Design for narrow screens first, then reflow for tablet and desktop.
- Preserve the existing drawer navigation, gallery, filters, free-base section, pricing, order steps, testimonials if backed by real assets, FAQ, detail dialogs, and WhatsApp CTAs.
- Keep tap targets comfortable, focus visible, keyboard and Escape behavior functional, and loading/empty/error states understandable.
- Motion is subtle and purposeful. Respect reduced-motion preferences.
- Do not add fake ratings, counters, testimonials, urgency, feature claims, or placeholder links.

## Color and typography
- Keep the current palette as a brand choice, not as a generic AI default. Purple is a BaseNama identity accent; do not spread it to every surface.
- Keep contrast readable for primary, secondary, and muted text.
- Retain the current display/body type roles unless a measured usability issue justifies a change.
- Use gradients, blur, shadows, badges, and glow only where they clarify hierarchy or serve the fantasy identity. Most content surfaces should remain calm and readable.

## Content voice
- Indonesian, direct, friendly, and specific.
- Avoid generic hype, invented claims, emoji decoration, and repeated filler.
- Use clear action labels that explain what happens next.
- Do not use decorative arrow characters in UI copy.

## Technical constraints
- Keep the existing static HTML/CSS/vanilla JavaScript implementation and Cloudflare Workers static-assets architecture.
- Main page: `site/index.html`. Gallery assets and manifest remain in `site/gallery/`.
- Preserve current URL, SEO metadata, Open Graph/Twitter metadata, Google Search Console verification, prices, ordering flow, WhatsApp destination, and existing functionality.
- Do not add a client framework, backend, analytics, AI feature, or third-party runtime dependency without explicit approval.
- Do not modify original/master artwork assets as part of UI cleanup.
- Do not put Anti-Slop branding or a badge on the public website; these are development rules, not customer-facing product features.

## Design dials
- ENERGY: 3/5 - confident fantasy character, without constant visual shouting.
- RHYTHM: 3/5 - a clear hero, compact browsing controls, image-led catalog, and quieter informational sections.
- MOTION: 2/5 - restrained transitions; motion supports state changes and feedback.

## Validation expectations
Before shipping, inspect at narrow mobile, intermediate/tablet, and desktop widths; verify theme behavior, gallery loading, filtering, dialogs, navigation, keyboard focus, reduced motion, and WhatsApp actions. Run available syntax/build checks. Report checks that were not run as NOT TESTED rather than implying success.
