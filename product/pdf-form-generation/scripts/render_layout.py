#!/usr/bin/env python3
"""
Render the visual layout of a habit-tracker page via Playwright, and record
the pixel coordinates of every fillable-looking element (checkbox squares,
name line, notes box) so a follow-up pypdf pass can overlay REAL AcroForm
widgets exactly on top of them.

Why two passes: Chromium's print-to-PDF path (what Playwright's page.pdf()
calls) rasterizes/vectorizes HTML <input> elements into their visual
appearance only -- it does not emit AcroForm form-field objects. Playwright
alone cannot produce genuinely fillable fields, only realistic-looking static
ink. pypdf is used afterward to add the real interactive widgets.
"""
import json
from playwright.sync_api import sync_playwright

PAGE_W_IN, PAGE_H_IN = 8.5, 11.0
MARGIN_IN = 0.6
CONTENT_W_PX = round((PAGE_W_IN - 2 * MARGIN_IN) * 96)  # 700.8 -> 701

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; }
  body { font-family: Helvetica, Arial, sans-serif; color: #1a1a1a; margin: 0; }
  h1 { font-size: 24px; margin: 0 0 4px 0; }
  .subtitle { font-size: 12px; color: #666; margin: 0 0 20px 0; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #999; padding: 6px; text-align: center; font-size: 11px; }
  th { background: #f0f0f0; }
  .habit-col { text-align: left; width: 22%; }
  .box { width: 18px; height: 18px; border: 1px solid #333; margin: 0 auto; }
  .notes-label { font-size: 12px; margin-top: 24px; margin-bottom: 6px; }
  .notes-box { border: 1px solid #999; height: 90px; width: 100%; }
  .name-row { font-size: 12px; margin-top: 6px; }
  .name-line { display: inline-block; border-bottom: 1px solid #333; width: 220px; height: 16px; }
</style>
</head>
<body>
  <h1>Weekly Habit Tracker</h1>
  <p class="subtitle">Check off each day you complete the habit. Fill in your name and weekly notes below.</p>

  <div class="name-row">Name: <span class="name-line" data-field="name"></span></div>
  <br>

  <table>
    <tr>
      <th class="habit-col">Habit</th>
      <th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th>
    </tr>
    <tr><td class="habit-col">Drink Water</td>
      <td><div class="box" data-field="water_mon"></div></td><td><div class="box" data-field="water_tue"></div></td><td><div class="box" data-field="water_wed"></div></td>
      <td><div class="box" data-field="water_thu"></div></td><td><div class="box" data-field="water_fri"></div></td><td><div class="box" data-field="water_sat"></div></td><td><div class="box" data-field="water_sun"></div></td>
    </tr>
    <tr><td class="habit-col">Exercise</td>
      <td><div class="box" data-field="exercise_mon"></div></td><td><div class="box" data-field="exercise_tue"></div></td><td><div class="box" data-field="exercise_wed"></div></td>
      <td><div class="box" data-field="exercise_thu"></div></td><td><div class="box" data-field="exercise_fri"></div></td><td><div class="box" data-field="exercise_sat"></div></td><td><div class="box" data-field="exercise_sun"></div></td>
    </tr>
    <tr><td class="habit-col">Read 10 Min</td>
      <td><div class="box" data-field="read_mon"></div></td><td><div class="box" data-field="read_tue"></div></td><td><div class="box" data-field="read_wed"></div></td>
      <td><div class="box" data-field="read_thu"></div></td><td><div class="box" data-field="read_fri"></div></td><td><div class="box" data-field="read_sat"></div></td><td><div class="box" data-field="read_sun"></div></td>
    </tr>
    <tr><td class="habit-col">Sleep 7+ Hrs</td>
      <td><div class="box" data-field="sleep_mon"></div></td><td><div class="box" data-field="sleep_tue"></div></td><td><div class="box" data-field="sleep_wed"></div></td>
      <td><div class="box" data-field="sleep_thu"></div></td><td><div class="box" data-field="sleep_fri"></div></td><td><div class="box" data-field="sleep_sat"></div></td><td><div class="box" data-field="sleep_sun"></div></td>
    </tr>
  </table>

  <p class="notes-label">Weekly notes:</p>
  <div class="notes-box" data-field="notes"></div>
</body>
</html>
"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": CONTENT_W_PX, "height": 2000})
        page.set_content(HTML)

        rects = page.eval_on_selector_all(
            "[data-field]",
            "els => els.map(el => { const r = el.getBoundingClientRect(); "
            "return {field: el.getAttribute('data-field'), x: r.x, y: r.y, w: r.width, h: r.height}; })",
        )

        page.pdf(
            path="/tmp/pdf-form-layout.pdf",
            width=f"{PAGE_W_IN}in",
            height=f"{PAGE_H_IN}in",
            margin={"top": f"{MARGIN_IN}in", "bottom": f"{MARGIN_IN}in",
                    "left": f"{MARGIN_IN}in", "right": f"{MARGIN_IN}in"},
            print_background=True,
        )
        browser.close()

    with open("/tmp/pdf-form-fields.json", "w") as f:
        json.dump({
            "page_w_in": PAGE_W_IN, "page_h_in": PAGE_H_IN, "margin_in": MARGIN_IN,
            "rects": rects,
        }, f, indent=2)

    print(f"wrote /tmp/pdf-form-layout.pdf and /tmp/pdf-form-fields.json ({len(rects)} fields)")


if __name__ == "__main__":
    main()
