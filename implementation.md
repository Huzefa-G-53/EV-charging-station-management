# Final EV Charging Admin Dashboard Visualizations Plan

## 1. Problem Analysis of Previous Visualizations

1. **Charger Availability**: Slicing identical counts across stations into 3 equal 33.3% pie slices provided zero insight. What the teacher requested was real-time charger status per station with clear station names and hover details.
2. **Charging Sessions Timeline**:
   - **Why was it a curve and why did it go up/down between two points?**
     Chart.js was configured with cubic Bézier spline interpolation (`tension: 0.35`). When consecutive days had equal values (e.g., 2 sessions on 16 Oct and 2 sessions on 17 Oct), the Bézier curve algorithm calculated control points based on neighboring gradients, causing an artificial downward "sag" between the two identical points. For discrete counts, curves are misleading.
   - **Was power consumed playing any role?**
     No, it was merely plotted as a secondary dashed line on a right-hand Y-axis, creating clutter and confusion. Power consumed is already tracked in its own dedicated Station Energy Delivered chart.
3. **EV Fleet Brand Charging Share**: Removed per user request.

---

## 2. Implemented Redesigned Dashboard: 3 High-Value, Domain-Accurate Charts

The dashboard is structured around 3 operational charts without cluttered dual axes or artificial curve interpolation:

```
+------------------------------------------+------------------------------------------+
| CHART 1 (Stacked Column Bar Chart)       | CHART 2 (Discrete Daily Bar Chart)       |
| Charger Real-Time Status by Station      | Charging Sessions Timeline (Past 7 Days) |
| Station names on X-axis, bay IDs on hover| Discrete daily bars (no dips or curves)  |
+------------------------------------------+------------------------------------------+
| CHART 3 (Full-Width Physical Bar Chart)                                             |
| Station Energy Delivered (Total kWh) Across All Hubs                                |
| Single physical metric (kWh) comparing Delhi, Mumbai, Bengaluru                     |
+-------------------------------------------------------------------------------------+
```

---

### Chart 1: Charger Real-Time Status by Station
* **Chart Type**: **Stacked Column Bar Chart**
* **Fields**:
  - X-Axis: **Station Names** clearly displayed (`Connaught Place (Delhi)`, `BKC Hub (Mumbai)`, `Indiranagar (Bengaluru)`).
  - Stacked Datasets:
    - **Available Bays** (`#10b981` Emerald Green)
    - **In Use (Charging)** (`#3b82f6` Royal Blue)
    - **Under Maintenance** (`#ef4444` Crimson Red)
  - Y-Axis: **Charger Bays** (0, 1, 2, 3, 4 with integer step size).
  - Hover Tooltip: Reveals specific charger IDs (`Available: 3 bays (#2, #3, #4)`, `In Use: 1 bay (#1)`), plus total station capacity.
* **Why this is the correct visualization**:
  - Fulfills teacher's requirement: Station names are clearly written on the X-axis, and hovering shows real-time charger status and specific charger IDs.

---

### Chart 2: Charging Sessions Timeline (Past 7 Days)
* **Chart Type**: **Discrete Daily Column Bar Chart**
* **Fields**:
  - X-Axis: Chronological Dates over the past 7 days (`14 Oct` to `20 Oct`).
  - Y-Axis: **Daily Charging Sessions Completed** (Exact integer scale: 0, 1, 2, 3, 4, 5, 6...).
  - Tooltip: `Sessions: X completed`.
* **Why this is the correct visualization**:
  - Each day has a solid bar of exact height (1, 1, 2, 2, 2, 4, 6) with **zero curves, zero dips, and zero overshooting**.
  - Power consumed has been completely removed from this chart, eliminating the confusing dual-axis clutter.

---

### Chart 3: Station Energy Delivered (Total kWh)
* **Chart Type**: **Full-Width Single-Metric Column Bar Chart**
* **Fields**:
  - X-Axis: Station Names (`Connaught Place (Delhi)`, `BKC Hub (Mumbai)`, `Indiranagar (Bengaluru)`).
  - Y-Axis: **Total Energy Dispensed in kWh** (`SUM(energy_consumed)`).
  - Color: `#0d9488` (Teal) with rounded bar tops.
  - Tooltip: `Total Energy: X kWh across Y sessions`.
* **Why this is the correct visualization**:
  - Pure operational comparison. Every bar represents the exact same physical unit (**kWh**).
  - Spans the full width of Row 2 for maximum readability across all network hubs.
