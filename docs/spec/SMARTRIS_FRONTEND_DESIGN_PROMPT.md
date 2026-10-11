# SmartRIS Frontend Design Engineering Prompt
## Product UI/UX Direction, Interaction Rules, and Implementation Guardrails

> **Purpose:** Use this document as the dedicated frontend design and implementation prompt for SmartRIS.
>
> **Project:** SmartRIS — Programmable Reflecting Surface Simulation and Optimization Platform.
>
> **Primary goal:** Build a minimal, professional, precise scientific interface that feels deliberately designed by an experienced product/design engineer—not a generic AI-generated dashboard.
>
> **Mandatory prerequisite:** Before creating or editing frontend code, find and read the user's existing `agent.md` frontend guardrail completely. Follow it. This prompt does not replace or override it. If `agent.md` is missing or ambiguous, stop frontend implementation and ask the user to provide or identify it.

---

# 1. Your role and mindset

Act as a principal product designer, design engineer, interaction designer, and senior frontend engineer working together.

Do not approach the task as “make a dashboard look modern.” Approach it as designing a professional scientific instrument for a person who needs to configure a model, run an experiment, understand the result, and trust what is displayed.

Think in this order:

1. **Purpose:** What is the user trying to accomplish?
2. **Hierarchy:** What does the user need to notice first?
3. **Clarity:** What must be understood before an action is taken?
4. **Feedback:** How will the interface communicate that an action worked or failed?
5. **Trust:** How will the user distinguish calculated results, assumptions, warnings, and estimates?
6. **Efficiency:** How can repeated work be made faster without hiding important controls?
7. **Consistency:** Do similar interactions behave the same way throughout the application?
8. **Accessibility:** Can the interface be used with a keyboard, at different viewport sizes, and by users with differing visual needs?
9. **Craft:** Are typography, spacing, states, charts, and details consistent and intentional?
10. **Restraint:** What can be removed without making the product harder to use?

The goal is not to impress with decoration. The goal is to make the scientific workflow feel obvious, calm, and reliable.

---

# 2. First action: inspect the project and obey `agent.md`

Before writing frontend code:

1. Inspect the repository structure.
2. Locate the exact `agent.md` file supplied by the user.
3. Read it in full.
4. Extract its requirements for:
   - Framework and component structure.
   - Styling approach.
   - Existing design system.
   - Dependency restrictions.
   - Naming conventions.
   - State management.
   - Accessibility.
   - Responsive design.
   - Testing and validation.
5. Inspect existing frontend source files and package configuration.
6. Identify reusable components and existing working patterns.
7. Write a short plan describing which pages, components, and interactions will be implemented.

**If `agent.md` is missing:** do not create or edit frontend files. Ask the user to provide the file or its exact path. Do not assume what it contains. Backend-only work may continue independently.

**If the repository already has a design system:** reuse it instead of creating a competing one.

**If this prompt conflicts with the user's guardrail:** the user's guardrail wins. Explain material conflicts rather than silently bypassing the rules.

Do not overwrite working files wholesale. Make focused, reviewable changes.

---

# 3. Product definition

SmartRIS is a scientific simulation interface for exploring a simplified programmable reflecting array.

The core workflow is:

1. Configure the array.
2. Choose a target direction.
3. Run a baseline and phase-controlled simulation.
4. Compare the resulting angular patterns.
5. inspect the programmed phase values.
6. Optionally explore a simplified directional communication–observation trade-off.
7. Save or export a result if the backend supports it.

The interface must support that workflow without forcing users to understand every equation before they can begin.

The UI is not:
- A marketing landing page.
- A generic SaaS admin dashboard.
- A chatbot interface.
- A collection of decorative cards.
- A fake real-time monitoring system.
- A hardware control panel pretending to connect to equipment.
- A full-wave electromagnetic solver UI.

Do not use AI-related product language, fake “intelligence” badges, invented performance scores, fake activity feeds, or invented experiment statistics.

---

# 4. Design philosophy

## 4.1 Minimal, not empty

Minimalism means removing visual noise while retaining the information required to perform the task.

Do:
- Keep a clear content hierarchy.
- Use whitespace to group related controls.
- Prefer direct labels over decorative headings.
- Show important scientific units beside their values.
- Use borders and background changes sparingly.
- Keep the most-used workflow easy to reach.
- Use one primary action per workflow.

Do not:
- Remove labels to make the screen look cleaner.
- Hide important units inside tooltips only.
- turn every value into a card.
- use large hero banners inside a working scientific application.
- create large empty panels just to make the layout feel spacious.
- make users hunt for the Run button.
- rely on icons where text would be clearer.

## 4.2 Professional, not sterile

Use a quiet, precise visual language. The product should feel like a well-designed engineering tool.

Prefer:
- A neutral background.
- High-contrast primary text.
- A restrained accent color.
- Subtle separators.
- Clear numerical typography.
- Consistent chart styling.
- Small, deliberate interactions.
- Real empty, loading, error, and success states.

Avoid:
- Neon gradients.
- Glassmorphism as a default.
- Oversized rounded cards everywhere.
- Glowing borders.
- Excessive shadows.
- Decorative 3D shapes.
- Random abstract blobs.
- Confetti or celebratory animations for routine calculations.
- Multiple competing accent colors.
- A “template marketplace” aesthetic.

## 4.3 Avoid generic AI-generated UI patterns

Do not automatically use:
- A giant gradient hero with a slogan.
- Four identical metric cards at the top of every page.
- Rounded cards nested inside other rounded cards.
- An icon beside every heading.
- Emojis as interface icons.
- Excessive pill badges.
- Fake live indicators.
- Random line icons without meaning.
- Generic copy such as “Unlock the power of insights.”
- Invented testimonials or usage statistics.
- A sidebar containing many pages that do not exist.
- Multiple fonts without a strong reason.
- Decorative charts with no analytical purpose.

Every element must have a clear function. If it does not improve understanding, navigation, action, or trust, remove it.

---

# 5. Visual direction

## 5.1 Overall direction

Use a restrained scientific-workbench aesthetic.

The interface should feel:
- Precise.
- Quiet.
- Legible.
- Structured.
- Responsive.
- Credible.
- Focused on data and experimentation.

It should not feel like a consumer social app or a generic analytics template.

## 5.2 Color system

Start with a small neutral palette and one restrained accent.

Suggested direction, subject to `agent.md`:
- Background: very light neutral or warm off-white.
- Main surfaces: white or near-white.
- Primary text: dark charcoal, not absolute black everywhere.
- Secondary text: muted neutral with adequate contrast.
- Borders: subtle cool gray.
- Accent: restrained deep blue or blue-teal.
- Success: muted green used only for actual success.
- Warning: amber used only for actionable warnings.
- Error: restrained red used for errors.

Do not use color as the only way to convey meaning.

Do not invent success states to make the UI feel lively.

If a dark theme is chosen, preserve the same hierarchy and contrast principles rather than simply inverting every color.

## 5.3 Define design tokens

Create a small token system using the project's established styling approach.

Define tokens for:
- Page background.
- Surface background.
- Primary text.
- Secondary text.
- Border.
- Accent.
- Success.
- Warning.
- Error.
- Focus ring.
- Spacing.
- Border radius.
- Typography sizes.
- Chart colors.
- Content width.
- Sidebar width if a sidebar is used.

Do not define dozens of tokens with no practical use. Tokens should reduce inconsistency, not create a second design project.

## 5.4 Typography

Choose one clear interface typeface and, if useful, a monospaced style for numerical or technical values.

Follow existing project conventions where practical.

Typography must establish hierarchy through:
- Size.
- Weight.
- Line height.
- Spacing.
- Color.

Avoid using bold text for every label.

Use tabular numerals for values that need visual comparison, if supported.

Scientific values should remain readable at normal laptop sizes.

Do not use ultra-light text weights for essential data.

Do not use tiny gray text for important instructions or units.

## 5.5 Spacing and layout

Use a consistent spacing scale.

Group related controls together and separate unrelated workflows.

Prefer a clear page grid over arbitrary card placement.

Avoid:
- Uneven gaps with no reason.
- Multiple competing alignments.
- Inconsistent panel padding.
- Excessively wide forms.
- Charts that become too small because of decorative side panels.
- Horizontal overflow at laptop widths.
- Important controls pushed below long decorative content.

Use responsive layouts that adapt without losing the main action or scientific context.

## 5.6 Borders, shadows, and radii

Use borders to define boundaries when needed.

Use shadows sparingly, primarily for overlays or elevation that conveys interaction.

Use a small, consistent set of corner radii.

Avoid giving every input, card, chart, and section a different radius.

Do not add depth merely for decoration.

---

# 6. Information architecture

Keep navigation small and task-oriented.

Recommended pages:

1. **Overview** — brief orientation, backend status, and recent/current working context only if real.
2. **Beam Steering** — the primary simulation workflow.
3. **Trade-off Lab** — the optional directional objective and optimization.
4. **Theory & Model** — equations, definitions, assumptions, and limitations.

If experiment history or exports are implemented, place them where they naturally belong in the existing workflow. Do not create a separate navigation item for a feature that does not exist.

Use clear page names. Avoid branded or cryptic names that require users to learn the product vocabulary.

## 6.1 Navigation behavior

- Keep current location visually clear.
- Make navigation labels explicit.
- Keep the number of items small.
- Ensure keyboard navigation works.
- Do not create nested navigation without a real information-architecture need.
- On small screens, provide a usable navigation pattern that does not dominate the page.
- Do not show disabled or unfinished destinations as if they were available features.

---

# 7. Page specification: Overview

## 7.1 Purpose

The overview page should orient the user and provide a direct path to a simulation. It is not a marketing homepage.

## 7.2 Content hierarchy

1. Product name and concise description.
2. Backend connection state.
3. Primary action: open or start a beam-steering simulation.
4. A concise model note.
5. Optional recent experiments only if real experiment storage exists.

## 7.3 Do not show

- Fake experiment counts.
- Fake user counts.
- Fake uptime.
- Fake “accuracy.”
- Fake real-time RF readings.
- Empty placeholder graphs.
- Decorative KPI cards with no meaningful purpose.

## 7.4 Backend status

Use explicit states:
- Connected.
- Unavailable.
- Checking.
- Unknown, if status cannot be determined.

Do not show “Connected” based only on a hardcoded frontend constant.

If the backend is unavailable, tell the user what the status means and how to retry. Do not turn a connection failure into a vague generic error.

---

# 8. Page specification: Beam Steering

This is the primary page. Spend most of the design effort here.

## 8.1 User's task

The user wants to configure an idealized linear array, select a target direction, run a simulation, and understand how phase control changes the angular pattern.

The page should make this workflow clear without making the user scroll through unnecessary content.

## 8.2 Recommended desktop layout

Use a simple two-column working layout:

- **Configuration column:** a stable, readable width for inputs and the primary action.
- **Results area:** the larger portion of the available width, focused on the angular pattern and comparison.

The chart should be the main visual object because it communicates the core result.

Do not force a three-column layout unless testing demonstrates a clear benefit.

At narrow widths, stack the configuration and results in a deliberate order. Preserve the primary action and result context.

## 8.3 Configuration controls

Provide clear, labeled controls for:
- Element count.
- Operating frequency.
- Element spacing.
- Target angle.
- Reflection magnitude, if supported by the backend.
- Angular resolution or sample count, if useful for the intended user.

Each control must:
- Display its unit.
- Have a sensible default.
- Explain important constraints.
- Use an appropriate input type.
- Validate values.
- Preserve the user's entered values after errors.
- Avoid silently correcting invalid input.

If element spacing is entered as a fraction of wavelength, make the relationship explicit and convert it consistently. Do not mix spacing in metres with spacing in wavelengths without clear labeling.

## 8.4 Primary action

Use one clearly dominant action, such as **Run simulation**.

Requirements:
- The action must call the real backend endpoint.
- Show a loading state while the request is running.
- Prevent duplicate submissions if appropriate.
- Do not fake progress.
- Keep the user's configuration visible.
- Show a clear error if the request fails.
- Distinguish the latest result from any older result.
- Make it easy to rerun after changing parameters.

Do not label a button “Optimize” when it only runs ideal steering phases. Use wording that accurately describes the calculation.

## 8.5 Results hierarchy

Display results in this order:

1. **Angular pattern comparison** — baseline versus controlled.
2. **Target-direction result** — normalized power and relative improvement, if valid.
3. **Phase settings** — per-element values.
4. **Configuration summary** — frequency, wavelength, spacing, element count, and target angle.
5. **Warnings and model notes** — only when relevant, with persistent access to the main limitations.

Do not turn every item into a separate large card.

Use inline metadata, compact metric groups, or restrained panels where appropriate.

## 8.6 Pattern chart

The chart is the central component of the page.

It must:
- Display actual arrays returned by the backend.
- Compare baseline and controlled patterns.
- Label angular position and normalized power.
- Distinguish linear power from dB clearly.
- Provide a legend.
- Allow users to inspect values if supported by the chart library.
- Use consistent axis limits between comparable results.
- Explain any numerical floor applied to dB values.
- Handle empty, loading, and error states.
- Resize well on desktop and smaller screens.
- Avoid excessive gridlines and decoration.
- Preserve chart readability when the legend or tooltips appear.

Do not call normalized array-factor power “received power,” “antenna gain,” or “RCS.”

If both linear and dB views are offered, make the selected view obvious and keep units clear. Do not show two charts by default unless they answer different questions.

## 8.7 Phase display

Show phase values in a compact chart or table.

Requirements:
- Identify each element.
- State whether phase is in degrees or radians.
- Clearly distinguish baseline and controlled phases.
- Use the same element ordering as the backend.
- Make values easy to compare.
- Avoid decorative animation.
- Do not display unlabeled arrays of numbers.

A compact table may be better than a chart when the element count is small. Select the presentation based on readability, not novelty.

## 8.8 Warnings

Warnings should be specific and actionable.

Examples:
- A spacing configuration may be susceptible to grating lobes under the selected scan conditions.
- A metric is unavailable because the baseline value is too close to zero.
- The displayed peak angle is limited by angular sampling.
- The model omits element patterns and mutual coupling.

Do not show generic warnings on every page. Show the relevant warning close to the affected result and explain how the user can respond.

---

# 9. Page specification: Trade-off Lab

## 9.1 Purpose

This page explores a simplified optimization objective that rewards power in a chosen receiver direction and penalizes it in a separate observation direction.

The interface must make the trade-off explicit and must not imply that the calculation proves stealth.

## 9.2 Controls

Provide:
- Receiver direction.
- Observation direction.
- Penalty coefficient.
- Optimization budget or iteration limit, if useful.
- Optional directional-power constraint if implemented.

Explain each control in plain language. Use tooltips or brief inline descriptions only when needed.

Do not put the mathematical equation behind a tooltip if it is central to understanding the experiment. Show the equation in a compact expandable explanation or nearby help section.

## 9.3 Results

Show:
- Initial and optimized patterns.
- Receiver-direction metric before and after.
- Observation-direction metric before and after.
- Objective value before and after.
- Constraint status.
- Evaluation count and stop reason.

Do not display only one success score. The user must be able to see the trade-off between objectives.

## 9.4 Constraint state

Use clear states:
- Satisfied.
- Not satisfied.
- No feasible candidate found within the configured search budget.
- Not applicable, if no constraint was requested.

Do not show green success styling for a failed constraint.

Do not claim a global optimum unless it is proven.

## 9.5 Scientific note

Keep a visible, concise note near the result:

“This experiment uses normalized directional array-factor power as a simplified proxy. It is not a full-wave electromagnetic simulation or a validated radar-cross-section calculation.”

The note should be readable without interrupting the main workflow.

---

# 10. Page specification: Theory & Model

## 10.1 Purpose

Help users understand the model without turning the main simulation page into a textbook.

## 10.2 Content

Explain:
- Frequency and wavelength.
- Phase and interference.
- Linear array geometry.
- Array-factor equation.
- Phase-controlled steering.
- Reflection magnitude.
- Normalized directional power.
- Trade-off objective.
- Assumptions and limitations.

Use clear headings and short sections.

Show equations with properly rendered mathematical notation where supported. Define symbols next to the equation.

## 10.3 Progressive disclosure

The main workflow should not require users to read every derivation.

Provide:
- Short inline explanations near controls.
- More complete derivations on the theory page.
- A persistent route to the assumptions and limitations.

Do not duplicate the entire theory page inside tooltips.

---

# 11. Interaction design

## 11.1 Every action needs a response

For each interactive element, define:
- What the user is trying to do.
- What state changes.
- What network request or calculation occurs.
- What success looks like.
- What failure looks like.
- What the user can do next.

Avoid controls that appear interactive but do nothing.

## 11.2 Forms

- Group related fields.
- Keep labels visible.
- Use appropriate controls for continuous versus discrete values.
- Provide units near the field.
- Show range constraints before an error where practical.
- Preserve input values after failure.
- Do not silently clamp values.
- Avoid validating every keystroke in a way that creates distracting errors.
- Validate again on submission.

## 11.3 Loading

- Use a restrained loading indicator.
- Keep the page layout stable while loading.
- Avoid shifting the entire page when a response arrives.
- Do not invent percentage progress.
- Prevent duplicate requests where appropriate.
- Make the latest request state obvious.

## 11.4 Empty states

An empty state should explain why there is no result and what action creates one.

Examples:
- Before the first simulation: “Configure the array and run a simulation to view its angular pattern.”
- No saved experiments: “No saved experiments yet.”
- No exportable result: explain that a successful simulation is required first.

Do not use a giant illustration or decorative empty-state card.

## 11.5 Errors

Errors should be concise and actionable.

Examples:
- “Could not reach the simulation server. Check that the backend is running and retry.”
- “Element count must be within the supported range.”
- “The phase vector must contain one value per element.”

Avoid generic messages such as “Something went wrong” when more information is available.

Do not expose stack traces in the UI.

## 11.6 Success feedback

Use restrained confirmation for real actions, such as saving an experiment or completing an export.

Do not show a success toast merely because a button was clicked. Confirm success only after the action actually succeeds.

## 11.7 Keyboard and focus

- All controls must be keyboard accessible.
- Focus indicators must be visible.
- Interactive chart controls should be reachable or have an accessible alternative.
- Do not trap focus unexpectedly.
- Do not rely on hover as the only way to reveal important information.

---

# 12. Design system and implementation craft

## 12.1 Tokens

Create or reuse a small design-token system for:
- Colors.
- Typography.
- Spacing.
- Radii.
- Borders.
- Focus states.
- Surface levels.
- Chart colors.
- Content widths.

Do not invent a large design system for four pages.

## 12.2 Components

Create reusable components only where reuse or consistency justifies them.

Likely reusable components:
- App layout.
- Page header.
- Simulation control group.
- Numeric input.
- Metric display.
- Chart panel.
- Loading state.
- Error notice.
- Model limitation note.

Avoid creating a separate component for every one-line wrapper.

Avoid components that accept dozens of unrelated boolean props.

Keep component APIs understandable.

## 12.3 State and data flow

- Keep API calls in a centralized client.
- Keep TypeScript contracts aligned with backend schemas.
- Keep numerical calculations in Python.
- Avoid duplicating derived metrics across components.
- Make loading, error, current result and stale result states explicit.
- Do not use global state unless there is a demonstrated need.
- Follow the state-management guidance in `agent.md`.

## 12.4 Dependency discipline

Before adding a package:
1. Check `agent.md`.
2. Check the existing package manifest.
3. Confirm the package solves a real problem.
4. Check compatibility.
5. Prefer existing dependencies if they are adequate.
6. Update the lockfile.
7. Verify the production build.

Do not add multiple icon libraries, multiple chart libraries, or multiple styling systems.

---

# 13. Responsive behavior

Design and verify at these practical viewport ranges:
- Wide desktop.
- Standard laptop.
- Tablet.
- Narrow mobile.

The exact breakpoints should follow the project's styling conventions.

At desktop widths:
- Use the available space for the chart.
- Keep controls readable.
- Avoid a needlessly wide text column.

At tablet widths:
- Reduce side-by-side complexity.
- Preserve chart labels.
- Keep controls grouped.

At mobile widths:
- Stack controls and results.
- Keep the Run action easy to find.
- Prevent chart overflow.
- Make form fields touch-friendly.
- Avoid horizontally scrolling the whole page.
- Ensure navigation remains usable.
- Avoid sticky panels that cover important content.

Do not rely on screenshots at one viewport as proof of responsive quality.

---

# 14. Accessibility and inclusive design

Meet practical WCAG-oriented standards.

- Use semantic headings in a logical order.
- Associate labels with inputs.
- Maintain sufficient contrast.
- Use visible keyboard focus.
- Ensure keyboard operation.
- Do not convey success or failure using color alone.
- Provide text explanations for chart results.
- Use meaningful accessible names for icon-only controls.
- Respect reduced-motion preferences if motion is used.
- Ensure errors can be discovered by assistive technology.
- Keep text readable at browser zoom.
- Avoid tiny labels for important scientific units.

Accessibility should be built into components rather than added as a final patch.

---

# 15. Scientific trust and visual honesty

This application presents scientific calculations. The UI must distinguish:

- User-entered parameters.
- Derived physical values such as wavelength.
- Model outputs.
- Numerical estimates.
- Warnings.
- Optimization status.
- Model assumptions.
- Physical measurements, if ever added in a future version.

Do not invent measured results.

Do not label normalized array-factor power as:
- Absolute received power.
- Physical antenna gain.
- Measured RCS.
- Experimental stealth performance.

Use exact labels such as:
- “Normalized power”
- “Normalized power (dB)”
- “Estimated main-lobe angle”
- “Optimization constraint”
- “Model limitation”

If a value is unavailable, show that it is unavailable rather than fabricating a number.

If a result comes from a simplified model, communicate that near the result, not only in a separate documentation file.

---

# 16. Content and microcopy

Use short, literal, respectful language.

Good examples:
- “Run simulation”
- “Target angle”
- “Element spacing”
- “Normalized power”
- “Baseline”
- “Phase-controlled”
- “Optimization did not satisfy the constraint”
- “The backend is unavailable”
- “View model assumptions”

Avoid:
- “Unlock powerful insights”
- “Revolutionize your RF workflow”
- “Supercharge your research”
- “Experience next-generation intelligence”
- “Amazing results”
- “Perfect stealth”
- “AI-powered” unless a real AI feature exists and is relevant.

Do not use exclamation marks as a substitute for feedback.

Use sentence case for labels and headings unless the existing design system uses another convention.

---

# 17. Frontend performance

- Avoid unnecessary re-renders for large chart arrays.
- Do not run expensive optimization in the browser if the backend owns it.
- Keep chart updates predictable.
- Avoid loading large libraries that are not used.
- Clean up event listeners and subscriptions.
- Handle unmounted or obsolete requests safely.
- Do not cache scientific results without a clear key and invalidation rule.
- Avoid premature micro-optimizations.
- Measure performance before claiming it is optimized.

---

# 18. Testing and quality assurance

## 18.1 Build checks

Run the project's actual:
- TypeScript check.
- Linter, if configured.
- Unit tests, if configured.
- Production build.

Do not invent npm scripts. Inspect `package.json` first.

## 18.2 Interaction checks

Manually verify:
- Backend connected state.
- Backend unavailable state.
- First-run empty state.
- Successful simulation.
- Changed parameter and rerun.
- Invalid input.
- API failure.
- Trade-off optimization.
- Infeasible constraint.
- Phase display.
- Export if implemented.
- Responsive layout.
- Keyboard navigation.

## 18.3 Visual review

Review screenshots or the running app at:
- Laptop viewport.
- Wider desktop viewport.
- Tablet width.
- Mobile width.

Look for:
- Inconsistent spacing.
- Text wrapping problems.
- Chart labels being cut off.
- Misaligned form fields.
- Excessive card nesting.
- Low contrast.
- Oversized empty regions.
- Competing primary actions.
- Accidental horizontal scrolling.
- Error messages hidden below the fold.

Do not claim visual review if no running app or screenshots were inspected.

---

# 19. Implementation sequence

Work in small, reviewable phases.

## Phase 0 — Inspect and plan
- Read `agent.md`.
- Inspect existing frontend code.
- Identify framework, styling and dependencies.
- Map the required pages and main workflow.
- Confirm API contracts.
- Write a concise plan.

Do not code the frontend if the guardrail file is missing.

## Phase 1 — Foundation
- Establish page shell and navigation.
- Establish typography, spacing and color tokens consistent with the guardrail.
- Add API client and typed contracts.
- Implement real backend status and error states.

## Phase 2 — Primary workflow
- Build beam-steering controls.
- Connect the real backend endpoint.
- Add loading and validation states.
- Render baseline and controlled patterns.
- Display target metrics and phase settings.

## Phase 3 — Secondary workflow
- Build the trade-off page only if the backend endpoint exists.
- Display initial/final values and constraint state.
- Explain the simplified proxy metric.

## Phase 4 — Theory and model
- Add short scientific explanations.
- Link to equations and limitations.
- Keep the main workflow uncluttered.

## Phase 5 — Refinement
- Review responsive behavior.
- Review accessibility.
- Review all empty, loading, error and success states.
- Remove unnecessary visual elements.
- Fix chart readability and spacing.

## Phase 6 — Verification
- Run type checking and production build.
- Run available tests.
- Perform manual interaction checks.
- Review the actual running application.
- Report remaining issues honestly.

---

# 20. Acceptance criteria

The frontend is not complete until all applicable criteria are satisfied.

## Guardrail
- [ ] The actual `agent.md` file was found and read before frontend work.
- [ ] Its requirements were followed.
- [ ] It was not overwritten or bypassed.

## Visual design
- [ ] The interface is minimal and professional.
- [ ] Typography and spacing are consistent.
- [ ] The visual hierarchy is clear.
- [ ] There are no decorative fake metrics.
- [ ] There is no generic gradient-hero template.
- [ ] The interface avoids unnecessary card nesting.
- [ ] The primary workflow is immediately understandable.

## Workflow
- [ ] User can configure an array.
- [ ] User can run a real backend simulation.
- [ ] Loading and error states work.
- [ ] Baseline and controlled results are compared.
- [ ] Phase values are clearly labeled.
- [ ] Results reflect the latest successful request.
- [ ] No interactive-looking control is inert.

## Scientific clarity
- [ ] Units are visible.
- [ ] Normalized power is accurately labeled.
- [ ] The dB floor is explained.
- [ ] Estimates are identified as estimates.
- [ ] The model limitation is visible.
- [ ] No unsupported physical or stealth claim appears.

## Accessibility and responsive design
- [ ] Inputs have labels.
- [ ] Focus is visible.
- [ ] Keyboard navigation works.
- [ ] Errors are understandable.
- [ ] Charts have textual context.
- [ ] The interface works at laptop, tablet and mobile widths.
- [ ] No unintended page-level horizontal overflow occurs.

## Engineering quality
- [ ] API calls are centralized.
- [ ] TypeScript types align with the backend.
- [ ] Scientific formulas are not duplicated in frontend code.
- [ ] No unnecessary dependency was added.
- [ ] Production build succeeds.
- [ ] Actual test results are reported honestly.

---

# 21. Final instructions to the frontend agent

Think like a design engineer responsible for the product's usability, not like a generator trying to fill a screen.

Before adding any component, ask:
1. What task does it support?
2. What information does it communicate?
3. Is it needed at this point in the workflow?
4. Can it be simpler?
5. Does it make the result easier to trust?
6. Does it follow `agent.md`?
7. Can its behavior be tested?

Prefer a small number of excellent screens over many mediocre ones.

Prefer real calculations and clear labels over visual theatrics.

Prefer predictable interactions over novelty.

Prefer consistency over unnecessary customization.

Prefer direct language over marketing copy.

Prefer visible scientific assumptions over exaggerated claims.

**Start by reading `agent.md` and inspecting the existing project. Then implement the beam-steering workflow as the first polished end-to-end experience. Do not create frontend files before the guardrail has been read.**
