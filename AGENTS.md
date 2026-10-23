# Repository Instructions

This repository uses the Anti-Slop ruleset for website, UI, copywriting, accessibility, mobile layout, and code-comment work.

<!-- antislop:start -->
## Anti-Slop

Before changing UI or copy, read `antislop.md` and `DESIGN.md`, then load the relevant skill:
- UI / visual: `skills/antislop-ui/SKILL.md`
- Copy & text: `skills/antislop-copywriting/SKILL.md`
- Accessibility: `skills/antislop-human/SKILL.md`
- Mobile / responsive: `skills/antislop-layoutmobile/SKILL.md`
- Code comments: `skills/antislop-code/SKILL.md`
- Core and delivery gate: `skills/antislop/SKILL.md`

Use **During** mode when implementing changes and **After** mode when auditing existing work. Follow the 38 core rules and run the Delivery Gate before describing work as ready. Do not claim a check passed unless it was actually run. Mark unrun checks NOT TESTED.

## BaseNama project constraints

- Preserve the current static HTML/CSS/vanilla JS + Cloudflare Workers assets architecture.
- Keep edits focused; do not rebuild the site or replace the design system without a concrete reason.
- Preserve gallery behavior and source assets, pricing, WhatsApp ordering, SEO and Search Console metadata, existing URL, and existing features.
- Keep the established Clash of Clans fantasy identity. Purple is intentional brand color here; apply Anti-Slop's purpose test rather than mechanically removing it.
- Mobile-first and responsive; keep accessible focus, keyboard interaction, meaningful loading/empty/error states, and reduced-motion support.
- No fake statistics, ratings, testimonials, customer claims, or ghost links.
- No decorative arrow characters or emoji in customer-facing UI.
- Do not add Anti-Slop UI, badges, or a public-facing “AI” feature. It is a development workflow.
- Do not introduce frameworks, runtime dependencies, analytics, backend services, or AI features without explicit approval.
<!-- antislop:end -->
