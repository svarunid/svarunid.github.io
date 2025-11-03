# AGENTS.md (Client)
This file contains client-specific guidelines for AI coding agents working on the frontend of Zhura.

## Design Guidelines
The section provides guidelines to follow when developing UI components & layouts. Yet at times be creative and take chances to peek out of the guidelines.

### Core Philosophy
**Dense Information Architecture. Minimal Visual Language.**

- Maximum data density without cognitive overload
- Monospace-first typography for tabular alignment
- Systematic color coding for data classification
- Surgical use of whitespace as functional separator
- Zero decorative elements

### Color System
- Adopt a low-saturation palette with high contrast for accessibility (WCAG AA minimum)
- Define 4–6 core colors: neutral grays for backgrounds/text, accents for interactions/states
- Use systematic coding: e.g., blue for positives/links, red for errors/alerts, green for success
- Maintain 80%+ dark mode default for reduced eye strain in prolonged sessions
- Test for color-blindness; provide alternatives like patterns or icons for differentiation

### Typography
- Monospace as the default for UI, tables, and labels
- Mono-blended Sans-serif for headings and longer narrative text
- Maintain tight line-height and consistent vertical rhythm
- Avoid italics, decorative weights, and wide tracking

### Layout & Spacing
- Employ strict 8px grid system for alignment; box elements with subtle borders (1px solid)
- Incorporate dotted/dashed lines for subtle hierarchy over solid shapes
- Maintain consistent gutters (16–24px) and margins (multiples of 8px) for breathing room
- Use whitespace surgically: vertical padding for sections (32–48px), horizontal for cards (16px)
- Structure in linear flows with optional side panels; balance density with zoned whitespace

### Components
- Use flat shapes with sharp edges and clear boundaries for all UI elements
- Convey state changes through color and structural shifts only; avoid animation or shadows
- Design components to feel fast, direct, and obvious—eliminate ambiguity in meaning or affordance
- Prioritize semantic clarity: buttons, cards, and inputs must intuitively signal purpose via form and hue
- Modularize for reuse: define base styles (e.g., 4px border-radius max, 1px stroke weight) adaptable by context

### Responsiveness
- Design fluid grids with 4–12 columns; breakpoints at 480px (mobile), 768px (tablet), 1024px+ (desktop)
- Stack vertically on small screens; use horizontal scroll only for tables with fixed headers
- Adapt typography sizes: reduce 10–20% below 768px; clamp max-width at 1200px
- Test on varied devices; prioritize content reflow over distortion
- Use relative units (rem/em) for scalable sizing; media queries for layout shifts

### Interaction
- Favor subtle animations (200–300ms ease-in-out) for state changes; avoid excess motion
- Use hover/focus states with outline or scale (1.02x) for clarity, not delight
- Group related actions in modular blocks; use progressive disclosure for dense content

## Technical Guidelines
The project is built on [Tailwind CSS](https://tailwindcss.com/) for styling and vanilla HTML & JS along with [Typescript](https://www.typescriptlang.org/), [HTMX](https://htmx.org/), [Alpine.js](https://alpinejs.dev/), [Lit](https://lit.dev/) for the frontend.

### TailwindCSS
Since the project is developed with Python, TailwindCSS will be used through the CLI.

- Use the `tailwindcss -i <input>.css -o <output>.css` command to compile tailwind classes.
  - Add the `-w` flag to re-compile on file changes.
  - Add the `-m` flag to minify the output.

The project uses TailwindCSS v4 that add breaking changes to the previous version. Below are a few major changes:
- Import tailwind using a regular CSS `@import "tailwindcss";` statement, not using the `@tailwind` directives.
- Use native cascade layer `@utility` to define custom utility classes.
```css
@utility tab-4 {
  tab-size: 4;
}
```
- Use CSS variables for all design tokens:
```css
/* In CSS */
.custom-element {
  background-color: var(--color-blue-500);
  font-family: var(--font-sans);
}
```
- Available CSS variable namespaces:
  - `--color-*`: Colors (e.g., `--color-blue-500`)
  - `--font-*`: Font families (e.g., `--font-sans`)
  - `--text-*`: Font sizes (e.g., `--text-xl`)
  - `--font-weight-*`: Font weights (e.g., `--font-weight-bold`)
  - `--spacing-*`: Spacing values (e.g., `--spacing-4`)
  - `--radius-*`: Border radius (e.g., `--radius-md`)
  - `--shadow-*`: Box shadows (e.g., `--shadow-lg`)
- Override entire namespaces or the whole theme:
```css
@theme {
  /* Override all font variables */
  --font-*: initial;
  
  /* Override the entire theme */
  --*: initial;
}
```
- Use container queries with `@container` and container-based breakpoints:
```html
<!-- Create a container context -->
<div class="@container">
  <!-- Elements that respond to container size, not viewport -->
  <div class="@sm:text-lg @md:text-xl @lg:text-2xl">
    Responsive to container
  </div>
</div>
```
- Create custom variants with `@variant` directive:

```css
@variant pointer-coarse (@media (pointer: coarse));
@variant theme-midnight (&:where([data-theme="midnight"] *));
```

Use the `context7` MCP server to with the library ID `/websites/tailwindcss` to refer to all documentation and migration guides.

### Frontend
The frontend has plain old HTML pages and along libraries that provide HTML attribute based JS functionalities (like HTMX & Alpine.js) and custom web components by Lit to promote component/layout reusability and Typescript for implementing JS modules.

It'll also use [Eleventy](https://www.11ty.dev/) for site generation from markdown information and [liquidjs](https://liquidjs.com/) as a template language.

Use pnpm to install dependencies and run scripts.

Use the context7 MCP server to refer to documentation:
- For HTMX use the library ID `/websites/htmx`
- For Alpine.js use the library ID `/websites/alpinejs_dev`
- For 11ty use the library ID `/11ty/11ty-website`

Use [codebase.md](https://codebase.md/lit/lit.dev?ext=md) to refer to the Lit documentation.
You can use query params to filter the results:
- `max_tokens` for maximum number of tokens to include in the result.
- `base_path` to filter for content from a specific directory. For example `packages%2Flit-dev-content%2Fsite%2Fdocs%2Fv3%2Fcomponents`
- `page` to navigate through pages.

Below is the directory sturcture of the lit documentation. Configure the `base_path` based on it:
```
└── packages
    └── lit-dev-content
        └── site
            └── docs
                └── v3
                    ├── components
                    │   ├── decorators.md
                    │   ├── defining.md
                    │   ├── events.md
                    │   ├── index.md
                    │   ├── lifecycle.md
                    │   ├── overview.md
                    │   ├── properties.md
                    │   ├── rendering.md
                    │   ├── shadow-dom.md
                    │   └── styles.md
                    ├── composition
                    │   ├── component-composition.md
                    │   ├── controllers.md
                    │   ├── index.md
                    │   ├── mixins.md
                    │   └── overview.md
                    ├── data
                    │   ├── context.md
                    │   ├── index.md
                    │   ├── signals.md
                    │   └── task.md
                    ├── index.md
                    ├── internal
                    │   ├── demos.md
                    │   └── styles.md
                    ├── libraries
                    │   ├── index.md
                    │   ├── labs.md
                    │   └── standalone-templates.md
                    ├── localization
                    │   ├── best-practices.md
                    │   ├── cli-and-config.md
                    │   ├── index.md
                    │   ├── overview.md
                    │   ├── runtime-mode.md
                    │   └── transform-mode.md
                    ├── releases
                    │   ├── index.md
                    │   └── upgrade.md
                    ├── resources
                    │   ├── community.md
                    │   └── index.md
                    ├── ssr
                    │   ├── authoring.md
                    │   ├── client-usage.md
                    │   ├── dom-emulation.md
                    │   ├── index.md
                    │   ├── overview.md
                    │   └── server-usage.md
                    ├── templates
                    │   ├── conditionals.md
                    │   ├── custom-directives.md
                    │   ├── directives.md
                    │   ├── expressions.md
                    │   ├── index.md
                    │   ├── lists.md
                    │   └── overview.md
                    └── tools
                        ├── adding-lit.md
                        ├── development.md
                        ├── index.md
                        ├── overview.md
                        ├── production.md
                        ├── publishing.md
                        ├── requirements.md
                        ├── starter-kits.md
                        └── testing.md
```
