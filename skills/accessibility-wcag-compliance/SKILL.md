---
name: accessibility-wcag-compliance
description: Web accessibility engineering compliant with WCAG 2.2 Level AA standards. Use when implementing accessible keyboard navigation, focus management, ARIA landmark roles, semantic heading hierarchy, color contrast verification, and screen reader testing.
---

# Web Accessibility (WCAG 2.2 Level AA) Engineering

## Purpose
Build inclusive, accessible web interfaces that comply with Web Content Accessibility Guidelines (WCAG 2.2 AA) and Section 508 legal standards.

---

## Core Technical Requirements

### 1. Keyboard Navigation & Focus Management
Every interactive control MUST be operable via keyboard alone (`Tab`, `Shift+Tab`, `Enter`, `Space`, `Escape`, and arrow keys).
- **Focus Indicators**: Never disable focus outlines with `outline: none` without providing an equally visible custom focus ring (`:focus-visible`).
- **Focus Trapping**: In modal dialogs, trap keyboard focus within the dialog container while open. On close, return focus to the trigger button that launched it.
- **Skip Links**: Provide a top-level skip link allowing screen-reader and keyboard users to bypass repetitive navigation:
  ```html
  <a href="#main-content" class="sr-only focus:not-sr-only">Skip to main content</a>
  ```

### 2. Semantic Structure & Landmark Roles
Use native HTML5 elements before reaching for ARIA attributes:
- Prefer `<button>` over `<div role="button">`.
- Use native `<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, and `<article>`.
- **Heading Order**: Strictly hierarchical (`<h1>` -> `<h2>` -> `<h3>`). Never skip levels for visual sizing; use CSS classes for typography scale.

### 3. Form Accessibility
Every input field MUST have an associated programmatic label:
```html
<label for="user-email">Email Address</label>
<input 
  id="user-email" 
  type="email" 
  name="email" 
  aria-describedby="email-hint email-error" 
  aria-invalid="false"
/>
<span id="email-hint" class="text-sm text-gray-500">We will never share your email.</span>
<span id="email-error" class="text-sm text-red-500" role="alert"></span>
```

### 4. Color Contrast Standards
- **Standard Text**: Contrast ratio must be at least **4.5:1** against the background.
- **Large Text** ($\ge 24	ext{px}$ or $\ge 18.5	ext{px}$ bold): Contrast ratio must be at least **3:1**.
- **UI Components & Icons**: Focus rings, button borders, and essential graphical elements must achieve at least **3:1**.
