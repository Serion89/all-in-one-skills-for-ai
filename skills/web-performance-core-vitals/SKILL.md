---
name: web-performance-core-vitals
description: Frontend performance optimization for Google Core Web Vitals. Use when optimizing Largest Contentful Paint (LCP), Interaction to Next Paint (INP), Cumulative Layout Shift (CLS), reducing bundle sizes, and optimizing critical render paths.
---

# Core Web Vitals & Frontend Performance Optimization

## Purpose
Systematically measure, analyze, and optimize web applications against Google's Core Web Vitals metrics: Largest Contentful Paint (LCP), Interaction to Next Paint (INP), and Cumulative Layout Shift (CLS).

---

## The Core Metric Targets

| Metric | Target (Good) | Primary Root Causes | Diagnostic & Remediation Playbook |
| :--- | :--- | :--- | :--- |
| **LCP** (Largest Contentful Paint) | $\le 2.5	ext{s}$ | Slow server TTFB, render-blocking CSS/JS, lazy-loading hero images | Preload critical hero images (`<link rel="preload">`), eliminate render-blocking fonts, inline critical CSS, ensure TTFB < 600ms. |
| **INP** (Interaction to Next Paint) | $\le 200	ext{ms}$ | Long tasks (>50ms) blocking main thread, heavy event handlers, synchronous DOM mutations | Yield to main thread via `scheduler.yield()` or `requestAnimationFrame()`, defer non-essential work, decouple state updates. |
| **CLS** (Cumulative Layout Shift) | $\le 0.1$ | Images without dimensions, dynamically injected ads, FOIT/FOUT web font swaps | Explicitly define `width` and `height` (or `aspect-ratio`) on all media containers, reserve banner slots, use `font-display: swap`. |

---

## Implementation Playbook

### 1. Hero Image Optimization (LCP)
Never lazy-load the primary hero image:
```html
<!-- CORRECT: Eager load with fetchpriority -->
<img 
  src="/hero-banner.webp" 
  alt="Dashboard Hero" 
  width="1200" 
  height="600" 
  fetchpriority="high" 
  decoding="async"
/>
```

### 2. Breaking Long Tasks (INP)
Yield control back to the browser's event loop during expensive computations:
```javascript
async function processLargeDataset(items) {
  for (let i = 0; i < items.length; i++) {
    processItem(items[i]);
    // Yield every 50 items so user clicks and typing remain responsive
    if (i % 50 === 0 && 'scheduler' in window && 'yield' in scheduler) {
      await scheduler.yield();
    }
  }
}
```

### 3. Font Optimization
Prevent layout shifts during font loading:
```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-display: swap;
  font-weight: 400 700;
}
```
