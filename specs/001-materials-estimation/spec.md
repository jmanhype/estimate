# Feature Specification: EstiMate - AI Materials Estimation for Home Renovations

**Feature Branch**: `001-materials-estimation`
**Created**: 2025-11-30
**Status**: Draft
**Input**: User description: "Create EstiMate - an AI-powered materials estimation app for home renovations that uses computer vision to scan rooms and calculate exact material quantities needed (drywall, paint, tiles, etc.). The app should: (1) Allow users to upload photos of rooms and answer project questions, (2) Generate precise shopping lists accounting for waste, cuts, and user skill level, (3) Learn from project data to improve accuracy for edge cases like uneven walls and complex cuts, (4) Support integration with retailer APIs (Home Depot, Lowe's) for seamless checkout, (5) Provide cost tracking, project timelines, and supplier price comparisons. Target users: DIY enthusiasts (initial) and small contractors (expansion). Monetization: freemium model with $9.99/month pro tier and $50-200/month business accounts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Photo-Based Material Estimation (Priority: P1)

A DIY homeowner wants to paint their living room but doesn't know how much paint to buy. They open EstiMate, upload 3-4 photos of the room, answer basic questions (ceiling height, door/window count), and receive an accurate estimate showing they need 2 gallons of paint plus primer, accounting for a 10% waste buffer based on their self-reported "beginner" skill level.

**Why this priority**: This is the core value proposition - solving the primary pain point of material waste through overbuying or project delays through underbuying. Without this capability, the app has no purpose.

**Independent Test**: Can be fully tested by uploading room photos, providing room details, and verifying the generated shopping list matches expected quantities within 10% accuracy for standard rectangular rooms.

**Acceptance Scenarios**:

1. **Given** a user with photos of a room, **When** they upload 3-4 photos and answer dimension questions (ceiling height, room measurements), **Then** the system generates a materials list for painting including paint volume, primer volume, and supplies (brushes, tape, drop cloths).
   - **Accessibility**: Photo upload component is keyboard accessible (Enter to trigger file picker), upload progress announced to screen readers, error states for file size/format have aria-live announcements.

2. **Given** a beginner DIY user, **When** they select "beginner" skill level, **Then** the waste buffer increases to 15% and the shopping list includes additional materials to account for mistakes.
   - **Accessibility**: Skill level radio buttons/dropdown keyboard navigable, selection announced to screen readers, help text explaining skill levels has adequate contrast.

3. **Given** a user uploading photos of a bathroom, **When** they select "tile installation" as project type, **Then** the system calculates tile quantity, grout, thinset, and spacers needed based on visible floor area.
   - **Accessibility**: Project type selector has clear focus indicators, descriptive labels for each option, selected state announced to assistive technologies.

4. **Given** a user with an irregularly shaped room, **When** they upload photos showing angled walls or non-standard features, **Then** the system prompts for additional measurements or photos to improve accuracy.
   - **Accessibility**: Additional measurement prompts have associated labels, validation errors keyboard accessible and screen reader compatible.

---

### User Story 2 - Shopping List with Waste Calculations (Priority: P1)

A homeowner planning to install flooring in two bedrooms uploads photos, answers questions about the material type (hardwood vs laminate vs tile), and receives a detailed shopping list showing exactly how many boxes of flooring they need, including waste calculations for cuts and pattern matching, broken down by room with a total summary.

**Why this priority**: The shopping list is the actionable output that prevents costly mistakes. This is what users take to the store or use for online ordering, making it essential for MVP viability.

**Independent Test**: Can be tested by providing room photos for a flooring project, verifying the shopping list includes per-room breakdowns, waste percentages, and matches manual calculations within 5%.

**Acceptance Scenarios**:

1. **Given** a user with a flooring project, **When** they complete the estimation, **Then** they receive a shopping list showing total square footage, waste percentage (typically 10-15% for flooring), number of boxes needed, and cost estimate.
   - **Accessibility**: Shopping list table has proper table headers, data cells associated with headers (scope attributes), summary information announced to screen readers.

2. **Given** a multi-room project, **When** the user adds multiple rooms, **Then** the shopping list consolidates materials across all rooms and shows both per-room and total quantities.
   - **Accessibility**: Expandable/collapsible room sections keyboard accessible (Enter/Space to toggle), expand/collapse state announced to screen readers.

3. **Given** a user who wants to save their shopping list, **When** they click "Save List", **Then** the system stores the list and allows them to access it later, email it, or export as PDF.
   - **Accessibility**: Save button has descriptive text, success/failure messages announced via aria-live, focus management for modal dialogs.

4. **Given** a user reviewing their shopping list, **When** they view material line items, **Then** each item shows quantity, unit (boxes, gallons, sq ft), waste factor applied, and estimated cost range.
   - **Accessibility**: Line item details readable by screen readers in logical order, cost information properly formatted for currency screen reader pronunciation.

---

### User Story 3 - Project Type Templates (Priority: P2)

A user wants to renovate their kitchen and selects "Kitchen Renovation" from a list of common project types. The app guides them through uploading photos of specific areas (walls for backsplash, floor, cabinets) and automatically structures the estimation for multiple material types - backsplash tiles, countertop square footage, flooring, paint - providing a comprehensive materials list for the entire project.

**Why this priority**: While not essential for initial launch, project templates significantly improve user experience for complex multi-material projects and reduce the learning curve. This bridges the gap between simple single-material estimates (P1) and advanced features (P3).

**Independent Test**: Can be tested by selecting a project template, following the guided workflow, and verifying that all expected material categories are included in the final shopping list.

**Acceptance Scenarios**:

1. **Given** a user starting a new estimate, **When** they select "Kitchen Renovation" template, **Then** the system prompts for photos and measurements for backsplash area, floor area, wall area, and cabinet area.
   - **Accessibility**: Template selector keyboard navigable, visual previews have alternative text, multi-step wizard indicates current step to screen readers.

2. **Given** a user following a project template, **When** they complete all required inputs, **Then** the shopping list is organized by project area (backsplash, flooring, walls) with subtotals and a grand total.
   - **Accessibility**: Organized list structure uses semantic headings (h2/h3), subtotals clearly labeled and associated with their sections.

3. **Given** a user who wants to customize a template, **When** they remove or add material categories, **Then** the system allows modification while maintaining estimation accuracy for remaining categories.
   - **Accessibility**: Add/remove category buttons keyboard accessible, changes announced to screen readers, confirmation dialogs have focus trap.

---

### User Story 4 - Cost Tracking and Budget Management (Priority: P2)

A DIY enthusiast planning a bathroom remodel has a $5,000 budget. They create an estimate in EstiMate, which shows their materials will cost approximately $3,200. As they shop, they mark items as "purchased" and enter actual costs. The app tracks their spending against the budget and alerts them when they're approaching or exceeding their limit.

**Why this priority**: Budget management is a key differentiator from basic calculator tools and addresses the pain point of cost overruns. This feature converts EstiMate from a one-time estimation tool into a project companion.

**Independent Test**: Can be tested by setting a project budget, generating an estimate, marking items as purchased with actual costs, and verifying budget tracking accuracy and alerts.

**Acceptance Scenarios**:

1. **Given** a user creating a project, **When** they set a budget of $5,000, **Then** the initial estimate shows projected costs and remaining budget.
   - **Accessibility**: Budget input field has associated label, currency formatting announced correctly by screen readers, budget meter/progress bar has accessible name and value.

2. **Given** a user shopping for materials, **When** they mark an item as "purchased" and enter the actual cost, **Then** the app updates actual spend, compares to estimated cost, and recalculates remaining budget.
   - **Accessibility**: Purchase checkbox keyboard accessible, cost input field validated with accessible error messages, budget update announced to screen readers.

3. **Given** a user approaching their budget limit, **When** actual spending reaches 90% of budget, **Then** the system displays a warning and suggests areas to reduce costs (lower-cost alternatives, reducing waste buffer).
   - **Accessibility**: Warning alerts use aria-live="assertive" for immediate announcement, warnings have adequate color contrast, icon-only warnings include text alternatives.

4. **Given** a user who has completed purchases, **When** they view the project summary, **Then** they see a comparison of estimated vs actual costs with variance analysis.
   - **Accessibility**: Summary data presented in accessible table format, visual charts include data tables or text equivalents, positive/negative variances indicated with text not just color.

---

### User Story 5 - Supplier Price Comparisons (Priority: P2)

A cost-conscious homeowner receives their materials estimate for a deck-building project and wants to find the best prices. EstiMate displays real-time pricing from Home Depot, Lowe's, and Menards for each material item, showing total cost comparisons and potential savings. The user can see they'll save $180 by splitting their shopping between two retailers.

**Why this priority**: Price comparison directly addresses the value proposition of reducing project costs by 20%. This feature enhances user retention by providing ongoing value beyond initial estimation.

**Independent Test**: Can be tested by generating an estimate, viewing price comparisons for each item, and verifying that prices are current and accurate within 24 hours of retailer website prices.

**Acceptance Scenarios**:

1. **Given** a user with a completed estimate, **When** they view their shopping list, **Then** each material item shows prices from at least 2 retailers with a "best price" indicator.
   - **Accessibility**: Price comparison table has proper column headers, best price indicator uses text label not just icon/color, sortable columns keyboard accessible.

2. **Given** a user comparing total costs, **When** they view the price comparison summary, **Then** the system shows total cost per retailer and highlights the lowest-cost option.
   - **Accessibility**: Summary highlights use semantic emphasis (<strong>), not just visual styling, savings amounts announced with currency formatting.

3. **Given** a user who wants optimized shopping, **When** they select "Optimize by price", **Then** the system suggests which items to buy from which retailer to minimize total cost, accounting for trip/shipping costs.
   - **Accessibility**: Optimization suggestions presented in accessible list format, retailer assignments clearly labeled, total savings calculation announced to screen readers.

4. **Given** price data that is outdated, **When** prices are more than 48 hours old, **Then** the system displays a "Price may have changed" disclaimer and offers to refresh.
   - **Accessibility**: Disclaimer has adequate contrast, refresh button keyboard accessible, loading state during refresh announced to screen readers.

---

### User Story 6 - Retailer Checkout Integration (Priority: P2)

A user completes their materials estimate for a new fence and wants to purchase immediately. They click "Buy from Home Depot" and EstiMate automatically adds all items to their Home Depot online cart with correct quantities. The user reviews the cart, adjusts if needed, and checks out through Home Depot's website without manually searching for each item.

**Why this priority**: Seamless checkout reduces friction between estimation and purchase, creating a direct path to revenue through affiliate partnerships or API integrations. This is a key monetization enabler.

**Independent Test**: Can be tested by completing an estimate, clicking retailer checkout integration, and verifying all items are correctly added to the retailer's cart with accurate quantities.

**Acceptance Scenarios**:

1. **Given** a user with a completed shopping list, **When** they click "Add to Home Depot Cart", **Then** the system opens the Home Depot website with all items added to cart, matching EstiMate quantities.
   - **Accessibility**: Checkout button has descriptive text indicating external link, new window/tab announced to screen readers, focus management when returning to EstiMate.

2. **Given** a user with retailer account integration, **When** they connect their Home Depot account, **Then** the system can directly add items to their cart without requiring manual login.
   - **Accessibility**: Account connection form fields have labels, OAuth flow keyboard navigable, connection status announced to screen readers.

3. **Given** items that are out of stock, **When** the system attempts to add them to cart, **Then** EstiMate displays an alert showing which items are unavailable and suggests alternatives.
   - **Accessibility**: Out-of-stock alerts use aria-live, alternative suggestions keyboard accessible, unavailable items clearly marked in list.

4. **Given** a user who wants to modify quantities before checkout, **When** they review the retailer cart, **Then** they can adjust quantities and EstiMate's saved list reflects the changes for tracking purposes.
   - **Accessibility**: Quantity adjustment controls keyboard accessible, changes synchronized and confirmed with accessible messaging.

---

### User Story 7 - Project Timeline Planning (Priority: P3)

A homeowner planning a multi-phase renovation creates estimates for each phase (demo, drywall, paint, flooring). EstiMate helps them create a project timeline showing when to order each set of materials and estimated completion dates based on typical DIY timeframes for each task.

**Why this priority**: Timeline planning is valuable for complex projects but not essential for MVP. Most users start with single-phase projects and can manage timing manually.

**Independent Test**: Can be tested by creating a multi-phase project, setting start date, and verifying the timeline shows realistic phase durations and material ordering dates.

**Acceptance Scenarios**:

1. **Given** a user creating a multi-phase project, **When** they define project phases, **Then** the system suggests typical durations for each phase based on project type and size.
   - **Accessibility**: Phase input fields keyboard accessible, date pickers keyboard navigable, suggested durations announced to screen readers.

2. **Given** a user planning material purchases, **When** they view the timeline, **Then** the system shows recommended order dates for each material set to arrive just-in-time for each phase.
   - **Accessibility**: Timeline visualization has text alternative or data table, dates formatted for screen reader pronunciation, milestones clearly labeled.

3. **Given** a user who completes a phase, **When** they mark it complete, **Then** the timeline adjusts subsequent phases and updates material order reminders.
   - **Accessibility**: Phase completion checkbox keyboard accessible, timeline updates announced via aria-live, revised dates communicated to screen readers.

---

### User Story 8 - AI Learning from Project Outcomes (Priority: P3)

After completing a deck-building project, a user returns to EstiMate and provides feedback: "I used exactly what was estimated for lumber, but needed 20% more concrete than predicted because ground was uneven." EstiMate records this feedback, and future concrete estimates for decks include enhanced checks for ground conditions and larger buffers when users indicate uneven terrain.

**Why this priority**: AI learning improves accuracy over time but requires significant user base and data collection infrastructure. This is valuable for long-term competitive advantage but not critical for initial launch.

**Independent Test**: Can be tested by submitting project feedback, verifying it's stored, and checking that future estimates for similar projects incorporate the learning (this may require manual review of estimation algorithms).

**Acceptance Scenarios**:

1. **Given** a user who completed a project, **When** they provide outcome feedback (actual materials used vs estimated), **Then** the system stores the data linked to project type, materials, and conditions.
   - **Accessibility**: Feedback form fields have labels, textarea for notes accessible, submission confirmation announced to screen readers.

2. **Given** accumulated feedback for a specific scenario (e.g., tile in bathrooms), **When** estimation algorithms are updated, **Then** new estimates for similar projects show improved accuracy based on learned patterns.
   - **Accessibility**: Updated estimates indicate data-driven adjustments with accessible explanations, confidence indicators readable by screen readers.

3. **Given** a user viewing an estimate, **When** the estimate includes AI-learned adjustments, **Then** the system displays an indicator showing "Based on 150 similar projects" to build confidence.
   - **Accessibility**: Confidence indicators have descriptive text, not icon-only representation, information accessible to screen readers.

---

### User Story 9 - Contractor Project Quoting (Priority: P3)

A small contractor uses EstiMate to create estimates for client projects. They upload photos from a client's home, generate materials lists, add their labor costs and markup, and export a professional-looking quote PDF branded with their company logo. The quote includes itemized materials, labor, total cost, and project timeline.

**Why this priority**: Contractor features represent a significant revenue opportunity ($50-200/month business accounts) but require different workflow and features than DIY users. This should be developed after establishing product-market fit with DIY segment.

**Independent Test**: Can be tested by creating an estimate with contractor account, adding labor costs and markup, exporting to PDF, and verifying professional formatting and branding options.

**Acceptance Scenarios**:

1. **Given** a contractor user, **When** they create an estimate, **Then** the system allows adding labor costs per task, markup percentages, and profit margins to generate client quotes.
   - **Accessibility**: Labor cost and markup inputs have labels, percentage fields validated accessibly, calculated totals announced to screen readers.

2. **Given** a contractor preparing a client quote, **When** they export to PDF, **Then** the document includes their company branding, professional formatting, terms and conditions, and itemized pricing.
   - **Accessibility**: PDF export generates tagged/accessible PDFs with proper structure, export button keyboard accessible, download progress announced.

3. **Given** a contractor managing multiple client projects, **When** they view their dashboard, **Then** they see all active quotes, accepted projects, and material tracking across clients.
   - **Accessibility**: Dashboard uses semantic structure (headings, lists), project cards keyboard navigable, status indicators have text labels not just colors.

4. **Given** a contractor who wants to track quote-to-close rate, **When** they mark quotes as "accepted", "rejected", or "pending", **Then** the system provides analytics on conversion rates and average project values.
   - **Accessibility**: Analytics charts have data table alternatives, status change controls keyboard accessible, metrics announced to screen readers.

---

### Edge Cases

- **What happens when uploaded photos are too dark or blurry to analyze?** System should detect poor image quality and prompt user to retake photos or manually enter dimensions as fallback.
  - **Accessibility**: Image quality warnings announced to screen readers, retry/manual entry options keyboard accessible.

- **How does the system handle rooms with complex irregular shapes (bay windows, vaulted ceilings, angled walls)?** System should provide manual measurement override options and prompt for additional photos/dimensions for irregular features.
  - **Accessibility**: Manual override controls keyboard accessible, additional measurement prompts clearly labeled for screen readers.

- **What happens when a material item is discontinued or unavailable at all retailers?** System should suggest comparable alternative products based on specifications and price range.
  - **Accessibility**: Discontinued item alerts use aria-live, alternative suggestions keyboard navigable, comparison details accessible.

- **How does the system account for local building codes affecting material requirements?** System should include optional location input and provide disclaimers that estimates may need adjustment for local codes, with links to local building department resources.
  - **Accessibility**: Location input autocomplete keyboard accessible, disclaimer links descriptive and keyboard navigable.

- **What happens when user skill level significantly impacts waste (e.g., first-time tile installer)?** System should provide skill-based waste multipliers and educational content explaining why beginners need larger buffers.
  - **Accessibility**: Educational content accessible (headings, lists), skill level explanations readable by screen readers, help icons have text alternatives.

- **How does the system handle materials sold in non-divisible units (e.g., tile boxes, paint gallons)?** System must round up to next full unit and show both exact calculated amount and actual purchase quantity.
  - **Accessibility**: Rounding explanation accessible, both calculated and actual quantities announced clearly to screen readers.

- **What happens when a user creates an estimate but doesn't purchase for several weeks and prices have changed significantly?** System should track estimate age and prompt users to refresh prices before purchasing if estimate is >7 days old.
  - **Accessibility**: Price refresh prompts use aria-live, refresh controls keyboard accessible, price age clearly communicated.

- **How does the system handle multi-story projects or outdoor projects where GPS/photos can't determine all dimensions?** System should provide manual input mode with guidance on how to measure and what measurements are needed.
  - **Accessibility**: Manual input guidance accessible, measurement instructions have clear structure, help content keyboard navigable.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Estimation (P1)

- **FR-001**: System MUST accept multiple photo uploads (minimum 3, maximum 20 photos per project) in common image formats (JPEG, PNG, HEIC).

- **FR-002**: System MUST extract dimensional data from photos using computer vision to identify walls, floors, ceilings, and boundaries.

- **FR-003**: System MUST prompt users for information that cannot be determined from photos (ceiling height, door/window count, material preferences).

- **FR-004**: System MUST support estimation for common project types including: painting (walls/ceilings), flooring (hardwood, laminate, tile, carpet), tiling (walls, floors), drywall installation, concrete/paving, roofing, decking, and fencing.

- **FR-005**: System MUST calculate material quantities with waste factors based on: material type (different waste rates for paint vs tile vs flooring), installation complexity (pattern matching for tile/flooring adds 10-20% waste), and user skill level (beginner: 15-20%, intermediate: 10-15%, expert: 5-10%).

- **FR-006**: System MUST generate itemized shopping lists showing: material name/description, quantity needed, unit of measure (gallons, sq ft, linear ft, boxes, bags), waste factor applied, and total quantity to purchase.

- **FR-007**: System MUST round up to full units for materials sold in discrete packages (e.g., tile boxes, paint gallons, lumber pieces) and show both calculated amount and actual purchase quantity.

- **FR-008**: System MUST allow users to save projects for later access, modification, and tracking.

#### User Accounts & Monetization (P1)

- **FR-009**: System MUST provide free tier access with limitations: maximum 3 active projects, basic project types only, price comparisons from 2 retailers max.

- **FR-010**: System MUST offer Pro tier subscription ($9.99/month) unlocking: unlimited projects, all project types, advanced features (cost tracking, timeline planning), price comparisons from all integrated retailers, and PDF export.

- **FR-011**: System MUST offer Business tier subscription ($50-200/month based on user count) including Pro features plus: contractor-specific tools (client quote generation, branding customization, multi-client management), team collaboration (share estimates with crew/clients), and analytics (quote-to-close tracking, historical data).

- **FR-012**: Users MUST be able to create accounts, log in, and manage their subscription tier and payment methods.

#### Cost Tracking & Budget Management (P2)

- **FR-013**: System MUST allow users to set project budgets and track estimated costs against budget in real-time.

- **FR-014**: System MUST allow users to mark shopping list items as "purchased" and enter actual costs paid.

- **FR-015**: System MUST calculate and display: budget remaining, variance between estimated and actual costs, and warnings when approaching budget limits (at 90% and 100%).

- **FR-016**: System MUST provide cost summary showing estimated total, actual spend to date, variance by line item, and final total upon project completion.

#### Price Comparison & Integration (P2)

- **FR-017**: System MUST integrate with retailer APIs or web scraping to retrieve current prices for materials from Home Depot and Lowe's at minimum.

- **FR-018**: System MUST display per-item pricing from available retailers, indicate best price, and show total cost comparison across retailers.

- **FR-019**: System MUST provide "optimize by price" functionality that suggests which items to purchase from which retailer to minimize total cost.

- **FR-020**: System MUST support checkout integration allowing users to add their complete shopping list to a retailer's online cart with one click.

- **FR-021**: System MUST update pricing data at least every 48 hours and display data age/freshness to users.

- **FR-022**: System MUST handle out-of-stock scenarios by flagging unavailable items and suggesting alternative products when possible.

#### Project Timeline Planning (P3)

- **FR-023**: System MUST allow users to create multi-phase projects and define task sequences (e.g., demo → drywall → paint → flooring).

- **FR-024**: System MUST suggest typical duration ranges for common tasks based on project size and user skill level.

- **FR-025**: System MUST generate project timelines showing phase start/end dates, material order dates, and completion milestones.

- **FR-026**: System MUST allow users to mark phases as complete and automatically adjust subsequent timeline dates.

#### AI Learning & Feedback (P3)

- **FR-027**: System MUST allow users to provide post-project feedback comparing actual materials used versus estimated amounts.

- **FR-028**: System MUST store project outcome data (estimated vs actual quantities, project conditions, user skill level, completion status) for analysis.

- **FR-029**: System MUST use aggregated project feedback to improve estimation accuracy for future similar projects through machine learning algorithms.

- **FR-030**: System MUST display confidence indicators on estimates showing "Based on N similar projects" when AI learning has been applied.

#### Contractor Features (P3)

- **FR-031**: Business tier users MUST be able to add labor costs, markup percentages, and profit margins to material estimates to generate client quotes.

- **FR-032**: Business tier users MUST be able to export professional quote PDFs with custom branding (logo, company name, contact info).

- **FR-033**: Business tier users MUST be able to manage multiple client projects simultaneously with separate tracking for each.

- **FR-034**: Business tier users MUST have access to analytics dashboard showing: total quotes created, quote-to-close conversion rate, average project value, and revenue trends.

## Accessibility Requirements (WCAG 2.1 AA)

All accessibility requirements are **Priority P1** to ensure compliance before initial launch.

### A. Interactive Elements & Keyboard Navigation

- **FR-035**: System MUST support full keyboard navigation for all user flows without requiring a mouse, using standard keyboard interactions:
  - Tab/Shift+Tab for focus movement between interactive elements
  - Enter/Space for activating buttons, links, and controls
  - Escape for closing modals, dropdowns, and canceling operations
  - Arrow keys for navigating within composite widgets (dropdowns, tabs, sliders)
  - Home/End for jumping to first/last items in lists and menus

- **FR-036**: All interactive elements (buttons, links, form inputs, custom controls) MUST have visible focus indicators that:
  - Display a minimum 2px outline or border when focused
  - Meet minimum 3:1 contrast ratio against the background
  - Are clearly distinguishable from non-focused states
  - Are NOT hidden or removed by CSS (outline: none is prohibited without alternative)

- **FR-037**: All interactive elements MUST have minimum touch target size of 44x44 CSS pixels for mobile/touch devices to support users with motor disabilities, including:
  - Buttons and links
  - Form controls (checkboxes, radio buttons, inputs)
  - Photo upload triggers
  - Shopping list action buttons (save, export, mark purchased)

- **FR-038**: All interactive elements MUST have accessible names that clearly describe their purpose:
  - Buttons use descriptive text, not generic labels like "Click here" or "Submit"
  - Icon-only buttons include aria-label or sr-only text
  - Form inputs have associated `<label>` elements or aria-labelledby
  - Links describe destination, not just "Read more" or "Click here"

### B. Visual Design & Color Contrast

- **FR-039**: All text content MUST meet WCAG 2.1 AA color contrast requirements:
  - Normal text (< 18pt or < 14pt bold): minimum 4.5:1 contrast ratio against background
  - Large text (≥ 18pt or ≥ 14pt bold): minimum 3:1 contrast ratio against background
  - Essential icons and graphical elements: minimum 3:1 contrast ratio

- **FR-040**: Information MUST NOT be conveyed by color alone:
  - Status indicators (error, success, warning) include icons or text labels
  - Charts and graphs include patterns or labels in addition to color coding
  - Form validation errors shown with icons and messages, not just red borders
  - Budget warnings (90%, 100%) indicated with text and icons, not just color changes
  - "Best price" indicators use text labels, not just color highlighting

- **FR-041**: Text sizing MUST use relative units (rem, em) rather than pixels to support browser zoom and user font preferences:
  - Base font size defined in rem units
  - Component text sizes scale proportionally with browser zoom
  - System supports browser zoom up to 200% without horizontal scrolling or content loss

- **FR-042**: All animations and transitions MUST respect the `prefers-reduced-motion` media query:
  - Users with motion sensitivity see instant state changes instead of animations
  - Carousels and auto-advancing content pause for reduced-motion users
  - Loading spinners use simpler, less distracting animations

### C. Content Structure & Semantics

- **FR-043**: All page content MUST use semantic HTML5 elements for proper document structure:
  - `<nav>` for navigation menus
  - `<main>` for primary page content
  - `<header>` and `<footer>` for page header/footer
  - `<article>` for self-contained content (project cards, shopping lists)
  - `<section>` for thematic groupings
  - `<aside>` for complementary content (tips, disclaimers)

- **FR-044**: Heading hierarchy MUST be logical and sequential without skipped levels:
  - Each page has exactly one `<h1>` describing the page purpose
  - Headings progress from h1 → h2 → h3 without skipping (no h1 → h3)
  - Headings describe the content that follows
  - Visual styling (size, weight) separated from semantic hierarchy

- **FR-045**: All images MUST have appropriate alternative text:
  - User-uploaded project photos: alt text auto-generated or user-provided describing room features
  - Decorative images: empty alt attribute (`alt=""`) or aria-hidden="true"
  - Informative icons: alt text or aria-label describing function
  - Complex images (charts, diagrams): detailed text alternative or data table equivalent

- **FR-046**: System MUST provide skip navigation links:
  - "Skip to main content" link appears on Tab focus at page top
  - Skips repetitive navigation to jump to primary content
  - Additional skip links for complex pages (skip to results, skip to filters)

### D. Forms & Validation

- **FR-047**: All form inputs MUST have associated labels:
  - `<label>` elements explicitly associated with inputs via `for` attribute
  - Or inputs have `aria-label` or `aria-labelledby` attributes
  - Placeholder text MUST NOT replace labels (placeholders disappear on input)
  - Required fields indicated with text (e.g., "required") not just asterisk

- **FR-048**: Form validation MUST be accessible to screen readers:
  - Error messages use `aria-live="assertive"` or `aria-live="polite"` for announcements
  - Invalid fields have `aria-invalid="true"` attribute
  - Error messages associated with fields via `aria-describedby`
  - Validation occurs both on real-time input and on form submission
  - Success messages also announced to screen readers

- **FR-049**: Error messages MUST be clear, specific, and actionable:
  - Describe what went wrong and how to fix it
  - Located near the relevant input field
  - Programmatically associated with the field
  - Include examples of valid input format when applicable

- **FR-050**: Form submission MUST include accessible loading and success/failure states:
  - Submit button shows loading state with accessible text (not just spinner)
  - Success confirmation announced via aria-live
  - Focus management returns to logical location after submission
  - Errors prevent submission and focus moves to first error

### E. Dynamic Content & ARIA

- **FR-051**: Custom UI components MUST implement proper ARIA roles, states, and properties:
  - Photo upload component: role="button" for upload trigger, aria-busy during upload, upload progress announced
  - Modals/dialogs: role="dialog", aria-modal="true", focus trap, Escape to close
  - Dropdowns/selects: role="combobox" or native `<select>`, arrow key navigation, selected state announced
  - Tabs: role="tablist", "tab", "tabpanel", arrow key navigation, selected tab indicated with aria-selected
  - Accordions: aria-expanded state, Enter/Space to toggle, content associated with trigger
  - Progress bars: role="progressbar", aria-valuenow, aria-valuemin, aria-valuemax, percentage announced
  - Price comparison tables: sortable columns have aria-sort state, sort direction announced

- **FR-052**: Loading states MUST be announced to screen readers:
  - Photo upload progress: aria-live region announces "Uploading photo 2 of 4, 50% complete"
  - Computer vision analysis: aria-live announces "Analyzing photos..." and "Analysis complete"
  - Price refresh: aria-live announces "Updating prices..." and "Prices updated"
  - Page/section loading: aria-busy="true" during load, focus management when complete

- **FR-053**: Error states MUST be accessible:
  - Network failures announced via aria-live="assertive"
  - Form validation errors associated with fields and announced
  - Out-of-stock items flagged with accessible status indicators
  - Image upload errors announced and provide retry option

- **FR-054**: Modal/dialog focus management MUST:
  - Move focus to modal when opened (to close button or first focusable element)
  - Trap focus within modal (Tab/Shift+Tab cycles through modal elements only)
  - Return focus to trigger element when modal closes
  - Close on Escape key press
  - Prevent background scrolling when modal open

### F. Testing & Validation

- **FR-055**: System MUST undergo automated accessibility testing in CI/CD pipeline:
  - axe-core accessibility scanner runs on all primary pages/components
  - Build fails if CRITICAL or HIGH severity issues detected
  - Accessibility tests run before each production deployment
  - Lighthouse accessibility audit score ≥95 for all primary user flows

- **FR-056**: System MUST undergo manual accessibility testing with assistive technologies:
  - NVDA (Windows) testing for all critical user flows
  - JAWS (Windows) testing for complex interactions
  - VoiceOver (macOS/iOS) testing for mobile experience
  - Keyboard-only testing (no mouse) for complete user journeys

- **FR-057**: System MUST include accessibility regression testing:
  - Automated accessibility tests in Playwright/Cypress test suite
  - Visual regression testing for focus indicators
  - Keyboard navigation tested in end-to-end test scenarios
  - Accessibility issues tracked and prioritized in backlog

- **FR-058**: System MUST verify WCAG 2.1 AA compliance before release:
  - Manual WCAG 2.1 Level AA compliance checklist completed
  - All Level A and Level AA success criteria met
  - Accessibility conformance statement published
  - Known issues documented with remediation timeline

#### Security Detail Requirements (P1)

- **FR-059**: System MUST implement CSRF (Cross-Site Request Forgery) protection for all state-changing operations using synchronizer tokens or SameSite cookies.

- **FR-060**: System MUST enforce password policy: minimum 12 characters, at least one uppercase, one lowercase, one number, one special character, and check against HaveIBeenPwned breach database.

- **FR-061**: System MUST use specific TLS 1.3 cipher suites: TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256, TLS_AES_128_GCM_SHA256 (in order of preference).

- **FR-062**: JWT tokens MUST include these claims: `sub` (user_id), `email`, `role`, `tier` (Free/Pro/Business), `iat` (issued at), `exp` (expiration), `iss` (issuer), and MUST be signed with RS256 algorithm.

- **FR-063**: System MUST support concurrent sessions across multiple devices with a maximum of 5 active sessions per user. Users MUST be able to view and revoke active sessions.

- **FR-064**: System MUST implement security incident response procedures including: breach detection alerts, user notification within 72 hours, audit log preservation, and incident timeline documentation.

- **FR-065**: System MUST undergo annual third-party penetration testing covering OWASP Top 10 vulnerabilities with all CRITICAL and HIGH findings resolved before production deployment.

- **FR-066**: System MUST define frontend vs backend validation boundary: frontend provides user experience validation (real-time feedback), backend enforces security validation (data integrity, authorization).

#### Performance Budget Requirements (P1)

- **FR-067**: Frontend JavaScript bundle size MUST NOT exceed 250KB (gzipped) for initial load. Code splitting MUST be implemented to load routes on-demand.

- **FR-068**: Frontend CSS bundle size MUST NOT exceed 50KB (gzipped). Unused Tailwind CSS classes MUST be purged in production builds.

- **FR-069**: Frontend MUST achieve Time-to-Interactive (TTI) ≤ 3.5 seconds and First Contentful Paint (FCP) ≤ 1.2 seconds on 4G mobile networks.

- **FR-070**: All images MUST be optimized with compression, lazy loading below the fold, and responsive srcset for different screen sizes. Photo uploads MUST be resized to maximum 1920px width before storage.

- **FR-071**: API response payloads MUST NOT exceed 500KB for list endpoints. Pagination MUST be implemented with maximum 100 items per page.

- **FR-072**: Third-party scripts (analytics, payment) MUST be loaded asynchronously and defer execution until after page interactive. Total third-party script size MUST NOT exceed 100KB.

- **FR-073**: System MUST implement progressive enhancement: core functionality (estimation, shopping list viewing) MUST work with JavaScript disabled, enhanced features require JavaScript.

- **FR-074**: System MUST support offline viewing of previously loaded projects and shopping lists using service workers and local storage (read-only mode).

- **FR-075**: Cloud provider SLAs MUST be validated and documented: Supabase (99.9% uptime), Railway (99.5% uptime), Vercel (99.99% edge network uptime), Stripe (99.99% API uptime).

### Key Entities *(include if feature involves data)*

- **User**: Represents a registered user account. Attributes include: user ID, email, name, subscription tier (Free/Pro/Business), skill level (beginner/intermediate/expert), account creation date, payment information.

- **Project**: Represents a renovation project. Attributes include: project ID, owner (User), project name, project type (painting, flooring, tiling, etc.), creation date, status (draft/in-progress/completed), budget amount, total estimated cost, total actual cost, photos (collection of ProjectPhoto entities), timeline (collection of ProjectPhase entities).

- **ProjectPhoto**: Represents an uploaded photo for analysis. Attributes include: photo ID, associated Project, image file reference, upload timestamp, analysis metadata (extracted dimensions, room type detection, quality score).

- **ShoppingList**: Represents the calculated materials list for a project. Attributes include: list ID, associated Project, creation date, last updated date, line items (collection of ShoppingListItem entities), total estimated cost.

- **ShoppingListItem**: Represents a single material item in a shopping list. Attributes include: item ID, associated ShoppingList, material name, material category (paint, tile, lumber, etc.), calculated quantity needed, waste factor applied, actual purchase quantity (rounded up to full units), unit of measure, estimated cost, actual cost (if purchased), purchase status (not purchased/purchased), retailer prices (collection of RetailerPrice entities).

- **RetailerPrice**: Represents pricing information from a specific retailer for a material item. Attributes include: price ID, associated ShoppingListItem, retailer name (Home Depot, Lowe's, etc.), unit price, availability status (in stock/out of stock/unknown), last updated timestamp, product URL.

- **ProjectPhase**: Represents a phase or task within a multi-phase project timeline. Attributes include: phase ID, associated Project, phase name, phase type (demo, drywall, paint, etc.), sequence order, estimated start date, estimated end date, estimated duration (days), actual start date, actual end date, status (not started/in progress/completed).

- **ProjectFeedback**: Represents user-submitted feedback after project completion. Attributes include: feedback ID, associated Project, submission date, estimated vs actual comparison (collection of material quantities), completion status, user notes, skill level at time of project, project conditions (e.g., uneven walls, complex cuts).

- **Subscription**: Represents a user's subscription details. Attributes include: subscription ID, associated User, tier (Free/Pro/Business), billing cycle (monthly/annual), price, payment method reference, start date, renewal date, status (active/cancelled/expired).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a basic estimation (photo upload through shopping list generation) in under 5 minutes for simple projects (single room, single material type).

- **SC-002**: Estimation accuracy is within 10% of actual materials needed for 80% of projects with standard rectangular rooms and typical conditions.

- **SC-003**: Users report reducing material waste by 15-20% compared to manual estimation methods or retailer calculators (measured through post-project surveys).

- **SC-004**: Free-to-Pro conversion rate reaches 10% within first 90 days of users creating their first estimate.

- **SC-005**: System supports 10,000 concurrent users without performance degradation (page load times remain under 2 seconds, photo analysis completes within 30 seconds).

- **SC-006**: Price comparison feature demonstrates average savings opportunity of $50+ per project for projects over $500 in materials.

- **SC-007**: Retailer checkout integration successfully transfers 95% of shopping list items to retailer carts without errors or missing items.

- **SC-008**: User satisfaction score (measured via in-app survey) reaches 4.2/5.0 or higher, with primary satisfaction drivers being accuracy, ease of use, and cost savings.

- **SC-009**: For Pro tier users, 60% create more than one project within their first month, indicating ongoing value and engagement.

- **SC-010**: Business tier contractors report 30% reduction in time spent on material takeoff and quote preparation compared to previous methods (measured through user interviews and surveys).

- **SC-011**: AI learning system improves estimation accuracy by 5% over first year as feedback data accumulates (measured by comparing estimates to actual usage for projects with feedback).

- **SC-012**: System maintains 99.5% uptime for core estimation functionality (photo upload, calculation, shopping list generation).

### Accessibility Success Criteria

- **SC-013**: System achieves 100% WCAG 2.1 Level AA automated test pass rate using axe-core accessibility scanner before each production release, with zero CRITICAL or HIGH severity issues.

- **SC-014**: System achieves zero keyboard navigation blockers in critical user flows (account creation, project creation, photo upload, shopping list generation, checkout integration) verified through manual testing.

- **SC-015**: All interactive elements have visible focus indicators meeting 3:1 contrast ratio, verified through automated and manual testing in all supported themes/color modes.

- **SC-016**: Screen reader users (NVDA, JAWS, VoiceOver) can complete core tasks independently without sighted assistance, verified through user testing with screen reader users:
  - Create account and log in
  - Upload photos and create estimation
  - Review shopping list
  - Track budget and mark items purchased
  - Export/save shopping list

- **SC-017**: System achieves Lighthouse accessibility score ≥95 for all primary user flows (homepage, project creation, shopping list, account management).

### Performance Success Criteria

- **SC-018**: Frontend JavaScript bundle size remains ≤250KB (gzipped) with CSS ≤50KB (gzipped) measured in production builds.

- **SC-019**: System achieves TTI ≤3.5s and FCP ≤1.2s on 4G mobile networks (tested with Chrome DevTools throttling).

### Security Success Criteria

- **SC-020**: Zero CRITICAL or HIGH security vulnerabilities reported in annual penetration testing, with all MEDIUM findings addressed within 30 days.

## Assumptions

- **A-001**: Users have smartphones or devices capable of taking clear photos in adequate lighting conditions. Minimum recommended device: iPhone 8 / Android equivalent (2017+) with 12MP camera.

- **A-002**: Retailer APIs (Home Depot, Lowe's) provide programmatic access to product pricing and cart management. If not available, system will use web scraping as fallback, updated every 48 hours.

- **A-003**: Computer vision analysis can achieve 85%+ accuracy for standard residential room dimensions from 3-4 photos. Users can manually override or supplement with measurements.

- **A-004**: Target users (DIY enthusiasts) have basic smartphone literacy and are comfortable uploading photos and filling out simple forms.

- **A-005**: Material waste factors are based on industry-standard estimates: paint 5-10%, flooring 10-15%, tile 10-20%, lumber 5-15% depending on cuts needed. These may need regional or project-specific adjustment.

- **A-006**: Free tier limitations are sufficient to demonstrate value while incentivizing upgrades. Initial limits: 3 active projects, 2 retailer price comparisons, no PDF export.

- **A-007**: Initial launch will support US market only, with materials and retailers common in US. International expansion will require localization of materials database, retailers, and measurement units.

- **A-008**: Contractor (Business tier) pricing of $50-200/month is based on number of user seats: Solo ($50), Small team 2-5 ($100), Medium team 6-15 ($200). This assumes contractors create 10-30 quotes per month and value time savings at $30-50/hour.

- **A-009**: Photo analysis and AI learning features require cloud infrastructure with GPU capabilities for computer vision models. Estimated costs: $0.05-0.10 per estimation for compute.

- **A-010**: Users will tolerate photo analysis time of 15-30 seconds. Analysis runs asynchronously with progress indicator.

- **A-011**: Price comparison data can be cached for 48 hours without significant user dissatisfaction. Real-time pricing lookups would add cost and latency.

- **A-012**: Initial material database will include 500-1000 most common materials across project types. Specialty materials may require manual entry or special requests.

- **A-013**: Screen reader users represent approximately 1-2% of total user base, but accessibility compliance is mandatory for all users including those with low vision, motor disabilities, and cognitive disabilities who benefit from keyboard navigation, high contrast, and clear content structure.

## Non-Goals *(what this feature explicitly does NOT include)*

- **NG-001**: Advanced 3D modeling or architectural CAD features - this is an estimation tool, not design software.

- **NG-002**: Direct contractor hiring or marketplace features - EstiMate focuses on materials estimation, not labor marketplace.

- **NG-003**: Permit assistance or building code compliance checking - users are responsible for understanding local requirements (app may provide general disclaimers and links to resources).

- **NG-004**: Material quality comparison or reviews - the app estimates quantities, not material selection guidance (may link to retailer reviews).

- **NG-005**: Project management features beyond basic timeline and cost tracking - no task assignment, team communication, or complex Gantt charts.

- **NG-006**: Professional estimating features for large commercial construction - target market is residential DIY and small contractors only.

- **NG-007**: Integration with contractor business management software (QuickBooks, ServiceTitan, etc.) - initial version is standalone, integrations may come in future releases.

- **NG-008**: Material procurement or delivery coordination - users purchase through retailer websites/stores independently.

- **NG-009**: Augmented reality (AR) room visualization - while valuable, AR adds complexity and is not essential for MVP estimation functionality.

- **NG-010**: Support for extremely specialized or rare project types (e.g., swimming pool construction, HVAC installation) - focus on common DIY renovation projects first.

## Dependencies

- **D-001**: Computer vision API or machine learning model capable of room dimension extraction from photos. Options include: cloud services (Google Cloud Vision, AWS Rekognition) or custom-trained models. Performance requirement: 85%+ accuracy on standard rooms.

- **D-002**: Retailer API access or web scraping capability for Home Depot and Lowe's product pricing and availability. Fallback to web scraping if APIs unavailable.

- **D-003**: Payment processing integration for subscription management (Stripe or equivalent). Must support monthly/annual billing, tier changes, and automatic renewals.

- **D-004**: Cloud hosting infrastructure with: scalable compute for photo analysis, database for user/project/pricing data (PostgreSQL), caching layer (Redis), object storage for photos (S3 or equivalent).

- **D-005**: Email service for transactional emails (account creation, password reset, subscription confirmations, payment receipts).

- **D-006**: Materials database with specifications, typical units of sale, waste factors, and product categories. Initial population may require manual data entry or scraping from retailer websites.

- **D-007**: Accessibility testing tools and infrastructure: axe-core integration in CI/CD, Lighthouse CI for automated scoring, screen reader testing environment (NVDA, JAWS licenses or VoiceOver on macOS/iOS).

## Open Questions

[None at this time - specification is complete based on provided requirements. Clarifications may emerge during planning or implementation phases.]
