
# import os
# import base64
# import io
# import numpy as np
# import pandas as pd

# import dash
# from dash import Dash, html, dcc, dash_table, no_update
# from dash.dependencies import Input, Output, State
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# # -----------------------------
# # App Setup (multi-page)
# # -----------------------------
# app = Dash(__name__, suppress_callback_exceptions=True)
# app.title = "Index Data Analysis"

# # Custom CSS to remove white borders and enhance dark theme
# app.index_string = '''
# <!DOCTYPE html>
# <html>
#     <head>
#         {%metas%}
#         <title>{%title%}</title>
#         {%favicon%}
#         {%css%}
#         <style>
#             * {
#                 margin: 0;
#                 padding: 0;
#                 box-sizing: border-box;
#             }
#             body {
#                 margin: 0;
#                 padding: 0;
#                 border: none !important;
#                 transition: background-color 0.3s ease, color 0.3s ease;
#             }
#             html {
#                 margin: 0;
#                 padding: 0;
#                 border: none !important;
#             }
#             #react-entry-point {
#                 margin: 0;
#                 padding: 0;
#                 border: none !important;
#             }
#             ._dash-loading {
#                 margin: 0;
#                 padding: 0;
#             }
#             #app-container {
#                 transition: background-color 0.3s ease, color 0.3s ease;
#             }
#             #navbar-container {
#                 transition: background-color 0.3s ease, color 0.3s ease;
#             }
#             #page-content {
#                 transition: color 0.3s ease;
#             }
#             /* Upload box hover effect */
#             [id="uploader"]:hover, [id="uploader-a"]:hover, [id="uploader-b"]:hover {
#                 border-color: rgba(0,200,150,0.6) !important;
#                 background: rgba(0,200,150,0.1) !important;
#                 transform: scale(1.01);
#                 box-shadow: 0 4px 16px rgba(0,200,150,0.2) !important;
#             }
#             [id="uploader"]:hover span:last-child, [id="uploader-a"]:hover span:last-child, [id="uploader-b"]:hover span:last-child {
#                 opacity: 1 !important;
#                 transform: scale(1.1);
#             }
#             /* DataTable dark theme styles */
#             .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
#                 background-color: #1a1a1a !important;
#                 color: rgba(255,255,255,0.9) !important;
#             }
#             .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table thead th {
#                 background-color: #252525 !important;
#                 color: rgba(255,255,255,0.95) !important;
#                 border-color: rgba(0,200,150,0.3) !important;
#             }
#             .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody tr {
#                 background-color: #1a1a1a !important;
#             }
#             .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody tr:nth-child(even) {
#                 background-color: #222222 !important;
#             }
#             .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody tr:hover {
#                 background-color: rgba(0,200,150,0.15) !important;
#             }
#             .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody td {
#                 border-color: rgba(255,255,255,0.1) !important;
#                 color: rgba(255,255,255,0.9) !important;
#             }
#             /* Dark theme for form inputs */
#             .Select-control, .Select-input, .Select-placeholder, .Select-value, .Select-value-label {
#                 background-color: rgba(255,255,255,0.1) !important;
#                 color: rgba(255,255,255,0.9) !important;
#                 border-color: rgba(255,255,255,0.2) !important;
#             }
#             .Select-menu-outer {
#                 background-color: #1a1a1a !important;
#                 border-color: rgba(255,255,255,0.2) !important;
#             }
#             .Select-option {
#                 background-color: #1a1a1a !important;
#                 color: rgba(255,255,255,0.9) !important;
#             }
#             .Select-option.is-focused {
#                 background-color: rgba(0,200,150,0.2) !important;
#             }
#             .Select-option.is-selected {
#                 background-color: rgba(0,200,150,0.4) !important;
#             }
#             input[type="text"], input[type="number"], input[type="date"] {
#                 background-color: rgba(255,255,255,0.1) !important;
#                 color: rgba(255,255,255,0.9) !important;
#                 border: 1px solid rgba(255,255,255,0.2) !important;
#                 border-radius: 4px !important;
#                 padding: 6px 8px !important;
#             }
#             input[type="text"]:focus, input[type="number"]:focus, input[type="date"]:focus {
#                 border-color: rgba(0,200,150,0.6) !important;
#                 outline: none !important;
#                 box-shadow: 0 0 0 2px rgba(0,200,150,0.2) !important;
#             }
#             input[type="text"]::placeholder, input[type="number"]::placeholder {
#                 color: rgba(255,255,255,0.5) !important;
#             }
#             .DateInput {
#                 background-color: rgba(255,255,255,0.1) !important;
#             }
#             .DateInput_input {
#                 background-color: rgba(255,255,255,0.1) !important;
#                 color: rgba(255,255,255,0.9) !important;
#                 border-color: rgba(255,255,255,0.2) !important;
#                 font-size: 14px !important;
#                 padding: 8px 10px !important;
#             }
#             .DateInput_input__focused {
#                 border-color: rgba(0,200,150,0.6) !important;
#                 box-shadow: 0 0 0 2px rgba(0,200,150,0.2) !important;
#             }
#             .DateRangePickerInput {
#                 background-color: rgba(255,255,255,0.1) !important;
#                 border-color: rgba(255,255,255,0.2) !important;
#                 border-radius: 4px !important;
#             }
#             .DateRangePickerInput__withBorder {
#                 border-radius: 4px !important;
#             }
#             .DateRangePickerInput__disabled {
#                 background-color: rgba(255,255,255,0.05) !important;
#             }
#             .DateRangePickerInput_arrow {
#                 border-left-color: rgba(255,255,255,0.5) !important;
#             }
#             .DateRangePickerInput_arrow_svg {
#                 fill: rgba(255,255,255,0.7) !important;
#             }
#             /* Fix DatePickerRange clear button overlap */
#             .DateInput__close {
#                 position: absolute !important;
#                 right: 8px !important;
#                 top: 50% !important;
#                 transform: translateY(-50%) !important;
#                 z-index: 10 !important;
#                 background: rgba(255,255,255,0.1) !important;
#                 border-radius: 50% !important;
#                 width: 20px !important;
#                 height: 20px !important;
#                 display: flex !important;
#                 align-items: center !important;
#                 justify-content: center !important;
#                 cursor: pointer !important;
#             }
#             .DateInput__close:hover {
#                 background: rgba(255,255,255,0.2) !important;
#             }
#             .DateInput__close svg {
#                 width: 12px !important;
#                 height: 12px !important;
#             }
#             .DateInput {
#                 position: relative !important;
#                 padding-right: 32px !important;
#             }
#             .DateRangePickerInput__withBorder {
#                 position: relative !important;
#             }
#             .DayPicker {
#                 background-color: #1a1a1a !important;
#                 color: rgba(255,255,255,0.9) !important;
#                 border: 1px solid rgba(255,255,255,0.2) !important;
#                 border-radius: 8px !important;
#             }
#             .DayPicker__week-header {
#                 color: rgba(255,255,255,0.7) !important;
#             }
#             .DayPicker-Day {
#                 color: rgba(255,255,255,0.9) !important;
#             }
#             .DayPicker-Day--selected {
#                 background-color: rgba(0,200,150,0.6) !important;
#                 color: white !important;
#             }
#             .DayPicker-Day--hovered {
#                 background-color: rgba(0,200,150,0.3) !important;
#             }
#             .DayPicker-Day--outside {
#                 color: rgba(255,255,255,0.3) !important;
#             }
#             /* Color-coded radio buttons for Drop (red) and Gain (green) */
#             #window-size-drop input[type="radio"],
#             #min-threshold-drop input[type="radio"],
#             #snap-month-drop input[type="checkbox"] {
#                 accent-color: rgba(239,68,68,0.8) !important;
#             }
#             #window-size-gain input[type="radio"],
#             #min-threshold-gain input[type="radio"],
#             #snap-month-gain input[type="checkbox"] {
#                 accent-color: rgba(34,197,94,0.8) !important;
#             }
#             /* Default accent for other radio/checkboxes */
#             input[type="radio"] {
#                 accent-color: rgba(0,200,150,0.8) !important;
#             }
#             input[type="checkbox"] {
#                 accent-color: rgba(0,200,150,0.8) !important;
#             }
#             /* Improved spacing for radio buttons and inputs */
#             .RadioItems, .Checklist {
#                 margin-bottom: 8px !important;
#             }
#             .RadioItems label, .Checklist label {
#                 margin-right: 12px !important;
#                 margin-bottom: 4px !important;
#             }
#             /* Better visual grouping for custom inputs */
#             input[type="number"] {
#                 margin-top: 4px !important;
#             }
#             /* Responsive grid support */
#             @media (max-width: 768px) {
#                 [style*="gridTemplateColumns"] {
#                     grid-template-columns: 1fr !important;
#                 }
#             }
#             /* Focus states for accessibility */
#             button:focus-visible, input:focus-visible, select:focus-visible {
#                 outline: none !important;
#             }
#             /* Hover states for buttons */
#             button:hover:not(:disabled) {
#                 transform: translateY(-1px);
#                 box-shadow: 0 6px 16px rgba(0,0,0,0.2) !important;
#             }
#             button:active:not(:disabled) {
#                 transform: translateY(0);
#             }
#             /* Disabled state styling */
#             button:disabled, input:disabled, select:disabled {
#                 opacity: 0.5 !important;
#                 cursor: not-allowed !important;
#             }
#             /* Improved input heights for consistency */
#             input[type="text"], input[type="number"] {
#                 height: 40px !important;
#                 min-height: 40px !important;
#             }
#             /* Card hover effect */
#             [style*="background"][style*="#121821"]:hover {
#                 box-shadow: 0 6px 16px rgba(0,0,0,0.4) !important;
#             }
#             /* Responsive button styling */
#             @media (max-width: 768px) {
#                 #analyze, #x-analyze {
#                     width: 100% !important;
#                     float: none !important;
#                 }
#                 .card-footer {
#                     text-align: center !important;
#                 }
#             }
#             /* DataTable pagination styling */
#             .dash-table-toolbar {
#                 background-color: #1a1a1a !important;
#                 color: rgba(255,255,255,0.9) !important;
#                 padding: 8px !important;
#                 display: flex !important;
#                 align-items: center !important;
#                 justify-content: center !important;
#                 gap: 8px !important;
#                 flex-wrap: wrap !important;
#             }
#             /* Style navigation buttons */
#             .dash-table-toolbar .previous-page, 
#             .dash-table-toolbar .next-page,
#             .dash-table-toolbar .first-page,
#             .dash-table-toolbar .last-page {
#                 background-color: rgba(255,255,255,0.1) !important;
#                 color: rgba(255,255,255,0.9) !important;
#                 border: 1px solid rgba(255,255,255,0.2) !important;
#                 border-radius: 4px !important;
#                 padding: 6px 12px !important;
#                 margin: 0 !important;
#                 min-width: 36px !important;
#                 height: 32px !important;
#                 cursor: pointer !important;
#                 display: inline-flex !important;
#                 align-items: center !important;
#                 justify-content: center !important;
#                 font-size: 14px !important;
#                 line-height: 1 !important;
#                 box-sizing: border-box !important;
#             }
#             .dash-table-toolbar .previous-page:hover, 
#             .dash-table-toolbar .next-page:hover,
#             .dash-table-toolbar .first-page:hover,
#             .dash-table-toolbar .last-page:hover {
#                 background-color: rgba(0,200,150,0.2) !important;
#                 border-color: rgba(0,200,150,0.4) !important;
#             }
#             .dash-table-toolbar .previous-page:disabled, 
#             .dash-table-toolbar .next-page:disabled,
#             .dash-table-toolbar .first-page:disabled,
#             .dash-table-toolbar .last-page:disabled {
#                 opacity: 0.3 !important;
#                 cursor: not-allowed !important;
#             }
#             /* Fix duplicate page number - hide all spans/divs that might show duplicate page number */
#             /* Target the container that holds the page input */
#             .dash-table-toolbar > div {
#                 display: inline-flex !important;
#                 align-items: center !important;
#                 position: relative !important;
#                 height: 32px !important;
#             }
#             /* Hide ALL child elements in the input container EXCEPT the input itself */
#             .dash-table-toolbar > div:has(input[type="number"]) > span,
#             .dash-table-toolbar > div:has(input[type="number"]) > div:not(:has(input)),
#             .dash-table-toolbar > div:has(input[type="number"]) > label,
#             .dash-table-toolbar > div:has(input[type="number"]) > *:not(input[type="number"]) {
#                 display: none !important;
#                 visibility: hidden !important;
#             }
#             /* Style the page number input */
#             .dash-table-toolbar input[type="number"] {
#                 background-color: rgba(255,255,255,0.1) !important;
#                 color: rgba(255,255,255,0.9) !important;
#                 border: 1px solid rgba(255,255,255,0.2) !important;
#                 border-radius: 4px !important;
#                 padding: 6px 10px !important;
#                 width: 60px !important;
#                 min-width: 60px !important;
#                 max-width: 60px !important;
#                 text-align: center !important;
#                 font-weight: 500 !important;
#                 font-size: 14px !important;
#                 line-height: 1.2 !important;
#                 height: 32px !important;
#                 -moz-appearance: textfield !important;
#                 box-sizing: border-box !important;
#                 display: inline-block !important;
#                 visibility: visible !important;
#                 position: relative !important;
#                 z-index: 1 !important;
#             }
#             /* Hide spinner buttons on number input */
#             .dash-table-toolbar input[type="number"]::-webkit-inner-spin-button,
#             .dash-table-toolbar input[type="number"]::-webkit-outer-spin-button {
#                 -webkit-appearance: none !important;
#                 margin: 0 !important;
#             }
#             /* Hide any duplicate inputs */
#             .dash-table-toolbar input[type="number"]:not(:first-of-type) {
#                 display: none !important;
#             }
#             /* Hide any pseudo-elements that might duplicate content */
#             .dash-table-toolbar > div::before,
#             .dash-table-toolbar > div::after,
#             .dash-table-toolbar input[type="number"]::before,
#             .dash-table-toolbar input[type="number"]::after {
#                 display: none !important;
#                 content: none !important;
#             }
#             /* Keep the "/ total" text visible - it's in the last div */
#             .dash-table-toolbar > div:last-child:not(:has(input)) {
#                 display: inline-block !important;
#                 color: rgba(255,255,255,0.7) !important;
#                 font-size: 14px !important;
#                 margin-left: 4px !important;
#                 visibility: visible !important;
#             }
#             .dash-table-toolbar > div:last-child:not(:has(input)) > * {
#                 display: inline !important;
#                 visibility: visible !important;
#             }
#             /* Additional fix: Hide any elements with class names that suggest duplicate page numbers */
#             .dash-table-toolbar .page-number,
#             .dash-table-toolbar [class*="current-page"],
#             .dash-table-toolbar [class*="page-input"] > span:not(:last-child),
#             .dash-table-toolbar [class*="page-input"] > div:not(:has(input)) {
#                 display: none !important;
#                 visibility: hidden !important;
#             }
#             /* Prevent any pseudo-elements from duplicating content */
#             .dash-table-toolbar input[type="number"]::before,
#             .dash-table-toolbar input[type="number"]::after {
#                 display: none !important;
#                 content: none !important;
#             }
#         </style>
#         <script>
#             // Fix duplicate page number in DataTable pagination
#             function fixPaginationDuplicates() {
#                 const toolbars = document.querySelectorAll('.dash-table-toolbar');
#                 toolbars.forEach(toolbar => {
#                     // Find the input container
#                     const inputContainers = Array.from(toolbar.children).filter(div => {
#                         return div.querySelector('input[type="number"]');
#                     });
                    
#                     inputContainers.forEach(container => {
#                         const input = container.querySelector('input[type="number"]');
#                         if (!input) return;
                        
#                         // Hide all children except the input itself
#                         Array.from(container.children).forEach(child => {
#                             if (child !== input && child.tagName !== 'SCRIPT') {
#                                 child.style.display = 'none';
#                                 child.style.visibility = 'hidden';
#                             }
#                         });
                        
#                         // Remove any text nodes or overlays
#                         const walker = document.createTreeWalker(
#                             container,
#                             NodeFilter.SHOW_TEXT,
#                             null,
#                             false
#                         );
#                         let node;
#                         while (node = walker.nextNode()) {
#                             if (node.parentElement !== input && node.textContent.trim() === input.value) {
#                                 node.textContent = '';
#                             }
#                         }
#                     });
#                 });
#             }
            
#             // Run on page load and after any updates
#             if (document.readyState === 'loading') {
#                 document.addEventListener('DOMContentLoaded', fixPaginationDuplicates);
#             } else {
#                 fixPaginationDuplicates();
#             }
            
#             // Use MutationObserver to fix duplicates when table updates
#             const observer = new MutationObserver(function(mutations) {
#                 let shouldFix = false;
#                 mutations.forEach(function(mutation) {
#                     if (mutation.addedNodes.length > 0) {
#                         mutation.addedNodes.forEach(function(node) {
#                             if (node.nodeType === 1 && (
#                                 node.classList.contains('dash-table-toolbar') ||
#                                 node.querySelector('.dash-table-toolbar')
#                             )) {
#                                 shouldFix = true;
#                             }
#                         });
#                     }
#                 });
#                 if (shouldFix) {
#                     setTimeout(fixPaginationDuplicates, 100);
#                 }
#             });
            
#             observer.observe(document.body, {
#                 childList: true,
#                 subtree: true
#             });
#         </script>
#     </head>
#     <body>
#         {%app_entry%}
#         <footer>
#             {%config%}
#             {%scripts%}
#             {%renderer%}
#         </footer>
#     </body>
# </html>
# '''

# # Expose the underlying Flask server for Gunicorn
# server = app.server

# # Stores (Single page)
# STORE_RAW = "store_raw_df"
# STORE_META = "store_meta"

# # Stores (Cross page)
# STORE_A = "store_raw_a"
# STORE_B = "store_raw_b"


# MONTH_OPTIONS = [{"label": m, "value": i} for i, m in enumerate(
#     ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], start=1
# )]

# # -----------------------------
# # Helpers
# # -----------------------------
# def parse_csv_flexible(contents: str, filename: str):
#     """
#     Accept TWO columns: one date/time-like and one numeric (names can be anything).
#     Detect them and normalize to ['datetime','index'].
#     """
#     if not filename or not filename.lower().endswith(".csv"):
#         return None, [], f"Please upload a CSV file. You uploaded: {filename}"

#     try:
#         _, content_string = contents.split(",")
#         decoded = base64.b64decode(content_string)
#         df0 = pd.read_csv(io.BytesIO(decoded))
#     except Exception as e:
#         return None, [], f"Failed to read CSV: {e}"

#     if df0.empty:
#         return None, [], "The CSV appears to be empty."
#     if df0.shape[1] < 2:
#         return None, [], "CSV must have at least two columns (a date column and a numeric column)."

#     warnings = []

#     # Find date-like column (≥50% parseable)
#     date_col = None
#     for c in df0.columns:
#         s = pd.to_datetime(df0[c], errors="coerce", infer_datetime_format=True)
#         if s.notna().mean() >= 0.5:
#             date_col = c
#             break
#     if date_col is None:
#         return None, [], "Could not detect a date column."

#     # Find numeric column (≥50% numeric)
#     num_col = None
#     for c in df0.columns:
#         if c == date_col:
#             continue
#         s = pd.to_numeric(df0[c], errors="coerce")
#         if s.notna().mean() >= 0.5:
#             num_col = c
#             break
#     if num_col is None:
#         return None, [], "Could not detect a numeric column."

#     df = pd.DataFrame({
#         "datetime": pd.to_datetime(df0[date_col], errors="coerce"),
#         "index": pd.to_numeric(df0[num_col], errors="coerce")
#     })
#     before = len(df)
#     df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)
#     dropped = before - len(df)
#     if dropped > 0:
#         warnings.append(f"Dropped {dropped} rows with invalid/missing values.")
#     return df, warnings, None


# def compute_range(preset: str, start_date, end_date, data_min: pd.Timestamp, data_max: pd.Timestamp, snap_month: bool):
#     """
#     Resolve (start, end) timestamps based on a preset or DatePickerRange values.
#     """
#     start, end = data_min, data_max

#     if preset in (None, "all"):
#         start, end = data_min, data_max
#     elif preset == "ytd":
#         end = data_max
#         start = pd.Timestamp(end.year, 1, 1)
#     elif preset == "1y":
#         end = data_max
#         start = end - pd.DateOffset(years=1)
#     elif preset == "3y":
#         end = data_max
#         start = end - pd.DateOffset(years=3)
#     elif preset == "6m":
#         end = data_max
#         start = end - pd.DateOffset(months=6)
#     else:  # "custom"
#         s = pd.to_datetime(start_date) if start_date else data_min
#         e = pd.to_datetime(end_date) if end_date else data_max
#         start, end = s, e

#     if snap_month:
#         start = pd.Timestamp(start.year, start.month, 1)
#         end = (pd.Timestamp(end.year, end.month, 1) + pd.offsets.MonthEnd(1)).normalize()

#     start = max(start, data_min)
#     end = min(end, data_max)
#     if start > end:
#         start, end = end, start
#     return start, end

# # -----------------------------
# # Weekend-aware window helpers
# # -----------------------------
# def end_trade_day_with_buffer(start: pd.Timestamp, window_size_days: int,
#                               buffer_minus: int = 1, buffer_plus: int = 1) -> pd.Timestamp:
#     """
#     Weekend-aware last trading day for a calendar-day window.
#     - Tentative end = start + (window_size_days - 1) calendar days.
#     - If tentative lands on weekend:
#         - If the backward adjustment would skip more than one day (e.g., Sat→Fri = -1 is OK,
#           Sun→Fri = -2 means instead take +1 and go forward to Monday).
#     """
#     if pd.isna(start):
#         return pd.NaT

#     start = (start if isinstance(start, pd.Timestamp) else pd.Timestamp(start)).normalize()
#     tentative = start + pd.Timedelta(days=max(int(window_size_days) - 1, 0))

#     weekday = tentative.weekday()  # Monday=0 … Sunday=6
#     # Saturday → -1 to Friday
#     if weekday == 5:
#         return tentative - pd.Timedelta(days=buffer_minus)
#     # Sunday → instead of -2 back to Friday, go +1 to Monday
#     elif weekday == 6:
#         return tentative + pd.Timedelta(days=buffer_plus)
#     # Weekday
#     return tentative


# def compute_windowed_returns_calendar(df: pd.DataFrame, window_size_days: int) -> pd.Series:
#     """
#     Compute % change using a calendar-day window with weekend-aware snapping.
#     Assumes df has columns ['datetime','index'] and is sorted by datetime.
#     For each row i at date D_i, find E_i = end_trade_day_with_buffer(D_i, window_size_days).
#     Use the latest available row with datetime <= E_i as end value.
#     """
#     if df.empty:
#         return pd.Series(dtype=float)

#     df = df.copy()
#     df["datetime"] = pd.to_datetime(df["datetime"]).dt.normalize()
#     df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)

#     dates = df["datetime"]
#     vals = pd.to_numeric(df["index"], errors="coerce").values

#     # Map unique day -> last row pos
#     date_to_lastpos = {}
#     for pos, day in enumerate(dates):
#         date_to_lastpos[day] = pos
#     unique_days = dates.drop_duplicates().reset_index(drop=True)

#     def pos_leq_day(target_day: pd.Timestamp):
#         # rightmost unique_days[idx] <= target_day
#         left, right = 0, len(unique_days) - 1
#         ans = -1
#         while left <= right:
#             mid = (left + right) // 2
#             if unique_days[mid] <= target_day:
#                 ans = mid
#                 left = mid + 1
#             else:
#                 right = mid - 1
#         if ans == -1:
#             return None
#         return date_to_lastpos[unique_days[ans]]

#     rets = np.full(len(df), np.nan, dtype=float)
#     ws = max(int(window_size_days or 1), 1)

#     for i in range(len(df)):
#         start_day = dates.iloc[i]
#         end_day = end_trade_day_with_buffer(start_day, ws)
#         j = pos_leq_day(end_day)
#         if j is None or j <= i:
#             continue
#         if np.isfinite(vals[i]) and np.isfinite(vals[j]) and vals[i] != 0:
#             rets[i] = (vals[j] / vals[i]) - 1.0

#     return pd.Series(rets, index=df.index, name=f"ret_{ws}d_cal")

# # ---------- Indicator helpers (no external TA dependency) ----------
# def ema(s: pd.Series, span: int):
#     return s.ewm(span=span, adjust=False).mean()

# def rsi(series: pd.Series, period: int = 14):
#     delta = series.diff()
#     up = (delta.clip(lower=0)).rolling(period).mean()
#     down = (-delta.clip(upper=0)).rolling(period).mean()
#     rs = up / (down.replace(0, np.nan))
#     out = 100 - (100 / (1 + rs))
#     return out

# def bbands_mid_upper_lower(price: pd.Series, window: int = 20, k: float = 2.0):
#     mid = price.rolling(window).mean()
#     std = price.rolling(window).std()
#     upper = mid + k * std
#     lower = mid - k * std
#     return mid, upper, lower

# def compute_calendar_return_series(df: pd.DataFrame, window_size_days: int) -> pd.Series:
#     """
#     Wrapper that returns weekend-aware calendar returns aligned to df.index,
#     using compute_windowed_returns_calendar.
#     """
#     return compute_windowed_returns_calendar(df[["datetime","index"]].copy(), window_size_days)

# def build_indicators(df: pd.DataFrame, price_col="index"):
#     """
#     Builds a feature table.
#     Weekend-aware for ret_5, ret_10, mom_10 via compute_windowed_returns_calendar.
#     Other rolling features operate on available trading days.
#     """
#     out = pd.DataFrame(index=df.index)
#     p = pd.to_numeric(df[price_col], errors="coerce").astype(float)

#     # returns, momentum & volatility
#     out["ret_1"]  = p.pct_change(1)

#     # weekend-aware multi-day returns
#     out["ret_5"]  = compute_calendar_return_series(df, 5)
#     out["ret_10"] = compute_calendar_return_series(df, 10)
#     # momentum over 10 calendar days == ret_10
#     out["mom_10"] = out["ret_10"]

#     # volatility based on daily returns (trading-day based)
#     out["vol_20"] = out["ret_1"].rolling(20).std()
#     out["vol_60"] = out["ret_1"].rolling(60).std()

#     # moving averages
#     out["sma_5"]   = p.rolling(5).mean()
#     out["sma_20"]  = p.rolling(20).mean()
#     out["ema_12"]  = ema(p, 12)
#     out["ema_26"]  = ema(p, 26)

#     # MACD family
#     macd_line = out["ema_12"] - out["ema_26"]
#     macd_sig  = ema(macd_line, 9)
#     out["macd"]      = macd_line
#     out["macd_sig"]  = macd_sig
#     out["macd_hist"] = macd_line - macd_sig

#     # RSI
#     out["rsi_14"] = rsi(p, 14)

#     # Bollinger
#     mid, up, lo = bbands_mid_upper_lower(p, 20, 2.0)
#     out["bb_mid"]   = mid
#     out["bb_up"]    = up
#     out["bb_lo"]    = lo
#     out["bb_width"] = (up - lo) / mid
#     out["bb_pos"]   = (p - mid) / (up - lo)

#     # drawdown features
#     rolling_max = p.cummax()
#     drawdown = p / rolling_max - 1.0
#     out["dd"]       = drawdown
#     out["dd_20"]    = (p / p.rolling(20).max() - 1.0)
#     out["dd_speed"] = drawdown.diff()

#     # combos
#     out["sma_gap_5_20"]  = out["sma_5"] / out["sma_20"] - 1.0
#     out["ema_gap_12_26"] = out["ema_12"] / out["ema_26"] - 1.0

#     return out

# # ---------- Updated analyses (now using weekend-aware returns everywhere) ----------
# def drop_event_analysis(df: pd.DataFrame, minimum_per_drop: float, windows_size: int):
#     """
#     Count drop events using weekend-aware windowed returns.
#     """
#     ret = compute_windowed_returns_calendar(df, windows_size)
#     ret = ret.dropna()
#     crossings = (ret <= -minimum_per_drop)
#     total_events = int(crossings.sum())
#     denom = max(len(ret), 1)
#     prob = total_events / denom
#     key = f"{windows_size} days and {minimum_per_drop * 100:.0f}% minimum percentage drop"
#     return {key: {"events": total_events, "probability": f"{prob:.2%}"}}

# def gain_event_analysis(df: pd.DataFrame, minimum_per_gain: float, windows_size: int):
#     """
#     Count gain events using weekend-aware windowed returns.
#     """
#     ret = compute_windowed_returns_calendar(df, windows_size)
#     ret = ret.dropna()
#     crossings = (ret >= minimum_per_gain)
#     total_events = int(crossings.sum())
#     denom = max(len(ret), 1)
#     prob = total_events / denom
#     key = f"{windows_size} days and {minimum_per_gain * 100:.0f}% minimum percentage gain"
#     return {key: {"events": total_events, "probability": f"{prob:.2%}"}}

# # ---------- Table to show first/last trade day ----------
# def build_trade_window_table(df: pd.DataFrame, window_size_days: int, limit: int = 200):
#     """
#     Table of start date, weekend-aware last trade day, and actual end present in data (<= last trade day).
#     """
#     if df.empty:
#         return html.Div()

#     df = df.copy()
#     df["datetime"] = pd.to_datetime(df["datetime"]).dt.normalize()
#     df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)

#     dates = df["datetime"]

#     # Map unique days to last position
#     date_to_lastpos = {}
#     for pos, day in enumerate(dates):
#         date_to_lastpos[day] = pos
#     unique_days = dates.drop_duplicates().reset_index(drop=True)

#     def pos_leq_day(target_day: pd.Timestamp):
#         left, right = 0, len(unique_days) - 1
#         ans = -1
#         while left <= right:
#             mid = (left + right) // 2
#             if unique_days[mid] <= target_day:
#                 ans = mid
#                 left = mid + 1
#             else:
#                 right = mid - 1
#         if ans == -1:
#             return None
#         return date_to_lastpos[unique_days[ans]]

#     ws = max(int(window_size_days or 1), 1)
#     rows = []
#     for i in range(len(df)):
#         start_day = dates.iloc[i]
#         last_trade_day = end_trade_day_with_buffer(start_day, ws)
#         j = pos_leq_day(last_trade_day)
#         actual_end = dates.iloc[j] if (j is not None and j > i) else pd.NaT
#         rows.append({
#             "Start (first day of trade)": start_day.date(),
#             "Last day of trade (weekend-aware)": last_trade_day.date() if pd.notna(last_trade_day) else None,
#             "Actual end in data (<= last trade day)": actual_end.date() if pd.notna(actual_end) else None,
#         })

#     df_out = pd.DataFrame(rows)
#     if limit and len(df_out) > limit:
#         df_out = df_out.head(limit)

#     table = dash_table.DataTable(
#         data=df_out.to_dict("records"),
#         columns=[{"name": c, "id": c} for c in df_out.columns],
#         page_size=min(20, len(df_out)) or 5,
#         page_action="native",
#         page_current=0,
#         style_table={"overflowX": "auto", "backgroundColor": "#1a1a1a"},
#         style_cell={
#             "textAlign": "left", 
#             "minWidth": "160px",
#             "backgroundColor": "#1a1a1a",
#             "color": "rgba(255,255,255,0.9)",
#             "border": "1px solid rgba(255,255,255,0.1)",
#             "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
#         },
#         style_header={
#             "backgroundColor": "#252525",
#             "color": "rgba(255,255,255,0.95)",
#             "fontWeight": "600",
#             "border": "1px solid rgba(0,200,150,0.3)",
#             "textAlign": "left"
#         },
#         style_data={
#             "backgroundColor": "#1a1a1a",
#             "color": "rgba(255,255,255,0.9)",
#             "border": "1px solid rgba(255,255,255,0.1)"
#         },
#         style_data_conditional=[
#             {
#                 "if": {"row_index": "even"},
#                 "backgroundColor": "#222222",
#             },
#             {
#                 "if": {"state": "selected"},
#                 "backgroundColor": "rgba(0,200,150,0.2)",
#                 "border": "1px solid rgba(0,200,150,0.5)"
#             }
#         ],
#         style_cell_conditional=[
#             {
#                 "if": {"column_id": "Start (first day of trade)"},
#                 "minWidth": "180px"
#             }
#         ]
#     )
#     return table

# # -----------------------------
# # Reusable UI Components
# # -----------------------------

# def PageContainer(children, **kwargs):
#     """Consistent page container with max-width and responsive padding"""
#     return html.Div(
#         children,
#         style={
#             "maxWidth": "1152px",  # max-w-6xl equivalent
#             "width": "100%",
#             "margin": "0 auto",
#             "padding": "16px 16px",
#             **kwargs.get("style", {})
#         },
#         **{k: v for k, v in kwargs.items() if k != "style"}
#     )

# def Card(children, header=None, footer=None, **kwargs):
#     """Reusable card component with header, content, and footer slots"""
#     card_children = []
#     if header:
#         card_children.append(html.Div(
#             header,
#             style={
#                 "padding": "0 0 16px 0",
#                 "borderBottom": "1px solid rgba(255,255,255,0.1)",
#                 "marginBottom": "16px"
#             }
#         ))
#     card_children.append(html.Div(children, style={"flex": 1}))
#     if footer:
#         card_children.append(html.Div(
#             footer,
#             style={
#                 "padding": "16px 0 0 0",
#                 "borderTop": "1px solid rgba(255,255,255,0.1)",
#                 "marginTop": "16px",
#                 "position": "sticky",
#                 "bottom": 0,
#                 "background": "#121821",
#                 "zIndex": 5
#             }
#         ))
    
#     card_style = {
#         "padding": "24px",
#         "background": "#121821",
#         "borderRadius": "12px",
#         "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
#         "border": "1px solid rgba(255,255,255,0.1)",
#         "display": "flex",
#         "flexDirection": "column",
#         "position": "relative"
#     }
#     card_style.update(kwargs.get("style", {}))
    
#     return html.Div(
#         card_children,
#         style=card_style,
#         **{k: v for k, v in kwargs.items() if k != "style"}
#     )

# def Field(label, input_component, helper_text=None, error_text=None, required=False, **kwargs):
#     """Reusable field component with label, input, helper text, and error message"""
#     label_style = {
#         "display": "block",
#         "fontSize": "14px",
#         "fontWeight": "600",
#         "color": "rgba(255,255,255,0.9)",
#         "marginBottom": "8px",
#         "lineHeight": "1.4"
#     }
#     if required:
#         label_style["color"] = "rgba(255,255,255,0.95)"
    
#     field_children = [
#         html.Label(label, style=label_style),
#         input_component
#     ]
    
#     if helper_text:
#         field_children.append(html.Div(
#             helper_text,
#             style={
#                 "fontSize": "12px",
#                 "color": "rgba(255,255,255,0.6)",
#                 "marginTop": "4px"
#             }
#         ))
    
#     if error_text:
#         field_children.append(html.Div(
#             error_text,
#             style={
#                 "fontSize": "12px",
#                 "color": "#ef4444",
#                 "marginTop": "4px"
#             }
#         ))
    
#     return html.Div(
#         field_children,
#         style={
#             "marginBottom": "20px",
#             **kwargs.get("style", {})
#         },
#         **{k: v for k, v in kwargs.items() if k != "style"}
#     )

# def RadioGroup(id, label, options, value=None, inline=True, accent_color=None, **kwargs):
#     """Reusable radio group component"""
#     input_style = {
#         "marginRight": "4px",
#         "cursor": "pointer",
#         "accentColor": accent_color or "rgba(0,200,150,0.8)"
#     }
#     label_style = {
#         "marginRight": "16px",
#         "cursor": "pointer",
#         "fontSize": "14px",
#         "color": "rgba(255,255,255,0.9)",
#         "display": "inline-block" if inline else "block"
#     }
    
#     return html.Div([
#         html.Label(label, style={
#             "display": "block",
#             "fontSize": "14px",
#             "fontWeight": "600",
#             "color": "rgba(255,255,255,0.9)",
#             "marginBottom": "8px"
#         }),
#         dcc.RadioItems(
#             id=id,
#             options=options,
#             value=value,
#             inline=inline,
#             inputStyle=input_style,
#             labelStyle=label_style,
#             **kwargs
#         )
#     ], style={"marginBottom": "20px"})

# def CheckboxGroup(id, label, options, value=None, inline=True, **kwargs):
#     """Reusable checkbox group component"""
#     input_style = {
#         "marginRight": "8px",
#         "cursor": "pointer"
#     }
#     label_style = {
#         "marginRight": "16px",
#         "cursor": "pointer",
#         "fontSize": "14px",
#         "color": "rgba(255,255,255,0.9)",
#         "display": "inline-block" if inline else "block"
#     }
    
#     return html.Div([
#         html.Label(label, style={
#             "display": "block",
#             "fontSize": "14px",
#             "fontWeight": "600",
#             "color": "rgba(255,255,255,0.9)",
#             "marginBottom": "8px"
#         }),
#         dcc.Checklist(
#             id=id,
#             options=options,
#             value=value or [],
#             inline=inline,
#             inputStyle=input_style,
#             labelStyle=label_style,
#             **kwargs
#         )
#     ], style={"marginBottom": "20px"})

# def DateRangePicker(id, label, preset_id=None, preset_options=None, preset_value="all",
#                     snap_id=None, snap_value=None, min_date=None, max_date=None,
#                     start_date=None, end_date=None, helper_text=None, **kwargs):
#     """Reusable date range picker with preset dropdown and snap to month"""
#     return html.Div([
#         html.Label(label, style={
#             "display": "block",
#             "fontSize": "14px",
#             "fontWeight": "600",
#             "color": "rgba(255,255,255,0.9)",
#             "marginBottom": "8px"
#         }),
#         html.Div([
#             html.Div([
#                 dcc.Dropdown(
#                     id=preset_id,
#                     options=preset_options or [
#                         {"label":"All","value":"all"},
#                         {"label":"YTD","value":"ytd"},
#                         {"label":"Last 1Y","value":"1y"},
#                         {"label":"Last 3Y","value":"3y"},
#                         {"label":"Last 6M","value":"6m"},
#                         {"label":"Custom","value":"custom"},
#                     ],
#                     value=preset_value,
#                     clearable=False,
#                     style={
#                         "width": "100%"
#                     }
#                 )
#             ], style={
#                 "flex": "0 0 160px"
#             }),
#             html.Div([
#                 dcc.DatePickerRange(
#                     id=id,
#                     display_format="YYYY-MM-DD",
#                     minimum_nights=0,
#                     clearable=True,
#                     persistence=True,
#                     min_date_allowed=min_date,
#                     max_date_allowed=max_date,
#                     start_date=start_date,
#                     end_date=end_date,
#                     style={
#                         "width": "100%"
#                     },
#                     **kwargs
#                 )
#             ], style={
#                 "flex": "1 1 auto",
#                 "minWidth": "300px"
#             }),
#             html.Div([
#                 dcc.Checklist(
#                     id=snap_id,
#                     options=[{"label": " Snap to month", "value": "snap"}],
#                     value=snap_value or ["snap"],
#                     inline=True,
#                     style={"display": "inline-block"}
#                 )
#             ], style={
#                 "flex": "0 0 auto",
#                 "display": "flex",
#                 "alignItems": "center"
#             })
#         ], style={
#             "display": "flex",
#             "alignItems": "center",
#             "flexWrap": "wrap",
#             "gap": "12px"
#         }),
#         helper_text and html.Div(
#             helper_text,
#             style={
#                 "fontSize": "12px",
#                 "color": "rgba(255,255,255,0.6)",
#                 "marginTop": "4px"
#             }
#         )
#     ], style={"marginBottom": "20px"})

# def FileDropzone(id, label, accept=".csv", filename=None, on_replace_id=None, on_remove_id=None, **kwargs):
#     """Reusable file dropzone component with drag/drop and click support"""
#     if filename:
#         # Show file info with replace/remove actions
#         return html.Div([
#             html.Label(label, style={
#                 "display": "block",
#                 "fontSize": "14px",
#                 "fontWeight": "600",
#                 "color": "rgba(255,255,255,0.9)",
#                 "marginBottom": "8px"
#             }),
#             html.Div([
#                 html.Div([
#                     html.Span("📄", style={"fontSize": "20px", "marginRight": "8px"}),
#                     html.Span(filename, style={
#                         "fontSize": "14px",
#                         "color": "rgba(255,255,255,0.9)",
#                         "flex": 1
#                     }),
#                     html.Button(
#                         "Replace",
#                         id=on_replace_id,
#                         n_clicks=0,
#                         style={
#                             "padding": "6px 12px",
#                             "marginRight": "8px",
#                             "borderRadius": "6px",
#                             "border": "1px solid rgba(255,255,255,0.2)",
#                             "background": "rgba(255,255,255,0.1)",
#                             "color": "rgba(255,255,255,0.9)",
#                             "cursor": "pointer",
#                             "fontSize": "12px"
#                         }
#                     ) if on_replace_id else None,
#                     html.Button(
#                         "Remove",
#                         id=on_remove_id,
#                         n_clicks=0,
#                         style={
#                             "padding": "6px 12px",
#                             "borderRadius": "6px",
#                             "border": "1px solid rgba(239,68,68,0.3)",
#                             "background": "rgba(239,68,68,0.1)",
#                             "color": "#ef4444",
#                             "cursor": "pointer",
#                             "fontSize": "12px"
#                         }
#                     ) if on_remove_id else None
#                 ], style={
#                     "display": "flex",
#                     "alignItems": "center",
#                     "padding": "12px 16px",
#                     "background": "rgba(0,200,150,0.1)",
#                     "borderRadius": "8px",
#                     "border": "1px solid rgba(0,200,150,0.3)"
#                 })
#             ])
#         ], style={"marginBottom": "20px"})
    
#     # Show upload zone
#     return html.Div([
#         html.Label(label, style={
#             "display": "block",
#             "fontSize": "14px",
#             "fontWeight": "600",
#             "color": "rgba(255,255,255,0.9)",
#             "marginBottom": "8px"
#         }),
#         dcc.Upload(
#             id=id,
#             children=html.Div([
#                 html.Div([
#                     html.Span("Drag and drop or ", style={
#                         "fontSize": "15px",
#                         "color": "rgba(255,255,255,0.7)"
#                     }),
#                     html.A("Select CSV File", style={
#                         "fontSize": "15px",
#                         "color": "#00c896",
#                         "fontWeight": "600",
#                         "textDecoration": "underline"
#                     })
#                 ], style={
#                     "display": "flex",
#                     "alignItems": "center",
#                     "gap": "8px"
#                 }),
#                 html.Span("📁", style={
#                     "fontSize": "24px",
#                     "marginLeft": "12px",
#                     "opacity": 0.8,
#                     "transition": "all 0.3s"
#                 })
#             ], style={
#                 "display": "flex",
#                 "alignItems": "center",
#                 "justifyContent": "center"
#             }),
#             style={
#                 "width": "100%",
#                 "height": "100px",
#                 "borderWidth": "2px",
#                 "borderStyle": "dashed",
#                 "borderColor": "rgba(0,200,150,0.3)",
#                 "borderRadius": "12px",
#                 "textAlign": "center",
#                 "background": "rgba(0,200,150,0.05)",
#                 "transition": "all 0.3s",
#                 "cursor": "pointer",
#                 "display": "flex",
#                 "flexDirection": "row",
#                 "justifyContent": "center",
#                 "alignItems": "center"
#             },
#             multiple=False,
#             accept=accept,
#             **kwargs
#         )
#     ], style={"marginBottom": "20px"})

# def Button(id, label, variant="primary", disabled=False, loading=False, full_width=False, **kwargs):
#     """Reusable button component with variants and states"""
#     base_style = {
#         "padding": "12px 24px",
#         "borderRadius": "8px",
#         "border": "none",
#         "fontWeight": "600",
#         "fontSize": "15px",
#         "cursor": "pointer" if not disabled and not loading else "not-allowed",
#         "transition": "all 0.3s",
#         "opacity": "0.6" if disabled or loading else "1"
#     }
    
#     if variant == "primary":
#         base_style.update({
#             "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#             "color": "white",
#             "boxShadow": "0 4px 12px rgba(102, 126, 234, 0.4)"
#         })
#     elif variant == "secondary":
#         base_style.update({
#             "background": "rgba(255,255,255,0.1)",
#             "color": "rgba(255,255,255,0.9)",
#             "border": "1px solid rgba(255,255,255,0.2)"
#         })
    
#     if full_width:
#         base_style["width"] = "100%"
    
#     button_label = f"{'⏳ ' if loading else ''}{label}"
    
#     return html.Button(
#         button_label,
#         id=id,
#         disabled=disabled or loading,
#         style={**base_style, **kwargs.get("style", {})},
#         **{k: v for k, v in kwargs.items() if k != "style"}
#     )

# # -----------------------------
# # Layouts: Home / Single / Cross
# # -----------------------------

# card_style = {
#     "display": "flex",
#     "flexDirection": "column",
#     "padding": "32px 36px",
#     "borderRadius": "20px",
#     "border": "none",
#     "boxShadow": "0 8px 24px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)",
#     "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#     "textDecoration": "none",
#     "color": "white",
#     "width": "320px",
#     "minHeight": "280px",
#     "height": "280px",
#     "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
#     "cursor": "pointer",
#     "justifyContent": "center",
#     "alignItems": "center",
#     "boxSizing": "border-box",
# }
# card_style_hover = {
#     "transform": "translateY(-4px)",
#     "boxShadow": "0 12px 32px rgba(0,0,0,0.18), 0 4px 12px rgba(0,0,0,0.12)",
# }

# def navbar():
#     # Always dark theme
#     bg_color = "#0a0a0a"
#     text_color = "white"
#     border_color = "rgba(255,255,255,0.1)"
    
#     return html.Div(
#         [
#             # Left side: Logo
#             html.Div([
#                 html.Img(
#                     src="https://starlab-public.s3.us-east-1.amazonaws.com/starlab_images/transparent-slc-rgb.png",
#                     style={
#                         "height": "36px",
#                         "marginRight": "20px",
#                         "objectFit": "contain"
#                     }
#                 ),
#             ], style={"display": "flex", "alignItems": "center", "flex": 1}),
            
#             # Right side: Navigation elements
#             html.Div([
#                 dcc.Link("Home", href="/", style={
#                     "marginRight": "20px", "textDecoration": "none",
#                     "color": text_color, "fontSize": "14px", "fontWeight": 500,
#                     "padding": "6px 12px", "borderRadius": "4px",
#                     "transition": "all 0.2s"
#                 }),
#                 dcc.Link("Single Index", href="/single", style={
#                     "marginRight": "20px", "textDecoration": "none",
#                     "color": text_color, "fontSize": "14px", "fontWeight": 500,
#                     "padding": "6px 12px", "borderRadius": "4px",
#                     "transition": "all 0.2s"
#                 }),
#                 dcc.Link("Cross Index", href="/cross", style={
#                     "textDecoration": "none",
#                     "color": text_color, "fontSize": "14px", "fontWeight": 500,
#                     "padding": "6px 12px", "borderRadius": "4px",
#                     "transition": "all 0.2s"
#                 }),
#             ], style={"display": "flex", "alignItems": "center"})
#         ],
#         style={
#             "padding": "14px 32px",
#             "background": bg_color,
#             "display": "flex",
#             "alignItems": "center",
#             "justifyContent": "space-between",
#             "boxShadow": "0 2px 8px rgba(0,0,0,0.3)",
#             "marginBottom": "0",
#             "borderBottom": f"1px solid {border_color}",
#             "transition": "background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease"
#         }
#     )

# def home_layout():
#     return html.Div(
#         [
#             html.Div([
#                 html.H1("Index Data Analysis", style={
#                     "fontSize":"48px", "fontWeight":700, "marginBottom":"16px",
#                     "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#                     "WebkitBackgroundClip":"text", "WebkitTextFillColor":"transparent",
#                     "backgroundClip":"text"
#                 }),
#                 html.P("Choose a workflow to begin your analysis:", style={
#                     "fontSize":"18px", "color":"#64748b", "marginBottom":"40px"
#                 }),
#             ], style={"textAlign":"center", "marginBottom":"48px"}),
#             html.Div(
#                 [
#                     dcc.Link(
#                         html.Div(
#                             [
#                                 html.Div("📊", style={"fontSize":"48px", "marginBottom":"16px"}),
#                                 html.H3("Single Index", style={"margin":"0 0 8px 0", "fontSize":"24px", "fontWeight":600}),
#                                 html.P("Analyze one index with comprehensive indicators", style={
#                                     "margin":0, "fontSize":"14px", "opacity":0.9
#                                 })
#                             ],
#                             style={**card_style, "textAlign":"center"}
#                         ),
#                         href="/single",
#                         style={"textDecoration":"none", "display":"flex"}
#                     ),
#                     dcc.Link(
#                         html.Div(
#                             [
#                                 html.Div("🔀", style={"fontSize":"48px", "marginBottom":"16px"}),
#                                 html.H3("Cross Index", style={"margin":"0 0 8px 0", "fontSize":"24px", "fontWeight":600}),
#                                 html.P("Compare two indexes side by side", style={
#                                     "margin":0, "fontSize":"14px", "opacity":0.9
#                                 })
#                             ],
#                             style={**card_style, "background":"linear-gradient(135deg, #f093fb 0%, #f5576c 100%)", "textAlign":"center"}
#                         ),
#                         href="/cross",
#                         style={"textDecoration":"none", "display":"flex"}
#                     ),
#                 ],
#                 style={
#                     "marginTop": "12px", 
#                     "display":"flex", 
#                     "justifyContent":"center", 
#                     "alignItems":"center",
#                     "flexWrap":"wrap",
#                     "gap":"24px"
#                 }
#             ),
#         ],
#         style={"maxWidth":"1200px","margin":"0 auto","padding":"48px 24px", "marginTop":"0"}
#     )

# # ---------- Single Index (FULL) ----------
# def single_layout():
#     return PageContainer([
#         # Header
#         html.Div([
#             html.H1("Single Index Analysis", style={
#                 "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
#                 "color":"rgba(255,255,255,0.95)"
#             }),
#             html.P("Upload a CSV with two columns: a date column and a numeric index column (headers can be anything).", style={
#                 "fontSize":"16px", "color":"rgba(255,255,255,0.7)", "marginBottom":"32px"
#             }),
#         ], style={"marginBottom": "32px"}),

#         # File Upload with Loading
#         dcc.Loading(
#             id="upload-loading",
#             type="circle",
#             children=html.Div([
#                 FileDropzone(
#                     id="uploader",
#                     label="Upload CSV File"
#                 ),
#                 html.Div(id="file-msg", style={"marginBottom": "8px", "fontSize": "14px"}),
#                 html.Div(id="warn-msg", style={"marginBottom": "8px", "fontSize": "14px"}),
#             ])
#         ),

#         # Analysis Types
#         Card([
#             CheckboxGroup(
#                 id="analysis-types",
#                 label="Analysis Type(s)",
#                 options=[{"label": " Drop", "value": "drop"},
#                          {"label": " Gain", "value": "gain"}],
#                 value=["drop", "gain"],
#                 inline=True
#             )
#         ], style={"marginBottom": "24px"}),

#         # Controls row: Drop (left) & Gain (right) - 2 column grid
#         html.Div([
#             # DROP CONTROLS
#             Card([
#                 html.H3("Drop Options", style={
#                     "marginBottom": "20px", "fontSize":"22px",
#                     "fontWeight":600, "color":"#ef4444"
#                 }),
#                 DateRangePicker(
#                         id="date-range-drop",
#                     label="Date Range",
#                     preset_id="preset-drop",
#                     preset_value="all",
#                     snap_id="snap-month-drop",
#                     snap_value=["snap"]
#                 ),
#                 html.Div([
#                     html.Label("Navigate to Date", style={
#                         "display": "block",
#                         "fontSize": "14px",
#                         "fontWeight": "600",
#                         "color": "rgba(255,255,255,0.9)",
#                         "marginBottom": "8px"
#                     }),
#                     html.Div([
#                     dcc.Dropdown(id="jump-year-drop", options=[], placeholder="Year",
#                                      style={"width":"100px","display":"inline-block","marginRight":"8px"}),
#                     dcc.Dropdown(id="jump-month-drop", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                     ], style={"display": "flex", "alignItems": "center"})
#                 ], style={"marginBottom": "20px"}),
#                 RadioGroup(
#                             id="window-size-drop",
#                     label="Analysis Period (days)",
#                     options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
#                              {"label": "7", "value": 7}, {"label": "10", "value": 10}],
#                     value=5,
#                     inline=True,
#                     accent_color="rgba(239,68,68,0.8)"
#                 ),
#                 Field(
#                     label="Custom Period (days)",
#                     input_component=dcc.Input(
#                             id="window-size-input-drop", type="number", min=1, step=1,
#                         placeholder="Enter custom days",
#                         style={
#                             "width": "100%",
#                             "height": "40px",
#                             "padding": "8px 12px",
#                             "fontSize": "14px",
#                             "background": "rgba(255,255,255,0.1)",
#                             "border": "1px solid rgba(255,255,255,0.2)",
#                             "borderRadius": "6px",
#                             "color": "rgba(255,255,255,0.9)"
#                         }
#                     ),
#                     helper_text="Optional: Enter a custom analysis period in days"
#                 ),
#                 RadioGroup(
#                             id="min-threshold-drop",
#                     label="Minimum Change Threshold (%)",
#                     options=[{"label":"1%","value":1},{"label":"3%","value":3},
#                              {"label":"5%","value":5},{"label":"10%","value":10}],
#                     value=3,
#                     inline=True,
#                     accent_color="rgba(239,68,68,0.8)"
#                 ),
#                 Field(
#                     label="Custom Threshold (%)",
#                     input_component=dcc.Input(
#                             id="min-threshold-input-drop", type="number", min=0, max=100, step=0.01,
#                             placeholder="e.g. 2.7", 
#                         style={
#                             "width": "100%",
#                             "height": "40px",
#                             "padding": "8px 12px",
#                             "fontSize": "14px",
#                             "background": "rgba(255,255,255,0.1)",
#                             "border": "1px solid rgba(255,255,255,0.2)",
#                             "borderRadius": "6px",
#                             "color": "rgba(255,255,255,0.9)"
#                         }
#                     ),
#                     helper_text="Optional: Enter a custom threshold (0-100%)"
#                 ),
#             ], style={
#                 "background": "rgba(239,68,68,0.08)",
#                 "border": "1px solid rgba(239,68,68,0.3)"
#             }),

#             # GAIN CONTROLS
#             Card([
#                 html.H3("Gain Options", style={
#                     "marginBottom": "20px", "fontSize":"22px",
#                     "fontWeight":600, "color":"#22c55e"
#                 }),
#                 DateRangePicker(
#                         id="date-range-gain",
#                     label="Date Range",
#                     preset_id="preset-gain",
#                     preset_value="all",
#                     snap_id="snap-month-gain",
#                     snap_value=["snap"]
#                 ),
#                 html.Div([
#                     html.Label("Navigate to Date", style={
#                         "display": "block",
#                         "fontSize": "14px",
#                         "fontWeight": "600",
#                         "color": "rgba(255,255,255,0.9)",
#                         "marginBottom": "8px"
#                     }),
#                     html.Div([
#                     dcc.Dropdown(id="jump-year-gain", options=[], placeholder="Year",
#                                      style={"width":"100px","display":"inline-block","marginRight":"8px"}),
#                     dcc.Dropdown(id="jump-month-gain", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                     ], style={"display": "flex", "alignItems": "center"})
#                 ], style={"marginBottom": "20px"}),
#                 RadioGroup(
#                             id="window-size-gain",
#                     label="Analysis Period (days)",
#                     options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
#                              {"label": "7", "value": 7}, {"label": "10", "value": 10}],
#                     value=5,
#                     inline=True,
#                     accent_color="rgba(34,197,94,0.8)"
#                 ),
#                 Field(
#                     label="Custom Period (days)",
#                     input_component=dcc.Input(
#                             id="window-size-input-gain", type="number", min=1, step=1,
#                         placeholder="Enter custom days",
#                         style={
#                             "width": "100%",
#                             "height": "40px",
#                             "padding": "8px 12px",
#                             "fontSize": "14px",
#                             "background": "rgba(255,255,255,0.1)",
#                             "border": "1px solid rgba(255,255,255,0.2)",
#                             "borderRadius": "6px",
#                             "color": "rgba(255,255,255,0.9)"
#                         }
#                     ),
#                     helper_text="Optional: Enter a custom analysis period in days"
#                 ),
#                 RadioGroup(
#                             id="min-threshold-gain",
#                     label="Minimum Change Threshold (%)",
#                     options=[{"label":"1%","value":1},{"label":"3%","value":3},
#                              {"label":"5%","value":5},{"label":"10%","value":10}],
#                     value=3,
#                     inline=True,
#                     accent_color="rgba(34,197,94,0.8)"
#                 ),
#                 Field(
#                     label="Custom Threshold (%)",
#                     input_component=dcc.Input(
#                             id="min-threshold-input-gain", type="number", min=0, max=100, step=0.01,
#                             placeholder="e.g. 2.7", 
#                         style={
#                             "width": "100%",
#                             "height": "40px",
#                             "padding": "8px 12px",
#                             "fontSize": "14px",
#                             "background": "rgba(255,255,255,0.1)",
#                             "border": "1px solid rgba(255,255,255,0.2)",
#                             "borderRadius": "6px",
#                             "color": "rgba(255,255,255,0.9)"
#                         }
#                     ),
#                     helper_text="Optional: Enter a custom threshold (0-100%)"
#                 ),
#             ], style={
#                 "background": "rgba(34,197,94,0.08)",
#                 "border": "1px solid rgba(34,197,94,0.3)"
#             }),
#         ], style={
#             "display": "grid",
#             "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))",
#             "gap": "24px",
#             "marginBottom": "24px"
#         }),

#         # INDICATORS - Collapsible card with multi-column layout
#         Card([
#         html.Div([
#             html.H3("Indicators", style={
#                 "marginBottom":"16px", "fontSize":"22px",
#                     "fontWeight":600, "color":"rgba(255,255,255,0.95)",
#                     "display": "inline-block",
#                     "marginRight": "16px"
#                 }),
#                 html.Button(
#                     "Select All", id="indicators-select-all", n_clicks=0,
#                     style={
#                         "padding": "6px 16px",
#                         "marginRight": "8px",
#                         "borderRadius": "6px",
#                         "border": "1px solid rgba(0,200,150,0.3)",
#                         "background": "rgba(0,200,150,0.1)",
#                         "color": "rgba(255,255,255,0.9)",
#                         "cursor": "pointer",
#                         "fontSize": "13px",
#                         "fontWeight": "500",
#                         "transition": "all 0.2s"
#                     }
#                 ),
#                 html.Button(
#                     "Clear All", id="indicators-clear-all", n_clicks=0,
#                     style={
#                         "padding": "6px 16px",
#                         "borderRadius": "6px",
#                         "border": "1px solid rgba(255,255,255,0.2)",
#                         "background": "rgba(255,255,255,0.1)",
#                         "color": "rgba(255,255,255,0.9)",
#                         "cursor": "pointer",
#                         "fontSize": "13px",
#                         "fontWeight": "500",
#                         "transition": "all 0.2s"
#                     }
#                 )
#             ], style={
#                 "marginBottom": "16px",
#                 "display": "flex",
#                 "alignItems": "center",
#                 "flexWrap": "wrap",
#                 "gap": "8px"
#             }),
#             html.Div([
#                 CheckboxGroup(
#                 id="indicators-select",
#                     label="",
#                 options=[
#                     {"label":" SMA (5 & 20)", "value":"sma"},
#                     {"label":" EMA (12 & 26)", "value":"ema"},
#                     {"label":" Bollinger Bands (20,2)", "value":"bb"},
#                     {"label":" RSI (14)", "value":"rsi"},
#                     {"label":" MACD (12,26,9)", "value":"macd"},
#                     {"label":" Volatility (20/60)", "value":"vol"},
#                     {"label":" Drawdown", "value":"dd"},
#                 ],
#                 value=["sma","ema","bb","rsi","macd","vol","dd"],
#                     inline=True
#                 )
#         ], style={
#                 "display": "flex",
#                 "flexWrap": "wrap",
#                 "gap": "8px"
#             })
#         ], footer=html.Div([
#             dcc.Loading(
#                 id="analyze-loading",
#                 type="circle",
#                 children=html.Div([
#                     Button(
#                         id="analyze",
#                         label="Analyze",
#                         variant="primary",
#                         full_width=False,
#                         style={"float": "right"}
#                     )
#                 ], style={
#                     "textAlign": "right",
#                     "width": "100%"
#                 }, className="card-footer")
#             )
#         ], style={
#             "textAlign": "right",
#             "width": "100%"
#         }, className="card-footer"), style={
#             "marginBottom": "24px",
#             "position": "relative",
#             "display": "flex",
#             "flexDirection": "column"
#         }),

#         # ---------- Results (Drop / Gain) ----------
#         dcc.Loading(
#             id="results-loading",
#             type="circle",
#             children=html.Div(id="results-container", style={"display": "none"}, children=[
#                 html.Div([
#                 html.H2("Drop Analysis", style={
#                     "fontSize":"28px", "fontWeight":700, "color":"#ef4444",
#                     "marginBottom":"20px"
#                 }),
#                 html.Div(id="analysis-output-drop", style={
#                     "border": "1px solid rgba(239,68,68,0.3)", "borderRadius": "16px",
#                     "padding": "20px", "margin": "10px 0",
#                     "background": "rgba(239,68,68,0.08)",
#                     "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"
#                 }),
#                 html.Div(id="return-chart-drop-container"),
#                 html.Div(id="bar-chart-drop-container"),
#                 html.Div(id="stats-drop", style={"margin": "24px 0"}),
#                 html.Div(id="trade-windows-drop-container"),
#             ], style={"flex": 1, "minWidth": "420px"}),

#             html.Div([
#                 html.H2("Gain Analysis", style={
#                     "fontSize":"28px", "fontWeight":700, "color":"#22c55e",
#                     "marginBottom":"20px"
#                 }),
#                 html.Div(id="analysis-output-gain", style={
#                     "border": "1px solid rgba(34,197,94,0.3)", "borderRadius": "16px",
#                     "padding": "20px", "margin": "10px 0",
#                     "background": "rgba(34,197,94,0.08)",
#                     "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"
#                 }),
#                 html.Div(id="return-chart-gain-container"),
#                 html.Div(id="bar-chart-gain-container"),
#                 html.Div(id="stats-gain", style={"margin": "24px 0"}),
#                 html.Div(id="trade-windows-gain-container"),
#             ], style={"flex": 1, "minWidth": "420px"}),
#             ])
#         ),

#         # ---------- Indicators figure ----------
#         html.Div(id="indicators-container"),

#         html.Hr(),
#         html.Div(id="preview", style={
#             "marginTop":"40px", "padding":"24px",
#             "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#             "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#             "border":"1px solid rgba(255,255,255,0.1)"
#         }),  # <<< Data Preview lives here (first 10 rows)

#         dcc.Store(id=STORE_RAW),
#         dcc.Store(id=STORE_META),
#     ])

# # ---------- Cross Index ----------
# def cross_layout():
#     return PageContainer([
#         # Header
#             html.Div([
#                 html.H1("Cross Index Analysis", style={
#                     "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
#                 "color":"rgba(255,255,255,0.95)"
#                 }),
#                 html.P("Compare two indexes side by side with correlation analysis", style={
#                 "fontSize":"16px", "color":"rgba(255,255,255,0.7)", "marginBottom":"32px"
#                 }),
#         ], style={"marginBottom": "32px"}),

#         # Upload Index A/B - 2 column grid
#             html.Div([
#             Card([
#                 dcc.Loading(
#                     id="upload-loading-a",
#                     type="circle",
#                         children=html.Div([
#                         FileDropzone(
#                             id="uploader-a",
#                             label="Upload Index A (CSV)"
#                         ),
#                         html.Div(id="file-msg-a", style={"marginBottom": "8px", "fontSize": "14px"}),
#                         html.Div(id="warn-msg-a", style={"marginBottom": "8px", "fontSize": "14px"}),
#                         html.Div(id="preview-a")
#                     ])
#                 )
#             ], style={"minHeight": "200px"}),

#             Card([
#                 dcc.Loading(
#                     id="upload-loading-b",
#                     type="circle",
#                         children=html.Div([
#                         FileDropzone(
#                             id="uploader-b",
#                             label="Upload Index B (CSV)"
#                         ),
#                         html.Div(id="file-msg-b", style={"marginBottom": "8px", "fontSize": "14px"}),
#                         html.Div(id="warn-msg-b", style={"marginBottom": "8px", "fontSize": "14px"}),
#                         html.Div(id="preview-b")
#                     ])
#                 )
#             ], style={"minHeight": "200px"}),
#                 ], style={
#             "display": "grid",
#             "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))",
#             "gap": "24px",
#             "marginBottom": "32px"
#         }),

#         # Analysis Settings Card
#         Card([
#                 html.H3("Analysis Settings", style={
#                 "fontSize":"24px", "fontWeight":600, "color":"rgba(255,255,255,0.95)",
#                     "marginBottom":"20px"
#                 }),
#             # Row 1: Date Range + Snap to month
#                 html.Div([
#                 html.Div([
#                     DateRangePicker(
#                         id="date-range-cross",
#                         label="Date Range",
#                         preset_id="preset-cross",
#                         preset_value="all",
#                         snap_id="snap-month-cross",
#                         snap_value=["snap"]
#                     )
#                 ], style={"flex": 1, "minWidth": "300px"})
#             ], style={
#                 "display": "flex",
#                 "alignItems": "flex-end",
#                 "gap": "16px",
#                 "marginBottom": "20px"
#             }),
#             # Row 2: Navigate to Date
#                 html.Div([
#                 html.Label("Navigate to Date", style={
#                     "display": "block",
#                     "fontSize": "14px",
#                     "fontWeight": "600",
#                     "color": "rgba(255,255,255,0.9)",
#                     "marginBottom": "8px"
#                 }),
#                 html.Div([
#                     dcc.Dropdown(id="jump-year-cross", options=[], placeholder="Year",
#                                  style={"width":"100px","display":"inline-block","marginRight":"8px"}),
#                     dcc.Dropdown(id="jump-month-cross", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                 ], style={"display": "flex", "alignItems": "center"})
#             ], style={"marginBottom": "20px"}),
#             # Row 3: Return Calculation Period
#             Field(
#                 label="Return Calculation Period (days)",
#                 input_component=dcc.Input(
#                     id="x-window",
#                     type="number",
#                     min=1,
#                     step=1,
#                     value=5,
#                         style={
#                         "width": "100%",
#                         "height": "40px",
#                         "padding": "8px 12px",
#                         "fontSize": "14px",
#                         "background": "rgba(255,255,255,0.1)",
#                         "border": "1px solid rgba(255,255,255,0.2)",
#                         "borderRadius": "6px",
#                         "color": "rgba(255,255,255,0.9)"
#                     }
#                 ),
#                 helper_text="Number of days for return calculation period"
#             ),
#         ], footer=html.Div([
#             dcc.Loading(
#                 id="x-analyze-loading",
#                 type="circle",
#                 children=html.Div([
#                     Button(
#                         id="x-analyze",
#                         label="Analyze",
#                         variant="primary",
#                         full_width=False,
#                         style={"float": "right"}
#                     )
#                 ], style={
#                     "textAlign": "right",
#                     "width": "100%"
#                 }, className="card-footer")
#             )
#         ], style={
#             "textAlign": "right",
#             "width": "100%"
#         }, className="card-footer"), style={"marginBottom": "32px"}),

#         # Results
#         dcc.Loading(
#             id="x-results-loading",
#             type="circle",
#             children=html.Div(id="x-results-container", children=[
#                 html.Div(id="x-line-levels-container"),
#                 html.Div(id="x-scatter-returns-container"),
#                 html.Div(id="x-line-returns-container"),
#                 html.Div(id="x-stats", style={"margin":"24px 0"}),
#                 html.Div(id="x-trade-windows-container"),
#             ], style={"marginTop":"32px"})
#         ),

#             dcc.Store(id=STORE_A),
#             dcc.Store(id=STORE_B),
#     ])

# # -----------------------------
# # Top-level app layout with router
# # -----------------------------
# app.layout = html.Div(
#     [
#         html.Div(id="navbar-container"),
#         dcc.Location(id="url"),
#         html.Div(id="page-content"),
#     ],
#     id="app-container",
#     style={"fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
#            "minHeight":"100vh","padding":"0", "margin":"0",
#            "background": "#0a0a0a",
#            "color": "white",
#            "transition": "background-color 0.3s ease, color 0.3s ease"}
# )

# # Navbar callback - always dark theme
# @app.callback(
#     Output("navbar-container", "children"),
#     Input("url", "pathname"),
#     prevent_initial_call=False
# )
# def update_navbar(pathname):
#     # Always return dark theme navbar
#     return navbar()


# # Router
# @app.callback(
#     Output("page-content", "children"),
#     Input("url", "pathname")
# )
# def render_page(pathname):
#     if pathname == "/single":
#         return single_layout()
#     elif pathname == "/cross":
#         return cross_layout()
#     else:
#         return home_layout()

# # -----------------------------
# # Indicators Select All / Clear All callback
# # -----------------------------
# @app.callback(
#     Output("indicators-select", "value"),
#     Input("indicators-select-all", "n_clicks"),
#     Input("indicators-clear-all", "n_clicks"),
#     State("indicators-select", "options"),
#     prevent_initial_call=True,
# )
# def update_indicators_select_all(select_all_clicks, clear_all_clicks, options):
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         return no_update
    
#     trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
#     if trigger_id == "indicators-select-all":
#         # Select all indicator values
#         return [opt["value"] for opt in options]
#     elif trigger_id == "indicators-clear-all":
#         # Clear all (return empty list)
#         return []
    
#     return no_update

# # -----------------------------
# # Upload callback (Single page)
# # -----------------------------
# @app.callback(
#     Output("file-msg", "children"),
#     Output("warn-msg", "children"),
#     Output("preview", "children"),          # <<< Data Preview here
#     Output(STORE_RAW, "data"),
#     Output(STORE_META, "data"),
#     # Drop bounds
#     Output("date-range-drop", "min_date_allowed"),
#     Output("date-range-drop", "max_date_allowed"),
#     Output("date-range-drop", "start_date"),
#     Output("date-range-drop", "end_date"),
#     # Gain bounds
#     Output("date-range-gain", "min_date_allowed"),
#     Output("date-range-gain", "max_date_allowed"),
#     Output("date-range-gain", "start_date"),
#     Output("date-range-gain", "end_date"),
#     # Year options for jump controls
#     Output("jump-year-drop", "options"),
#     Output("jump-year-drop", "value"),
#     Output("jump-month-drop", "value"),
#     Output("jump-year-gain", "options"),
#     Output("jump-year-gain", "value"),
#     Output("jump-month-gain", "value"),
#     Input("uploader", "contents"),
#     State("uploader", "filename"),
#     prevent_initial_call=True,
# )
# def on_upload_single(contents, filename):
#     if contents is None:
#         return (no_update,)*19

#     df, warns, err = parse_csv_flexible(contents, filename)
#     if err:
#         return (html.Div(err, style={"color":"crimson"}), None, None, None, None,
#                 no_update, no_update, no_update, no_update,
#                 no_update, no_update, no_update, no_update,
#                 [], None, None, [], None, None)

#     info = html.Div([
#         html.Strong("Uploaded:"), html.Span(f" {filename} "),
#         html.Span(" · Detected columns: ['datetime','index']"),
#         html.Span(f" · Rows: {len(df)}"),
#     ])
#     warn_block = (html.Div([html.Strong("Warnings:"),
#                    html.Ul([html.Li(w) for w in warns])], style={"color":"#996800"}) if warns else None)

#     # --- Data Preview (first 10 rows)
#     table = dash_table.DataTable(
#         data=df.head(10).to_dict("records"),
#         columns=[{"name": c, "id": c} for c in df.columns],
#         page_size=10, 
#         style_table={"overflowX": "auto", "backgroundColor": "#1a1a1a"},
#         style_cell={
#             "textAlign": "left", 
#             "minWidth": "120px",
#             "backgroundColor": "#1a1a1a",
#             "color": "rgba(255,255,255,0.9)",
#             "border": "1px solid rgba(255,255,255,0.1)",
#             "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
#         },
#         style_header={
#             "backgroundColor": "#252525",
#             "color": "rgba(255,255,255,0.95)",
#             "fontWeight": "600",
#             "border": "1px solid rgba(0,200,150,0.3)",
#             "textAlign": "left"
#         },
#         style_data={
#             "backgroundColor": "#1a1a1a",
#             "color": "rgba(255,255,255,0.9)",
#             "border": "1px solid rgba(255,255,255,0.1)"
#         },
#         style_data_conditional=[
#             {
#                 "if": {"row_index": "even"},
#                 "backgroundColor": "#222222",
#             },
#             {
#                 "if": {"state": "selected"},
#                 "backgroundColor": "rgba(0,200,150,0.2)",
#                 "border": "1px solid rgba(0,200,150,0.5)"
#             }
#         ],
#     )

#     raw_payload = {
#         "filename": filename,
#         "columns": list(df.columns),
#         "rows": int(len(df)),
#         "csv_b64": base64.b64encode(df.to_csv(index=False).encode()).decode(),
#     }
#     meta = {"summary": {"rows": int(len(df)), "columns": list(df.columns)}}

#     min_d = df["datetime"].min().date()
#     max_d = df["datetime"].max().date()
#     years = list(range(min_d.year, max_d.year + 1))
#     year_options = [{"label": str(y), "value": y} for y in years]

#     return (
#         info, warn_block, html.Div([html.H3("Preview (first 10 rows)"), table]),
#         raw_payload, meta,
#         min_d, max_d, min_d, max_d,
#         min_d, max_d, min_d, max_d,
#         year_options, min_d.year, 1,
#         year_options, min_d.year, 1
#     )

# # Preset → custom when dates edited (Single page)
# @app.callback(Output("preset-drop", "value"),
#               Input("date-range-drop", "start_date"),
#               Input("date-range-drop", "end_date"),
#               prevent_initial_call=True)
# def force_custom_drop(_s, _e):
#     return "custom"

# @app.callback(Output("preset-gain", "value"),
#               Input("date-range-gain", "start_date"),
#               Input("date-range-gain", "end_date"),
#               prevent_initial_call=True)
# def force_custom_gain(_s, _e):
#     return "custom"

# # Jump-to initial_visible_month (Single page)
# @app.callback(
#     Output("date-range-drop", "initial_visible_month"),
#     Input("jump-year-drop", "value"),
#     Input("jump-month-drop", "value"),
#     State("date-range-drop", "initial_visible_month"),
#     prevent_initial_call=True
# )
# def jump_drop(year, month, _cur):
#     if year and month:
#         return pd.Timestamp(int(year), int(month), 1)
#     return no_update

# @app.callback(
#     Output("date-range-gain", "initial_visible_month"),
#     Input("jump-year-gain", "value"),
#     Input("jump-month-gain", "value"),
#     State("date-range-gain", "initial_visible_month"),
#     prevent_initial_call=True
# )
# def jump_gain(year, month, _cur):
#     if year and month:
#         return pd.Timestamp(int(year), int(month), 1)
#     return no_update

# # -----------------------------
# # Analyze callback (Single page)
# # -----------------------------
# @app.callback(
#     # DROP outputs
#     Output("analysis-output-drop", "children"),
#     Output("return-chart-drop-container", "children"),
#     Output("bar-chart-drop-container", "children"),
#     Output("stats-drop", "children"),
#     Output("trade-windows-drop-container", "children"),
#     # GAIN outputs
#     Output("analysis-output-gain", "children"),
#     Output("return-chart-gain-container", "children"),
#     Output("bar-chart-gain-container", "children"),
#     Output("stats-gain", "children"),
#     Output("trade-windows-gain-container", "children"),
#     # INDICATOR figure
#     Output("indicators-container", "children"),
#     # Results container visibility
#     Output("results-container", "style"),
#     Input("analyze", "n_clicks"),
#     State(STORE_RAW, "data"),
#     State("analysis-types", "value"),
#     # Drop states
#     State("preset-drop", "value"),
#     State("date-range-drop", "start_date"),
#     State("date-range-drop", "end_date"),
#     State("snap-month-drop", "value"),
#     State("window-size-drop", "value"),
#     State("window-size-input-drop", "value"),
#     State("min-threshold-drop", "value"),
#     State("min-threshold-input-drop", "value"),
#     # Gain states
#     State("preset-gain", "value"),
#     State("date-range-gain", "start_date"),
#     State("date-range-gain", "end_date"),
#     State("snap-month-gain", "value"),
#     State("window-size-gain", "value"),
#     State("window-size-input-gain", "value"),
#     State("min-threshold-gain", "value"),
#     State("min-threshold-input-gain", "value"),
#     # Indicators toggles
#     State("indicators-select", "value"),
#     prevent_initial_call=True,
# )
# def run_analysis_single(n_clicks, raw_payload, analysis_types,
#                  preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop,
#                  preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain,
#                  indicators_selected):
#     if not n_clicks:
#         return (no_update,) * 12
#     if not raw_payload:
#         # Hide all results when no data
#         hidden_style = {"display": "none"}
#         return (None, None, None, None, None, None, None, None, None, None, None, hidden_style)

#     try:
#         csv_bytes = base64.b64decode(raw_payload["csv_b64"].encode())
#         df = pd.read_csv(io.BytesIO(csv_bytes))
#     except Exception as e:
#         # Hide all results on error
#         hidden_style = {"display": "none"}
#         return (None, None, None, None, None, None, None, None, None, None, None, hidden_style)

#     df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
#     df["index"] = pd.to_numeric(df["index"], errors="coerce")
#     df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)

#     data_min, data_max = df["datetime"].min(), df["datetime"].max()

#     def build_outputs(mode: str,
#                       preset, sdate, edate, snap, ws_radio, ws_custom, th_radio, th_custom):
#         snap_month = ("snap" in (snap or []))
#         start, end = compute_range(preset, sdate, edate, data_min, data_max, snap_month)
#         dff = df[(df["datetime"] >= start) & (df["datetime"] <= end)].reset_index(drop=True)
#         if dff.empty:
#             msg = html.Div(f"No data in selected date range ({start.date()} to {end.date()}).", style={"color": "crimson"})
#             empty = go.Figure()
#             return msg, empty, empty, None, None

#         ws = int(ws_custom) if ws_custom else int(ws_radio)
#         th_pct = float(th_custom) if th_custom is not None else float(th_radio)
#         th_frac = th_pct / 100.0

#         # Weekend-aware summary
#         if mode == "gain":
#             summary = gain_event_analysis(dff, minimum_per_gain=th_frac, windows_size=ws)
#             title = "Gain Event Analysis"
#             label = "Min Gain: "
#             sign = +1
#             color = "#22c55e"
#         else:
#             summary = drop_event_analysis(dff, minimum_per_drop=th_frac, windows_size=ws)
#             title = "Drop Event Analysis"
#             label = "Min Drop: "
#             sign = -1
#             color = "#ef4444"

#         (k, v), = summary.items()
#         bg_color = "rgba(34,197,94,0.08)" if mode == "gain" else "rgba(239,68,68,0.08)"
#         border_color = "rgba(34,197,94,0.3)" if mode == "gain" else "rgba(239,68,68,0.3)"
#         card = html.Div([
#             html.H3(title, style={"marginTop": 0, "fontSize": "24px", "fontWeight": 700, "color": "inherit"}),
#             html.P([
#                 html.Strong("Change over: "), f"{ws} calendar days (weekend-aware) ",
#                 html.Span(" · "),
#                 html.Strong("Range: "), f"{start.date()} → {end.date()} ",
#                 html.Span(" · "),
#                 html.Strong(label), f"{th_pct:.2f}%",
#             ], style={"fontSize": "14px", "color": "inherit", "opacity": 0.8, "marginBottom": "20px"}),
#             html.Div([
#                 html.Div([
#                     html.Div("Events", style={"color": "rgba(255,255,255,0.7)", "fontSize": "13px", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
#                     html.Div(str(v["events"]), style={"fontSize": "36px", "fontWeight": 700, "color": color, "marginTop": "8px"}),
#                 ], style={"flex": 1, "textAlign": "center", "padding": "16px", "background": "rgba(255,255,255,0.05)", "borderRadius": "12px", "border": "1px solid rgba(255,255,255,0.1)"}),
#                 html.Div([
#                     html.Div("Probability", style={"color": "rgba(255,255,255,0.7)", "fontSize": "13px", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
#                     html.Div(v["probability"], style={"fontSize": "36px", "fontWeight": 700, "color": color, "marginTop": "8px"}),
#                 ], style={"flex": 1, "textAlign": "center", "padding": "16px", "background": "rgba(255,255,255,0.05)", "borderRadius": "12px", "border": "1px solid rgba(255,255,255,0.1)"}),
#             ], style={"display": "flex", "gap": "16px", "marginTop": "12px"}),
#         ], style={"border": f"1px solid {border_color}", "borderRadius": "16px", "padding": "24px", "background": bg_color, "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"})

#         # Weekend-aware returns for visuals
#         ret = compute_windowed_returns_calendar(dff, ws)
#         mask = ~ret.isna()
#         x_time = dff.loc[mask, "datetime"]
#         y_pct = ret.loc[mask].values * 100.0

#         # Return chart
#         line_fig = go.Figure()
#         if len(y_pct) > 0:
#             line_fig.add_trace(go.Scatter(x=x_time, y=y_pct, mode="lines", name=f"{ws}-day % change"))
#             th_line = sign * th_frac * 100.0
#             line_fig.add_trace(go.Scatter(x=x_time, y=[th_line]*len(x_time), mode="lines",
#                                           name="Threshold", line=dict(dash="dash")))
#             idx = np.arange(len(y_pct))
#             z = np.polyfit(idx, y_pct, 1)
#             trend = z[0]*idx + z[1]
#             line_fig.add_trace(go.Scatter(x=x_time, y=trend, mode="lines", name="Trend", line=dict(dash="dot")))
#         line_fig.update_layout(
#             template="plotly_dark",
#             plot_bgcolor="rgba(26,26,26,0.8)",
#             paper_bgcolor="rgba(10,10,10,0.8)",
#             font=dict(color="rgba(255,255,255,0.9)"),
#             margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
#             xaxis_title="Time", 
#             yaxis_title="% change",
#             legend=dict(
#                 orientation="h",
#                 yanchor="bottom",
#                 y=1.01,  # Position just above the chart
#                 xanchor="center",
#                 x=0.5,
#                 bgcolor="rgba(10,10,10,0.9)",
#                 bordercolor="rgba(255,255,255,0.2)",
#                 borderwidth=1,
#                 itemwidth=30,
#                 font=dict(size=10)
#             ),
#             xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
#             yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
#         )

#         # Bar chart (counts & probabilities by threshold)
#         ret_clean = ret.dropna()
#         N = len(ret_clean)
#         thresholds_pct = [i for i in range(1, 11)]
#         labels = [f"{t}%" for t in thresholds_pct]
#         if mode == "gain":
#             counts = np.array([(ret_clean >= (t/100.0)).sum() for t in thresholds_pct], dtype=int)
#             bar_title = f"{ws}-day gain events"
#         else:
#             counts = np.array([(ret_clean <= -(t/100.0)).sum() for t in thresholds_pct], dtype=int)
#             bar_title = f"{ws}-day drop events"
#         probs = (counts / N) * 100.0 if N > 0 else np.zeros_like(counts, dtype=float)

#         bar_fig = make_subplots(specs=[[{"secondary_y": True}]])
#         bar_fig.add_trace(
#             go.Bar(
#                 x=labels, y=counts, name="Count",
#                 marker_color=color,
#                 text=[f"{c:,}" for c in counts], textposition="outside",
#                 cliponaxis=False,
#                 customdata=np.round(probs, 2),
#                 hovertemplate="<b>%{x}</b><br>Count: %{y:,}<br>Probability: %{customdata:.2f}%<extra></extra>",
#             ),
#             secondary_y=False,
#         )
#         max_prob = float(probs.max()) if len(probs) else 0.0
#         y2_top = max(5.0, np.ceil(max_prob * 1.15 / 5.0) * 5.0)
#         bar_fig.update_layout(
#             template="plotly_dark",
#             plot_bgcolor="rgba(26,26,26,0.8)",
#             paper_bgcolor="rgba(10,10,10,0.8)",
#             font=dict(color="rgba(255,255,255,0.9)"),
#             title=dict(
#                 text=bar_title + (f"  · N={N}" if N else ""),
#                 x=0.5,
#                 xanchor="center",
#                 y=0.98,
#                 yanchor="top"
#             ),
#             margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
#             legend=dict(
#                 orientation="h",
#                 yanchor="bottom",
#                 y=1.01,  # Position just above the chart
#                 xanchor="center",
#                 x=0.5,
#                 bgcolor="rgba(10,10,10,0.9)",
#                 bordercolor="rgba(255,255,255,0.2)",
#                 borderwidth=1,
#                 itemwidth=30,
#                 font=dict(size=10)
#             ),
#             xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
#             yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
#             bargap=0.2
#         )
#         bar_fig.update_yaxes(title_text="Count of events", secondary_y=False)
#         bar_fig.update_yaxes(title_text="Probability (%)", range=[0, y2_top], secondary_y=True)

#         # Stats
#         if N > 0:
#             desc = ret_clean.describe()
#             stats_list = [
#                 ("Data points", f"{int(desc['count'])}"),
#                 ("Average change", f"{desc['mean']*100:.2f}%"),
#                 ("Typical variability (stdev)", f"{desc['std']*100:.2f}%"),
#                 ("Biggest drop", f"{desc['min']*100:.2f}%"),
#                 ("25th percentile", f"{desc['25%']*100:.2f}%"),
#                 ("Median (middle)", f"{desc['50%']*100:.2f}%"),
#                 ("75th percentile", f"{desc['75%']*100:.2f}%"),
#                 ("Biggest rise", f"{desc['max']*100:.2f}%"),
#             ]
#         else:
#             stats_list = [("Data points", "0")]
#         stats_view = html.Div([
#             html.H4("Change summary", style={"margin": "0 0 16px 0", "fontSize": "20px", "fontWeight": 600, "color": "inherit"}),
#             html.Ul([html.Li(html.Span([html.Strong(k + ": ", style={"color": "inherit"}), v]), style={
#                 "marginBottom": "8px", "fontSize": "14px", "color": "inherit", "opacity": 0.9
#             }) for k, v in stats_list], style={"listStyle": "none", "padding": 0})
#         ], style={"background": "rgba(255,255,255,0.05)", "border": "1px solid rgba(255,255,255,0.1)",
#                   "borderRadius": "16px", "padding": "24px", "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"})

#         # Trade windows list
#         # trade_table = build_trade_window_table(dff[["datetime","index"]], ws, limit=200)
        
#         # Wrap graphs and tables in containers with proper styling
#         return_chart_container = html.Div([
#             dcc.Graph(figure=line_fig, config={"displayModeBar": False}, style={"height": "320px"})
#         ], style={
#             "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#             "padding":"16px", "marginBottom":"16px",
#             "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#             "border":"1px solid rgba(255,255,255,0.1)"
#         })
        
#         bar_chart_container = html.Div([
#             dcc.Graph(figure=bar_fig, config={"displayModeBar": False}, style={"height": "320px"})
#         ], style={
#             "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#             "padding":"16px", "marginBottom":"16px",
#             "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#             "border":"1px solid rgba(255,255,255,0.1)"
#         })
        
#         # COMMENTED OUT FOR DEBUGGING - Trade windows data hidden
#         # trade_windows_container = html.Div([
#         #     html.H4("Trade windows (first and last day)", style={
#         #         "fontSize":"20px", "fontWeight":600, "color":"inherit",
#         #         "marginTop":"32px", "marginBottom":"16px"
#         #     }),
#         #     trade_table
#         # ], style={
#         #     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#         #     "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#         #     "border":"1px solid rgba(255,255,255,0.1)"
#         # })
#         trade_windows_container = html.Div()  # Empty placeholder

#         return card, return_chart_container, bar_chart_container, stats_view, trade_windows_container, dff

#     want_drop = "drop" in (analysis_types or [])
#     want_gain = "gain" in (analysis_types or [])

#     drop_out = build_outputs("drop",
#                              preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop) \
#                if want_drop else (html.Div("Drop disabled"), None, None, None, None, None)

#     gain_out = build_outputs("gain",
#                              preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain) \
#                if want_gain else (html.Div("Gain disabled"), None, None, None, None, None)

#     # Build indicators figure from the union of the filtered range (prefer gain range if both same; else use full df slice)
#     # We'll use the DROP slice if available, else GAIN slice, else overall df.
#     dff_for_indicators = None
#     if drop_out[-1] is not None:
#         dff_for_indicators = drop_out[-1]
#     if gain_out[-1] is not None:
#         # if both exist, take intersection of their date windows to keep consistent
#         if dff_for_indicators is not None:
#             s1, e1 = dff_for_indicators["datetime"].min(), dff_for_indicators["datetime"].max()
#             s2, e2 = gain_out[-1]["datetime"].min(), gain_out[-1]["datetime"].max()
#             s, e = max(s1, s2), min(e1, e2)
#             dff_for_indicators = df[(df["datetime"]>=s) & (df["datetime"]<=e)].reset_index(drop=True)
#         else:
#             dff_for_indicators = gain_out[-1]
#     if dff_for_indicators is None:
#         dff_for_indicators = df.copy()

#     # --- Build indicators and figure
#     feats = build_indicators(dff_for_indicators[["datetime","index"]].copy())
#     price = dff_for_indicators["index"].astype(float)
#     time = dff_for_indicators["datetime"]

#     show_sma  = "sma"  in (indicators_selected or [])
#     show_ema  = "ema"  in (indicators_selected or [])
#     show_bb   = "bb"   in (indicators_selected or [])
#     show_rsi  = "rsi"  in (indicators_selected or [])
#     show_macd = "macd" in (indicators_selected or [])
#     show_vol  = "vol"  in (indicators_selected or [])
#     show_dd   = "dd"   in (indicators_selected or [])

#     # Determine which rows to show
#     row1_needed = any([True, show_sma, show_ema, show_bb, show_vol, show_dd])  # price always shown
#     row2_needed = show_rsi
#     row3_needed = show_macd

#     rows = (1 if row1_needed else 0) + (1 if row2_needed else 0) + (1 if row3_needed else 0)
#     if rows == 0:
#         rows = 1  # safety

#     fig_ind = make_subplots(
#         rows=rows, cols=1, shared_xaxes=True,
#         row_heights=[0.5 if rows==3 else (0.65 if rows==2 else 1.0)] + ([0.25] if rows>=2 else []) + ([0.25] if rows==3 else []),
#         vertical_spacing=0.06,
#         specs=[[{"secondary_y": True}] for _ in range(rows)]
#     )

#     # helper to map logical row numbers
#     cur_row = 1
#     row_price = cur_row
#     # Row 1: Price + overlays
#     fig_ind.add_trace(go.Scatter(x=time, y=price, mode="lines", name="Price"), row=row_price, col=1, secondary_y=False)

#     if show_sma:
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["sma_5"],  mode="lines", name="SMA 5"),  row=row_price, col=1, secondary_y=False)
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["sma_20"], mode="lines", name="SMA 20"), row=row_price, col=1, secondary_y=False)
#     if show_ema:
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["ema_12"], mode="lines", name="EMA 12"), row=row_price, col=1, secondary_y=False)
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["ema_26"], mode="lines", name="EMA 26"), row=row_price, col=1, secondary_y=False)
#     if show_bb:
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["bb_mid"], mode="lines", name="BB Mid"),   row=row_price, col=1, secondary_y=False)
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["bb_up"],  mode="lines", name="BB Upper"), row=row_price, col=1, secondary_y=False)
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["bb_lo"],  mode="lines", name="BB Lower"), row=row_price, col=1, secondary_y=False)
#     if show_vol:
#         # plot vol_20 on secondary y to keep scales tidy
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["vol_20"], mode="lines", name="Vol 20 (stdev)"),
#                           row=row_price, col=1, secondary_y=True)
#     if show_dd:
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["dd"], mode="lines", name="Drawdown"),
#                           row=row_price, col=1, secondary_y=True)

#     fig_ind.update_yaxes(title_text="Price", row=row_price, col=1, secondary_y=False)
#     if show_vol or show_dd:
#         fig_ind.update_yaxes(title_text="Vol / DD", row=row_price, col=1, secondary_y=True)

#     # Row 2: RSI (if needed)
#     if row2_needed:
#         cur_row += 1
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["rsi_14"], mode="lines", name="RSI (14)"),
#                           row=cur_row, col=1, secondary_y=False)
#         fig_ind.add_hline(y=70, line=dict(dash="dash"), row=cur_row, col=1)
#         fig_ind.add_hline(y=30, line=dict(dash="dash"), row=cur_row, col=1)
#         fig_ind.update_yaxes(title_text="RSI", range=[0, 100], row=cur_row, col=1)

#     # Row 3: MACD (if needed)
#     if row3_needed:
#         cur_row += 1
#         fig_ind.add_trace(go.Bar(x=time, y=feats["macd_hist"], name="MACD Hist"),
#                           row=cur_row, col=1, secondary_y=False)
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["macd"],     mode="lines", name="MACD"),
#                           row=cur_row, col=1, secondary_y=False)
#         fig_ind.add_trace(go.Scatter(x=time, y=feats["macd_sig"], mode="lines", name="MACD Signal"),
#                           row=cur_row, col=1, secondary_y=False)
#         fig_ind.update_yaxes(title_text="MACD", row=cur_row, col=1)

#     # Calculate proper margins to accommodate legend outside plotting area
#     # Legend will be positioned above the chart, so we need extra top margin
#     legend_height = 60  # Estimated height for horizontal legend
#     top_margin = 120 + legend_height  # Extra top margin for legend above chart
#     bottom_margin = 80  # Base bottom margin
    
#     fig_ind.update_layout(
#         template="plotly_dark",
#         plot_bgcolor="rgba(26,26,26,0.8)",
#         paper_bgcolor="rgba(10,10,10,0.8)",
#         font=dict(color="rgba(255,255,255,0.9)"),
#         margin=dict(t=top_margin, r=10, l=40, b=bottom_margin),  # Extra top margin for legend above
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.01,  # Position just above the chart (outside plotting area)
#             xanchor="center",
#             x=0.5,
#             itemwidth=30,
#             font=dict(size=10),
#             bgcolor="rgba(10,10,10,0.9)",
#             bordercolor="rgba(255,255,255,0.2)",
#             borderwidth=1,
#             tracegroupgap=10,  # Space between legend items
#             entrywidthmode="fraction",
#             entrywidth=0.15  # Control width of legend items
#         ),
#         title=dict(
#             text="Indicators (weekend-aware where applicable)",
#             x=0.5,
#             xanchor="center",
#             font=dict(size=16),
#             y=0.95,
#             yanchor="top"
#         ),
#         xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
#         yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
#     )
    
#     # Update all subplot x-axes to have consistent styling and prevent overlap
#     for i in range(1, cur_row + 1):
#         fig_ind.update_xaxes(
#             showgrid=True,
#             gridcolor="rgba(255,255,255,0.1)",
#             row=i, col=1
#     )

#     # Unpack results for return
#     drop_card, drop_line, drop_bar, drop_stats, drop_table, _dff_drop = drop_out
#     gain_card, gain_line, gain_bar, gain_stats, gain_table, _dff_gain = gain_out
    
#     # Wrap indicators figure in container
#     indicators_container = html.Div([
#         html.H3("Indicator Charts", style={
#             "fontSize":"28px", "fontWeight":700, "color":"inherit",
#             "marginTop":"40px", "marginBottom":"20px"
#         }),
#         dcc.Graph(figure=fig_ind, config={"displayModeBar": False}, style={"height":"540px"})
#     ], style={
#         "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#         "padding":"20px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#         "border":"1px solid rgba(255,255,255,0.1)"
#     })
    
#     # Show results container
#     results_style = {"display": "flex", "gap": "20px", "flexWrap": "wrap"}

#     return (drop_card, drop_line, drop_bar, drop_stats, drop_table,
#             gain_card, gain_line, gain_bar, gain_stats, gain_table,
#             indicators_container, results_style)

# # -----------------------------
# # Upload callback (CROSS page)
# # -----------------------------
# @app.callback(
#     # A side
#     Output("file-msg-a", "children"),
#     Output("warn-msg-a", "children"),
#     Output("preview-a", "children"),
#     Output(STORE_A, "data"),
#     # B side
#     Output("file-msg-b", "children"),
#     Output("warn-msg-b", "children"),
#     Output("preview-b", "children"),
#     Output(STORE_B, "data"),
#     # Date range bounds (shared)
#     Output("date-range-cross", "min_date_allowed"),
#     Output("date-range-cross", "max_date_allowed"),
#     Output("date-range-cross", "start_date"),
#     Output("date-range-cross", "end_date"),
#     # Year jump options
#     Output("jump-year-cross", "options"),
#     Output("jump-year-cross", "value"),
#     Output("jump-month-cross", "value"),

#     Input("uploader-a", "contents"),
#     State("uploader-a", "filename"),
#     Input("uploader-b", "contents"),
#     State("uploader-b", "filename"),
#     prevent_initial_call=True,
# )
# def upload_cross(contents_a, filename_a, contents_b, filename_b):
#     out = [no_update]*15

#     # Parse A
#     dfA = warnsA = errA = None
#     if contents_a is not None:
#         dfA, warnsA, errA = parse_csv_flexible(contents_a, filename_a)
#         if errA:
#             out[0] = html.Div(errA, style={"color":"crimson"})
#             out[1] = None
#             out[2] = None
#             out[3] = None
#         else:
#             out[0] = html.Div([html.Strong("A uploaded:"), f" {filename_a} · Rows: {len(dfA)}"])
#             out[1] = (html.Div([html.Strong("Warnings:"), html.Ul([html.Li(w) for w in warnsA])],
#                                style={"color":"#996800"}) if warnsA else None)
#             tableA = dash_table.DataTable(
#                 data=dfA.head(10).to_dict("records"),
#                 columns=[{"name": c, "id": c} for c in dfA.columns],
#                 page_size=10, 
#                 style_table={"overflowX":"auto", "backgroundColor": "#1a1a1a"},
#                 style_cell={
#                     "textAlign":"left",
#                     "minWidth":"120px",
#                     "backgroundColor": "#1a1a1a",
#                     "color": "rgba(255,255,255,0.9)",
#                     "border": "1px solid rgba(255,255,255,0.1)",
#                     "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
#                 },
#                 style_header={
#                     "backgroundColor": "#252525",
#                     "color": "rgba(255,255,255,0.95)",
#                     "fontWeight": "600",
#                     "border": "1px solid rgba(0,200,150,0.3)",
#                     "textAlign": "left"
#                 },
#                 style_data={
#                     "backgroundColor": "#1a1a1a",
#                     "color": "rgba(255,255,255,0.9)",
#                     "border": "1px solid rgba(255,255,255,0.1)"
#                 },
#                 style_data_conditional=[
#                     {
#                         "if": {"row_index": "even"},
#                         "backgroundColor": "#222222",
#                     },
#                     {
#                         "if": {"state": "selected"},
#                         "backgroundColor": "rgba(0,200,150,0.2)",
#                         "border": "1px solid rgba(0,200,150,0.5)"
#                     }
#                 ],
#             )
#             out[2] = html.Div([html.H4("Preview A (first 10)"), tableA])
#             out[3] = {
#                 "filename": filename_a,
#                 "csv_b64": base64.b64encode(dfA.to_csv(index=False).encode()).decode()
#             }

#     # Parse B
#     dfB = warnsB = errB = None
#     if contents_b is not None:
#         dfB, warnsB, errB = parse_csv_flexible(contents_b, filename_b)
#         if errB:
#             out[4] = html.Div(errB, style={"color":"crimson"})
#             out[5] = None
#             out[6] = None
#             out[7] = None
#         else:
#             out[4] = html.Div([html.Strong("B uploaded:"), f" {filename_b} · Rows: {len(dfB)}"])
#             out[5] = (html.Div([html.Strong("Warnings:"), html.Ul([html.Li(w) for w in warnsB])],
#                                style={"color":"#996800"}) if warnsB else None)
#             tableB = dash_table.DataTable(
#                 data=dfB.head(10).to_dict("records"),
#                 columns=[{"name": c, "id": c} for c in dfB.columns],
#                 page_size=10, 
#                 style_table={"overflowX":"auto", "backgroundColor": "#1a1a1a"},
#                 style_cell={
#                     "textAlign":"left",
#                     "minWidth":"120px",
#                     "backgroundColor": "#1a1a1a",
#                     "color": "rgba(255,255,255,0.9)",
#                     "border": "1px solid rgba(255,255,255,0.1)",
#                     "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
#                 },
#                 style_header={
#                     "backgroundColor": "#252525",
#                     "color": "rgba(255,255,255,0.95)",
#                     "fontWeight": "600",
#                     "border": "1px solid rgba(0,200,150,0.3)",
#                     "textAlign": "left"
#                 },
#                 style_data={
#                     "backgroundColor": "#1a1a1a",
#                     "color": "rgba(255,255,255,0.9)",
#                     "border": "1px solid rgba(255,255,255,0.1)"
#                 },
#                 style_data_conditional=[
#                     {
#                         "if": {"row_index": "even"},
#                         "backgroundColor": "#222222",
#                     },
#                     {
#                         "if": {"state": "selected"},
#                         "backgroundColor": "rgba(0,200,150,0.2)",
#                         "border": "1px solid rgba(0,200,150,0.5)"
#                     }
#                 ],
#             )
#             out[6] = html.Div([html.H4("Preview B (first 10)"), tableB])
#             out[7] = {
#                 "filename": filename_b,
#                 "csv_b64": base64.b64encode(dfB.to_csv(index=False).encode()).decode()
#             }

#     # Set date bounds based on whichever is loaded; if both, use intersection
#     if dfA is None and dfB is None:
#         return tuple(out)

#     if dfA is not None and dfB is not None:
#         min_d = max(dfA["datetime"].min().date(), dfB["datetime"].min().date())
#         max_d = min(dfA["datetime"].max().date(), dfB["datetime"].max().date())
#         if min_d > max_d:
#             # No overlap
#             out[8]  = None
#             out[9]  = None
#             out[10] = None
#             out[11] = None
#             out[12] = []
#             out[13] = None
#             out[14] = None
#             return tuple(out)
#     elif dfA is not None:
#         min_d = dfA["datetime"].min().date()
#         max_d = dfA["datetime"].max().date()
#     else:
#         min_d = dfB["datetime"].min().date()
#         max_d = dfB["datetime"].max().date()

#     years = list(range(min_d.year, max_d.year + 1))
#     year_options = [{"label": str(y), "value": y} for y in years]

#     out[8]  = min_d
#     out[9]  = max_d
#     out[10] = min_d
#     out[11] = max_d
#     out[12] = year_options
#     out[13] = min_d.year
#     out[14] = 1
#     return tuple(out)

# # Preset → custom when dates edited (CROSS page)
# @app.callback(Output("preset-cross", "value"),
#               Input("date-range-cross", "start_date"),
#               Input("date-range-cross", "end_date"),
#               prevent_initial_call=True)
# def force_custom_cross(_s, _e):
#     return "custom"

# # Jump-to initial_visible_month (CROSS page)
# @app.callback(
#     Output("date-range-cross", "initial_visible_month"),
#     Input("jump-year-cross", "value"),
#     Input("jump-month-cross", "value"),
#     State("date-range-cross", "initial_visible_month"),
#     prevent_initial_call=True
# )
# def jump_cross(year, month, _cur):
#     if year and month:
#         return pd.Timestamp(int(year), int(month), 1)
#     return no_update

# # -----------------------------
# # Analyze callback (CROSS page)
# # -----------------------------
# @app.callback(
#     Output("x-line-levels-container", "children"),
#     Output("x-scatter-returns-container", "children"),
#     Output("x-line-returns-container", "children"),
#     Output("x-stats", "children"),
#     Output("x-trade-windows-container", "children"),
#     Output("x-results-container", "style"),
#     Input("x-analyze", "n_clicks"),
#     State(STORE_A, "data"),
#     State(STORE_B, "data"),
#     State("preset-cross", "value"),
#     State("date-range-cross", "start_date"),
#     State("date-range-cross", "end_date"),
#     State("snap-month-cross", "value"),
#     State("x-window", "value"),
#     prevent_initial_call=True,
# )
# def run_cross(n_clicks, rawA, rawB, preset, sd, ed, snap_val, win):
#     if not n_clicks:
#         return (no_update,) * 6
#     if not rawA or not rawB:
#         # Hide all results when no data
#         hidden_style = {"display": "none"}
#         return None, None, None, None, None, hidden_style

#     # Load A & B
#     try:
#         dfA = pd.read_csv(io.BytesIO(base64.b64decode(rawA["csv_b64"].encode())))
#         dfB = pd.read_csv(io.BytesIO(base64.b64decode(rawB["csv_b64"].encode())))
#     except Exception as e:
#         # Hide all results on error
#         hidden_style = {"display": "none"}
#         return None, None, None, None, None, hidden_style

#     for df in (dfA, dfB):
#         df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
#         df["index"] = pd.to_numeric(df["index"], errors="coerce")
#     dfA = dfA.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)
#     dfB = dfB.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)

#     # Determine overall range intersection
#     data_min = max(dfA["datetime"].min(), dfB["datetime"].min())
#     data_max = min(dfA["datetime"].max(), dfB["datetime"].max())
#     if data_min >= data_max:
#         # Hide all results when no overlap
#         hidden_style = {"display": "none"}
#         return None, None, None, None, None, hidden_style

#     snap = ("snap" in (snap_val or []))
#     start, end = compute_range(preset, sd, ed, data_min, data_max, snap)

#     # Slice to range and inner-join on dates for level chart
#     A_in = dfA[(dfA["datetime"]>=start) & (dfA["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"A"})
#     B_in = dfB[(dfB["datetime"]>=start) & (dfB["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"B"})
#     levels = pd.merge(A_in, B_in, on="datetime", how="inner")
#     if levels.empty:
#         # Hide all results when no data in range
#         hidden_style = {"display": "none"}
#         return None, None, None, None, None, hidden_style

#     # -------- Chart 1: Levels normalized to 100 at range start --------
#     baseA = levels["A"].iloc[0]
#     baseB = levels["B"].iloc[0]
#     normA = 100 * levels["A"] / baseA
#     normB = 100 * levels["B"] / baseB

#     fig_levels = go.Figure()
#     fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normA, mode="lines", name="Index A (norm. to 100)"))
#     fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normB, mode="lines", name="Index B (norm. to 100)"))
#     fig_levels.update_layout(
#         template="plotly_dark",
#         plot_bgcolor="rgba(26,26,26,0.8)",
#         paper_bgcolor="rgba(10,10,10,0.8)",
#         font=dict(color="rgba(255,255,255,0.9)"),
#         title=f"Both Indexes (normalized) · {start.date()} → {end.date()}",
#         margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
#         xaxis_title="Date", 
#         yaxis_title="Indexed level (start=100)",
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.01,
#             xanchor="center",
#             x=0.5,
#             bgcolor="rgba(10,10,10,0.9)",
#             bordercolor="rgba(255,255,255,0.2)",
#             borderwidth=1,
#             itemwidth=30,
#             font=dict(size=10)
#         ),
#         xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
#         yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
#     )

#     # -------- Weekend-aware returns (window size in calendar days) --------
#     win = max(int(win or 1), 1)
#     retA_series = compute_windowed_returns_calendar(dfA, win)
#     retB_series = compute_windowed_returns_calendar(dfB, win)

#     tmpA = dfA.assign(retA=retA_series)
#     tmpB = dfB.assign(retB=retB_series)
#     tmpA = tmpA[(tmpA["datetime"]>=start) & (tmpA["datetime"]<=end)]
#     tmpB = tmpB[(tmpB["datetime"]>=start) & (tmpB["datetime"]<=end)]

#     rets = pd.merge(
#         tmpA[["datetime","retA"]],
#         tmpB[["datetime","retB"]],
#         on="datetime",
#         how="inner"
#     ).dropna(subset=["retA","retB"])

#     if rets.empty:
#         # Hide all results when no returns data
#         hidden_style = {"display": "none"}
#         return None, None, None, None, None, hidden_style

#     # -------- Chart 2: Correlation scatter (windowed returns) --------
#     x = rets["retB"].values * 100.0
#     y = rets["retA"].values * 100.0
#     if len(x) >= 2:
#         corr = float(np.corrcoef(x, y)[0,1])
#     else:
#         corr = float("nan")

#     fig_scatter = go.Figure()
#     fig_scatter.add_trace(go.Scatter(
#         x=x, y=y, mode="markers", name=f"{win}-day returns",
#         hovertemplate="B: %{x:.2f}%<br>A: %{y:.2f}%<extra></extra>"
#     ))
#     if len(x) >= 2:
#         m, b = np.polyfit(x, y, 1)
#         xfit = np.linspace(x.min(), x.max(), 100)
#         yfit = m*xfit + b
#         fig_scatter.add_trace(go.Scatter(x=xfit, y=yfit, mode="lines", name="Fit", line=dict(dash="dash")))
#         subtitle = f"Pearson corr = {corr:.2f} · slope≈{m:.2f} (beta A on B)"
#     else:
#         subtitle = "Pearson corr = n/a"
#     fig_scatter.update_layout(
#         template="plotly_dark",
#         plot_bgcolor="rgba(26,26,26,0.8)",
#         paper_bgcolor="rgba(10,10,10,0.8)",
#         font=dict(color="rgba(255,255,255,0.9)"),
#         title=dict(
#             text=f"Correlation (windowed returns) — {subtitle}",
#             x=0.5,
#             xanchor="center",
#             y=0.98,
#             yanchor="top"
#         ),
#         margin=dict(t=100, r=10, l=50, b=50),  # Increased top margin for legend
#         xaxis_title=f"Index B {win}-day return (%)",
#         yaxis_title=f"Index A {win}-day return (%)",
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.01,
#             xanchor="center",
#             x=0.5,
#             bgcolor="rgba(10,10,10,0.9)",
#             bordercolor="rgba(255,255,255,0.2)",
#             borderwidth=1,
#             itemwidth=30,
#             font=dict(size=10)
#         ),
#         xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
#         yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
#     )

#     # -------- Chart 3: Windowed returns through time --------
#     ret_time = rets.reset_index(drop=True)
#     fig_returns = go.Figure()
#     fig_returns.add_trace(go.Scatter(
#         x=ret_time["datetime"], y=ret_time["retA"]*100.0, mode="lines", name=f"A {win}-day %"
#     ))
#     fig_returns.add_trace(go.Scatter(
#         x=ret_time["datetime"], y=ret_time["retB"]*100.0, mode="lines", name=f"B {win}-day %"
#     ))
#     fig_returns.update_layout(
#         template="plotly_dark",
#         plot_bgcolor="rgba(26,26,26,0.8)",
#         paper_bgcolor="rgba(10,10,10,0.8)",
#         font=dict(color="rgba(255,255,255,0.9)"),
#         title=f"{win}-day Returns Over Time · {start.date()} → {end.date()}",
#         margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
#         xaxis_title="Date", 
#         yaxis_title=f"{win}-day return (%)",
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.01,
#             xanchor="center",
#             x=0.5,
#             bgcolor="rgba(10,10,10,0.9)",
#             bordercolor="rgba(255,255,255,0.2)",
#             borderwidth=1,
#             itemwidth=30,
#             font=dict(size=10)
#         ),
#         xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
#         yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
#     )

#     # -------- Stats card --------
#     def stats_block(name, s):
#         desc = s.describe()
#         items = [
#             ("Data points", f"{int(desc['count'])}"),
#             ("Average %",   f"{desc['mean']*100:.2f}%"),
#             ("Std dev %",   f"{desc['std']*100:.2f}%"),
#             ("Min %",       f"{desc['min']*100:.2f}%"),
#             ("25% %",       f"{desc['25%']*100:.2f}%"),
#             ("Median %",    f"{desc['50%']*100:.2f}%"),
#             ("75% %",       f"{desc['75%']*100:.2f}%"),
#             ("Max %",       f"{desc['max']*100:.2f}%"),
#         ]
#         return html.Div([
#             html.H4(name, style={"margin":"0 0 16px 0", "fontSize":"18px", "fontWeight":600, "color":"inherit"}),
#             html.Ul([html.Li(html.Span([html.Strong(k + ": ", style={"color":"inherit"}), v]), style={
#                 "marginBottom":"8px", "fontSize":"14px", "color":"inherit", "opacity":0.9
#             }) for k, v in items], style={"listStyle":"none", "padding":0})
#         ], style={"flex":1, "background":"rgba(255,255,255,0.05)","border":"1px solid rgba(255,255,255,0.1)",
#                   "borderRadius":"16px","padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)"})

#     corr_text = html.Div([
#         html.H4("Relationship", style={"margin":"0 0 12px 0", "fontSize":"18px", "fontWeight":600, "color":"inherit"}),
#         html.P(f"Pearson correlation (windowed returns): {corr:.2f}" if np.isfinite(corr) else
#                "Pearson correlation (windowed returns): n/a", style={
#                    "fontSize":"16px", "color":"inherit", "opacity":0.9, "margin":0,
#                    "fontWeight":500 if np.isfinite(corr) else 400
#                })
#     ], style={"flex":1, "background":"rgba(0,200,150,0.08)","border":"1px solid rgba(0,200,150,0.3)",
#               "borderRadius":"16px","padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)"})

#     stats_view = html.Div([
#         html.Div([
#             stats_block("Index A — Stats", rets["retA"]),
#             stats_block("Index B — Stats", rets["retB"]),
#             corr_text
#         ], style={"display":"flex","gap":"12px","flexWrap":"wrap"})
#     ])

#     twin = html.Div()  # Empty placeholder
    
#     # Wrap graphs in containers
#     levels_container = html.Div([
#         dcc.Graph(figure=fig_levels, config={"displayModeBar": False}, style={"height":"360px"})
#     ], style={
#         "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#         "padding":"20px", "marginBottom":"24px",
#         "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#         "border":"1px solid rgba(255,255,255,0.1)"
#     })
    
#     scatter_container = html.Div([
#         dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}, style={"height":"360px"})
#     ], style={
#         "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#         "padding":"20px", "marginBottom":"24px",
#         "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#         "border":"1px solid rgba(255,255,255,0.1)"
#     })
    
#     returns_container = html.Div([
#         dcc.Graph(figure=fig_returns, config={"displayModeBar": False}, style={"height":"360px"})
#     ], style={
#         "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#         "padding":"20px", "marginBottom":"24px",
#         "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#         "border":"1px solid rgba(255,255,255,0.1)"
#     })
    
#     # Show results container
#     results_style = {"marginTop": "32px"}

#     return levels_container, scatter_container, returns_container, stats_view, twin, results_style


# # Local run (useful for dev & Render health checks)
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8050))
#     app.run_server(host="0.0.0.0", port=port, debug=False)



# # ===============================================================================================================================================================================================================


import os
import base64
import io
import numpy as np
import pandas as pd

import dash
from dash import Dash, html, dcc, dash_table, no_update
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------
# App Setup (multi-page)
# -----------------------------
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Index Data Analysis"

# Custom CSS to remove white borders and enhance dark theme
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                margin: 0;
                padding: 0;
                border: none !important;
                transition: background-color 0.3s ease, color 0.3s ease;
            }
            html {
                margin: 0;
                padding: 0;
                border: none !important;
            }
            #react-entry-point {
                margin: 0;
                padding: 0;
                border: none !important;
            }
            ._dash-loading {
                margin: 0;
                padding: 0;
            }
            #app-container {
                transition: background-color 0.3s ease, color 0.3s ease;
            }
            #navbar-container {
                transition: background-color 0.3s ease, color 0.3s ease;
            }
            #page-content {
                transition: color 0.3s ease;
            }
            /* Upload box hover effect */
            [id="uploader"]:hover, [id="uploader-a"]:hover, [id="uploader-b"]:hover {
                border-color: rgba(0,200,150,0.6) !important;
                background: rgba(0,200,150,0.1) !important;
                transform: scale(1.01);
                box-shadow: 0 4px 16px rgba(0,200,150,0.2) !important;
            }
            [id="uploader"]:hover span:last-child, [id="uploader-a"]:hover span:last-child, [id="uploader-b"]:hover span:last-child {
                opacity: 1 !important;
                transform: scale(1.1);
            }
            /* DataTable dark theme styles */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
                background-color: #1a1a1a !important;
                color: rgba(255,255,255,0.9) !important;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table thead th {
                background-color: #252525 !important;
                color: rgba(255,255,255,0.95) !important;
                border-color: rgba(0,200,150,0.3) !important;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody tr {
                background-color: #1a1a1a !important;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody tr:nth-child(even) {
                background-color: #222222 !important;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody tr:hover {
                background-color: rgba(0,200,150,0.15) !important;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table tbody td {
                border-color: rgba(255,255,255,0.1) !important;
                color: rgba(255,255,255,0.9) !important;
            }
            /* Dark theme for form inputs */
            .Select-control, .Select-input, .Select-placeholder, .Select-value, .Select-value-label {
                background-color: rgba(255,255,255,0.1) !important;
                color: rgba(255,255,255,0.9) !important;
                border-color: rgba(255,255,255,0.2) !important;
            }
            .Select-menu-outer {
                background-color: #1a1a1a !important;
                border-color: rgba(255,255,255,0.2) !important;
            }
            .Select-option {
                background-color: #1a1a1a !important;
                color: rgba(255,255,255,0.9) !important;
            }
            .Select-option.is-focused {
                background-color: rgba(0,200,150,0.2) !important;
            }
            .Select-option.is-selected {
                background-color: rgba(0,200,150,0.4) !important;
            }
            input[type="text"], input[type="number"], input[type="date"] {
                background-color: rgba(255,255,255,0.1) !important;
                color: rgba(255,255,255,0.9) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                border-radius: 4px !important;
                padding: 6px 8px !important;
            }
            input[type="text"]:focus, input[type="number"]:focus, input[type="date"]:focus {
                border-color: rgba(0,200,150,0.6) !important;
                outline: none !important;
                box-shadow: 0 0 0 2px rgba(0,200,150,0.2) !important;
            }
            input[type="text"]::placeholder, input[type="number"]::placeholder {
                color: rgba(255,255,255,0.5) !important;
            }
            .DateInput {
                background-color: rgba(255,255,255,0.1) !important;
            }
            .DateInput_input {
                background-color: rgba(255,255,255,0.1) !important;
                color: rgba(255,255,255,0.9) !important;
                border-color: rgba(255,255,255,0.2) !important;
                font-size: 14px !important;
                padding: 8px 10px !important;
            }
            .DateInput_input__focused {
                border-color: rgba(0,200,150,0.6) !important;
                box-shadow: 0 0 0 2px rgba(0,200,150,0.2) !important;
            }
            .DateRangePickerInput {
                background-color: rgba(255,255,255,0.1) !important;
                border-color: rgba(255,255,255,0.2) !important;
                border-radius: 4px !important;
            }
            .DateRangePickerInput__withBorder {
                border-radius: 4px !important;
            }
            .DateRangePickerInput__disabled {
                background-color: rgba(255,255,255,0.05) !important;
            }
            .DateRangePickerInput_arrow {
                border-left-color: rgba(255,255,255,0.5) !important;
            }
            .DateRangePickerInput_arrow_svg {
                fill: rgba(255,255,255,0.7) !important;
            }
            /* Fix DatePickerRange clear button overlap */
            .DateInput__close {
                position: absolute !important;
                right: 8px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                z-index: 10 !important;
                background: rgba(255,255,255,0.1) !important;
                border-radius: 50% !important;
                width: 20px !important;
                height: 20px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                cursor: pointer !important;
            }
            .DateInput__close:hover {
                background: rgba(255,255,255,0.2) !important;
            }
            .DateInput__close svg {
                width: 12px !important;
                height: 12px !important;
            }
            .DateInput {
                position: relative !important;
                padding-right: 32px !important;
            }
            .DateRangePickerInput__withBorder {
                position: relative !important;
            }
            .DayPicker {
                background-color: #1a1a1a !important;
                color: rgba(255,255,255,0.9) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                border-radius: 8px !important;
            }
            .DayPicker__week-header {
                color: rgba(255,255,255,0.7) !important;
            }
            .DayPicker-Day {
                color: rgba(255,255,255,0.9) !important;
            }
            .DayPicker-Day--selected {
                background-color: rgba(0,200,150,0.6) !important;
                color: white !important;
            }
            .DayPicker-Day--hovered {
                background-color: rgba(0,200,150,0.3) !important;
            }
            .DayPicker-Day--outside {
                color: rgba(255,255,255,0.3) !important;
            }
            /* Color-coded radio buttons for Drop (red) and Gain (green) */
            #window-size-drop input[type="radio"],
            #min-threshold-drop input[type="radio"],
            #snap-month-drop input[type="checkbox"] {
                accent-color: rgba(239,68,68,0.8) !important;
            }
            #window-size-gain input[type="radio"],
            #min-threshold-gain input[type="radio"],
            #snap-month-gain input[type="checkbox"] {
                accent-color: rgba(34,197,94,0.8) !important;
            }
            /* Default accent for other radio/checkboxes */
            input[type="radio"] {
                accent-color: rgba(0,200,150,0.8) !important;
            }
            input[type="checkbox"] {
                accent-color: rgba(0,200,150,0.8) !important;
            }
            /* Improved spacing for radio buttons and inputs */
            .RadioItems, .Checklist {
                margin-bottom: 8px !important;
            }
            .RadioItems label, .Checklist label {
                margin-right: 12px !important;
                margin-bottom: 4px !important;
            }
            /* Better visual grouping for custom inputs */
            input[type="number"] {
                margin-top: 4px !important;
            }
            /* Responsive grid support */
            @media (max-width: 768px) {
                [style*="gridTemplateColumns"] {
                    grid-template-columns: 1fr !important;
                }
            }
            /* Focus states for accessibility */
            button:focus-visible, input:focus-visible, select:focus-visible {
                outline: none !important;
            }
            /* Hover states for buttons */
            button:hover:not(:disabled) {
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.2) !important;
            }
            button:active:not(:disabled) {
                transform: translateY(0);
            }
            /* Disabled state styling */
            button:disabled, input:disabled, select:disabled {
                opacity: 0.5 !important;
                cursor: not-allowed !important;
            }
            /* Improved input heights for consistency */
            input[type="text"], input[type="number"] {
                height: 40px !important;
                min-height: 40px !important;
            }
            /* Card hover effect */
            [style*="background"][style*="#121821"]:hover {
                box-shadow: 0 6px 16px rgba(0,0,0,0.4) !important;
            }
            /* Responsive button styling */
            @media (max-width: 768px) {
                #analyze, #x-analyze {
                    width: 100% !important;
                    float: none !important;
                }
                .card-footer {
                    text-align: center !important;
                }
            }
            /* DataTable pagination styling */
            .dash-table-toolbar {
                background-color: #1a1a1a !important;
                color: rgba(255,255,255,0.9) !important;
                padding: 8px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 8px !important;
                flex-wrap: wrap !important;
            }
            /* Style navigation buttons */
            .dash-table-toolbar .previous-page, 
            .dash-table-toolbar .next-page,
            .dash-table-toolbar .first-page,
            .dash-table-toolbar .last-page {
                background-color: rgba(255,255,255,0.1) !important;
                color: rgba(255,255,255,0.9) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                border-radius: 4px !important;
                padding: 6px 12px !important;
                margin: 0 !important;
                min-width: 36px !important;
                height: 32px !important;
                cursor: pointer !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 14px !important;
                line-height: 1 !important;
                box-sizing: border-box !important;
            }
            .dash-table-toolbar .previous-page:hover, 
            .dash-table-toolbar .next-page:hover,
            .dash-table-toolbar .first-page:hover,
            .dash-table-toolbar .last-page:hover {
                background-color: rgba(0,200,150,0.2) !important;
                border-color: rgba(0,200,150,0.4) !important;
            }
            .dash-table-toolbar .previous-page:disabled, 
            .dash-table-toolbar .next-page:disabled,
            .dash-table-toolbar .first-page:disabled,
            .dash-table-toolbar .last-page:disabled {
                opacity: 0.3 !important;
                cursor: not-allowed !important;
            }
            /* Fix duplicate page number - hide all spans/divs that might show duplicate page number */
            /* Target the container that holds the page input */
            .dash-table-toolbar > div {
                display: inline-flex !important;
                align-items: center !important;
                position: relative !important;
                height: 32px !important;
            }
            /* Hide ALL child elements in the input container EXCEPT the input itself */
            .dash-table-toolbar > div:has(input[type="number"]) > span,
            .dash-table-toolbar > div:has(input[type="number"]) > div:not(:has(input)),
            .dash-table-toolbar > div:has(input[type="number"]) > label,
            .dash-table-toolbar > div:has(input[type="number"]) > *:not(input[type="number"]) {
                display: none !important;
                visibility: hidden !important;
            }
            /* Style the page number input */
            .dash-table-toolbar input[type="number"] {
                background-color: rgba(255,255,255,0.1) !important;
                color: rgba(255,255,255,0.9) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                border-radius: 4px !important;
                padding: 6px 10px !important;
                width: 60px !important;
                min-width: 60px !important;
                max-width: 60px !important;
                text-align: center !important;
                font-weight: 500 !important;
                font-size: 14px !important;
                line-height: 1.2 !important;
                height: 32px !important;
                -moz-appearance: textfield !important;
                box-sizing: border-box !important;
                display: inline-block !important;
                visibility: visible !important;
                position: relative !important;
                z-index: 1 !important;
            }
            /* Hide spinner buttons on number input */
            .dash-table-toolbar input[type="number"]::-webkit-inner-spin-button,
            .dash-table-toolbar input[type="number"]::-webkit-outer-spin-button {
                -webkit-appearance: none !important;
                margin: 0 !important;
            }
            /* Hide any duplicate inputs */
            .dash-table-toolbar input[type="number"]:not(:first-of-type) {
                display: none !important;
            }
            /* Hide any pseudo-elements that might duplicate content */
            .dash-table-toolbar > div::before,
            .dash-table-toolbar > div::after,
            .dash-table-toolbar input[type="number"]::before,
            .dash-table-toolbar input[type="number"]::after {
                display: none !important;
                content: none !important;
            }
            /* Keep the "/ total" text visible - it's in the last div */
            .dash-table-toolbar > div:last-child:not(:has(input)) {
                display: inline-block !important;
                color: rgba(255,255,255,0.7) !important;
                font-size: 14px !important;
                margin-left: 4px !important;
                visibility: visible !important;
            }
            .dash-table-toolbar > div:last-child:not(:has(input)) > * {
                display: inline !important;
                visibility: visible !important;
            }
            /* Additional fix: Hide any elements with class names that suggest duplicate page numbers */
            .dash-table-toolbar .page-number,
            .dash-table-toolbar [class*="current-page"],
            .dash-table-toolbar [class*="page-input"] > span:not(:last-child),
            .dash-table-toolbar [class*="page-input"] > div:not(:has(input)) {
                display: none !important;
                visibility: hidden !important;
            }
            /* Prevent any pseudo-elements from duplicating content */
            .dash-table-toolbar input[type="number"]::before,
            .dash-table-toolbar input[type="number"]::after {
                display: none !important;
                content: none !important;
            }
        </style>
        <script>
            // Fix duplicate page number in DataTable pagination
            function fixPaginationDuplicates() {
                const toolbars = document.querySelectorAll('.dash-table-toolbar');
                toolbars.forEach(toolbar => {
                    // Find the input container
                    const inputContainers = Array.from(toolbar.children).filter(div => {
                        return div.querySelector('input[type="number"]');
                    });
                    
                    inputContainers.forEach(container => {
                        const input = container.querySelector('input[type="number"]');
                        if (!input) return;
                        
                        // Hide all children except the input itself
                        Array.from(container.children).forEach(child => {
                            if (child !== input && child.tagName !== 'SCRIPT') {
                                child.style.display = 'none';
                                child.style.visibility = 'hidden';
                            }
                        });
                        
                        // Remove any text nodes or overlays
                        const walker = document.createTreeWalker(
                            container,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        let node;
                        while (node = walker.nextNode()) {
                            if (node.parentElement !== input && node.textContent.trim() === input.value) {
                                node.textContent = '';
                            }
                        }
                    });
                });
            }
            
            // Run on page load and after any updates
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', fixPaginationDuplicates);
            } else {
                fixPaginationDuplicates();
            }
            
            // Use MutationObserver to fix duplicates when table updates
            const observer = new MutationObserver(function(mutations) {
                let shouldFix = false;
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach(function(node) {
                            if (node.nodeType === 1 && (
                                node.classList.contains('dash-table-toolbar') ||
                                node.querySelector('.dash-table-toolbar')
                            )) {
                                shouldFix = true;
                            }
                        });
                    }
                });
                if (shouldFix) {
                    setTimeout(fixPaginationDuplicates, 100);
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Expose the underlying Flask server for Gunicorn
server = app.server

# Stores (Single page)
STORE_RAW = "store_raw_df"
STORE_META = "store_meta"

# Stores (Cross page)
STORE_A = "store_raw_a"
STORE_B = "store_raw_b"


MONTH_OPTIONS = [{"label": m, "value": i} for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], start=1
)]

# -----------------------------
# Helpers
# -----------------------------
def parse_csv_flexible(contents: str, filename: str):
    """
    Accept TWO columns: one date/time-like and one numeric (names can be anything).
    Detect them and normalize to ['datetime','index'].
    """
    if not filename or not filename.lower().endswith(".csv"):
        return None, [], f"Please upload a CSV file. You uploaded: {filename}"

    try:
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df0 = pd.read_csv(io.BytesIO(decoded))
    except Exception as e:
        return None, [], f"Failed to read CSV: {e}"

    if df0.empty:
        return None, [], "The CSV appears to be empty."
    if df0.shape[1] < 2:
        return None, [], "CSV must have at least two columns (a date column and a numeric column)."

    warnings = []

    # Find date-like column (≥50% parseable)
    date_col = None
    for c in df0.columns:
        s = pd.to_datetime(df0[c], errors="coerce", infer_datetime_format=True)
        if s.notna().mean() >= 0.5:
            date_col = c
            break
    if date_col is None:
        return None, [], "Could not detect a date column."

    # Find numeric column (≥50% numeric)
    num_col = None
    for c in df0.columns:
        if c == date_col:
            continue
        s = pd.to_numeric(df0[c], errors="coerce")
        if s.notna().mean() >= 0.5:
            num_col = c
            break
    if num_col is None:
        return None, [], "Could not detect a numeric column."

    df = pd.DataFrame({
        "datetime": pd.to_datetime(df0[date_col], errors="coerce"),
        "index": pd.to_numeric(df0[num_col], errors="coerce")
    })
    before = len(df)
    df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)
    dropped = before - len(df)
    if dropped > 0:
        warnings.append(f"Dropped {dropped} rows with invalid/missing values.")
    return df, warnings, None


def compute_range(preset: str, start_date, end_date, data_min: pd.Timestamp, data_max: pd.Timestamp, snap_month: bool):
    """
    Resolve (start, end) timestamps based on a preset or DatePickerRange values.
    """
    start, end = data_min, data_max

    if preset in (None, "all"):
        start, end = data_min, data_max
    elif preset == "ytd":
        end = data_max
        start = pd.Timestamp(end.year, 1, 1)
    elif preset == "1y":
        end = data_max
        start = end - pd.DateOffset(years=1)
    elif preset == "3y":
        end = data_max
        start = end - pd.DateOffset(years=3)
    elif preset == "6m":
        end = data_max
        start = end - pd.DateOffset(months=6)
    else:  # "custom"
        s = pd.to_datetime(start_date) if start_date else data_min
        e = pd.to_datetime(end_date) if end_date else data_max
        start, end = s, e

    if snap_month:
        start = pd.Timestamp(start.year, start.month, 1)
        end = (pd.Timestamp(end.year, end.month, 1) + pd.offsets.MonthEnd(1)).normalize()

    start = max(start, data_min)
    end = min(end, data_max)
    if start > end:
        start, end = end, start
    return start, end

# -----------------------------
# Weekend-aware window helpers
# -----------------------------
def end_trade_day_with_buffer(start: pd.Timestamp, window_size_days: int,
                              buffer_minus: int = 1, buffer_plus: int = 1) -> pd.Timestamp:
    """
    Weekend-aware last trading day for a calendar-day window.
    - Tentative end = start + (window_size_days - 1) calendar days.
    - If tentative lands on weekend:
        - If the backward adjustment would skip more than one day (e.g., Sat→Fri = -1 is OK,
          Sun→Fri = -2 means instead take +1 and go forward to Monday).
    """
    if pd.isna(start):
        return pd.NaT

    start = (start if isinstance(start, pd.Timestamp) else pd.Timestamp(start)).normalize()
    tentative = start + pd.Timedelta(days=max(int(window_size_days) - 1, 0))

    weekday = tentative.weekday()  # Monday=0 … Sunday=6
    # Saturday → -1 to Friday
    if weekday == 5:
        return tentative - pd.Timedelta(days=buffer_minus)
    # Sunday → instead of -2 back to Friday, go +1 to Monday
    elif weekday == 6:
        return tentative + pd.Timedelta(days=buffer_plus)
    # Weekday
    return tentative


def compute_windowed_returns_calendar(df: pd.DataFrame, window_size_days: int) -> pd.Series:
    """
    Compute % change using a calendar-day window with weekend-aware snapping.
    Assumes df has columns ['datetime','index'] and is sorted by datetime.
    For each row i at date D_i, find E_i = end_trade_day_with_buffer(D_i, window_size_days).
    Use the latest available row with datetime <= E_i as end value.
    """
    if df.empty:
        return pd.Series(dtype=float)

    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.normalize()
    df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)

    dates = df["datetime"]
    vals = pd.to_numeric(df["index"], errors="coerce").values

    # Map unique day -> last row pos
    date_to_lastpos = {}
    for pos, day in enumerate(dates):
        date_to_lastpos[day] = pos
    unique_days = dates.drop_duplicates().reset_index(drop=True)

    def pos_leq_day(target_day: pd.Timestamp):
        # rightmost unique_days[idx] <= target_day
        left, right = 0, len(unique_days) - 1
        ans = -1
        while left <= right:
            mid = (left + right) // 2
            if unique_days[mid] <= target_day:
                ans = mid
                left = mid + 1
            else:
                right = mid - 1
        if ans == -1:
            return None
        return date_to_lastpos[unique_days[ans]]

    rets = np.full(len(df), np.nan, dtype=float)
    ws = max(int(window_size_days or 1), 1)

    for i in range(len(df)):
        start_day = dates.iloc[i]
        end_day = end_trade_day_with_buffer(start_day, ws)
        j = pos_leq_day(end_day)
        if j is None or j <= i:
            continue
        if np.isfinite(vals[i]) and np.isfinite(vals[j]) and vals[i] != 0:
            rets[i] = (vals[j] / vals[i]) - 1.0

    return pd.Series(rets, index=df.index, name=f"ret_{ws}d_cal")

# ---------- Indicator helpers (no external TA dependency) ----------
def ema(s: pd.Series, span: int):
    return s.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14):
    delta = series.diff()
    up = (delta.clip(lower=0)).rolling(period).mean()
    down = (-delta.clip(upper=0)).rolling(period).mean()
    rs = up / (down.replace(0, np.nan))
    out = 100 - (100 / (1 + rs))
    return out

def bbands_mid_upper_lower(price: pd.Series, window: int = 20, k: float = 2.0):
    mid = price.rolling(window).mean()
    std = price.rolling(window).std()
    upper = mid + k * std
    lower = mid - k * std
    return mid, upper, lower

def compute_calendar_return_series(df: pd.DataFrame, window_size_days: int) -> pd.Series:
    """
    Wrapper that returns weekend-aware calendar returns aligned to df.index,
    using compute_windowed_returns_calendar.
    """
    return compute_windowed_returns_calendar(df[["datetime","index"]].copy(), window_size_days)

def build_indicators(df: pd.DataFrame, price_col="index"):
    """
    Builds a feature table.
    Weekend-aware for ret_5, ret_10, mom_10 via compute_windowed_returns_calendar.
    Other rolling features operate on available trading days.
    """
    out = pd.DataFrame(index=df.index)
    p = pd.to_numeric(df[price_col], errors="coerce").astype(float)

    # returns, momentum & volatility
    out["ret_1"]  = p.pct_change(1)

    # weekend-aware multi-day returns
    out["ret_5"]  = compute_calendar_return_series(df, 5)
    out["ret_10"] = compute_calendar_return_series(df, 10)
    # momentum over 10 calendar days == ret_10
    out["mom_10"] = out["ret_10"]

    # volatility based on daily returns (trading-day based)
    out["vol_20"] = out["ret_1"].rolling(20).std()
    out["vol_60"] = out["ret_1"].rolling(60).std()

    # moving averages
    out["sma_5"]   = p.rolling(5).mean()
    out["sma_20"]  = p.rolling(20).mean()
    out["ema_12"]  = ema(p, 12)
    out["ema_26"]  = ema(p, 26)

    # MACD family
    macd_line = out["ema_12"] - out["ema_26"]
    macd_sig  = ema(macd_line, 9)
    out["macd"]      = macd_line
    out["macd_sig"]  = macd_sig
    out["macd_hist"] = macd_line - macd_sig

    # RSI
    out["rsi_14"] = rsi(p, 14)

    # Bollinger
    mid, up, lo = bbands_mid_upper_lower(p, 20, 2.0)
    out["bb_mid"]   = mid
    out["bb_up"]    = up
    out["bb_lo"]    = lo
    out["bb_width"] = (up - lo) / mid
    out["bb_pos"]   = (p - mid) / (up - lo)

    # drawdown features
    rolling_max = p.cummax()
    drawdown = p / rolling_max - 1.0
    out["dd"]       = drawdown
    out["dd_20"]    = (p / p.rolling(20).max() - 1.0)
    out["dd_speed"] = drawdown.diff()

    # combos
    out["sma_gap_5_20"]  = out["sma_5"] / out["sma_20"] - 1.0
    out["ema_gap_12_26"] = out["ema_12"] / out["ema_26"] - 1.0

    return out

# ---------- Updated analyses (now using weekend-aware returns everywhere) ----------
def drop_event_analysis(df: pd.DataFrame, minimum_per_drop: float, windows_size: int):
    """
    Count drop events using weekend-aware windowed returns.
    """
    ret = compute_windowed_returns_calendar(df, windows_size)
    ret = ret.dropna()
    crossings = (ret <= -minimum_per_drop)
    total_events = int(crossings.sum())
    denom = max(len(ret), 1)
    prob = total_events / denom
    key = f"{windows_size} days and {minimum_per_drop * 100:.0f}% minimum percentage drop"
    return {key: {"events": total_events, "probability": f"{prob:.2%}"}}

def gain_event_analysis(df: pd.DataFrame, minimum_per_gain: float, windows_size: int):
    """
    Count gain events using weekend-aware windowed returns.
    """
    ret = compute_windowed_returns_calendar(df, windows_size)
    ret = ret.dropna()
    crossings = (ret >= minimum_per_gain)
    total_events = int(crossings.sum())
    denom = max(len(ret), 1)
    prob = total_events / denom
    key = f"{windows_size} days and {minimum_per_gain * 100:.0f}% minimum percentage gain"
    return {key: {"events": total_events, "probability": f"{prob:.2%}"}}

# ---------- Table to show first/last trade day ----------
def build_trade_window_table(df: pd.DataFrame, window_size_days: int, limit: int = 200):
    """
    Table of start date, weekend-aware last trade day, and actual end present in data (<= last trade day).
    """
    if df.empty:
        return html.Div()

    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.normalize()
    df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)

    dates = df["datetime"]

    # Map unique days to last position
    date_to_lastpos = {}
    for pos, day in enumerate(dates):
        date_to_lastpos[day] = pos
    unique_days = dates.drop_duplicates().reset_index(drop=True)

    def pos_leq_day(target_day: pd.Timestamp):
        left, right = 0, len(unique_days) - 1
        ans = -1
        while left <= right:
            mid = (left + right) // 2
            if unique_days[mid] <= target_day:
                ans = mid
                left = mid + 1
            else:
                right = mid - 1
        if ans == -1:
            return None
        return date_to_lastpos[unique_days[ans]]

    ws = max(int(window_size_days or 1), 1)
    rows = []
    for i in range(len(df)):
        start_day = dates.iloc[i]
        last_trade_day = end_trade_day_with_buffer(start_day, ws)
        j = pos_leq_day(last_trade_day)
        actual_end = dates.iloc[j] if (j is not None and j > i) else pd.NaT
        rows.append({
            "Start (first day of trade)": start_day.date(),
            "Last day of trade (weekend-aware)": last_trade_day.date() if pd.notna(last_trade_day) else None,
            "Actual end in data (<= last trade day)": actual_end.date() if pd.notna(actual_end) else None,
        })

    df_out = pd.DataFrame(rows)
    if limit and len(df_out) > limit:
        df_out = df_out.head(limit)

    table = dash_table.DataTable(
        data=df_out.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df_out.columns],
        page_size=min(20, len(df_out)) or 5,
        page_action="native",
        page_current=0,
        style_table={"overflowX": "auto", "backgroundColor": "#1a1a1a"},
        style_cell={
            "textAlign": "left", 
            "minWidth": "160px",
            "backgroundColor": "#1a1a1a",
            "color": "rgba(255,255,255,0.9)",
            "border": "1px solid rgba(255,255,255,0.1)",
            "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
        },
        style_header={
            "backgroundColor": "#252525",
            "color": "rgba(255,255,255,0.95)",
            "fontWeight": "600",
            "border": "1px solid rgba(0,200,150,0.3)",
            "textAlign": "left"
        },
        style_data={
            "backgroundColor": "#1a1a1a",
            "color": "rgba(255,255,255,0.9)",
            "border": "1px solid rgba(255,255,255,0.1)"
        },
        style_data_conditional=[
            {
                "if": {"row_index": "even"},
                "backgroundColor": "#222222",
            },
            {
                "if": {"state": "selected"},
                "backgroundColor": "rgba(0,200,150,0.2)",
                "border": "1px solid rgba(0,200,150,0.5)"
            }
        ],
        style_cell_conditional=[
            {
                "if": {"column_id": "Start (first day of trade)"},
                "minWidth": "180px"
            }
        ]
    )
    return table

# -----------------------------
# Reusable UI Components
# -----------------------------

def PageContainer(children, **kwargs):
    """Consistent page container with max-width and responsive padding"""
    return html.Div(
        children,
        style={
            "maxWidth": "1152px",  # max-w-6xl equivalent
            "width": "100%",
            "margin": "0 auto",
            "padding": "16px 16px",
            **kwargs.get("style", {})
        },
        **{k: v for k, v in kwargs.items() if k != "style"}
    )

def Card(children, header=None, footer=None, **kwargs):
    """Reusable card component with header, content, and footer slots"""
    card_children = []
    if header:
        card_children.append(html.Div(
            header,
            style={
                "padding": "0 0 16px 0",
                "borderBottom": "1px solid rgba(255,255,255,0.1)",
                "marginBottom": "16px"
            }
        ))
    card_children.append(html.Div(children, style={"flex": 1}))
    if footer:
        card_children.append(html.Div(
            footer,
            style={
                "padding": "16px 0 0 0",
                "borderTop": "1px solid rgba(255,255,255,0.1)",
                "marginTop": "16px",
                "position": "sticky",
                "bottom": 0,
                "background": "#121821",
                "zIndex": 5
            }
        ))
    
    card_style = {
        "padding": "24px",
        "background": "#121821",
        "borderRadius": "12px",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
        "border": "1px solid rgba(255,255,255,0.1)",
        "display": "flex",
        "flexDirection": "column",
        "position": "relative"
    }
    card_style.update(kwargs.get("style", {}))
    
    return html.Div(
        card_children,
        style=card_style,
        **{k: v for k, v in kwargs.items() if k != "style"}
    )

def Field(label, input_component, helper_text=None, error_text=None, required=False, **kwargs):
    """Reusable field component with label, input, helper text, and error message"""
    label_style = {
        "display": "block",
        "fontSize": "14px",
        "fontWeight": "600",
        "color": "rgba(255,255,255,0.9)",
        "marginBottom": "8px",
        "lineHeight": "1.4"
    }
    if required:
        label_style["color"] = "rgba(255,255,255,0.95)"
    
    field_children = [
        html.Label(label, style=label_style),
        input_component
    ]
    
    if helper_text:
        field_children.append(html.Div(
            helper_text,
            style={
                "fontSize": "12px",
                "color": "rgba(255,255,255,0.6)",
                "marginTop": "4px"
            }
        ))
    
    if error_text:
        field_children.append(html.Div(
            error_text,
            style={
                "fontSize": "12px",
                "color": "#ef4444",
                "marginTop": "4px"
            }
        ))
    
    return html.Div(
        field_children,
        style={
            "marginBottom": "20px",
            **kwargs.get("style", {})
        },
        **{k: v for k, v in kwargs.items() if k != "style"}
    )

def RadioGroup(id, label, options, value=None, inline=True, accent_color=None, **kwargs):
    """Reusable radio group component"""
    input_style = {
        "marginRight": "4px",
        "cursor": "pointer",
        "accentColor": accent_color or "rgba(0,200,150,0.8)"
    }
    label_style = {
        "marginRight": "16px",
        "cursor": "pointer",
        "fontSize": "14px",
        "color": "rgba(255,255,255,0.9)",
        "display": "inline-block" if inline else "block"
    }
    
    return html.Div([
        html.Label(label, style={
            "display": "block",
            "fontSize": "14px",
            "fontWeight": "600",
            "color": "rgba(255,255,255,0.9)",
            "marginBottom": "8px"
        }),
        dcc.RadioItems(
            id=id,
            options=options,
            value=value,
            inline=inline,
            inputStyle=input_style,
            labelStyle=label_style,
            **kwargs
        )
    ], style={"marginBottom": "20px"})

def CheckboxGroup(id, label, options, value=None, inline=True, **kwargs):
    """Reusable checkbox group component"""
    input_style = {
        "marginRight": "8px",
        "cursor": "pointer"
    }
    label_style = {
        "marginRight": "16px",
        "cursor": "pointer",
        "fontSize": "14px",
        "color": "rgba(255,255,255,0.9)",
        "display": "inline-block" if inline else "block"
    }
    
    return html.Div([
        html.Label(label, style={
            "display": "block",
            "fontSize": "14px",
            "fontWeight": "600",
            "color": "rgba(255,255,255,0.9)",
            "marginBottom": "8px"
        }),
        dcc.Checklist(
            id=id,
            options=options,
            value=value or [],
            inline=inline,
            inputStyle=input_style,
            labelStyle=label_style,
            **kwargs
        )
    ], style={"marginBottom": "20px"})

def DateRangePicker(id, label, preset_id=None, preset_options=None, preset_value="all",
                    snap_id=None, snap_value=None, min_date=None, max_date=None,
                    start_date=None, end_date=None, helper_text=None, **kwargs):
    """Reusable date range picker with preset dropdown and snap to month"""
    return html.Div([
        html.Label(label, style={
            "display": "block",
            "fontSize": "14px",
            "fontWeight": "600",
            "color": "rgba(255,255,255,0.9)",
            "marginBottom": "8px"
        }),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id=preset_id,
                    options=preset_options or [
                        {"label":"All","value":"all"},
                        {"label":"YTD","value":"ytd"},
                        {"label":"Last 1Y","value":"1y"},
                        {"label":"Last 3Y","value":"3y"},
                        {"label":"Last 6M","value":"6m"},
                        {"label":"Custom","value":"custom"},
                    ],
                    value=preset_value,
                    clearable=False,
                    style={
                        "width": "100%"
                    }
                )
            ], style={
                "flex": "0 0 160px"
            }),
            html.Div([
                dcc.DatePickerRange(
                    id=id,
                    display_format="YYYY-MM-DD",
                    minimum_nights=0,
                    clearable=True,
                    persistence=True,
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=start_date,
                    end_date=end_date,
                    style={
                        "width": "100%"
                    },
                    **kwargs
                )
            ], style={
                "flex": "1 1 auto",
                "minWidth": "300px"
            }),
            html.Div([
                dcc.Checklist(
                    id=snap_id,
                    options=[{"label": " Snap to month", "value": "snap"}],
                    value=snap_value or ["snap"],
                    inline=True,
                    style={"display": "inline-block"}
                )
            ], style={
                "flex": "0 0 auto",
                "display": "flex",
                "alignItems": "center"
            })
        ], style={
            "display": "flex",
            "alignItems": "center",
            "flexWrap": "wrap",
            "gap": "12px"
        }),
        helper_text and html.Div(
            helper_text,
            style={
                "fontSize": "12px",
                "color": "rgba(255,255,255,0.6)",
                "marginTop": "4px"
            }
        )
    ], style={"marginBottom": "20px"})

def FileDropzone(id, label, accept=".csv", filename=None, on_replace_id=None, on_remove_id=None, **kwargs):
    """Reusable file dropzone component with drag/drop and click support"""
    if filename:
        # Show file info with replace/remove actions
        return html.Div([
            html.Label(label, style={
                "display": "block",
                "fontSize": "14px",
                "fontWeight": "600",
                "color": "rgba(255,255,255,0.9)",
                "marginBottom": "8px"
            }),
            html.Div([
                html.Div([
                    html.Span("📄", style={"fontSize": "20px", "marginRight": "8px"}),
                    html.Span(filename, style={
                        "fontSize": "14px",
                        "color": "rgba(255,255,255,0.9)",
                        "flex": 1
                    }),
                    html.Button(
                        "Replace",
                        id=on_replace_id,
                        n_clicks=0,
                        style={
                            "padding": "6px 12px",
                            "marginRight": "8px",
                            "borderRadius": "6px",
                            "border": "1px solid rgba(255,255,255,0.2)",
                            "background": "rgba(255,255,255,0.1)",
                            "color": "rgba(255,255,255,0.9)",
                            "cursor": "pointer",
                            "fontSize": "12px"
                        }
                    ) if on_replace_id else None,
                    html.Button(
                        "Remove",
                        id=on_remove_id,
                        n_clicks=0,
                        style={
                            "padding": "6px 12px",
                            "borderRadius": "6px",
                            "border": "1px solid rgba(239,68,68,0.3)",
                            "background": "rgba(239,68,68,0.1)",
                            "color": "#ef4444",
                            "cursor": "pointer",
                            "fontSize": "12px"
                        }
                    ) if on_remove_id else None
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "12px 16px",
                    "background": "rgba(0,200,150,0.1)",
                    "borderRadius": "8px",
                    "border": "1px solid rgba(0,200,150,0.3)"
                })
            ])
        ], style={"marginBottom": "20px"})
    
    # Show upload zone
    return html.Div([
        html.Label(label, style={
            "display": "block",
            "fontSize": "14px",
            "fontWeight": "600",
            "color": "rgba(255,255,255,0.9)",
            "marginBottom": "8px"
        }),
        dcc.Upload(
            id=id,
            children=html.Div([
                html.Div([
                    html.Span("Drag and drop or ", style={
                        "fontSize": "15px",
                        "color": "rgba(255,255,255,0.7)"
                    }),
                    html.A("Select CSV File", style={
                        "fontSize": "15px",
                        "color": "#00c896",
                        "fontWeight": "600",
                        "textDecoration": "underline"
                    })
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px"
                }),
                html.Span("📁", style={
                    "fontSize": "24px",
                    "marginLeft": "12px",
                    "opacity": 0.8,
                    "transition": "all 0.3s"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center"
            }),
            style={
                "width": "100%",
                "height": "100px",
                "borderWidth": "2px",
                "borderStyle": "dashed",
                "borderColor": "rgba(0,200,150,0.3)",
                "borderRadius": "12px",
                "textAlign": "center",
                "background": "rgba(0,200,150,0.05)",
                "transition": "all 0.3s",
                "cursor": "pointer",
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "center",
                "alignItems": "center"
            },
            multiple=False,
            accept=accept,
            **kwargs
        )
    ], style={"marginBottom": "20px"})

def Button(id, label, variant="primary", disabled=False, loading=False, full_width=False, **kwargs):
    """Reusable button component with variants and states"""
    base_style = {
        "padding": "12px 24px",
        "borderRadius": "8px",
        "border": "none",
        "fontWeight": "600",
        "fontSize": "15px",
        "cursor": "pointer" if not disabled and not loading else "not-allowed",
        "transition": "all 0.3s",
        "opacity": "0.6" if disabled or loading else "1"
    }
    
    if variant == "primary":
        base_style.update({
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "color": "white",
            "boxShadow": "0 4px 12px rgba(102, 126, 234, 0.4)"
        })
    elif variant == "secondary":
        base_style.update({
            "background": "rgba(255,255,255,0.1)",
            "color": "rgba(255,255,255,0.9)",
            "border": "1px solid rgba(255,255,255,0.2)"
        })
    
    if full_width:
        base_style["width"] = "100%"
    
    button_label = f"{'⏳ ' if loading else ''}{label}"
    
    return html.Button(
        button_label,
        id=id,
        disabled=disabled or loading,
        style={**base_style, **kwargs.get("style", {})},
        **{k: v for k, v in kwargs.items() if k != "style"}
    )

# -----------------------------
# Layouts: Home / Single / Cross
# -----------------------------

card_style = {
    "display": "flex",
    "flexDirection": "column",
    "padding": "32px 36px",
    "borderRadius": "20px",
    "border": "none",
    "boxShadow": "0 8px 24px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)",
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "textDecoration": "none",
    "color": "white",
    "width": "320px",
    "minHeight": "280px",
    "height": "280px",
    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    "cursor": "pointer",
    "justifyContent": "center",
    "alignItems": "center",
    "boxSizing": "border-box",
}
card_style_hover = {
    "transform": "translateY(-4px)",
    "boxShadow": "0 12px 32px rgba(0,0,0,0.18), 0 4px 12px rgba(0,0,0,0.12)",
}

def navbar():
    # Always dark theme
    bg_color = "#0a0a0a"
    text_color = "white"
    border_color = "rgba(255,255,255,0.1)"
    
    return html.Div(
        [
            # Left side: Logo
            html.Div([
                html.Img(
                    src="https://starlab-public.s3.us-east-1.amazonaws.com/starlab_images/transparent-slc-rgb.png",
                    style={
                        "height": "36px",
                        "marginRight": "20px",
                        "objectFit": "contain"
                    }
                ),
            ], style={"display": "flex", "alignItems": "center", "flex": 1}),
            
            # Right side: Navigation elements
            html.Div([
                dcc.Link("Home", href="/", style={
                    "marginRight": "20px", "textDecoration": "none",
                    "color": text_color, "fontSize": "14px", "fontWeight": 500,
                    "padding": "6px 12px", "borderRadius": "4px",
                    "transition": "all 0.2s"
                }),
                dcc.Link("Single Index", href="/single", style={
                    "marginRight": "20px", "textDecoration": "none",
                    "color": text_color, "fontSize": "14px", "fontWeight": 500,
                    "padding": "6px 12px", "borderRadius": "4px",
                    "transition": "all 0.2s"
                }),
                dcc.Link("Cross Index", href="/cross", style={
                    "marginRight": "20px", "textDecoration": "none",
                    "color": text_color, "fontSize": "14px", "fontWeight": 500,
                    "padding": "6px 12px", "borderRadius": "4px",
                    "transition": "all 0.2s"
                }),
                dcc.Link([
                    html.Span("📖 ", style={"marginRight": "4px"}),
                    "Documentation"
                ], href="/docs", style={
                    "textDecoration": "none",
                    "color": text_color, "fontSize": "14px", "fontWeight": 600,
                    "padding": "8px 16px", "borderRadius": "6px",
                    "transition": "all 0.2s",
                    "background": "linear-gradient(135deg, rgba(102,126,234,0.3) 0%, rgba(118,75,162,0.3) 100%)",
                    "border": "1px solid rgba(102,126,234,0.4)"
                }),
            ], style={"display": "flex", "alignItems": "center"})
        ],
        style={
            "padding": "14px 32px",
            "background": bg_color,
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.3)",
            "marginBottom": "0",
            "borderBottom": f"1px solid {border_color}",
            "transition": "background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease"
        }
    )

def home_layout():
    return html.Div(
        [
            html.Div([
                html.H1("Index Data Analysis", style={
                    "fontSize":"48px", "fontWeight":700, "marginBottom":"16px",
                    "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "WebkitBackgroundClip":"text", "WebkitTextFillColor":"transparent",
                    "backgroundClip":"text"
                }),
                html.P("Powerful financial data analysis made simple - no expertise required!", style={
                    "fontSize":"20px", "color":"rgba(255,255,255,0.7)", "marginBottom":"12px"
                }),
                html.P([
                    "📊 Upload your CSV data • 🔍 Get instant insights • 📈 Visualize trends"
                ], style={
                    "fontSize":"16px", "color":"rgba(255,255,255,0.6)", "marginBottom":"40px"
                }),
            ], style={"textAlign":"center", "marginBottom":"48px"}),
            
            html.Div(
                [
                    dcc.Link(
                        html.Div(
                            [
                                html.Div("📊", style={"fontSize":"48px", "marginBottom":"16px"}),
                                html.H3("Single Index Analysis", style={"margin":"0 0 12px 0", "fontSize":"24px", "fontWeight":600}),
                                html.P("Perfect for analyzing one market index in depth", style={
                                    "margin":"0 0 12px 0", "fontSize":"15px", "opacity":0.95, "lineHeight":"1.5"
                                }),
                                html.Div([
                                    html.Div("✓ Find drop & gain events", style={"fontSize":"13px", "marginBottom":"6px", "opacity":0.85}),
                                    html.Div("✓ Technical indicators", style={"fontSize":"13px", "marginBottom":"6px", "opacity":0.85}),
                                    html.Div("✓ Statistical analysis", style={"fontSize":"13px", "opacity":0.85}),
                                ], style={"textAlign":"left", "paddingLeft":"20px"})
                            ],
                            style={**card_style, "textAlign":"center"}
                        ),
                        href="/single",
                        style={"textDecoration":"none", "display":"flex"}
                    ),
                    dcc.Link(
                        html.Div(
                            [
                                html.Div("🔀", style={"fontSize":"48px", "marginBottom":"16px"}),
                                html.H3("Cross Index Comparison", style={"margin":"0 0 12px 0", "fontSize":"24px", "fontWeight":600}),
                                html.P("Compare two indexes to understand their relationship", style={
                                    "margin":"0 0 12px 0", "fontSize":"15px", "opacity":0.95, "lineHeight":"1.5"
                                }),
                                html.Div([
                                    html.Div("✓ Correlation analysis", style={"fontSize":"13px", "marginBottom":"6px", "opacity":0.85}),
                                    html.Div("✓ Relative performance", style={"fontSize":"13px", "marginBottom":"6px", "opacity":0.85}),
                                    html.Div("✓ Side-by-side visualization", style={"fontSize":"13px", "opacity":0.85}),
                                ], style={"textAlign":"left", "paddingLeft":"20px"})
                            ],
                            style={**card_style, "background":"linear-gradient(135deg, #f093fb 0%, #f5576c 100%)", "textAlign":"center"}
                        ),
                        href="/cross",
                        style={"textDecoration":"none", "display":"flex"}
                    ),
                ],
                style={
                    "marginTop": "12px", 
                    "display":"flex", 
                    "justifyContent":"center", 
                    "alignItems":"stretch",
                    "flexWrap":"wrap",
                    "gap":"24px"
                }
            ),
            
            # Quick start guide
            html.Div([
                Card([
                    html.H3("🚀 Quick Start Guide", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"16px"}),
                    html.Div([
                        html.Div([
                            html.Strong("1. ", style={"color":"#667eea", "fontSize":"18px"}),
                            html.Strong("Prepare Your Data", style={"color":"rgba(255,255,255,0.95)"}),
                            html.P("CSV file with 2 columns: Date and Index Value", style={"fontSize":"14px", "color":"rgba(255,255,255,0.7)", "marginTop":"4px", "marginLeft":"24px"})
                        ], style={"marginBottom":"16px"}),
                        html.Div([
                            html.Strong("2. ", style={"color":"#667eea", "fontSize":"18px"}),
                            html.Strong("Choose Analysis Type", style={"color":"rgba(255,255,255,0.95)"}),
                            html.P("Single index for detailed analysis or Cross index for comparison", style={"fontSize":"14px", "color":"rgba(255,255,255,0.7)", "marginTop":"4px", "marginLeft":"24px"})
                        ], style={"marginBottom":"16px"}),
                        html.Div([
                            html.Strong("3. ", style={"color":"#667eea", "fontSize":"18px"}),
                            html.Strong("Upload & Analyze", style={"color":"rgba(255,255,255,0.95)"}),
                            html.P("Upload your file, configure settings, and click Analyze", style={"fontSize":"14px", "color":"rgba(255,255,255,0.7)", "marginTop":"4px", "marginLeft":"24px"})
                        ], style={"marginBottom":"16px"}),
                        html.Div([
                            html.Strong("4. ", style={"color":"#667eea", "fontSize":"18px"}),
                            html.Strong("Explore Results", style={"color":"rgba(255,255,255,0.95)"}),
                            html.P("View charts, statistics, and insights", style={"fontSize":"14px", "color":"rgba(255,255,255,0.7)", "marginTop":"4px", "marginLeft":"24px"})
                        ]),
                    ]),
                    html.Div([
                        html.A([
                            html.Span("📖 ", style={"marginRight":"6px"}),
                            "View Full Documentation"
                        ], href="/docs", style={
                            "display":"inline-block",
                            "marginTop":"24px",
                            "padding":"12px 24px",
                            "background":"linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%)",
                            "border":"1px solid rgba(102,126,234,0.4)",
                            "color":"#667eea",
                            "textDecoration":"none",
                            "borderRadius":"8px",
                            "fontWeight":"600",
                            "fontSize":"14px",
                            "transition":"all 0.3s"
                        })
                    ], style={"textAlign":"center"})
                ], style={"maxWidth":"600px", "margin":"48px auto 0"})
            ])
        ],
        style={"maxWidth":"1200px","margin":"0 auto","padding":"48px 24px", "marginTop":"0"}
    )

# ---------- Single Index (FULL) ----------
def single_layout():
    return PageContainer([
        # Header
        html.Div([
            html.H1("📊 Single Index Analysis", style={
                "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
                "color":"rgba(255,255,255,0.95)"
            }),
            html.P([
                "Analyze market movements, find significant drops and gains, and understand trends with technical indicators."
            ], style={
                "fontSize":"17px", "color":"rgba(255,255,255,0.8)", "marginBottom":"8px"
            }),
            html.P([
                "💡 ", html.Strong("Required Data Format:", style={"color":"#00c896"}), 
                " CSV file with 2 columns - a date column and a numeric index value column (column names can be anything). ",
                html.A("See examples in docs →", href="/docs#data-format", style={"color":"#667eea", "textDecoration":"underline"})
            ], style={
                "fontSize":"14px", "color":"rgba(255,255,255,0.6)", "marginBottom":"32px",
                "padding":"12px 16px", "background":"rgba(0,200,150,0.08)", 
                "borderRadius":"8px", "border":"1px solid rgba(0,200,150,0.2)"
            }),
        ], style={"marginBottom": "32px"}),

        # File Upload with Loading
        dcc.Loading(
            id="upload-loading",
            type="circle",
            children=html.Div([
                FileDropzone(
                    id="uploader",
                    label="Upload CSV File"
                ),
                html.Div(id="file-msg", style={"marginBottom": "8px", "fontSize": "14px"}),
                html.Div(id="warn-msg", style={"marginBottom": "8px", "fontSize": "14px"}),
            ])
        ),

        # Analysis Types
        Card([
            html.Div([
                html.H3("🎯 What do you want to analyze?", style={
                    "fontSize":"20px", "fontWeight":600, "color":"rgba(255,255,255,0.95)", "marginBottom":"12px"
                }),
                html.P("Select one or both types of analysis to run on your data:", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.7)", "marginBottom":"16px"
                }),
            ]),
            CheckboxGroup(
                id="analysis-types",
                label="Analysis Type(s)",
                options=[
                    {"label": " 📉 Drop Analysis - Find periods where the index decreased", "value": "drop"},
                    {"label": " 📈 Gain Analysis - Find periods where the index increased", "value": "gain"}
                ],
                value=["drop", "gain"],
                inline=False
            ),
            html.P([
                "💡 ", html.Strong("Tip:", style={"color":"#00c896"}),
                " Analyzing both helps you understand the full picture of market volatility and opportunities."
            ], style={
                "fontSize":"13px", "color":"rgba(255,255,255,0.6)", "marginTop":"12px",
                "padding":"8px 12px", "background":"rgba(255,255,255,0.03)",
                "borderRadius":"6px"
            })
        ], style={"marginBottom": "24px"}),

        # Controls row: Drop (left) & Gain (right) - 2 column grid
        html.Div([
            # DROP CONTROLS
            Card([
                html.H3("📉 Drop Analysis Options", style={
                    "marginBottom": "8px", "fontSize":"22px",
                    "fontWeight":600, "color":"#ef4444"
                }),
                html.P("Configure settings to identify when the index decreased significantly", style={
                    "fontSize":"13px", "color":"rgba(255,255,255,0.6)", "marginBottom":"20px"
                }),
                DateRangePicker(
                        id="date-range-drop",
                    label="Date Range",
                    preset_id="preset-drop",
                    preset_value="all",
                    snap_id="snap-month-drop",
                    snap_value=["snap"]
                ),
                html.Div([
                    html.Label("Navigate to Date", style={
                        "display": "block",
                        "fontSize": "14px",
                        "fontWeight": "600",
                        "color": "rgba(255,255,255,0.9)",
                        "marginBottom": "8px"
                    }),
                    html.Div([
                    dcc.Dropdown(id="jump-year-drop", options=[], placeholder="Year",
                                     style={"width":"100px","display":"inline-block","marginRight":"8px"}),
                    dcc.Dropdown(id="jump-month-drop", options=MONTH_OPTIONS, placeholder="Month",
                                 style={"width":"120px","display":"inline-block"}),
                    ], style={"display": "flex", "alignItems": "center"})
                ], style={"marginBottom": "20px"}),
                RadioGroup(
                            id="window-size-drop",
                    label="Analysis Period (days)",
                    options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
                             {"label": "7", "value": 7}, {"label": "10", "value": 10}],
                    value=5,
                    inline=True,
                    accent_color="rgba(239,68,68,0.8)"
                ),
                Field(
                    label="Custom Period (days)",
                    input_component=dcc.Input(
                            id="window-size-input-drop", type="number", min=1, step=1,
                        placeholder="Enter custom days",
                        style={
                            "width": "100%",
                            "height": "40px",
                            "padding": "8px 12px",
                            "fontSize": "14px",
                            "background": "rgba(255,255,255,0.1)",
                            "border": "1px solid rgba(255,255,255,0.2)",
                            "borderRadius": "6px",
                            "color": "rgba(255,255,255,0.9)"
                        }
                    ),
                    helper_text="Optional: Enter a custom analysis period in days"
                ),
                RadioGroup(
                            id="min-threshold-drop",
                    label="Minimum Change Threshold (%)",
                    options=[{"label":"1%","value":1},{"label":"3%","value":3},
                             {"label":"5%","value":5},{"label":"10%","value":10}],
                    value=3,
                    inline=True,
                    accent_color="rgba(239,68,68,0.8)"
                ),
                Field(
                    label="Custom Threshold (%)",
                    input_component=dcc.Input(
                            id="min-threshold-input-drop", type="number", min=0, max=100, step=0.01,
                            placeholder="e.g. 2.7", 
                        style={
                            "width": "100%",
                            "height": "40px",
                            "padding": "8px 12px",
                            "fontSize": "14px",
                            "background": "rgba(255,255,255,0.1)",
                            "border": "1px solid rgba(255,255,255,0.2)",
                            "borderRadius": "6px",
                            "color": "rgba(255,255,255,0.9)"
                        }
                    ),
                    helper_text="Optional: Enter a custom threshold (0-100%)"
                ),
            ], style={
                "background": "rgba(239,68,68,0.08)",
                "border": "1px solid rgba(239,68,68,0.3)"
            }),

            # GAIN CONTROLS
            Card([
                html.H3("📈 Gain Analysis Options", style={
                    "marginBottom": "8px", "fontSize":"22px",
                    "fontWeight":600, "color":"#22c55e"
                }),
                html.P("Configure settings to identify when the index increased significantly", style={
                    "fontSize":"13px", "color":"rgba(255,255,255,0.6)", "marginBottom":"20px"
                }),
                DateRangePicker(
                        id="date-range-gain",
                    label="Date Range",
                    preset_id="preset-gain",
                    preset_value="all",
                    snap_id="snap-month-gain",
                    snap_value=["snap"]
                ),
                html.Div([
                    html.Label("Navigate to Date", style={
                        "display": "block",
                        "fontSize": "14px",
                        "fontWeight": "600",
                        "color": "rgba(255,255,255,0.9)",
                        "marginBottom": "8px"
                    }),
                    html.Div([
                    dcc.Dropdown(id="jump-year-gain", options=[], placeholder="Year",
                                     style={"width":"100px","display":"inline-block","marginRight":"8px"}),
                    dcc.Dropdown(id="jump-month-gain", options=MONTH_OPTIONS, placeholder="Month",
                                 style={"width":"120px","display":"inline-block"}),
                    ], style={"display": "flex", "alignItems": "center"})
                ], style={"marginBottom": "20px"}),
                RadioGroup(
                            id="window-size-gain",
                    label="Analysis Period (days)",
                    options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
                             {"label": "7", "value": 7}, {"label": "10", "value": 10}],
                    value=5,
                    inline=True,
                    accent_color="rgba(34,197,94,0.8)"
                ),
                Field(
                    label="Custom Period (days)",
                    input_component=dcc.Input(
                            id="window-size-input-gain", type="number", min=1, step=1,
                        placeholder="Enter custom days",
                        style={
                            "width": "100%",
                            "height": "40px",
                            "padding": "8px 12px",
                            "fontSize": "14px",
                            "background": "rgba(255,255,255,0.1)",
                            "border": "1px solid rgba(255,255,255,0.2)",
                            "borderRadius": "6px",
                            "color": "rgba(255,255,255,0.9)"
                        }
                    ),
                    helper_text="Optional: Enter a custom analysis period in days"
                ),
                RadioGroup(
                            id="min-threshold-gain",
                    label="Minimum Change Threshold (%)",
                    options=[{"label":"1%","value":1},{"label":"3%","value":3},
                             {"label":"5%","value":5},{"label":"10%","value":10}],
                    value=3,
                    inline=True,
                    accent_color="rgba(34,197,94,0.8)"
                ),
                Field(
                    label="Custom Threshold (%)",
                    input_component=dcc.Input(
                            id="min-threshold-input-gain", type="number", min=0, max=100, step=0.01,
                            placeholder="e.g. 2.7", 
                        style={
                            "width": "100%",
                            "height": "40px",
                            "padding": "8px 12px",
                            "fontSize": "14px",
                            "background": "rgba(255,255,255,0.1)",
                            "border": "1px solid rgba(255,255,255,0.2)",
                            "borderRadius": "6px",
                            "color": "rgba(255,255,255,0.9)"
                        }
                    ),
                    helper_text="Optional: Enter a custom threshold (0-100%)"
                ),
            ], style={
                "background": "rgba(34,197,94,0.08)",
                "border": "1px solid rgba(34,197,94,0.3)"
            }),
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))",
            "gap": "24px",
            "marginBottom": "24px"
        }),

        # INDICATORS - Collapsible card with multi-column layout
        Card([
        html.Div([
            html.H3("Indicators", style={
                "marginBottom":"16px", "fontSize":"22px",
                    "fontWeight":600, "color":"rgba(255,255,255,0.95)",
                    "display": "inline-block",
                    "marginRight": "16px"
                }),
                html.Button(
                    "Select All", id="indicators-select-all", n_clicks=0,
                    style={
                        "padding": "6px 16px",
                        "marginRight": "8px",
                        "borderRadius": "6px",
                        "border": "1px solid rgba(0,200,150,0.3)",
                        "background": "rgba(0,200,150,0.1)",
                        "color": "rgba(255,255,255,0.9)",
                        "cursor": "pointer",
                        "fontSize": "13px",
                        "fontWeight": "500",
                        "transition": "all 0.2s"
                    }
                ),
                html.Button(
                    "Clear All", id="indicators-clear-all", n_clicks=0,
                    style={
                        "padding": "6px 16px",
                        "borderRadius": "6px",
                        "border": "1px solid rgba(255,255,255,0.2)",
                        "background": "rgba(255,255,255,0.1)",
                        "color": "rgba(255,255,255,0.9)",
                        "cursor": "pointer",
                        "fontSize": "13px",
                        "fontWeight": "500",
                        "transition": "all 0.2s"
                    }
                )
            ], style={
                "marginBottom": "16px",
                "display": "flex",
                "alignItems": "center",
                "flexWrap": "wrap",
                "gap": "8px"
            }),
            html.Div([
                CheckboxGroup(
                id="indicators-select",
                    label="",
                options=[
                    {"label":" SMA (5 & 20)", "value":"sma"},
                    {"label":" EMA (12 & 26)", "value":"ema"},
                    {"label":" Bollinger Bands (20,2)", "value":"bb"},
                    {"label":" RSI (14)", "value":"rsi"},
                    {"label":" MACD (12,26,9)", "value":"macd"},
                    {"label":" Volatility (20/60)", "value":"vol"},
                    {"label":" Drawdown", "value":"dd"},
                ],
                value=["sma","ema","bb","rsi","macd","vol","dd"],
                    inline=True
                )
        ], style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "8px"
            })
        ], footer=html.Div([
            dcc.Loading(
                id="analyze-loading",
                type="circle",
                children=html.Div([
                    Button(
                        id="analyze",
                        label="Analyze",
                        variant="primary",
                        full_width=False,
                        style={"float": "right"}
                    )
                ], style={
                    "textAlign": "right",
                    "width": "100%"
                }, className="card-footer")
            )
        ], style={
            "textAlign": "right",
            "width": "100%"
        }, className="card-footer"), style={
            "marginBottom": "24px",
            "position": "relative",
            "display": "flex",
            "flexDirection": "column"
        }),

        # ---------- Results (Drop / Gain) ----------
        dcc.Loading(
            id="results-loading",
            type="circle",
            children=html.Div(id="results-container", style={"display": "none"}, children=[
                html.Div([
                html.H2("Drop Analysis", style={
                    "fontSize":"28px", "fontWeight":700, "color":"#ef4444",
                    "marginBottom":"20px"
                }),
                html.Div(id="analysis-output-drop", style={
                    "border": "1px solid rgba(239,68,68,0.3)", "borderRadius": "16px",
                    "padding": "20px", "margin": "10px 0",
                    "background": "rgba(239,68,68,0.08)",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"
                }),
                html.Div(id="return-chart-drop-container"),
                html.Div(id="bar-chart-drop-container"),
                html.Div(id="stats-drop", style={"margin": "24px 0"}),
                html.Div(id="trade-windows-drop-container"),
            ], style={"flex": 1, "minWidth": "420px"}),

            html.Div([
                html.H2("Gain Analysis", style={
                    "fontSize":"28px", "fontWeight":700, "color":"#22c55e",
                    "marginBottom":"20px"
                }),
                html.Div(id="analysis-output-gain", style={
                    "border": "1px solid rgba(34,197,94,0.3)", "borderRadius": "16px",
                    "padding": "20px", "margin": "10px 0",
                    "background": "rgba(34,197,94,0.08)",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"
                }),
                html.Div(id="return-chart-gain-container"),
                html.Div(id="bar-chart-gain-container"),
                html.Div(id="stats-gain", style={"margin": "24px 0"}),
                html.Div(id="trade-windows-gain-container"),
            ], style={"flex": 1, "minWidth": "420px"}),
            ])
        ),

        # ---------- Indicators figure ----------
        html.Div(id="indicators-container"),

        html.Hr(),
        html.Div(id="preview", style={
            "marginTop":"40px", "padding":"24px",
            "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
            "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
            "border":"1px solid rgba(255,255,255,0.1)"
        }),  # <<< Data Preview lives here (first 10 rows)

        dcc.Store(id=STORE_RAW),
        dcc.Store(id=STORE_META),
    ])

# ---------- Cross Index ----------
def cross_layout():
    return PageContainer([
        # Header
            html.Div([
                html.H1("🔀 Cross Index Analysis", style={
                    "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
                "color":"rgba(255,255,255,0.95)"
                }),
                html.P([
                    "Compare two different indexes to understand their relationship, correlation, and relative performance over time."
                ], style={
                    "fontSize":"17px", "color":"rgba(255,255,255,0.8)", "marginBottom":"8px"
                }),
                html.P([
                    "💡 ", html.Strong("How it works:", style={"color":"#00c896"}), 
                    " Upload two CSV files (same format as Single Index), set a date range, and see how they move together. ",
                    html.A("Learn more in docs →", href="/docs#cross-index", style={"color":"#f5576c", "textDecoration":"underline"})
                ], style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.6)", "marginBottom":"32px",
                    "padding":"12px 16px", "background":"rgba(245,87,108,0.08)", 
                    "borderRadius":"8px", "border":"1px solid rgba(245,87,108,0.2)"
                }),
        ], style={"marginBottom": "32px"}),

        # Upload Index A/B - 2 column grid
            html.Div([
            Card([
                dcc.Loading(
                    id="upload-loading-a",
                    type="circle",
                        children=html.Div([
                        FileDropzone(
                            id="uploader-a",
                            label="Upload Index A (CSV)"
                        ),
                        html.Div(id="file-msg-a", style={"marginBottom": "8px", "fontSize": "14px"}),
                        html.Div(id="warn-msg-a", style={"marginBottom": "8px", "fontSize": "14px"}),
                        html.Div(id="preview-a")
                    ])
                )
            ], style={"minHeight": "200px"}),

            Card([
                dcc.Loading(
                    id="upload-loading-b",
                    type="circle",
                        children=html.Div([
                        FileDropzone(
                            id="uploader-b",
                            label="Upload Index B (CSV)"
                        ),
                        html.Div(id="file-msg-b", style={"marginBottom": "8px", "fontSize": "14px"}),
                        html.Div(id="warn-msg-b", style={"marginBottom": "8px", "fontSize": "14px"}),
                        html.Div(id="preview-b")
                    ])
                )
            ], style={"minHeight": "200px"}),
                ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))",
            "gap": "24px",
            "marginBottom": "32px"
        }),

        # Analysis Settings Card
        Card([
                html.H3("⚙️ Analysis Settings", style={
                    "fontSize":"24px", "fontWeight":600, "color":"rgba(255,255,255,0.95)",
                    "marginBottom":"8px"
                }),
                html.P("Configure the time range and calculation period for comparing both indexes", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.7)", "marginBottom":"20px"
                }),
            # Row 1: Date Range + Snap to month
                html.Div([
                html.Div([
                    DateRangePicker(
                        id="date-range-cross",
                        label="Date Range",
                        preset_id="preset-cross",
                        preset_value="all",
                        snap_id="snap-month-cross",
                        snap_value=["snap"]
                    )
                ], style={"flex": 1, "minWidth": "300px"})
            ], style={
                "display": "flex",
                "alignItems": "flex-end",
                "gap": "16px",
                "marginBottom": "20px"
            }),
            # Row 2: Navigate to Date
                html.Div([
                html.Label("Navigate to Date", style={
                    "display": "block",
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "color": "rgba(255,255,255,0.9)",
                    "marginBottom": "8px"
                }),
                html.Div([
                    dcc.Dropdown(id="jump-year-cross", options=[], placeholder="Year",
                                 style={"width":"100px","display":"inline-block","marginRight":"8px"}),
                    dcc.Dropdown(id="jump-month-cross", options=MONTH_OPTIONS, placeholder="Month",
                                 style={"width":"120px","display":"inline-block"}),
                ], style={"display": "flex", "alignItems": "center"})
            ], style={"marginBottom": "20px"}),
            # Row 3: Return Calculation Period
            Field(
                label="Return Calculation Period (days)",
                input_component=dcc.Input(
                    id="x-window",
                    type="number",
                    min=1,
                    step=1,
                    value=5,
                    placeholder="e.g., 5",
                        style={
                        "width": "100%",
                        "height": "40px",
                        "padding": "8px 12px",
                        "fontSize": "14px",
                        "background": "rgba(255,255,255,0.1)",
                        "border": "1px solid rgba(255,255,255,0.2)",
                        "borderRadius": "6px",
                        "color": "rgba(255,255,255,0.9)"
                    }
                ),
                helper_text="How many days to use when calculating returns (e.g., 5 days = weekly returns). This measures price change over X-day periods for both indexes."
            ),
        ], footer=html.Div([
            dcc.Loading(
                id="x-analyze-loading",
                type="circle",
                children=html.Div([
                    Button(
                        id="x-analyze",
                        label="Analyze",
                        variant="primary",
                        full_width=False,
                        style={"float": "right"}
                    )
                ], style={
                    "textAlign": "right",
                    "width": "100%"
                }, className="card-footer")
            )
        ], style={
            "textAlign": "right",
            "width": "100%"
        }, className="card-footer"), style={"marginBottom": "32px"}),

        # Results
        dcc.Loading(
            id="x-results-loading",
            type="circle",
            children=html.Div(id="x-results-container", children=[
                html.Div(id="x-line-levels-container"),
                html.Div(id="x-scatter-returns-container"),
                html.Div(id="x-line-returns-container"),
                html.Div(id="x-stats", style={"margin":"24px 0"}),
                html.Div(id="x-trade-windows-container"),
            ], style={"marginTop":"32px"})
        ),

            dcc.Store(id=STORE_A),
            dcc.Store(id=STORE_B),
    ])

# ---------- Documentation Page ----------
def docs_layout():
    return PageContainer([
        # Header
        html.Div([
            html.H1("📖 Documentation", style={
                "fontSize":"42px", "fontWeight":700, "marginBottom":"16px",
                "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "WebkitBackgroundClip":"text", "WebkitTextFillColor":"transparent",
                "backgroundClip":"text"
            }),
            html.P("Complete guide to using the Index Data Analysis application", style={
                "fontSize":"18px", "color":"rgba(255,255,255,0.7)", "marginBottom":"48px"
            }),
        ], style={"textAlign":"center"}),

        # Table of Contents
        Card([
            html.H2("📑 Table of Contents", style={"marginBottom":"20px", "fontSize":"26px", "fontWeight":600, "color":"rgba(255,255,255,0.95)"}),
            html.Ul([
                html.Li(html.A("1. What is this app?", href="#what-is", style={"color":"#667eea", "textDecoration":"none"})),
                html.Li(html.A("2. Data Format Requirements", href="#data-format", style={"color":"#667eea", "textDecoration":"none"})),
                html.Li(html.A("3. Single Index Analysis", href="#single-index", style={"color":"#667eea", "textDecoration":"none"})),
                html.Li(html.A("4. Cross Index Analysis", href="#cross-index", style={"color":"#667eea", "textDecoration":"none"})),
                html.Li(html.A("5. Understanding Key Concepts", href="#concepts", style={"color":"#667eea", "textDecoration":"none"})),
                html.Li(html.A("6. Technical Indicators Explained", href="#indicators", style={"color":"#667eea", "textDecoration":"none"})),
                html.Li(html.A("7. Examples & Use Cases", href="#examples", style={"color":"#667eea", "textDecoration":"none"})),
            ], style={"fontSize":"16px", "lineHeight":"2", "color":"rgba(255,255,255,0.9)"})
        ], style={"marginBottom":"32px"}),

        # Section 1: What is this app?
        html.Div(id="what-is"),
        Card([
            html.H2("1️⃣ What is this app?", style={"marginBottom":"20px", "fontSize":"28px", "fontWeight":600, "color":"#667eea"}),
            html.P([
                "The Index Data Analysis app is a powerful tool designed to analyze financial index data. ",
                "It helps you understand market movements by analyzing price changes over time and identifying ",
                "significant events like drops and gains."
            ], style={"fontSize":"16px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"16px"}),
            html.P([
                html.Strong("Two Main Features:", style={"color":"#667eea"}),
            ], style={"fontSize":"16px", "marginBottom":"12px"}),
            html.Ul([
                html.Li([html.Strong("Single Index Analysis:"), " Analyze one market index in depth, finding drop and gain events with detailed statistics and visualizations."]),
                html.Li([html.Strong("Cross Index Analysis:"), " Compare two different indexes to see how they move together, their correlation, and relative performance."]),
            ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginLeft":"20px"})
        ], style={"marginBottom":"32px"}),

        # Section 2: Data Format
        html.Div(id="data-format"),
        Card([
            html.H2("2️⃣ Data Format Requirements", style={"marginBottom":"20px", "fontSize":"28px", "fontWeight":600, "color":"#667eea"}),
            html.P([
                "Your CSV file must contain ", html.Strong("exactly two columns", style={"color":"#00c896"}), ":"
            ], style={"fontSize":"16px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"16px"}),
            html.Ul([
                html.Li([html.Strong("Column 1:"), " A date or datetime column (any reasonable date format works)"]),
                html.Li([html.Strong("Column 2:"), " A numeric column representing the index value (price, level, etc.)"]),
            ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginLeft":"20px", "marginBottom":"20px"}),
            
            html.H3("✅ Example of Valid Data:", style={"fontSize":"20px", "fontWeight":600, "color":"#22c55e", "marginBottom":"12px"}),
            html.Pre([
                "Date,Index\n",
                "2024-01-01,1000.5\n",
                "2024-01-02,1005.2\n",
                "2024-01-03,998.7\n",
                "2024-01-04,1012.3"
            ], style={
                "background":"rgba(34,197,94,0.1)", "padding":"16px", "borderRadius":"8px",
                "border":"1px solid rgba(34,197,94,0.3)", "fontSize":"14px",
                "color":"rgba(255,255,255,0.95)", "overflowX":"auto"
            }),
            
            html.Div([
                html.Strong("💡 Important Notes:", style={"color":"#00c896", "display":"block", "marginBottom":"8px"}),
                html.Ul([
                    html.Li("Column headers can have any name - the app automatically detects which is the date and which is numeric"),
                    html.Li("The app handles common date formats automatically (YYYY-MM-DD, MM/DD/YYYY, etc.)"),
                    html.Li("Rows with missing or invalid data will be automatically removed"),
                    html.Li("Data will be automatically sorted by date"),
                ], style={"fontSize":"14px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.8)", "marginLeft":"20px"})
            ], style={"marginTop":"20px", "padding":"16px", "background":"rgba(0,200,150,0.08)", "borderRadius":"8px", "border":"1px solid rgba(0,200,150,0.3)"})
        ], style={"marginBottom":"32px"}),

        # Section 3: Single Index Analysis
        html.Div(id="single-index"),
        Card([
            html.H2("3️⃣ Single Index Analysis", style={"marginBottom":"20px", "fontSize":"28px", "fontWeight":600, "color":"#667eea"}),
            html.P("This mode analyzes a single market index to identify significant price movements.", style={
                "fontSize":"16px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"24px"
            }),
            
            html.H3("📤 Step 1: Upload Your Data", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
            html.P("Click or drag & drop your CSV file into the upload area. You'll see a preview of your data once it's loaded.", style={
                "fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"20px"
            }),
            
            html.H3("🎯 Step 2: Choose Analysis Type", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
            html.Ul([
                html.Li([html.Strong("Drop Analysis (Red):", style={"color":"#ef4444"}), " Identifies periods where the index fell by a specified percentage"]),
                html.Li([html.Strong("Gain Analysis (Green):", style={"color":"#22c55e"}), " Identifies periods where the index rose by a specified percentage"]),
                html.Li("You can analyze both simultaneously!")
            ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginLeft":"20px", "marginBottom":"20px"}),
            
            html.H3("⚙️ Step 3: Configure Parameters", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
            html.Div([
                html.Strong("📅 Date Range:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P("Select the time period to analyze. Options include All time, Year-to-Date (YTD), Last 1 Year, Last 3 Years, Last 6 Months, or Custom range.", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"
                }),
                
                html.Strong("📍 Navigate to Date:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P("Jump directly to a specific year/month in your data for quick analysis of a particular time period.", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"
                }),
                
                html.Strong("📊 Analysis Period (days):", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P([
                    "The time window to measure price changes. For example, a 5-day period means 'from day X to day X+5'. ",
                    "Common choices: 3 days (short-term), 5 days (weekly), 7 days (weekly), 10 days (two weeks). ",
                    "You can also enter a custom period."
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"}),
                
                html.Strong("📉 Minimum Change Threshold:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P([
                    "The minimum percentage change to count as a significant event. ",
                    "For example, 3% means only drops/gains of 3% or more are counted. ",
                    "Lower thresholds = more events found, Higher thresholds = only major events."
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"}),
                
                html.Strong("📅 Snap to Month:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P("When enabled, the analysis period starts at the beginning of the month and ends at month-end. Useful for clean monthly reporting.", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"
                }),
            ], style={"marginLeft":"20px", "marginBottom":"20px"}),
            
            html.H3("📊 Step 4: View Results", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
            html.P("After clicking 'Analyze', you'll see:", style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"12px"}),
            html.Ul([
                html.Li([html.Strong("Event Statistics:"), " Total number of drop/gain events found and their probability"]),
                html.Li([html.Strong("Return Distribution Chart:"), " Visual distribution of all returns during the analysis period"]),
                html.Li([html.Strong("Bar Chart:"), " Count of events that crossed your threshold"]),
                html.Li([html.Strong("Statistical Summary:"), " Mean, median, standard deviation, and other key metrics"]),
                html.Li([html.Strong("Trade Windows Table:"), " Detailed table showing start/end dates for each analysis window"]),
                html.Li([html.Strong("Technical Indicators:"), " RSI, MACD, Bollinger Bands, and more (see section 6)"]),
            ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginLeft":"20px"}),
        ], style={"marginBottom":"32px"}),

        # Section 4: Cross Index Analysis
        html.Div(id="cross-index"),
        Card([
            html.H2("4️⃣ Cross Index Analysis", style={"marginBottom":"20px", "fontSize":"28px", "fontWeight":600, "color":"#f5576c"}),
            html.P("This mode compares two different indexes to understand their relationship and relative performance.", style={
                "fontSize":"16px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"24px"
            }),
            
            html.H3("📤 Step 1: Upload Both Indexes", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
            html.P("Upload two separate CSV files - one for Index A and one for Index B. Both must follow the same data format (see Section 2).", style={
                "fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"20px"
            }),
            
            html.H3("⚙️ Step 2: Configure Analysis Settings", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
            html.Ul([
                html.Li([html.Strong("Date Range:"), " The time period to compare. The app will only analyze dates where both indexes have data."]),
                html.Li([html.Strong("Return Calculation Period:"), " Number of days to use when calculating returns for both indexes (typically 5 days)."]),
            ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginLeft":"20px", "marginBottom":"20px"}),
            
            html.H3("📊 Step 3: Understanding the Results", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
            html.Div([
                html.Strong("📈 Price Levels Over Time:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P("Shows both indexes plotted together so you can see their overall trends and movements.", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"
                }),
                
                html.Strong("🎯 Scatter Plot:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P("Each point represents the returns of both indexes on the same day. If points cluster along a line, the indexes move together (correlated). Scattered points mean independent movement.", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"
                }),
                
                html.Strong("📊 Returns Over Time:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.P("Compares the percentage returns of both indexes over time, making it easy to see which performed better during specific periods.", style={
                    "fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"16px"
                }),
                
                html.Strong("📐 Correlation Coefficient:", style={"display":"block", "marginBottom":"8px", "color":"#667eea"}),
                html.Ul([
                    html.Li([html.Strong("+1.0:"), " Perfect positive correlation (always move together)"]),
                    html.Li([html.Strong("0.0:"), " No correlation (independent movement)"]),
                    html.Li([html.Strong("-1.0:"), " Perfect negative correlation (always move opposite)"]),
                    html.Li([html.Strong("0.7 to 1.0:"), " Strong positive correlation"]),
                    html.Li([html.Strong("0.3 to 0.7:"), " Moderate positive correlation"]),
                ], style={"fontSize":"14px", "lineHeight":"1.6", "color":"rgba(255,255,255,0.85)", "marginLeft":"20px"}),
            ], style={"marginLeft":"20px"}),
        ], style={"marginBottom":"32px"}),

        # Section 5: Key Concepts
        html.Div(id="concepts"),
        Card([
            html.H2("5️⃣ Understanding Key Concepts", style={"marginBottom":"20px", "fontSize":"28px", "fontWeight":600, "color":"#667eea"}),
            
            html.Div([
                html.H3("📊 Returns", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    "A return is the percentage change in index value over a period. ",
                    html.Strong("Formula:"), " ((End Value - Start Value) / Start Value) × 100"
                ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"16px"}),
                html.P([
                    html.Strong("Example:"), " If an index goes from 1000 to 1050 over 5 days, the 5-day return is ((1050-1000)/1000) × 100 = 5%"
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.8)", "marginBottom":"24px", "fontStyle":"italic"}),
            ]),
            
            html.Div([
                html.H3("📅 Weekend-Aware Calculations", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    "Financial markets are closed on weekends. This app intelligently handles weekends by: ",
                    html.Ul([
                        html.Li("If an analysis period ends on Saturday, it uses Friday's data"),
                        html.Li("If it ends on Sunday, it uses Monday's data"),
                        html.Li("This ensures accurate calendar-based analysis without gaps")
                    ], style={"marginTop":"8px", "lineHeight":"1.6"})
                ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"24px"}),
            ]),
            
            html.Div([
                html.H3("📈 Probability", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    "The probability shown is: (Number of Events / Total Analysis Windows) × 100"
                ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"12px"}),
                html.P([
                    html.Strong("Example:"), " If you find 45 drop events out of 500 analysis windows, the probability is 45/500 = 9%"
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.8)", "fontStyle":"italic"}),
            ]),
        ], style={"marginBottom":"32px"}),

        # Section 6: Technical Indicators
        html.Div(id="indicators"),
        Card([
            html.H2("6️⃣ Technical Indicators Explained", style={"marginBottom":"20px", "fontSize":"28px", "fontWeight":600, "color":"#667eea"}),
            html.P("When you analyze a single index, the app calculates various technical indicators used by traders and analysts:", style={
                "fontSize":"16px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginBottom":"24px"
            }),
            
            html.Div([
                html.H3("📊 Moving Averages (SMA, EMA)", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    html.Strong("What it is:"), " Average of prices over a period. SMA = simple average, EMA = gives more weight to recent prices."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"8px"}),
                html.P([
                    html.Strong("How to use it:"), " When price crosses above MA = potential uptrend. When price crosses below MA = potential downtrend."
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"20px"}),
            ]),
            
            html.Div([
                html.H3("📉 MACD (Moving Average Convergence Divergence)", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    html.Strong("What it is:"), " Shows the relationship between two moving averages (12-day EMA - 26-day EMA)."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"8px"}),
                html.P([
                    html.Strong("How to use it:"), " When MACD crosses above signal line = bullish signal. When MACD crosses below signal line = bearish signal."
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"20px"}),
            ]),
            
            html.Div([
                html.H3("💪 RSI (Relative Strength Index)", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    html.Strong("What it is:"), " Measures momentum on a scale of 0-100."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"8px"}),
                html.P([
                    html.Strong("How to use it:"),
                    html.Ul([
                        html.Li("RSI > 70: Potentially overbought (may drop soon)"),
                        html.Li("RSI < 30: Potentially oversold (may rise soon)"),
                        html.Li("RSI around 50: Neutral momentum")
                    ], style={"marginTop":"8px", "lineHeight":"1.6"})
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"20px"}),
            ]),
            
            html.Div([
                html.H3("📊 Bollinger Bands", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    html.Strong("What it is:"), " Shows a middle line (20-day average) with upper and lower bands (±2 standard deviations)."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"8px"}),
                html.P([
                    html.Strong("How to use it:"), " Price near upper band = potentially overbought. Price near lower band = potentially oversold. Narrowing bands = low volatility (potential breakout coming)."
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"20px"}),
            ]),
            
            html.Div([
                html.H3("📉 Volatility", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    html.Strong("What it is:"), " Measures how much prices fluctuate (standard deviation of returns)."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"8px"}),
                html.P([
                    html.Strong("How to use it:"), " High volatility = larger price swings (higher risk/opportunity). Low volatility = stable prices (lower risk/opportunity)."
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginBottom":"20px"}),
            ]),
            
            html.Div([
                html.H3("📉 Drawdown", style={"fontSize":"20px", "fontWeight":600, "color":"#00c896", "marginBottom":"8px"}),
                html.P([
                    html.Strong("What it is:"), " How far the price has fallen from its recent peak."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"8px"}),
                html.P([
                    html.Strong("How to use it:"), " Large drawdowns indicate significant losses from recent highs. Recovery from drawdown shows resilience."
                ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)"}),
            ]),
        ], style={"marginBottom":"32px"}),

        # Section 7: Examples
        html.Div(id="examples"),
        Card([
            html.H2("7️⃣ Examples & Use Cases", style={"marginBottom":"20px", "fontSize":"28px", "fontWeight":600, "color":"#667eea"}),
            
            html.Div([
                html.H3("💼 Use Case 1: Risk Assessment", style={"fontSize":"22px", "fontWeight":600, "color":"#f5576c", "marginBottom":"12px"}),
                html.P([
                    html.Strong("Scenario:"), " You want to understand how often the S&P 500 drops by 5% or more in a week."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"12px"}),
                html.Div([
                    html.Strong("Steps:", style={"display":"block", "marginBottom":"8px"}),
                    html.Ol([
                        html.Li("Upload your S&P 500 CSV data"),
                        html.Li("Select 'Drop' analysis"),
                        html.Li("Set Analysis Period to 7 days"),
                        html.Li("Set Minimum Threshold to 5%"),
                        html.Li("Click Analyze"),
                    ], style={"lineHeight":"1.8", "marginLeft":"20px"}),
                    html.P([
                        html.Strong("Result:"), " You'll see the probability (e.g., '8%') meaning that 7-day drops of 5%+ occur in 8% of all 7-day periods."
                    ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginTop":"12px"})
                ], style={"marginLeft":"20px", "marginBottom":"24px"}),
            ]),
            
            html.Div([
                html.H3("📈 Use Case 2: Growth Opportunities", style={"fontSize":"22px", "fontWeight":600, "color":"#22c55e", "marginBottom":"12px"}),
                html.P([
                    html.Strong("Scenario:"), " You want to find periods when a stock gained 10% or more in 10 days."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"12px"}),
                html.Div([
                    html.Strong("Steps:", style={"display":"block", "marginBottom":"8px"}),
                    html.Ol([
                        html.Li("Upload your stock index data"),
                        html.Li("Select 'Gain' analysis"),
                        html.Li("Set Analysis Period to 10 days"),
                        html.Li("Set Minimum Threshold to 10%"),
                        html.Li("Check the Trade Windows table to see exact dates of these events"),
                    ], style={"lineHeight":"1.8", "marginLeft":"20px"}),
                    html.P([
                        html.Strong("Result:"), " You'll see all periods where this occurred, helping you understand growth patterns."
                    ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginTop":"12px"})
                ], style={"marginLeft":"20px", "marginBottom":"24px"}),
            ]),
            
            html.Div([
                html.H3("🔀 Use Case 3: Comparing Indexes", style={"fontSize":"22px", "fontWeight":600, "color":"#667eea", "marginBottom":"12px"}),
                html.P([
                    html.Strong("Scenario:"), " You want to see if technology stocks move with the overall market."
                ], style={"fontSize":"15px", "color":"rgba(255,255,255,0.9)", "marginBottom":"12px"}),
                html.Div([
                    html.Strong("Steps:", style={"display":"block", "marginBottom":"8px"}),
                    html.Ol([
                        html.Li("Go to Cross Index Analysis"),
                        html.Li("Upload S&P 500 data as Index A"),
                        html.Li("Upload NASDAQ data as Index B"),
                        html.Li("Set a 5-day return period"),
                        html.Li("Click Analyze"),
                    ], style={"lineHeight":"1.8", "marginLeft":"20px"}),
                    html.P([
                        html.Strong("Result:"), " A correlation of 0.85 or higher means they move together strongly. Lower correlation means more independent movement."
                    ], style={"fontSize":"14px", "color":"rgba(255,255,255,0.85)", "marginTop":"12px"})
                ], style={"marginLeft":"20px", "marginBottom":"24px"}),
            ]),
            
            html.Div([
                html.H3("💡 Pro Tips", style={"fontSize":"22px", "fontWeight":600, "color":"#00c896", "marginBottom":"12px"}),
                html.Ul([
                    html.Li([html.Strong("Start with common settings:"), " 5-day period, 3% threshold"]),
                    html.Li([html.Strong("Use YTD:"), " To analyze current year performance"]),
                    html.Li([html.Strong("Compare different thresholds:"), " Run analysis with 3%, 5%, and 10% to see different risk levels"]),
                    html.Li([html.Strong("Check weekend behavior:"), " The app handles weekends automatically - no manual adjustments needed"]),
                    html.Li([html.Strong("Look at indicators together:"), " RSI + MACD + Bollinger Bands give a complete picture"]),
                ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)", "marginLeft":"20px"})
            ], style={"padding":"20px", "background":"rgba(0,200,150,0.08)", "borderRadius":"12px", "border":"1px solid rgba(0,200,150,0.3)"}),
        ], style={"marginBottom":"32px"}),

        # Footer
        Card([
            html.H3("❓ Need More Help?", style={"fontSize":"22px", "fontWeight":600, "color":"#667eea", "marginBottom":"12px"}),
            html.P([
                "This documentation covers all the main features and concepts. ",
                "If you're still unsure about something, start with the examples above and experiment with your data. ",
                "The app is designed to be intuitive - just upload your CSV and try the preset options first!"
            ], style={"fontSize":"15px", "lineHeight":"1.8", "color":"rgba(255,255,255,0.9)"}),
            html.Div([
                html.A("← Back to Home", href="/", style={
                    "display":"inline-block", "marginTop":"20px", "padding":"12px 24px",
                    "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "color":"white", "textDecoration":"none", "borderRadius":"8px",
                    "fontWeight":"600", "fontSize":"15px"
                })
            ])
        ], style={"marginTop":"32px", "textAlign":"center"})
    ], style={"maxWidth":"900px", "margin":"0 auto"})

# -----------------------------
# Top-level app layout with router
# -----------------------------
app.layout = html.Div(
    [
        html.Div(id="navbar-container"),
        dcc.Location(id="url"),
        html.Div(id="page-content"),
    ],
    id="app-container",
    style={"fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
           "minHeight":"100vh","padding":"0", "margin":"0",
           "background": "#0a0a0a",
           "color": "white",
           "transition": "background-color 0.3s ease, color 0.3s ease"}
)

# Navbar callback - always dark theme
@app.callback(
    Output("navbar-container", "children"),
    Input("url", "pathname"),
    prevent_initial_call=False
)
def update_navbar(pathname):
    # Always return dark theme navbar
    return navbar()


# Router
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page(pathname):
    if pathname == "/single":
        return single_layout()
    elif pathname == "/cross":
        return cross_layout()
    elif pathname == "/docs":
        return docs_layout()
    else:
        return home_layout()

# -----------------------------
# Indicators Select All / Clear All callback
# -----------------------------
@app.callback(
    Output("indicators-select", "value"),
    Input("indicators-select-all", "n_clicks"),
    Input("indicators-clear-all", "n_clicks"),
    State("indicators-select", "options"),
    prevent_initial_call=True,
)
def update_indicators_select_all(select_all_clicks, clear_all_clicks, options):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "indicators-select-all":
        # Select all indicator values
        return [opt["value"] for opt in options]
    elif trigger_id == "indicators-clear-all":
        # Clear all (return empty list)
        return []
    
    return no_update

# -----------------------------
# Upload callback (Single page)
# -----------------------------
@app.callback(
    Output("file-msg", "children"),
    Output("warn-msg", "children"),
    Output("preview", "children"),          # <<< Data Preview here
    Output(STORE_RAW, "data"),
    Output(STORE_META, "data"),
    # Drop bounds
    Output("date-range-drop", "min_date_allowed"),
    Output("date-range-drop", "max_date_allowed"),
    Output("date-range-drop", "start_date"),
    Output("date-range-drop", "end_date"),
    # Gain bounds
    Output("date-range-gain", "min_date_allowed"),
    Output("date-range-gain", "max_date_allowed"),
    Output("date-range-gain", "start_date"),
    Output("date-range-gain", "end_date"),
    # Year options for jump controls
    Output("jump-year-drop", "options"),
    Output("jump-year-drop", "value"),
    Output("jump-month-drop", "value"),
    Output("jump-year-gain", "options"),
    Output("jump-year-gain", "value"),
    Output("jump-month-gain", "value"),
    Input("uploader", "contents"),
    State("uploader", "filename"),
    prevent_initial_call=True,
)
def on_upload_single(contents, filename):
    if contents is None:
        return (no_update,)*19

    df, warns, err = parse_csv_flexible(contents, filename)
    if err:
        return (html.Div(err, style={"color":"crimson"}), None, None, None, None,
                no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update,
                [], None, None, [], None, None)

    info = html.Div([
        html.Strong("Uploaded:"), html.Span(f" {filename} "),
        html.Span(" · Detected columns: ['datetime','index']"),
        html.Span(f" · Rows: {len(df)}"),
    ])
    warn_block = (html.Div([html.Strong("Warnings:"),
                   html.Ul([html.Li(w) for w in warns])], style={"color":"#996800"}) if warns else None)

    # --- Data Preview (first 10 rows)
    table = dash_table.DataTable(
        data=df.head(10).to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=10, 
        style_table={"overflowX": "auto", "backgroundColor": "#1a1a1a"},
        style_cell={
            "textAlign": "left", 
            "minWidth": "120px",
            "backgroundColor": "#1a1a1a",
            "color": "rgba(255,255,255,0.9)",
            "border": "1px solid rgba(255,255,255,0.1)",
            "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
        },
        style_header={
            "backgroundColor": "#252525",
            "color": "rgba(255,255,255,0.95)",
            "fontWeight": "600",
            "border": "1px solid rgba(0,200,150,0.3)",
            "textAlign": "left"
        },
        style_data={
            "backgroundColor": "#1a1a1a",
            "color": "rgba(255,255,255,0.9)",
            "border": "1px solid rgba(255,255,255,0.1)"
        },
        style_data_conditional=[
            {
                "if": {"row_index": "even"},
                "backgroundColor": "#222222",
            },
            {
                "if": {"state": "selected"},
                "backgroundColor": "rgba(0,200,150,0.2)",
                "border": "1px solid rgba(0,200,150,0.5)"
            }
        ],
    )

    raw_payload = {
        "filename": filename,
        "columns": list(df.columns),
        "rows": int(len(df)),
        "csv_b64": base64.b64encode(df.to_csv(index=False).encode()).decode(),
    }
    meta = {"summary": {"rows": int(len(df)), "columns": list(df.columns)}}

    min_d = df["datetime"].min().date()
    max_d = df["datetime"].max().date()
    years = list(range(min_d.year, max_d.year + 1))
    year_options = [{"label": str(y), "value": y} for y in years]

    return (
        info, warn_block, html.Div([html.H3("Preview (first 10 rows)"), table]),
        raw_payload, meta,
        min_d, max_d, min_d, max_d,
        min_d, max_d, min_d, max_d,
        year_options, min_d.year, 1,
        year_options, min_d.year, 1
    )

# Preset → custom when dates edited (Single page)
@app.callback(Output("preset-drop", "value"),
              Input("date-range-drop", "start_date"),
              Input("date-range-drop", "end_date"),
              prevent_initial_call=True)
def force_custom_drop(_s, _e):
    return "custom"

@app.callback(Output("preset-gain", "value"),
              Input("date-range-gain", "start_date"),
              Input("date-range-gain", "end_date"),
              prevent_initial_call=True)
def force_custom_gain(_s, _e):
    return "custom"

# Jump-to initial_visible_month (Single page)
@app.callback(
    Output("date-range-drop", "initial_visible_month"),
    Input("jump-year-drop", "value"),
    Input("jump-month-drop", "value"),
    State("date-range-drop", "initial_visible_month"),
    prevent_initial_call=True
)
def jump_drop(year, month, _cur):
    if year and month:
        return pd.Timestamp(int(year), int(month), 1)
    return no_update

@app.callback(
    Output("date-range-gain", "initial_visible_month"),
    Input("jump-year-gain", "value"),
    Input("jump-month-gain", "value"),
    State("date-range-gain", "initial_visible_month"),
    prevent_initial_call=True
)
def jump_gain(year, month, _cur):
    if year and month:
        return pd.Timestamp(int(year), int(month), 1)
    return no_update

# -----------------------------
# Analyze callback (Single page)
# -----------------------------
@app.callback(
    # DROP outputs
    Output("analysis-output-drop", "children"),
    Output("return-chart-drop-container", "children"),
    Output("bar-chart-drop-container", "children"),
    Output("stats-drop", "children"),
    Output("trade-windows-drop-container", "children"),
    # GAIN outputs
    Output("analysis-output-gain", "children"),
    Output("return-chart-gain-container", "children"),
    Output("bar-chart-gain-container", "children"),
    Output("stats-gain", "children"),
    Output("trade-windows-gain-container", "children"),
    # INDICATOR figure
    Output("indicators-container", "children"),
    # Results container visibility
    Output("results-container", "style"),
    Input("analyze", "n_clicks"),
    State(STORE_RAW, "data"),
    State("analysis-types", "value"),
    # Drop states
    State("preset-drop", "value"),
    State("date-range-drop", "start_date"),
    State("date-range-drop", "end_date"),
    State("snap-month-drop", "value"),
    State("window-size-drop", "value"),
    State("window-size-input-drop", "value"),
    State("min-threshold-drop", "value"),
    State("min-threshold-input-drop", "value"),
    # Gain states
    State("preset-gain", "value"),
    State("date-range-gain", "start_date"),
    State("date-range-gain", "end_date"),
    State("snap-month-gain", "value"),
    State("window-size-gain", "value"),
    State("window-size-input-gain", "value"),
    State("min-threshold-gain", "value"),
    State("min-threshold-input-gain", "value"),
    # Indicators toggles
    State("indicators-select", "value"),
    prevent_initial_call=True,
)
def run_analysis_single(n_clicks, raw_payload, analysis_types,
                 preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop,
                 preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain,
                 indicators_selected):
    if not n_clicks:
        return (no_update,) * 12
    if not raw_payload:
        # Hide all results when no data
        hidden_style = {"display": "none"}
        return (None, None, None, None, None, None, None, None, None, None, None, hidden_style)

    try:
        csv_bytes = base64.b64decode(raw_payload["csv_b64"].encode())
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        # Hide all results on error
        hidden_style = {"display": "none"}
        return (None, None, None, None, None, None, None, None, None, None, None, hidden_style)

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["index"] = pd.to_numeric(df["index"], errors="coerce")
    df = df.dropna(subset=["datetime", "index"]).sort_values("datetime").reset_index(drop=True)

    data_min, data_max = df["datetime"].min(), df["datetime"].max()

    def build_outputs(mode: str,
                      preset, sdate, edate, snap, ws_radio, ws_custom, th_radio, th_custom):
        snap_month = ("snap" in (snap or []))
        start, end = compute_range(preset, sdate, edate, data_min, data_max, snap_month)
        dff = df[(df["datetime"] >= start) & (df["datetime"] <= end)].reset_index(drop=True)
        if dff.empty:
            msg = html.Div(f"No data in selected date range ({start.date()} to {end.date()}).", style={"color": "crimson"})
            empty = go.Figure()
            return msg, empty, empty, None, None

        ws = int(ws_custom) if ws_custom else int(ws_radio)
        th_pct = float(th_custom) if th_custom is not None else float(th_radio)
        th_frac = th_pct / 100.0

        # Weekend-aware summary
        if mode == "gain":
            summary = gain_event_analysis(dff, minimum_per_gain=th_frac, windows_size=ws)
            title = "Gain Event Analysis"
            label = "Min Gain: "
            sign = +1
            color = "#22c55e"
        else:
            summary = drop_event_analysis(dff, minimum_per_drop=th_frac, windows_size=ws)
            title = "Drop Event Analysis"
            label = "Min Drop: "
            sign = -1
            color = "#ef4444"

        (k, v), = summary.items()
        bg_color = "rgba(34,197,94,0.08)" if mode == "gain" else "rgba(239,68,68,0.08)"
        border_color = "rgba(34,197,94,0.3)" if mode == "gain" else "rgba(239,68,68,0.3)"
        card = html.Div([
            html.H3(title, style={"marginTop": 0, "fontSize": "24px", "fontWeight": 700, "color": "inherit"}),
            html.P([
                html.Strong("Change over: "), f"{ws} calendar days (weekend-aware) ",
                html.Span(" · "),
                html.Strong("Range: "), f"{start.date()} → {end.date()} ",
                html.Span(" · "),
                html.Strong(label), f"{th_pct:.2f}%",
            ], style={"fontSize": "14px", "color": "inherit", "opacity": 0.8, "marginBottom": "20px"}),
            html.Div([
                html.Div([
                    html.Div("Events", style={"color": "rgba(255,255,255,0.7)", "fontSize": "13px", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                    html.Div(str(v["events"]), style={"fontSize": "36px", "fontWeight": 700, "color": color, "marginTop": "8px"}),
                ], style={"flex": 1, "textAlign": "center", "padding": "16px", "background": "rgba(255,255,255,0.05)", "borderRadius": "12px", "border": "1px solid rgba(255,255,255,0.1)"}),
                html.Div([
                    html.Div("Probability", style={"color": "rgba(255,255,255,0.7)", "fontSize": "13px", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                    html.Div(v["probability"], style={"fontSize": "36px", "fontWeight": 700, "color": color, "marginTop": "8px"}),
                ], style={"flex": 1, "textAlign": "center", "padding": "16px", "background": "rgba(255,255,255,0.05)", "borderRadius": "12px", "border": "1px solid rgba(255,255,255,0.1)"}),
            ], style={"display": "flex", "gap": "16px", "marginTop": "12px"}),
        ], style={"border": f"1px solid {border_color}", "borderRadius": "16px", "padding": "24px", "background": bg_color, "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"})

        # Weekend-aware returns for visuals
        ret = compute_windowed_returns_calendar(dff, ws)
        mask = ~ret.isna()
        x_time = dff.loc[mask, "datetime"]
        y_pct = ret.loc[mask].values * 100.0

        # Return chart
        line_fig = go.Figure()
        if len(y_pct) > 0:
            line_fig.add_trace(go.Scatter(x=x_time, y=y_pct, mode="lines", name=f"{ws}-day % change"))
            th_line = sign * th_frac * 100.0
            line_fig.add_trace(go.Scatter(x=x_time, y=[th_line]*len(x_time), mode="lines",
                                          name="Threshold", line=dict(dash="dash")))
            idx = np.arange(len(y_pct))
            z = np.polyfit(idx, y_pct, 1)
            trend = z[0]*idx + z[1]
            line_fig.add_trace(go.Scatter(x=x_time, y=trend, mode="lines", name="Trend", line=dict(dash="dot")))
        line_fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(26,26,26,0.8)",
            paper_bgcolor="rgba(10,10,10,0.8)",
            font=dict(color="rgba(255,255,255,0.9)"),
            margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
            xaxis_title="Time", 
            yaxis_title="% change",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,  # Position just above the chart
                xanchor="center",
                x=0.5,
                bgcolor="rgba(10,10,10,0.9)",
                bordercolor="rgba(255,255,255,0.2)",
                borderwidth=1,
                itemwidth=30,
                font=dict(size=10)
            ),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        )

        # Bar chart (counts & probabilities by threshold)
        ret_clean = ret.dropna()
        N = len(ret_clean)
        thresholds_pct = [i for i in range(1, 11)]
        labels = [f"{t}%" for t in thresholds_pct]
        if mode == "gain":
            counts = np.array([(ret_clean >= (t/100.0)).sum() for t in thresholds_pct], dtype=int)
            bar_title = f"{ws}-day gain events"
        else:
            counts = np.array([(ret_clean <= -(t/100.0)).sum() for t in thresholds_pct], dtype=int)
            bar_title = f"{ws}-day drop events"
        probs = (counts / N) * 100.0 if N > 0 else np.zeros_like(counts, dtype=float)

        bar_fig = make_subplots(specs=[[{"secondary_y": True}]])
        bar_fig.add_trace(
            go.Bar(
                x=labels, y=counts, name="Count",
                marker_color=color,
                text=[f"{c:,}" for c in counts], textposition="outside",
                cliponaxis=False,
                customdata=np.round(probs, 2),
                hovertemplate="<b>%{x}</b><br>Count: %{y:,}<br>Probability: %{customdata:.2f}%<extra></extra>",
            ),
            secondary_y=False,
        )
        max_prob = float(probs.max()) if len(probs) else 0.0
        y2_top = max(5.0, np.ceil(max_prob * 1.15 / 5.0) * 5.0)
        bar_fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(26,26,26,0.8)",
            paper_bgcolor="rgba(10,10,10,0.8)",
            font=dict(color="rgba(255,255,255,0.9)"),
            title=dict(
                text=bar_title + (f"  · N={N}" if N else ""),
                x=0.5,
                xanchor="center",
                y=0.98,
                yanchor="top"
            ),
            margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,  # Position just above the chart
                xanchor="center",
                x=0.5,
                bgcolor="rgba(10,10,10,0.9)",
                bordercolor="rgba(255,255,255,0.2)",
                borderwidth=1,
                itemwidth=30,
                font=dict(size=10)
            ),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            bargap=0.2
        )
        bar_fig.update_yaxes(title_text="Count of events", secondary_y=False)
        bar_fig.update_yaxes(title_text="Probability (%)", range=[0, y2_top], secondary_y=True)

        # Stats
        if N > 0:
            desc = ret_clean.describe()
            stats_list = [
                ("Data points", f"{int(desc['count'])}"),
                ("Average change", f"{desc['mean']*100:.2f}%"),
                ("Typical variability (stdev)", f"{desc['std']*100:.2f}%"),
                ("Biggest drop", f"{desc['min']*100:.2f}%"),
                ("25th percentile", f"{desc['25%']*100:.2f}%"),
                ("Median (middle)", f"{desc['50%']*100:.2f}%"),
                ("75th percentile", f"{desc['75%']*100:.2f}%"),
                ("Biggest rise", f"{desc['max']*100:.2f}%"),
            ]
        else:
            stats_list = [("Data points", "0")]
        stats_view = html.Div([
            html.H4("Change summary", style={"margin": "0 0 16px 0", "fontSize": "20px", "fontWeight": 600, "color": "inherit"}),
            html.Ul([html.Li(html.Span([html.Strong(k + ": ", style={"color": "inherit"}), v]), style={
                "marginBottom": "8px", "fontSize": "14px", "color": "inherit", "opacity": 0.9
            }) for k, v in stats_list], style={"listStyle": "none", "padding": 0})
        ], style={"background": "rgba(255,255,255,0.05)", "border": "1px solid rgba(255,255,255,0.1)",
                  "borderRadius": "16px", "padding": "24px", "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"})

        # Trade windows list
        # trade_table = build_trade_window_table(dff[["datetime","index"]], ws, limit=200)
        
        # Wrap graphs and tables in containers with proper styling
        return_chart_container = html.Div([
            dcc.Graph(figure=line_fig, config={"displayModeBar": False}, style={"height": "320px"})
        ], style={
            "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
            "padding":"16px", "marginBottom":"16px",
            "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
            "border":"1px solid rgba(255,255,255,0.1)"
        })
        
        bar_chart_container = html.Div([
            dcc.Graph(figure=bar_fig, config={"displayModeBar": False}, style={"height": "320px"})
        ], style={
            "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
            "padding":"16px", "marginBottom":"16px",
            "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
            "border":"1px solid rgba(255,255,255,0.1)"
        })
        
        # COMMENTED OUT FOR DEBUGGING - Trade windows data hidden
        # trade_windows_container = html.Div([
        #     html.H4("Trade windows (first and last day)", style={
        #         "fontSize":"20px", "fontWeight":600, "color":"inherit",
        #         "marginTop":"32px", "marginBottom":"16px"
        #     }),
        #     trade_table
        # ], style={
        #     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
        #     "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
        #     "border":"1px solid rgba(255,255,255,0.1)"
        # })
        trade_windows_container = html.Div()  # Empty placeholder

        return card, return_chart_container, bar_chart_container, stats_view, trade_windows_container, dff

    want_drop = "drop" in (analysis_types or [])
    want_gain = "gain" in (analysis_types or [])

    drop_out = build_outputs("drop",
                             preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop) \
               if want_drop else (html.Div("Drop disabled"), None, None, None, None, None)

    gain_out = build_outputs("gain",
                             preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain) \
               if want_gain else (html.Div("Gain disabled"), None, None, None, None, None)

    # Build indicators figure from the union of the filtered range (prefer gain range if both same; else use full df slice)
    # We'll use the DROP slice if available, else GAIN slice, else overall df.
    dff_for_indicators = None
    if drop_out[-1] is not None:
        dff_for_indicators = drop_out[-1]
    if gain_out[-1] is not None:
        # if both exist, take intersection of their date windows to keep consistent
        if dff_for_indicators is not None:
            s1, e1 = dff_for_indicators["datetime"].min(), dff_for_indicators["datetime"].max()
            s2, e2 = gain_out[-1]["datetime"].min(), gain_out[-1]["datetime"].max()
            s, e = max(s1, s2), min(e1, e2)
            dff_for_indicators = df[(df["datetime"]>=s) & (df["datetime"]<=e)].reset_index(drop=True)
        else:
            dff_for_indicators = gain_out[-1]
    if dff_for_indicators is None:
        dff_for_indicators = df.copy()

    # --- Build indicators and figure
    feats = build_indicators(dff_for_indicators[["datetime","index"]].copy())
    price = dff_for_indicators["index"].astype(float)
    time = dff_for_indicators["datetime"]

    show_sma  = "sma"  in (indicators_selected or [])
    show_ema  = "ema"  in (indicators_selected or [])
    show_bb   = "bb"   in (indicators_selected or [])
    show_rsi  = "rsi"  in (indicators_selected or [])
    show_macd = "macd" in (indicators_selected or [])
    show_vol  = "vol"  in (indicators_selected or [])
    show_dd   = "dd"   in (indicators_selected or [])

    # Determine which rows to show
    row1_needed = any([True, show_sma, show_ema, show_bb, show_vol, show_dd])  # price always shown
    row2_needed = show_rsi
    row3_needed = show_macd

    rows = (1 if row1_needed else 0) + (1 if row2_needed else 0) + (1 if row3_needed else 0)
    if rows == 0:
        rows = 1  # safety

    fig_ind = make_subplots(
        rows=rows, cols=1, shared_xaxes=True,
        row_heights=[0.5 if rows==3 else (0.65 if rows==2 else 1.0)] + ([0.25] if rows>=2 else []) + ([0.25] if rows==3 else []),
        vertical_spacing=0.06,
        specs=[[{"secondary_y": True}] for _ in range(rows)]
    )

    # helper to map logical row numbers
    cur_row = 1
    row_price = cur_row
    # Row 1: Price + overlays
    fig_ind.add_trace(go.Scatter(x=time, y=price, mode="lines", name="Price"), row=row_price, col=1, secondary_y=False)

    if show_sma:
        fig_ind.add_trace(go.Scatter(x=time, y=feats["sma_5"],  mode="lines", name="SMA 5"),  row=row_price, col=1, secondary_y=False)
        fig_ind.add_trace(go.Scatter(x=time, y=feats["sma_20"], mode="lines", name="SMA 20"), row=row_price, col=1, secondary_y=False)
    if show_ema:
        fig_ind.add_trace(go.Scatter(x=time, y=feats["ema_12"], mode="lines", name="EMA 12"), row=row_price, col=1, secondary_y=False)
        fig_ind.add_trace(go.Scatter(x=time, y=feats["ema_26"], mode="lines", name="EMA 26"), row=row_price, col=1, secondary_y=False)
    if show_bb:
        fig_ind.add_trace(go.Scatter(x=time, y=feats["bb_mid"], mode="lines", name="BB Mid"),   row=row_price, col=1, secondary_y=False)
        fig_ind.add_trace(go.Scatter(x=time, y=feats["bb_up"],  mode="lines", name="BB Upper"), row=row_price, col=1, secondary_y=False)
        fig_ind.add_trace(go.Scatter(x=time, y=feats["bb_lo"],  mode="lines", name="BB Lower"), row=row_price, col=1, secondary_y=False)
    if show_vol:
        # plot vol_20 on secondary y to keep scales tidy
        fig_ind.add_trace(go.Scatter(x=time, y=feats["vol_20"], mode="lines", name="Vol 20 (stdev)"),
                          row=row_price, col=1, secondary_y=True)
    if show_dd:
        fig_ind.add_trace(go.Scatter(x=time, y=feats["dd"], mode="lines", name="Drawdown"),
                          row=row_price, col=1, secondary_y=True)

    fig_ind.update_yaxes(title_text="Price", row=row_price, col=1, secondary_y=False)
    if show_vol or show_dd:
        fig_ind.update_yaxes(title_text="Vol / DD", row=row_price, col=1, secondary_y=True)

    # Row 2: RSI (if needed)
    if row2_needed:
        cur_row += 1
        fig_ind.add_trace(go.Scatter(x=time, y=feats["rsi_14"], mode="lines", name="RSI (14)"),
                          row=cur_row, col=1, secondary_y=False)
        fig_ind.add_hline(y=70, line=dict(dash="dash"), row=cur_row, col=1)
        fig_ind.add_hline(y=30, line=dict(dash="dash"), row=cur_row, col=1)
        fig_ind.update_yaxes(title_text="RSI", range=[0, 100], row=cur_row, col=1)

    # Row 3: MACD (if needed)
    if row3_needed:
        cur_row += 1
        fig_ind.add_trace(go.Bar(x=time, y=feats["macd_hist"], name="MACD Hist"),
                          row=cur_row, col=1, secondary_y=False)
        fig_ind.add_trace(go.Scatter(x=time, y=feats["macd"],     mode="lines", name="MACD"),
                          row=cur_row, col=1, secondary_y=False)
        fig_ind.add_trace(go.Scatter(x=time, y=feats["macd_sig"], mode="lines", name="MACD Signal"),
                          row=cur_row, col=1, secondary_y=False)
        fig_ind.update_yaxes(title_text="MACD", row=cur_row, col=1)

    # Calculate proper margins to accommodate legend outside plotting area
    # Legend will be positioned above the chart, so we need extra top margin
    legend_height = 60  # Estimated height for horizontal legend
    top_margin = 120 + legend_height  # Extra top margin for legend above chart
    bottom_margin = 80  # Base bottom margin
    
    fig_ind.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(26,26,26,0.8)",
        paper_bgcolor="rgba(10,10,10,0.8)",
        font=dict(color="rgba(255,255,255,0.9)"),
        margin=dict(t=top_margin, r=10, l=40, b=bottom_margin),  # Extra top margin for legend above
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,  # Position just above the chart (outside plotting area)
            xanchor="center",
            x=0.5,
            itemwidth=30,
            font=dict(size=10),
            bgcolor="rgba(10,10,10,0.9)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            tracegroupgap=10,  # Space between legend items
            entrywidthmode="fraction",
            entrywidth=0.15  # Control width of legend items
        ),
        title=dict(
            text="Indicators (weekend-aware where applicable)",
            x=0.5,
            xanchor="center",
            font=dict(size=16),
            y=0.95,
            yanchor="top"
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
    )
    
    # Update all subplot x-axes to have consistent styling and prevent overlap
    for i in range(1, cur_row + 1):
        fig_ind.update_xaxes(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)",
            row=i, col=1
    )

    # Unpack results for return
    drop_card, drop_line, drop_bar, drop_stats, drop_table, _dff_drop = drop_out
    gain_card, gain_line, gain_bar, gain_stats, gain_table, _dff_gain = gain_out
    
    # Wrap indicators figure in container
    indicators_container = html.Div([
        html.H3("Indicator Charts", style={
            "fontSize":"28px", "fontWeight":700, "color":"inherit",
            "marginTop":"40px", "marginBottom":"20px"
        }),
        dcc.Graph(figure=fig_ind, config={"displayModeBar": False}, style={"height":"540px"})
    ], style={
        "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
        "padding":"20px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
        "border":"1px solid rgba(255,255,255,0.1)"
    })
    
    # Show results container
    results_style = {"display": "flex", "gap": "20px", "flexWrap": "wrap"}

    return (drop_card, drop_line, drop_bar, drop_stats, drop_table,
            gain_card, gain_line, gain_bar, gain_stats, gain_table,
            indicators_container, results_style)

# -----------------------------
# Upload callback (CROSS page)
# -----------------------------
@app.callback(
    # A side
    Output("file-msg-a", "children"),
    Output("warn-msg-a", "children"),
    Output("preview-a", "children"),
    Output(STORE_A, "data"),
    # B side
    Output("file-msg-b", "children"),
    Output("warn-msg-b", "children"),
    Output("preview-b", "children"),
    Output(STORE_B, "data"),
    # Date range bounds (shared)
    Output("date-range-cross", "min_date_allowed"),
    Output("date-range-cross", "max_date_allowed"),
    Output("date-range-cross", "start_date"),
    Output("date-range-cross", "end_date"),
    # Year jump options
    Output("jump-year-cross", "options"),
    Output("jump-year-cross", "value"),
    Output("jump-month-cross", "value"),

    Input("uploader-a", "contents"),
    State("uploader-a", "filename"),
    Input("uploader-b", "contents"),
    State("uploader-b", "filename"),
    prevent_initial_call=True,
)
def upload_cross(contents_a, filename_a, contents_b, filename_b):
    out = [no_update]*15

    # Parse A
    dfA = warnsA = errA = None
    if contents_a is not None:
        dfA, warnsA, errA = parse_csv_flexible(contents_a, filename_a)
        if errA:
            out[0] = html.Div(errA, style={"color":"crimson"})
            out[1] = None
            out[2] = None
            out[3] = None
        else:
            out[0] = html.Div([html.Strong("A uploaded:"), f" {filename_a} · Rows: {len(dfA)}"])
            out[1] = (html.Div([html.Strong("Warnings:"), html.Ul([html.Li(w) for w in warnsA])],
                               style={"color":"#996800"}) if warnsA else None)
            tableA = dash_table.DataTable(
                data=dfA.head(10).to_dict("records"),
                columns=[{"name": c, "id": c} for c in dfA.columns],
                page_size=10, 
                style_table={"overflowX":"auto", "backgroundColor": "#1a1a1a"},
                style_cell={
                    "textAlign":"left",
                    "minWidth":"120px",
                    "backgroundColor": "#1a1a1a",
                    "color": "rgba(255,255,255,0.9)",
                    "border": "1px solid rgba(255,255,255,0.1)",
                    "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
                },
                style_header={
                    "backgroundColor": "#252525",
                    "color": "rgba(255,255,255,0.95)",
                    "fontWeight": "600",
                    "border": "1px solid rgba(0,200,150,0.3)",
                    "textAlign": "left"
                },
                style_data={
                    "backgroundColor": "#1a1a1a",
                    "color": "rgba(255,255,255,0.9)",
                    "border": "1px solid rgba(255,255,255,0.1)"
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "even"},
                        "backgroundColor": "#222222",
                    },
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "rgba(0,200,150,0.2)",
                        "border": "1px solid rgba(0,200,150,0.5)"
                    }
                ],
            )
            out[2] = html.Div([html.H4("Preview A (first 10)"), tableA])
            out[3] = {
                "filename": filename_a,
                "csv_b64": base64.b64encode(dfA.to_csv(index=False).encode()).decode()
            }

    # Parse B
    dfB = warnsB = errB = None
    if contents_b is not None:
        dfB, warnsB, errB = parse_csv_flexible(contents_b, filename_b)
        if errB:
            out[4] = html.Div(errB, style={"color":"crimson"})
            out[5] = None
            out[6] = None
            out[7] = None
        else:
            out[4] = html.Div([html.Strong("B uploaded:"), f" {filename_b} · Rows: {len(dfB)}"])
            out[5] = (html.Div([html.Strong("Warnings:"), html.Ul([html.Li(w) for w in warnsB])],
                               style={"color":"#996800"}) if warnsB else None)
            tableB = dash_table.DataTable(
                data=dfB.head(10).to_dict("records"),
                columns=[{"name": c, "id": c} for c in dfB.columns],
                page_size=10, 
                style_table={"overflowX":"auto", "backgroundColor": "#1a1a1a"},
                style_cell={
                    "textAlign":"left",
                    "minWidth":"120px",
                    "backgroundColor": "#1a1a1a",
                    "color": "rgba(255,255,255,0.9)",
                    "border": "1px solid rgba(255,255,255,0.1)",
                    "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
                },
                style_header={
                    "backgroundColor": "#252525",
                    "color": "rgba(255,255,255,0.95)",
                    "fontWeight": "600",
                    "border": "1px solid rgba(0,200,150,0.3)",
                    "textAlign": "left"
                },
                style_data={
                    "backgroundColor": "#1a1a1a",
                    "color": "rgba(255,255,255,0.9)",
                    "border": "1px solid rgba(255,255,255,0.1)"
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "even"},
                        "backgroundColor": "#222222",
                    },
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "rgba(0,200,150,0.2)",
                        "border": "1px solid rgba(0,200,150,0.5)"
                    }
                ],
            )
            out[6] = html.Div([html.H4("Preview B (first 10)"), tableB])
            out[7] = {
                "filename": filename_b,
                "csv_b64": base64.b64encode(dfB.to_csv(index=False).encode()).decode()
            }

    # Set date bounds based on whichever is loaded; if both, use intersection
    if dfA is None and dfB is None:
        return tuple(out)

    if dfA is not None and dfB is not None:
        min_d = max(dfA["datetime"].min().date(), dfB["datetime"].min().date())
        max_d = min(dfA["datetime"].max().date(), dfB["datetime"].max().date())
        if min_d > max_d:
            # No overlap
            out[8]  = None
            out[9]  = None
            out[10] = None
            out[11] = None
            out[12] = []
            out[13] = None
            out[14] = None
            return tuple(out)
    elif dfA is not None:
        min_d = dfA["datetime"].min().date()
        max_d = dfA["datetime"].max().date()
    else:
        min_d = dfB["datetime"].min().date()
        max_d = dfB["datetime"].max().date()

    years = list(range(min_d.year, max_d.year + 1))
    year_options = [{"label": str(y), "value": y} for y in years]

    out[8]  = min_d
    out[9]  = max_d
    out[10] = min_d
    out[11] = max_d
    out[12] = year_options
    out[13] = min_d.year
    out[14] = 1
    return tuple(out)

# Preset → custom when dates edited (CROSS page)
@app.callback(Output("preset-cross", "value"),
              Input("date-range-cross", "start_date"),
              Input("date-range-cross", "end_date"),
              prevent_initial_call=True)
def force_custom_cross(_s, _e):
    return "custom"

# Jump-to initial_visible_month (CROSS page)
@app.callback(
    Output("date-range-cross", "initial_visible_month"),
    Input("jump-year-cross", "value"),
    Input("jump-month-cross", "value"),
    State("date-range-cross", "initial_visible_month"),
    prevent_initial_call=True
)
def jump_cross(year, month, _cur):
    if year and month:
        return pd.Timestamp(int(year), int(month), 1)
    return no_update

# -----------------------------
# Analyze callback (CROSS page)
# -----------------------------
@app.callback(
    Output("x-line-levels-container", "children"),
    Output("x-scatter-returns-container", "children"),
    Output("x-line-returns-container", "children"),
    Output("x-stats", "children"),
    Output("x-trade-windows-container", "children"),
    Output("x-results-container", "style"),
    Input("x-analyze", "n_clicks"),
    State(STORE_A, "data"),
    State(STORE_B, "data"),
    State("preset-cross", "value"),
    State("date-range-cross", "start_date"),
    State("date-range-cross", "end_date"),
    State("snap-month-cross", "value"),
    State("x-window", "value"),
    prevent_initial_call=True,
)
def run_cross(n_clicks, rawA, rawB, preset, sd, ed, snap_val, win):
    if not n_clicks:
        return (no_update,) * 6
    if not rawA or not rawB:
        # Hide all results when no data
        hidden_style = {"display": "none"}
        return None, None, None, None, None, hidden_style

    # Load A & B
    try:
        dfA = pd.read_csv(io.BytesIO(base64.b64decode(rawA["csv_b64"].encode())))
        dfB = pd.read_csv(io.BytesIO(base64.b64decode(rawB["csv_b64"].encode())))
    except Exception as e:
        # Hide all results on error
        hidden_style = {"display": "none"}
        return None, None, None, None, None, hidden_style

    for df in (dfA, dfB):
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["index"] = pd.to_numeric(df["index"], errors="coerce")
    dfA = dfA.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)
    dfB = dfB.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)

    # Determine overall range intersection
    data_min = max(dfA["datetime"].min(), dfB["datetime"].min())
    data_max = min(dfA["datetime"].max(), dfB["datetime"].max())
    if data_min >= data_max:
        # Hide all results when no overlap
        hidden_style = {"display": "none"}
        return None, None, None, None, None, hidden_style

    snap = ("snap" in (snap_val or []))
    start, end = compute_range(preset, sd, ed, data_min, data_max, snap)

    # Slice to range and inner-join on dates for level chart
    A_in = dfA[(dfA["datetime"]>=start) & (dfA["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"A"})
    B_in = dfB[(dfB["datetime"]>=start) & (dfB["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"B"})
    levels = pd.merge(A_in, B_in, on="datetime", how="inner")
    if levels.empty:
        # Hide all results when no data in range
        hidden_style = {"display": "none"}
        return None, None, None, None, None, hidden_style

    # -------- Chart 1: Levels normalized to 100 at range start --------
    baseA = levels["A"].iloc[0]
    baseB = levels["B"].iloc[0]
    normA = 100 * levels["A"] / baseA
    normB = 100 * levels["B"] / baseB

    fig_levels = go.Figure()
    fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normA, mode="lines", name="Index A (norm. to 100)"))
    fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normB, mode="lines", name="Index B (norm. to 100)"))
    fig_levels.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(26,26,26,0.8)",
        paper_bgcolor="rgba(10,10,10,0.8)",
        font=dict(color="rgba(255,255,255,0.9)"),
        title=f"Both Indexes (normalized) · {start.date()} → {end.date()}",
        margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
        xaxis_title="Date", 
        yaxis_title="Indexed level (start=100)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(10,10,10,0.9)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            itemwidth=30,
            font=dict(size=10)
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
    )

    # -------- Weekend-aware returns (window size in calendar days) --------
    win = max(int(win or 1), 1)
    retA_series = compute_windowed_returns_calendar(dfA, win)
    retB_series = compute_windowed_returns_calendar(dfB, win)

    tmpA = dfA.assign(retA=retA_series)
    tmpB = dfB.assign(retB=retB_series)
    tmpA = tmpA[(tmpA["datetime"]>=start) & (tmpA["datetime"]<=end)]
    tmpB = tmpB[(tmpB["datetime"]>=start) & (tmpB["datetime"]<=end)]

    rets = pd.merge(
        tmpA[["datetime","retA"]],
        tmpB[["datetime","retB"]],
        on="datetime",
        how="inner"
    ).dropna(subset=["retA","retB"])

    if rets.empty:
        # Hide all results when no returns data
        hidden_style = {"display": "none"}
        return None, None, None, None, None, hidden_style

    # -------- Chart 2: Correlation scatter (windowed returns) --------
    x = rets["retB"].values * 100.0
    y = rets["retA"].values * 100.0
    if len(x) >= 2:
        corr = float(np.corrcoef(x, y)[0,1])
    else:
        corr = float("nan")

    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=x, y=y, mode="markers", name=f"{win}-day returns",
        hovertemplate="B: %{x:.2f}%<br>A: %{y:.2f}%<extra></extra>"
    ))
    if len(x) >= 2:
        m, b = np.polyfit(x, y, 1)
        xfit = np.linspace(x.min(), x.max(), 100)
        yfit = m*xfit + b
        fig_scatter.add_trace(go.Scatter(x=xfit, y=yfit, mode="lines", name="Fit", line=dict(dash="dash")))
        subtitle = f"Pearson corr = {corr:.2f} · slope≈{m:.2f} (beta A on B)"
    else:
        subtitle = "Pearson corr = n/a"
    fig_scatter.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(26,26,26,0.8)",
        paper_bgcolor="rgba(10,10,10,0.8)",
        font=dict(color="rgba(255,255,255,0.9)"),
        title=dict(
            text=f"Correlation (windowed returns) — {subtitle}",
            x=0.5,
            xanchor="center",
            y=0.98,
            yanchor="top"
        ),
        margin=dict(t=100, r=10, l=50, b=50),  # Increased top margin for legend
        xaxis_title=f"Index B {win}-day return (%)",
        yaxis_title=f"Index A {win}-day return (%)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(10,10,10,0.9)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            itemwidth=30,
            font=dict(size=10)
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
    )

    # -------- Chart 3: Windowed returns through time --------
    ret_time = rets.reset_index(drop=True)
    fig_returns = go.Figure()
    fig_returns.add_trace(go.Scatter(
        x=ret_time["datetime"], y=ret_time["retA"]*100.0, mode="lines", name=f"A {win}-day %"
    ))
    fig_returns.add_trace(go.Scatter(
        x=ret_time["datetime"], y=ret_time["retB"]*100.0, mode="lines", name=f"B {win}-day %"
    ))
    fig_returns.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(26,26,26,0.8)",
        paper_bgcolor="rgba(10,10,10,0.8)",
        font=dict(color="rgba(255,255,255,0.9)"),
        title=f"{win}-day Returns Over Time · {start.date()} → {end.date()}",
        margin=dict(t=100, r=10, l=40, b=40),  # Increased top margin for legend
        xaxis_title="Date", 
        yaxis_title=f"{win}-day return (%)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(10,10,10,0.9)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            itemwidth=30,
            font=dict(size=10)
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
    )

    # -------- Stats card --------
    def stats_block(name, s):
        desc = s.describe()
        items = [
            ("Data points", f"{int(desc['count'])}"),
            ("Average %",   f"{desc['mean']*100:.2f}%"),
            ("Std dev %",   f"{desc['std']*100:.2f}%"),
            ("Min %",       f"{desc['min']*100:.2f}%"),
            ("25% %",       f"{desc['25%']*100:.2f}%"),
            ("Median %",    f"{desc['50%']*100:.2f}%"),
            ("75% %",       f"{desc['75%']*100:.2f}%"),
            ("Max %",       f"{desc['max']*100:.2f}%"),
        ]
        return html.Div([
            html.H4(name, style={"margin":"0 0 16px 0", "fontSize":"18px", "fontWeight":600, "color":"inherit"}),
            html.Ul([html.Li(html.Span([html.Strong(k + ": ", style={"color":"inherit"}), v]), style={
                "marginBottom":"8px", "fontSize":"14px", "color":"inherit", "opacity":0.9
            }) for k, v in items], style={"listStyle":"none", "padding":0})
        ], style={"flex":1, "background":"rgba(255,255,255,0.05)","border":"1px solid rgba(255,255,255,0.1)",
                  "borderRadius":"16px","padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)"})

    corr_text = html.Div([
        html.H4("Relationship", style={"margin":"0 0 12px 0", "fontSize":"18px", "fontWeight":600, "color":"inherit"}),
        html.P(f"Pearson correlation (windowed returns): {corr:.2f}" if np.isfinite(corr) else
               "Pearson correlation (windowed returns): n/a", style={
                   "fontSize":"16px", "color":"inherit", "opacity":0.9, "margin":0,
                   "fontWeight":500 if np.isfinite(corr) else 400
               })
    ], style={"flex":1, "background":"rgba(0,200,150,0.08)","border":"1px solid rgba(0,200,150,0.3)",
              "borderRadius":"16px","padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)"})

    stats_view = html.Div([
        html.Div([
            stats_block("Index A — Stats", rets["retA"]),
            stats_block("Index B — Stats", rets["retB"]),
            corr_text
        ], style={"display":"flex","gap":"12px","flexWrap":"wrap"})
    ])

    twin = html.Div()  # Empty placeholder
    
    # Wrap graphs in containers
    levels_container = html.Div([
        dcc.Graph(figure=fig_levels, config={"displayModeBar": False}, style={"height":"360px"})
    ], style={
        "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
        "padding":"20px", "marginBottom":"24px",
        "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
        "border":"1px solid rgba(255,255,255,0.1)"
    })
    
    scatter_container = html.Div([
        dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}, style={"height":"360px"})
    ], style={
        "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
        "padding":"20px", "marginBottom":"24px",
        "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
        "border":"1px solid rgba(255,255,255,0.1)"
    })
    
    returns_container = html.Div([
        dcc.Graph(figure=fig_returns, config={"displayModeBar": False}, style={"height":"360px"})
    ], style={
        "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
        "padding":"20px", "marginBottom":"24px",
        "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
        "border":"1px solid rgba(255,255,255,0.1)"
    })
    
    # Show results container
    results_style = {"marginTop": "32px"}

    return levels_container, scatter_container, returns_container, stats_view, twin, results_style


# Local run (useful for dev & Render health checks)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)




