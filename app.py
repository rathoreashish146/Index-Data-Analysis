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
#         style_table={"overflowX": "auto"},
#         style_cell={"textAlign": "left", "minWidth": "160px"},
#     )
#     return table

# # -----------------------------
# # Layouts: Home / Single / Cross
# # -----------------------------

# card_style = {
#     "display": "inline-block",
#     "padding": "32px 36px",
#     "borderRadius": "20px",
#     "border": "none",
#     "boxShadow": "0 8px 24px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)",
#     "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#     "textDecoration": "none",
#     "color": "white",
#     "width": "320px",
#     "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
#     "cursor": "pointer",
# }
# card_style_hover = {
#     "transform": "translateY(-4px)",
#     "boxShadow": "0 12px 32px rgba(0,0,0,0.18), 0 4px 12px rgba(0,0,0,0.12)",
# }

# def navbar():
#     return html.Div(
#         [
#             dcc.Link("Home", href="/", style={
#                 "marginRight":"24px", "fontWeight":600, "textDecoration":"none",
#                 "color":"#1e293b", "fontSize":"16px", "padding":"8px 16px",
#                 "borderRadius":"8px", "transition":"all 0.2s",
#                 "hover": {"background":"#f1f5f9", "color":"#667eea"}
#             }),
#             dcc.Link("Single Index", href="/single", style={
#                 "marginRight":"24px", "textDecoration":"none",
#                 "color":"#475569", "fontSize":"16px", "padding":"8px 16px",
#                 "borderRadius":"8px", "transition":"all 0.2s",
#                 "fontWeight":500
#             }),
#             dcc.Link("Cross Index", href="/cross", style={
#                 "textDecoration":"none", "color":"#475569",
#                 "fontSize":"16px", "padding":"8px 16px",
#                 "borderRadius":"8px", "transition":"all 0.2s",
#                 "fontWeight":500
#             }),
#         ],
#         style={
#             "padding":"20px 32px", "borderBottom":"2px solid #e2e8f0",
#             "marginBottom":"32px", "background":"white",
#             "boxShadow":"0 2px 8px rgba(0,0,0,0.04)",
#             "borderRadius":"0 0 12px 12px"
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
#                         style={"marginRight": "24px", "textDecoration":"none"}
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
#                         style={"textDecoration":"none"}
#                     ),
#                 ],
#                 style={"marginTop": "12px", "display":"flex", "justifyContent":"center", "flexWrap":"wrap"}
#             ),
#         ],
#         style={"maxWidth":"1200px","margin":"0 auto","padding":"48px 24px"}
#     )

# # ---------- Single Index (FULL) ----------
# def single_layout():
#     return html.Div([
#         html.Div([
#             html.H1("Single Index Analysis", style={
#                 "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
#                 "color":"#1e293b"
#             }),
#             html.P("Upload a CSV with two columns: a date column and a numeric index column (headers can be anything).", style={
#                 "fontSize":"16px", "color":"#64748b", "marginBottom":"32px"
#             }),
#         ]),

#         dcc.Upload(
#             id="uploader",
#             children=html.Div([
#                 html.Div("📁", style={"fontSize":"32px", "marginBottom":"8px"}),
#                 html.Div("Drag and Drop or ", style={"fontSize":"16px", "color":"#64748b"}),
#                 html.A("Select CSV File", style={"fontSize":"16px", "color":"#667eea", "fontWeight":600, "textDecoration":"underline"})
#             ]),
#             style={
#                 "width":"100%","height":"120px","lineHeight":"120px",
#                 "borderWidth":"2px","borderStyle":"dashed","borderColor":"#cbd5e1",
#                 "borderRadius":"16px","textAlign":"center","margin":"10px 0",
#                 "background":"linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
#                 "transition":"all 0.3s", "cursor":"pointer",
#                 "display":"flex", "flexDirection":"column", "justifyContent":"center", "alignItems":"center"
#             },
#             multiple=False, accept=".csv",
#         ),

#         html.Div(id="file-msg", style={"marginBottom": "8px"}),
#         html.Div(id="warn-msg", style={"marginBottom": "8px"}),

#         html.Div([
#             html.Label("Analysis Type(s)", style={
#                 "fontWeight": "600", "fontSize":"16px", "color":"#1e293b",
#                 "marginBottom":"12px", "display":"block"
#             }),
#             dcc.Checklist(
#                 id="analysis-types",
#                 options=[{"label": " Drop", "value": "drop"},
#                          {"label": " Gain", "value": "gain"}],
#                 value=["drop", "gain"], inline=True,
#                 inputStyle={"marginRight": "8px", "cursor":"pointer"},
#                 labelStyle={
#                     "display": "inline-block", "marginRight": "24px",
#                     "fontSize":"15px", "color":"#475569", "cursor":"pointer"
#                 },
#             ),
#         ], style={
#             "marginBottom": "24px", "padding":"20px",
#             "background":"white", "borderRadius":"12px",
#             "boxShadow":"0 2px 8px rgba(0,0,0,0.06)"
#         }),

#         # Controls row: Drop (left) & Gain (right)
#         html.Div([

#             # -------------------- DROP CONTROLS --------------------
#             html.Div([
#                 html.H3("Drop Options", style={
#                     "marginBottom": "16px", "fontSize":"22px",
#                     "fontWeight":600, "color":"#dc2626"
#                 }),

#                 # Date range + Jump to
#                 html.Div([
#                     html.Label("Date Range", style={"fontWeight": "600"}),
#                     dcc.Dropdown(
#                         id="preset-drop",
#                         options=[
#                             {"label":"All","value":"all"},
#                             {"label":"YTD","value":"ytd"},
#                             {"label":"Last 1Y","value":"1y"},
#                             {"label":"Last 3Y","value":"3y"},
#                             {"label":"Last 6M","value":"6m"},
#                             {"label":"Custom","value":"custom"},
#                         ],
#                         value="all", clearable=False,
#                         style={"width":"180px","marginRight":"8px","display":"inline-block"}
#                     ),
#                     dcc.DatePickerRange(
#                         id="date-range-drop",
#                         display_format="YYYY-MM-DD",
#                         minimum_nights=0, clearable=True, persistence=True,
#                         style={"display":"inline-block"}
#                     ),
#                     dcc.Checklist(
#                         id="snap-month-drop",
#                         options=[{"label":" Snap to month", "value":"snap"}],
#                         value=["snap"], inline=True,
#                         style={"marginLeft":"10px", "display":"inline-block"}
#                     ),
#                 ], style={"margin":"6px 4px 4px 0"}),

#                 html.Div([
#                     html.Span("Jump to:", style={"marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-year-drop", options=[], placeholder="Year",
#                                  style={"width":"100px","display":"inline-block","marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-month-drop", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                 ], style={"marginBottom":"8px"}),

#                 html.Div([
#                     html.Label("Change over (days)", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="window-size-drop",
#                         options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
#                                  {"label": "7", "value": 7}, {"label": "10", "value": 10}],
#                         value=5, inline=True
#                     ),
#                     dcc.Input(
#                         id="window-size-input-drop", type="number", min=1, step=1,
#                         placeholder="custom", style={"marginLeft":"8px","width":"100px"}
#                     )
#                 ], style={"margin":"6px 0"}),

#                 html.Div([
#                     html.Label("Min % Threshold", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="min-threshold-drop",
#                         options=[{"label":"1%","value":1},{"label":"3%","value":3},
#                                  {"label":"5%","value":5},{"label":"10%","value":10}],
#                         value=3, inline=True
#                     ),
#                     dcc.Input(
#                         id="min-threshold-input-drop", type="number", min=0, max=100, step=0.01,
#                         placeholder="e.g. 2.7", style={"marginLeft":"8px","width":"120px"}
#                     )
#                 ], style={"margin":"6px 0"}),
#             ], style={
#                 "flex":1, "minWidth":"420px", "padding":"24px",
#                 "background":"white", "borderRadius":"16px",
#                 "boxShadow":"0 4px 12px rgba(0,0,0,0.08)",
#                 "border":"2px solid #fee2e2"
#             }),

#             # -------------------- GAIN CONTROLS --------------------
#             html.Div([
#                 html.H3("Gain Options", style={
#                     "marginBottom": "16px", "fontSize":"22px",
#                     "fontWeight":600, "color":"#16a34a"
#                 }),

#                 html.Div([
#                     html.Label("Date Range", style={"fontWeight": "600"}),
#                     dcc.Dropdown(
#                         id="preset-gain",
#                         options=[
#                             {"label":"All","value":"all"},
#                             {"label":"YTD","value":"ytd"},
#                             {"label":"Last 1Y","value":"1y"},
#                             {"label":"Last 3Y","value":"3y"},
#                             {"label":"Last 6M","value":"6m"},
#                             {"label":"Custom","value":"custom"},
#                         ],
#                         value="all", clearable=False,
#                         style={"width":"180px","marginRight":"8px","display":"inline-block"}
#                     ),
#                     dcc.DatePickerRange(
#                         id="date-range-gain",
#                         display_format="YYYY-MM-DD",
#                         minimum_nights=0, clearable=True, persistence=True,
#                         style={"display":"inline-block"}
#                     ),
#                     dcc.Checklist(
#                         id="snap-month-gain",
#                         options=[{"label":" Snap to month", "value":"snap"}],
#                         value=["snap"], inline=True,
#                         style={"marginLeft":"10px", "display":"inline-block"}
#                     )
#                 ], style={"margin":"6px 4px 4px 0"}),

#                 html.Div([
#                     html.Span("Jump to:", style={"marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-year-gain", options=[], placeholder="Year",
#                                  style={"width":"100px","display":"inline-block","marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-month-gain", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                 ], style={"marginBottom":"8px"}),

#                 html.Div([
#                     html.Label("Change over (days)", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="window-size-gain",
#                         options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
#                                  {"label": "7", "value": 7}, {"label": "10", "value": 10}],
#                         value=5, inline=True
#                     ),
#                     dcc.Input(
#                         id="window-size-input-gain", type="number", min=1, step=1,
#                         placeholder="custom", style={"marginLeft":"8px","width":"100px"}
#                     )
#                 ], style={"margin":"6px 0"}),

#                 html.Div([
#                     html.Label("Min % Threshold", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="min-threshold-gain",
#                         options=[{"label":"1%","value":1},{"label":"3%","value":3},
#                                  {"label":"5%","value":5},{"label":"10%","value":10}],
#                         value=3, inline=True
#                     ),
#                     dcc.Input(
#                         id="min-threshold-input-gain", type="number", min=0, max=100, step=0.01,
#                         placeholder="e.g. 2.7", style={"marginLeft":"8px","width":"120px"}
#                     )
#                 ], style={"margin":"6px 0"}),
#             ], style={
#                 "flex":1, "minWidth":"420px", "padding":"24px",
#                 "background":"white", "borderRadius":"16px",
#                 "boxShadow":"0 4px 12px rgba(0,0,0,0.08)",
#                 "border":"2px solid #dcfce7"
#             }),

#         ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"8px"}),

#         # -------------------- INDICATORS TOGGLES --------------------
#         html.Div([
#             html.H3("Indicators", style={
#                 "marginBottom":"16px", "fontSize":"22px",
#                 "fontWeight":600, "color":"#1e293b"
#             }),
#             dcc.Checklist(
#                 id="indicators-select",
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
#                 inline=True,
#                 inputStyle={"marginRight":"8px", "cursor":"pointer"},
#                 labelStyle={
#                     "display":"inline-block","marginRight":"16px",
#                     "fontSize":"14px", "color":"#475569", "cursor":"pointer"
#                 }
#             ),
#         ], style={
#             "margin":"24px 0", "padding":"24px",
#             "background":"white", "borderRadius":"16px",
#             "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#         }),

#         html.Div([
#             html.Button(
#                 "Analyze", id="analyze", n_clicks=0,
#                 style={
#                     "padding":"14px 32px","borderRadius":"12px","border":"none",
#                     "fontWeight":600,"cursor":"pointer",
#                     "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#                     "color":"white", "fontSize":"16px",
#                     "boxShadow":"0 4px 12px rgba(102, 126, 234, 0.4)",
#                     "transition":"all 0.3s"
#                 }
#             )
#         ], style={"textAlign":"right","margin":"24px 0 32px"}),

#         # ---------- Results (Drop / Gain) ----------
#         html.Div([
#             html.Div([
#                 html.H2("Drop Analysis", style={
#                     "fontSize":"28px", "fontWeight":700, "color":"#dc2626",
#                     "marginBottom":"20px"
#                 }),
#                 html.Div(id="analysis-output-drop", style={
#                     "border": "2px solid #fee2e2", "borderRadius": "16px",
#                     "padding": "20px", "margin": "10px 0",
#                     "background": "linear-gradient(135deg, #fef2f2 0%, #ffffff 100%)",
#                     "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"
#                 }),
#                 html.Div([
#                     dcc.Graph(id="return-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"white", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.06)"
#                 }),
#                 html.Div([
#                     dcc.Graph(id="bar-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"white", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.06)"
#                 }),
#                 html.Div(id="stats-drop", style={"margin": "24px 0"}),
#                 html.H4("Trade windows (first and last day)", style={
#                     "fontSize":"20px", "fontWeight":600, "color":"#1e293b",
#                     "marginTop":"32px", "marginBottom":"16px"
#                 }),
#                 html.Div(id="trade-windows-drop", style={
#                     "background":"white", "borderRadius":"12px",
#                     "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.06)"
#                 }),
#             ], style={"flex": 1, "minWidth": "420px"}),

#             html.Div([
#                 html.H2("Gain Analysis", style={
#                     "fontSize":"28px", "fontWeight":700, "color":"#16a34a",
#                     "marginBottom":"20px"
#                 }),
#                 html.Div(id="analysis-output-gain", style={
#                     "border": "2px solid #dcfce7", "borderRadius": "16px",
#                     "padding": "20px", "margin": "10px 0",
#                     "background": "linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%)",
#                     "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"
#                 }),
#                 html.Div([
#                     dcc.Graph(id="return-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"white", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.06)"
#                 }),
#                 html.Div([
#                     dcc.Graph(id="bar-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"white", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.06)"
#                 }),
#                 html.Div(id="stats-gain", style={"margin": "24px 0"}),
#                 html.H4("Trade windows (first and last day)", style={
#                     "fontSize":"20px", "fontWeight":600, "color":"#1e293b",
#                     "marginTop":"32px", "marginBottom":"16px"
#                 }),
#                 html.Div(id="trade-windows-gain", style={
#                     "background":"white", "borderRadius":"12px",
#                     "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.06)"
#                 }),
#             ], style={"flex": 1, "minWidth": "420px"}),
#         ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),

#         # ---------- Indicators figure ----------
#         html.H3("Indicator Charts", style={
#             "fontSize":"28px", "fontWeight":700, "color":"#1e293b",
#             "marginTop":"40px", "marginBottom":"20px"
#         }),
#         html.Div([
#             dcc.Graph(id="indicators-figure", config={"displayModeBar": False}, style={"height":"540px"}),
#         ], style={
#             "background":"white", "borderRadius":"16px",
#             "padding":"20px", "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#         }),

#         html.Hr(),
#         html.Div(id="preview", style={
#             "marginTop":"40px", "padding":"24px",
#             "background":"white", "borderRadius":"16px",
#             "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#         }),  # <<< Data Preview lives here (first 10 rows)

#         dcc.Store(id=STORE_RAW),
#         dcc.Store(id=STORE_META),
#     ],
#     style={"maxWidth":"1400px","margin":"0 auto","padding":"32px 24px"})

# # ---------- Cross Index ----------
# def cross_layout():
#     return html.Div(
#         [
#             html.Div([
#                 html.H1("Cross Index Analysis", style={
#                     "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
#                     "color":"#1e293b"
#                 }),
#                 html.P("Compare two indexes side by side with correlation analysis", style={
#                     "fontSize":"16px", "color":"#64748b", "marginBottom":"32px"
#                 }),
#             ]),

#             html.Div([
#                 html.Div([
#                     html.H3("Upload Index A (CSV)", style={
#                         "fontSize":"20px", "fontWeight":600, "color":"#1e293b",
#                         "marginBottom":"16px"
#                     }),
#                     dcc.Upload(
#                         id="uploader-a",
#                         children=html.Div([
#                             html.Div("📁", style={"fontSize":"28px", "marginBottom":"6px"}),
#                             html.Div("Drag & drop or ", style={"fontSize":"15px", "color":"#64748b"}),
#                             html.A("Select CSV", style={"fontSize":"15px", "color":"#667eea", "fontWeight":600, "textDecoration":"underline"})
#                         ]),
#                         style={
#                             "width":"100%","height":"100px",
#                             "borderWidth":"2px","borderStyle":"dashed","borderColor":"#cbd5e1",
#                             "borderRadius":"16px","textAlign":"center",
#                             "margin":"10px 0",
#                             "background":"linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
#                             "display":"flex", "flexDirection":"column", "justifyContent":"center", "alignItems":"center",
#                             "cursor":"pointer", "transition":"all 0.3s"
#                         },
#                         multiple=False, accept=".csv",
#                     ),
#                     html.Div(id="file-msg-a", style={"marginBottom": "6px"}),
#                     html.Div(id="warn-msg-a", style={"marginBottom": "6px"}),
#                     html.Div(id="preview-a"),
#                 ], style={
#                     "flex":1, "minWidth":"420px", "padding":"24px",
#                     "background":"white", "borderRadius":"16px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#                 }),

#                 html.Div([
#                     html.H3("Upload Index B (CSV)", style={
#                         "fontSize":"20px", "fontWeight":600, "color":"#1e293b",
#                         "marginBottom":"16px"
#                     }),
#                     dcc.Upload(
#                         id="uploader-b",
#                         children=html.Div([
#                             html.Div("📁", style={"fontSize":"28px", "marginBottom":"6px"}),
#                             html.Div("Drag & drop or ", style={"fontSize":"15px", "color":"#64748b"}),
#                             html.A("Select CSV", style={"fontSize":"15px", "color":"#667eea", "fontWeight":600, "textDecoration":"underline"})
#                         ]),
#                         style={
#                             "width":"100%","height":"100px",
#                             "borderWidth":"2px","borderStyle":"dashed","borderColor":"#cbd5e1",
#                             "borderRadius":"16px","textAlign":"center",
#                             "margin":"10px 0",
#                             "background":"linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
#                             "display":"flex", "flexDirection":"column", "justifyContent":"center", "alignItems":"center",
#                             "cursor":"pointer", "transition":"all 0.3s"
#                         },
#                         multiple=False, accept=".csv",
#                     ),
#                     html.Div(id="file-msg-b", style={"marginBottom": "6px"}),
#                     html.Div(id="warn-msg-b", style={"marginBottom": "6px"}),
#                     html.Div(id="preview-b"),
#                 ], style={
#                     "flex":1, "minWidth":"420px", "padding":"24px",
#                     "background":"white", "borderRadius":"16px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#                 }),
#             ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"32px"}),

#             html.Hr(),

#             html.Div([
#                 html.H3("Analysis Settings", style={
#                     "fontSize":"24px", "fontWeight":600, "color":"#1e293b",
#                     "marginBottom":"20px"
#                 }),
#                 html.Div([
#                     html.Label("Date Range", style={"fontWeight":"600","marginRight":"8px"}),
#                     dcc.Dropdown(
#                         id="preset-cross",
#                         options=[
#                             {"label":"All","value":"all"},
#                             {"label":"YTD","value":"ytd"},
#                             {"label":"Last 1Y","value":"1y"},
#                             {"label":"Last 3Y","value":"3y"},
#                             {"label":"Last 6M","value":"6m"},
#                             {"label":"Custom","value":"custom"},
#                         ],
#                         value="all", clearable=False,
#                         style={"width":"160px","display":"inline-block","marginRight":"8px"}
#                     ),
#                     dcc.DatePickerRange(
#                         id="date-range-cross",
#                         display_format="YYYY-MM-DD",
#                         minimum_nights=0, clearable=True, persistence=True,
#                         style={"display":"inline-block","marginRight":"8px"}
#                     ),
#                     dcc.Checklist(
#                         id="snap-month-cross",
#                         options=[{"label":" Snap to month", "value":"snap"}],
#                         value=["snap"], inline=True,
#                         style={"display":"inline-block"}
#                     ),
#                 ], style={"marginBottom":"8px"}),

#                 html.Div([
#                     html.Span("Jump to:", style={"marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-year-cross", options=[], placeholder="Year",
#                                  style={"width":"100px","display":"inline-block","marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-month-cross", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                 ], style={"marginBottom":"12px"}),

#                 html.Div([
#                     html.Label("Window size (days) for returns", style={"fontWeight":"600","marginRight":"8px"}),
#                     dcc.Input(id="x-window", type="number", min=1, step=1, value=5,
#                               style={"width":"140px"}),
#                 ], style={"marginBottom":"6px"}),

#                 html.Div([
#                     html.Button(
#                         "Analyze", id="x-analyze", n_clicks=0,
#                         style={
#                             "padding":"14px 32px","borderRadius":"12px","border":"none",
#                             "fontWeight":600,"cursor":"pointer",
#                             "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#                             "color":"white", "fontSize":"16px",
#                             "boxShadow":"0 4px 12px rgba(102, 126, 234, 0.4)",
#                             "transition":"all 0.3s"
#                         }
#                     )
#                 ], style={"textAlign":"right","margin":"24px 0 12px"}),
#             ], style={
#                 "background":"white","border":"none",
#                 "borderRadius":"16px","padding":"24px",
#                 "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#             }),

#             # ---- Results ----
#             html.Div([
#                 html.Div([
#                     dcc.Graph(id="x-line-levels", config={"displayModeBar": False}, style={"height":"360px"}),
#                 ], style={
#                     "background":"white", "borderRadius":"16px",
#                     "padding":"20px", "marginBottom":"24px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#                 }),
#                 html.Div([
#                     dcc.Graph(id="x-scatter-returns", config={"displayModeBar": False}, style={"height":"360px"}),
#                 ], style={
#                     "background":"white", "borderRadius":"16px",
#                     "padding":"20px", "marginBottom":"24px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#                 }),
#                 html.Div([
#                     dcc.Graph(id="x-line-returns", config={"displayModeBar": False}, style={"height":"360px"}),
#                 ], style={
#                     "background":"white", "borderRadius":"16px",
#                     "padding":"20px", "marginBottom":"24px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#                 }),
#                 html.Div(id="x-stats", style={"margin":"24px 0"}),
#                 html.H4("Trade windows (first and last day)", style={
#                     "fontSize":"22px", "fontWeight":600, "color":"#1e293b",
#                     "marginTop":"32px", "marginBottom":"16px"
#                 }),
#                 html.Div(id="x-trade-windows", style={
#                     "background":"white", "borderRadius":"16px",
#                     "padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"
#                 }),
#             ], style={"marginTop":"32px"}),

#             dcc.Store(id=STORE_A),
#             dcc.Store(id=STORE_B),

#             html.Div(dcc.Link("← Back to Home", href="/", style={
#                 "textDecoration":"none", "color":"#667eea", "fontWeight":500,
#                 "fontSize":"16px", "marginTop":"32px", "display":"inline-block"
#             }))
#         ],
#         style={"maxWidth":"1400px","margin":"0 auto","padding":"32px 24px"}
#     )

# # -----------------------------
# # Top-level app layout with router
# # -----------------------------
# app.layout = html.Div(
#     [
#         navbar(),
#         dcc.Location(id="url"),
#         html.Div(id="page-content")
#     ],
#     style={"fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
#            "background":"linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)","minHeight":"100vh","padding":"0"}
# )

# # Router
# @app.callback(Output("page-content", "children"), Input("url", "pathname"))
# def render_page(pathname):
#     if pathname == "/single":
#         return single_layout()
#     elif pathname == "/cross":
#         return cross_layout()
#     else:
#         return home_layout()

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
#         page_size=10, style_table={"overflowX": "auto"},
#         style_cell={"textAlign": "left", "minWidth": "120px"},
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
#     Output("return-chart-drop", "figure"),
#     Output("bar-chart-drop", "figure"),
#     Output("stats-drop", "children"),
#     Output("trade-windows-drop", "children"),
#     # GAIN outputs
#     Output("analysis-output-gain", "children"),
#     Output("return-chart-gain", "figure"),
#     Output("bar-chart-gain", "figure"),
#     Output("stats-gain", "children"),
#     Output("trade-windows-gain", "children"),
#     # INDICATOR figure
#     Output("indicators-figure", "figure"),
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
#         return (no_update,) * 11
#     if not raw_payload:
#         msg = html.Div("Please upload a CSV first.", style={"color": "crimson"})
#         empty = go.Figure()
#         return msg, empty, empty, None, None, msg, empty, empty, None, None, empty

#     try:
#         csv_bytes = base64.b64decode(raw_payload["csv_b64"].encode())
#         df = pd.read_csv(io.BytesIO(csv_bytes))
#     except Exception as e:
#         msg = html.Div(f"Failed to load stored data: {e}", style={"color": "crimson"})
#         empty = go.Figure()
#         return msg, empty, empty, None, None, msg, empty, empty, None, None, empty

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
#             color = "#3b82f6"
#         else:
#             summary = drop_event_analysis(dff, minimum_per_drop=th_frac, windows_size=ws)
#             title = "Drop Event Analysis"
#             label = "Min Drop: "
#             sign = -1
#             color = "#ef4444"

#         (k, v), = summary.items()
#         card = html.Div([
#             html.H3(title, style={"marginTop": 0, "fontSize": "24px", "fontWeight": 700, "color": "#1e293b"}),
#             html.P([
#                 html.Strong("Change over: "), f"{ws} calendar days (weekend-aware) ",
#                 html.Span(" · "),
#                 html.Strong("Range: "), f"{start.date()} → {end.date()} ",
#                 html.Span(" · "),
#                 html.Strong(label), f"{th_pct:.2f}%",
#             ], style={"fontSize": "14px", "color": "#64748b", "marginBottom": "20px"}),
#             html.Div([
#                 html.Div([
#                     html.Div("Events", style={"color": "#64748b", "fontSize": "13px", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
#                     html.Div(str(v["events"]), style={"fontSize": "36px", "fontWeight": 700, "color": color, "marginTop": "8px"}),
#                 ], style={"flex": 1, "textAlign": "center", "padding": "16px", "background": "white", "borderRadius": "12px"}),
#                 html.Div([
#                     html.Div("Probability", style={"color": "#64748b", "fontSize": "13px", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
#                     html.Div(v["probability"], style={"fontSize": "36px", "fontWeight": 700, "color": color, "marginTop": "8px"}),
#                 ], style={"flex": 1, "textAlign": "center", "padding": "16px", "background": "white", "borderRadius": "12px"}),
#             ], style={"display": "flex", "gap": "16px", "marginTop": "12px"}),
#         ], style={"border": "none", "borderRadius": "16px", "padding": "24px", "background": "linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)", "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"})

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
#         line_fig.update_layout(template="plotly_white", margin=dict(t=30, r=10, l=40, b=40),
#                                xaxis_title="Time", yaxis_title="% change",
#                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

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
#             template="plotly_white", title=bar_title + (f"  · N={N}" if N else ""),
#             margin=dict(t=50, r=10, l=40, b=40),
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#             bargap=0.2,
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
#             html.H4("Change summary", style={"margin": "0 0 16px 0", "fontSize": "20px", "fontWeight": 600, "color": "#1e293b"}),
#             html.Ul([html.Li(html.Span([html.Strong(k + ": ", style={"color": "#1e293b"}), v]), style={
#                 "marginBottom": "8px", "fontSize": "14px", "color": "#475569"
#             }) for k, v in stats_list], style={"listStyle": "none", "padding": 0})
#         ], style={"background": "linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)", "border": "none",
#                   "borderRadius": "16px", "padding": "24px", "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"})

#         # Trade windows list
#         trade_table = build_trade_window_table(dff[["datetime","index"]], ws, limit=200)

#         return card, line_fig, bar_fig, stats_view, trade_table, dff

#     want_drop = "drop" in (analysis_types or [])
#     want_gain = "gain" in (analysis_types or [])

#     drop_out = build_outputs("drop",
#                              preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop) \
#                if want_drop else (html.Div("Drop disabled"), go.Figure(), go.Figure(), None, None, None)

#     gain_out = build_outputs("gain",
#                              preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain) \
#                if want_gain else (html.Div("Gain disabled"), go.Figure(), go.Figure(), None, None, None)

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

#     fig_ind.update_layout(
#         template="plotly_white",
#         margin=dict(t=40, r=10, l=40, b=40),
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         title="Indicators (weekend-aware where applicable)"
#     )

#     # Unpack results for return
#     drop_card, drop_line, drop_bar, drop_stats, drop_table, _dff_drop = drop_out
#     gain_card, gain_line, gain_bar, gain_stats, gain_table, _dff_gain = gain_out

#     return (drop_card, drop_line, drop_bar, drop_stats, drop_table,
#             gain_card, gain_line, gain_bar, gain_stats, gain_table,
#             fig_ind)

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
#                 page_size=10, style_table={"overflowX":"auto"},
#                 style_cell={"textAlign":"left","minWidth":"120px"}
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
#                 page_size=10, style_table={"overflowX":"auto"},
#                 style_cell={"textAlign":"left","minWidth":"120px"}
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
#     Output("x-line-levels", "figure"),
#     Output("x-scatter-returns", "figure"),
#     Output("x-line-returns", "figure"),
#     Output("x-stats", "children"),
#     Output("x-trade-windows", "children"),
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
#     empty = go.Figure()
#     if not n_clicks:
#         return empty, empty, empty, None, None
#     if not rawA or not rawB:
#         msg = html.Div("Please upload both Index A and Index B CSVs.", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     # Load A & B
#     try:
#         dfA = pd.read_csv(io.BytesIO(base64.b64decode(rawA["csv_b64"].encode())))
#         dfB = pd.read_csv(io.BytesIO(base64.b64decode(rawB["csv_b64"].encode())))
#     except Exception as e:
#         msg = html.Div(f"Failed to load stored data: {e}", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     for df in (dfA, dfB):
#         df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
#         df["index"] = pd.to_numeric(df["index"], errors="coerce")
#     dfA = dfA.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)
#     dfB = dfB.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)

#     # Determine overall range intersection
#     data_min = max(dfA["datetime"].min(), dfB["datetime"].min())
#     data_max = min(dfA["datetime"].max(), dfB["datetime"].max())
#     if data_min >= data_max:
#         msg = html.Div("No overlapping dates between A and B.", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     snap = ("snap" in (snap_val or []))
#     start, end = compute_range(preset, sd, ed, data_min, data_max, snap)

#     # Slice to range and inner-join on dates for level chart
#     A_in = dfA[(dfA["datetime"]>=start) & (dfA["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"A"})
#     B_in = dfB[(dfB["datetime"]>=start) & (dfB["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"B"})
#     levels = pd.merge(A_in, B_in, on="datetime", how="inner")
#     if levels.empty:
#         msg = html.Div("No overlapping data inside the selected date range.", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     # -------- Chart 1: Levels normalized to 100 at range start --------
#     baseA = levels["A"].iloc[0]
#     baseB = levels["B"].iloc[0]
#     normA = 100 * levels["A"] / baseA
#     normB = 100 * levels["B"] / baseB

#     fig_levels = go.Figure()
#     fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normA, mode="lines", name="Index A (norm. to 100)"))
#     fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normB, mode="lines", name="Index B (norm. to 100)"))
#     fig_levels.update_layout(
#         template="plotly_white", title=f"Both Indexes (normalized) · {start.date()} → {end.date()}",
#         margin=dict(t=50, r=10, l=40, b=40),
#         xaxis_title="Date", yaxis_title="Indexed level (start=100)",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
#         msg = html.Div("Not enough data to compute weekend-aware windowed returns in this range.", style={"color":"crimson"})
#         return fig_levels, empty, empty, msg, None

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
#         template="plotly_white", title=f"Correlation (windowed returns) — {subtitle}",
#         margin=dict(t=60, r=10, l=50, b=50),
#         xaxis_title=f"Index B {win}-day return (%)",
#         yaxis_title=f"Index A {win}-day return (%)"
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
#         template="plotly_white",
#         title=f"{win}-day Returns Over Time · {start.date()} → {end.date()}",
#         margin=dict(t=50, r=10, l=40, b=40),
#         xaxis_title="Date", yaxis_title=f"{win}-day return (%)",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
#             html.H4(name, style={"margin":"0 0 16px 0", "fontSize":"18px", "fontWeight":600, "color":"#1e293b"}),
#             html.Ul([html.Li(html.Span([html.Strong(k + ": ", style={"color":"#1e293b"}), v]), style={
#                 "marginBottom":"8px", "fontSize":"14px", "color":"#475569"
#             }) for k, v in items], style={"listStyle":"none", "padding":0})
#         ], style={"flex":1, "background":"linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)","border":"none",
#                   "borderRadius":"16px","padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"})

#     corr_text = html.Div([
#         html.H4("Relationship", style={"margin":"0 0 12px 0", "fontSize":"18px", "fontWeight":600, "color":"#1e293b"}),
#         html.P(f"Pearson correlation (windowed returns): {corr:.2f}" if np.isfinite(corr) else
#                "Pearson correlation (windowed returns): n/a", style={
#                    "fontSize":"16px", "color":"#475569", "margin":0,
#                    "fontWeight":500 if np.isfinite(corr) else 400
#                })
#     ], style={"flex":1, "background":"linear-gradient(135deg, #fff7ed 0%, #ffffff 100%)","border":"2px solid #fde68a",
#               "borderRadius":"16px","padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.08)"})

#     stats_view = html.Div([
#         html.Div([
#             stats_block("Index A — Stats", rets["retA"]),
#             stats_block("Index B — Stats", rets["retB"]),
#             corr_text
#         ], style={"display":"flex","gap":"12px","flexWrap":"wrap"})
#     ])

#     # -------- Trade windows tables --------
#     tableA = build_trade_window_table(tmpA[["datetime","index"]], win, limit=200)
#     tableB = build_trade_window_table(tmpB[["datetime","index"]], win, limit=200)
#     twin = html.Div([
#         html.Div([html.H5("Index A trade windows"), tableA], style={"flex":1,"minWidth":"380px"}),
#         html.Div([html.H5("Index B trade windows"), tableB], style={"flex":1,"minWidth":"380px"}),
#     ], style={"display":"flex","gap":"16px","flexWrap":"wrap"})

#     return fig_levels, fig_scatter, fig_returns, stats_view, twin


# # Local run (useful for dev & Render health checks)
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8050))
#     app.run_server(host="0.0.0.0", port=port, debug=False)


# =================================================================================================================================================================================================================




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
#         </style>
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

# # Store (Theme)
# STORE_THEME = "store_theme"

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
#     )
#     return table

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

# def navbar(theme="dark"):
#     is_dark = theme == "dark"
#     bg_color = "#0a0a0a" if is_dark else "#ffffff"
#     text_color = "white" if is_dark else "#1e293b"
#     border_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
    
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
            
#             # Right side: Navigation elements and theme toggle
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
#                     "marginRight": "20px", "textDecoration": "none",
#                     "color": text_color, "fontSize": "14px", "fontWeight": 500,
#                     "padding": "6px 12px", "borderRadius": "4px",
#                     "transition": "all 0.2s"
#                 }),
#                 html.Button(
#                     "🌙" if is_dark else "☀️",
#                     id="theme-toggle",
#                     n_clicks=0,
#                     style={
#                         "background": "transparent",
#                         "border": f"1px solid {border_color}",
#                         "color": text_color,
#                         "fontSize": "18px",
#                         "padding": "6px 12px",
#                         "borderRadius": "6px",
#                         "cursor": "pointer",
#                         "transition": "all 0.2s",
#                         "marginLeft": "10px"
#                     }
#                 )
#             ], style={"display": "flex", "alignItems": "center"})
#         ],
#         style={
#             "padding": "14px 32px",
#             "background": bg_color,
#             "display": "flex",
#             "alignItems": "center",
#             "justifyContent": "space-between",
#             "boxShadow": "0 2px 8px rgba(0,0,0,0.3)" if is_dark else "0 2px 8px rgba(0,0,0,0.1)",
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
#     return html.Div([
#         html.Div([
#             html.H1("Single Index Analysis", style={
#                 "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
#                 "color":"inherit"
#             }),
#             html.P("Upload a CSV with two columns: a date column and a numeric index column (headers can be anything).", style={
#                 "fontSize":"16px", "color":"inherit", "opacity":0.8, "marginBottom":"32px"
#             }),
#         ]),

#         dcc.Upload(
#             id="uploader",
#             children=html.Div([
#                 html.Div([
#                     html.Span("Drag and Drop or ", style={"fontSize":"16px", "color":"rgba(255,255,255,0.7)"}),
#                     html.A("Select CSV File", style={"fontSize":"16px", "color":"#00c896", "fontWeight":600, "textDecoration":"underline"})
#                 ], style={"display":"flex", "alignItems":"center", "gap":"8px"}),
#                 html.Span("📁", style={"fontSize":"24px", "marginLeft":"12px", "opacity":0.8, "transition":"all 0.3s"}),
#             ], style={"display":"flex", "alignItems":"center", "justifyContent":"center"}),
#             style={
#                 "width":"100%","height":"100px",
#                 "borderWidth":"2px","borderStyle":"dashed","borderColor":"rgba(0,200,150,0.3)",
#                 "borderRadius":"16px","textAlign":"center","margin":"10px 0",
#                 "background":"rgba(0,200,150,0.05)",
#                 "transition":"all 0.3s", "cursor":"pointer",
#                 "display":"flex", "flexDirection":"row", "justifyContent":"center", "alignItems":"center"
#             },
#             multiple=False, accept=".csv",
#         ),

#         html.Div(id="file-msg", style={"marginBottom": "8px"}),
#         html.Div(id="warn-msg", style={"marginBottom": "8px"}),

#         html.Div([
#             html.Label("Analysis Type(s)", style={
#                 "fontWeight": "600", "fontSize":"16px", "color":"inherit",
#                 "marginBottom":"12px", "display":"block"
#             }),
#             dcc.Checklist(
#                 id="analysis-types",
#                 options=[{"label": " Drop", "value": "drop"},
#                          {"label": " Gain", "value": "gain"}],
#                 value=["drop", "gain"], inline=True,
#                 inputStyle={"marginRight": "8px", "cursor":"pointer"},
#                 labelStyle={
#                     "display": "inline-block", "marginRight": "24px",
#                     "fontSize":"15px", "color":"#475569", "cursor":"pointer"
#                 },
#             ),
#         ], style={
#             "marginBottom": "24px", "padding":"20px",
#             "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#             "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#             "border":"1px solid rgba(255,255,255,0.1)"
#         }),

#         # Controls row: Drop (left) & Gain (right)
#         html.Div([

#             # -------------------- DROP CONTROLS --------------------
#             html.Div([
#                 html.H3("Drop Options", style={
#                     "marginBottom": "16px", "fontSize":"22px",
#                     "fontWeight":600, "color":"#ef4444"
#                 }),

#                 # Date range + Jump to
#                 html.Div([
#                     html.Label("Date Range", style={"fontWeight": "600"}),
#                     dcc.Dropdown(
#                         id="preset-drop",
#                         options=[
#                             {"label":"All","value":"all"},
#                             {"label":"YTD","value":"ytd"},
#                             {"label":"Last 1Y","value":"1y"},
#                             {"label":"Last 3Y","value":"3y"},
#                             {"label":"Last 6M","value":"6m"},
#                             {"label":"Custom","value":"custom"},
#                         ],
#                         value="all", clearable=False,
#                         style={"width":"180px","marginRight":"8px","display":"inline-block"}
#                     ),
#                     dcc.DatePickerRange(
#                         id="date-range-drop",
#                         display_format="YYYY-MM-DD",
#                         minimum_nights=0, clearable=True, persistence=True,
#                         style={"display":"inline-block"}
#                     ),
#                     dcc.Checklist(
#                         id="snap-month-drop",
#                         options=[{"label":" Snap to month", "value":"snap"}],
#                         value=["snap"], inline=True,
#                         style={"marginLeft":"10px", "display":"inline-block"}
#                     ),
#                 ], style={"margin":"6px 4px 4px 0"}),

#                 html.Div([
#                     html.Span("Jump to:", style={"marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-year-drop", options=[], placeholder="Year",
#                                  style={"width":"100px","display":"inline-block","marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-month-drop", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                 ], style={"marginBottom":"8px"}),

#                 html.Div([
#                     html.Label("Change over (days)", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="window-size-drop",
#                         options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
#                                  {"label": "7", "value": 7}, {"label": "10", "value": 10}],
#                         value=5, inline=True
#                     ),
#                     dcc.Input(
#                         id="window-size-input-drop", type="number", min=1, step=1,
#                         placeholder="custom", style={"marginLeft":"8px","width":"100px"}
#                     )
#                 ], style={"margin":"6px 0"}),

#                 html.Div([
#                     html.Label("Min % Threshold", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="min-threshold-drop",
#                         options=[{"label":"1%","value":1},{"label":"3%","value":3},
#                                  {"label":"5%","value":5},{"label":"10%","value":10}],
#                         value=3, inline=True
#                     ),
#                     dcc.Input(
#                         id="min-threshold-input-drop", type="number", min=0, max=100, step=0.01,
#                         placeholder="e.g. 2.7", style={"marginLeft":"8px","width":"120px"}
#                     )
#                 ], style={"margin":"6px 0"}),
#             ], style={
#                 "flex":1, "minWidth":"420px", "padding":"24px",
#                 "background":"rgba(239,68,68,0.08)", "borderRadius":"16px",
#                 "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                 "border":"1px solid rgba(239,68,68,0.3)"
#             }),

#             # -------------------- GAIN CONTROLS --------------------
#             html.Div([
#                 html.H3("Gain Options", style={
#                     "marginBottom": "16px", "fontSize":"22px",
#                     "fontWeight":600, "color":"#22c55e"
#                 }),

#                 html.Div([
#                     html.Label("Date Range", style={"fontWeight": "600"}),
#                     dcc.Dropdown(
#                         id="preset-gain",
#                         options=[
#                             {"label":"All","value":"all"},
#                             {"label":"YTD","value":"ytd"},
#                             {"label":"Last 1Y","value":"1y"},
#                             {"label":"Last 3Y","value":"3y"},
#                             {"label":"Last 6M","value":"6m"},
#                             {"label":"Custom","value":"custom"},
#                         ],
#                         value="all", clearable=False,
#                         style={"width":"180px","marginRight":"8px","display":"inline-block"}
#                     ),
#                     dcc.DatePickerRange(
#                         id="date-range-gain",
#                         display_format="YYYY-MM-DD",
#                         minimum_nights=0, clearable=True, persistence=True,
#                         style={"display":"inline-block"}
#                     ),
#                     dcc.Checklist(
#                         id="snap-month-gain",
#                         options=[{"label":" Snap to month", "value":"snap"}],
#                         value=["snap"], inline=True,
#                         style={"marginLeft":"10px", "display":"inline-block"}
#                     )
#                 ], style={"margin":"6px 4px 4px 0"}),

#                 html.Div([
#                     html.Span("Jump to:", style={"marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-year-gain", options=[], placeholder="Year",
#                                  style={"width":"100px","display":"inline-block","marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-month-gain", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                 ], style={"marginBottom":"8px"}),

#                 html.Div([
#                     html.Label("Change over (days)", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="window-size-gain",
#                         options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
#                                  {"label": "7", "value": 7}, {"label": "10", "value": 10}],
#                         value=5, inline=True
#                     ),
#                     dcc.Input(
#                         id="window-size-input-gain", type="number", min=1, step=1,
#                         placeholder="custom", style={"marginLeft":"8px","width":"100px"}
#                     )
#                 ], style={"margin":"6px 0"}),

#                 html.Div([
#                     html.Label("Min % Threshold", style={"fontWeight": "600"}),
#                     dcc.RadioItems(
#                         id="min-threshold-gain",
#                         options=[{"label":"1%","value":1},{"label":"3%","value":3},
#                                  {"label":"5%","value":5},{"label":"10%","value":10}],
#                         value=3, inline=True
#                     ),
#                     dcc.Input(
#                         id="min-threshold-input-gain", type="number", min=0, max=100, step=0.01,
#                         placeholder="e.g. 2.7", style={"marginLeft":"8px","width":"120px"}
#                     )
#                 ], style={"margin":"6px 0"}),
#             ], style={
#                 "flex":1, "minWidth":"420px", "padding":"24px",
#                 "background":"rgba(34,197,94,0.08)", "borderRadius":"16px",
#                 "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                 "border":"1px solid rgba(34,197,94,0.3)"
#             }),

#         ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"8px"}),

#         # -------------------- INDICATORS TOGGLES --------------------
#         html.Div([
#             html.H3("Indicators", style={
#                 "marginBottom":"16px", "fontSize":"22px",
#                 "fontWeight":600, "color":"#1e293b"
#             }),
#             dcc.Checklist(
#                 id="indicators-select",
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
#                 inline=True,
#                 inputStyle={"marginRight":"8px", "cursor":"pointer"},
#                 labelStyle={
#                     "display":"inline-block","marginRight":"16px",
#                     "fontSize":"14px", "color":"#475569", "cursor":"pointer"
#                 }
#             ),
#         ], style={
#             "margin":"24px 0", "padding":"24px",
#             "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#             "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#             "border":"1px solid rgba(255,255,255,0.1)"
#         }),

#         html.Div([
#             html.Button(
#                 "Analyze", id="analyze", n_clicks=0,
#                 style={
#                     "padding":"14px 32px","borderRadius":"12px","border":"none",
#                     "fontWeight":600,"cursor":"pointer",
#                     "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#                     "color":"white", "fontSize":"16px",
#                     "boxShadow":"0 4px 12px rgba(102, 126, 234, 0.4)",
#                     "transition":"all 0.3s"
#                 }
#             )
#         ], style={"textAlign":"right","margin":"24px 0 32px"}),

#         # ---------- Results (Drop / Gain) ----------
#         html.Div([
#             html.Div([
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
#                 html.Div([
#                 dcc.Graph(id="return-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#                 html.Div([
#                 dcc.Graph(id="bar-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#                 html.Div(id="stats-drop", style={"margin": "24px 0"}),
#                 html.H4("Trade windows (first and last day)", style={
#                     "fontSize":"20px", "fontWeight":600, "color":"inherit",
#                     "marginTop":"32px", "marginBottom":"16px"
#                 }),
#                 html.Div(id="trade-windows-drop", style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#                     "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
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
#                 html.Div([
#                 dcc.Graph(id="return-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#                 html.Div([
#                 dcc.Graph(id="bar-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
#                 ], style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#                     "padding":"16px", "marginBottom":"16px",
#                     "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#                 html.Div(id="stats-gain", style={"margin": "24px 0"}),
#                 html.H4("Trade windows (first and last day)", style={
#                     "fontSize":"20px", "fontWeight":600, "color":"inherit",
#                     "marginTop":"32px", "marginBottom":"16px"
#                 }),
#                 html.Div(id="trade-windows-gain", style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
#                     "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#             ], style={"flex": 1, "minWidth": "420px"}),
#         ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),

#         # ---------- Indicators figure ----------
#         html.H3("Indicator Charts", style={
#             "fontSize":"28px", "fontWeight":700, "color":"inherit",
#             "marginTop":"40px", "marginBottom":"20px"
#         }),
#         html.Div([
#         dcc.Graph(id="indicators-figure", config={"displayModeBar": False}, style={"height":"540px"}),
#         ], style={
#             "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#             "padding":"20px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#             "border":"1px solid rgba(255,255,255,0.1)"
#         }),

#         html.Hr(),
#         html.Div(id="preview", style={
#             "marginTop":"40px", "padding":"24px",
#             "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#             "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#             "border":"1px solid rgba(255,255,255,0.1)"
#         }),  # <<< Data Preview lives here (first 10 rows)

#         dcc.Store(id=STORE_RAW),
#         dcc.Store(id=STORE_META),
#     ],
#     style={"maxWidth":"1400px","margin":"0 auto","padding":"32px 24px", "marginTop":"0"})

# # ---------- Cross Index ----------
# def cross_layout():
#     return html.Div(
#         [
#             html.Div([
#                 html.H1("Cross Index Analysis", style={
#                     "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
#                     "color":"inherit"
#                 }),
#                 html.P("Compare two indexes side by side with correlation analysis", style={
#                     "fontSize":"16px", "color":"inherit", "opacity":0.8, "marginBottom":"32px"
#                 }),
#             ]),

#             html.Div([
#                 html.Div([
#                 html.H3("Upload Index A (CSV)", style={
#                     "fontSize":"20px", "fontWeight":600, "color":"inherit",
#                     "marginBottom":"16px"
#                 }),
#                     dcc.Upload(
#                         id="uploader-a",
#                         children=html.Div([
#                             html.Div([
#                                 html.Span("Drag & drop or ", style={"fontSize":"15px", "color":"rgba(255,255,255,0.7)"}),
#                                 html.A("Select CSV", style={"fontSize":"15px", "color":"#00c896", "fontWeight":600, "textDecoration":"underline"})
#                             ], style={"display":"flex", "alignItems":"center", "gap":"8px"}),
#                             html.Span("📁", style={"fontSize":"24px", "marginLeft":"12px", "opacity":0.8, "transition":"all 0.3s"}),
#                         ], style={"display":"flex", "alignItems":"center", "justifyContent":"center"}),
#                         style={
#                             "width":"100%","height":"100px",
#                             "borderWidth":"2px","borderStyle":"dashed","borderColor":"rgba(0,200,150,0.3)",
#                             "borderRadius":"16px","textAlign":"center",
#                             "margin":"10px 0",
#                             "background":"rgba(0,200,150,0.05)",
#                             "display":"flex", "flexDirection":"row", "justifyContent":"center", "alignItems":"center",
#                             "cursor":"pointer", "transition":"all 0.3s"
#                         },
#                         multiple=False, accept=".csv",
#                     ),
#                     html.Div(id="file-msg-a", style={"marginBottom": "6px"}),
#                     html.Div(id="warn-msg-a", style={"marginBottom": "6px"}),
#                     html.Div(id="preview-a"),
#                 ], style={
#                     "flex":1, "minWidth":"420px", "padding":"24px",
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),

#                 html.Div([
#                 html.H3("Upload Index B (CSV)", style={
#                     "fontSize":"20px", "fontWeight":600, "color":"inherit",
#                     "marginBottom":"16px"
#                 }),
#                     dcc.Upload(
#                         id="uploader-b",
#                         children=html.Div([
#                             html.Div([
#                                 html.Span("Drag & drop or ", style={"fontSize":"15px", "color":"rgba(255,255,255,0.7)"}),
#                                 html.A("Select CSV", style={"fontSize":"15px", "color":"#00c896", "fontWeight":600, "textDecoration":"underline"})
#                             ], style={"display":"flex", "alignItems":"center", "gap":"8px"}),
#                             html.Span("📁", style={"fontSize":"24px", "marginLeft":"12px", "opacity":0.8, "transition":"all 0.3s"}),
#                         ], style={"display":"flex", "alignItems":"center", "justifyContent":"center"}),
#                         style={
#                             "width":"100%","height":"100px",
#                             "borderWidth":"2px","borderStyle":"dashed","borderColor":"rgba(0,200,150,0.3)",
#                             "borderRadius":"16px","textAlign":"center",
#                             "margin":"10px 0",
#                             "background":"rgba(0,200,150,0.05)",
#                             "display":"flex", "flexDirection":"row", "justifyContent":"center", "alignItems":"center",
#                             "cursor":"pointer", "transition":"all 0.3s"
#                         },
#                         multiple=False, accept=".csv",
#                     ),
#                     html.Div(id="file-msg-b", style={"marginBottom": "6px"}),
#                     html.Div(id="warn-msg-b", style={"marginBottom": "6px"}),
#                     html.Div(id="preview-b"),
#                 ], style={
#                     "flex":1, "minWidth":"420px", "padding":"24px",
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#             ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"32px"}),

#             html.Hr(),

#             html.Div([
#                 html.H3("Analysis Settings", style={
#                     "fontSize":"24px", "fontWeight":600, "color":"inherit",
#                     "marginBottom":"20px"
#                 }),
#                 html.Div([
#                     html.Label("Date Range", style={"fontWeight":"600","marginRight":"8px"}),
#                     dcc.Dropdown(
#                         id="preset-cross",
#                         options=[
#                             {"label":"All","value":"all"},
#                             {"label":"YTD","value":"ytd"},
#                             {"label":"Last 1Y","value":"1y"},
#                             {"label":"Last 3Y","value":"3y"},
#                             {"label":"Last 6M","value":"6m"},
#                             {"label":"Custom","value":"custom"},
#                         ],
#                         value="all", clearable=False,
#                         style={"width":"160px","display":"inline-block","marginRight":"8px"}
#                     ),
#                     dcc.DatePickerRange(
#                         id="date-range-cross",
#                         display_format="YYYY-MM-DD",
#                         minimum_nights=0, clearable=True, persistence=True,
#                         style={"display":"inline-block","marginRight":"8px"}
#                     ),
#                     dcc.Checklist(
#                         id="snap-month-cross",
#                         options=[{"label":" Snap to month", "value":"snap"}],
#                         value=["snap"], inline=True,
#                         style={"display":"inline-block"}
#                     ),
#                 ], style={"marginBottom":"8px"}),

#                 html.Div([
#                     html.Span("Jump to:", style={"marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-year-cross", options=[], placeholder="Year",
#                                  style={"width":"100px","display":"inline-block","marginRight":"6px"}),
#                     dcc.Dropdown(id="jump-month-cross", options=MONTH_OPTIONS, placeholder="Month",
#                                  style={"width":"120px","display":"inline-block"}),
#                 ], style={"marginBottom":"12px"}),

#                 html.Div([
#                     html.Label("Window size (days) for returns", style={"fontWeight":"600","marginRight":"8px"}),
#                     dcc.Input(id="x-window", type="number", min=1, step=1, value=5,
#                               style={"width":"140px"}),
#                 ], style={"marginBottom":"6px"}),

#                 html.Div([
#                     html.Button(
#                         "Analyze", id="x-analyze", n_clicks=0,
#                         style={
#                             "padding":"14px 32px","borderRadius":"12px","border":"none",
#                             "fontWeight":600,"cursor":"pointer",
#                             "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#                             "color":"white", "fontSize":"16px",
#                             "boxShadow":"0 4px 12px rgba(102, 126, 234, 0.4)",
#                             "transition":"all 0.3s"
#                         }
#                     )
#                 ], style={"textAlign":"right","margin":"24px 0 12px"}),
#             ], style={
#                 "background":"rgba(255,255,255,0.05)","border":"1px solid rgba(255,255,255,0.1)",
#                 "borderRadius":"16px","padding":"24px",
#                 "boxShadow":"0 4px 12px rgba(0,0,0,0.3)"
#             }),

#             # ---- Results ----
#             html.Div([
#             html.Div([
#                 dcc.Graph(id="x-line-levels", config={"displayModeBar": False}, style={"height":"360px"}),
#                 ], style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#                     "padding":"20px", "marginBottom":"24px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#                 html.Div([
#                 dcc.Graph(id="x-scatter-returns", config={"displayModeBar": False}, style={"height":"360px"}),
#                 ], style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#                     "padding":"20px", "marginBottom":"24px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#                 html.Div([
#                 dcc.Graph(id="x-line-returns", config={"displayModeBar": False}, style={"height":"360px"}),
#                 ], style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#                     "padding":"20px", "marginBottom":"24px",
#                     "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#                 html.Div(id="x-stats", style={"margin":"24px 0"}),
#                 html.H4("Trade windows (first and last day)", style={
#                     "fontSize":"22px", "fontWeight":600, "color":"inherit",
#                     "marginTop":"32px", "marginBottom":"16px"
#                 }),
#                 html.Div(id="x-trade-windows", style={
#                     "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
#                     "padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
#                     "border":"1px solid rgba(255,255,255,0.1)"
#                 }),
#             ], style={"marginTop":"32px"}),

#             dcc.Store(id=STORE_A),
#             dcc.Store(id=STORE_B),

#             html.Div(dcc.Link("← Back to Home", href="/", style={
#                 "textDecoration":"none", "color":"#00c896", "fontWeight":500,
#                 "fontSize":"16px", "marginTop":"32px", "display":"inline-block"
#             }))
#         ],
#         style={"maxWidth":"1400px","margin":"0 auto","padding":"32px 24px"}
#     )

# # -----------------------------
# # Top-level app layout with router
# # -----------------------------
# app.layout = html.Div(
#     [
#         html.Div(id="navbar-container"),
#         dcc.Location(id="url"),
#         html.Div(id="page-content"),
#         dcc.Store(id=STORE_THEME, data="dark", storage_type="memory")
#     ],
#     id="app-container",
#     style={"fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
#            "minHeight":"100vh","padding":"0", "margin":"0",
#            "transition": "background-color 0.3s ease, color 0.3s ease"}
# )

# # Theme toggle callback
# @app.callback(
#     Output(STORE_THEME, "data"),
#     Input("theme-toggle", "n_clicks"),
#     State(STORE_THEME, "data"),
#     prevent_initial_call=True
# )
# def toggle_theme(n_clicks, current_theme):
#     # Handle first click and subsequent clicks
#     if current_theme is None or current_theme == "":
#         return "light"  # If no theme set, toggle to light
#     # Toggle between dark and light
#     return "light" if current_theme == "dark" else "dark"

# # Theme and Navbar callbacks
# @app.callback(
#     Output("navbar-container", "children"),
#     Output("app-container", "style"),
#     Input(STORE_THEME, "data")
# )
# def update_navbar_and_theme(theme):
#     if theme is None:
#         theme = "dark"  # Default to dark if theme is None
#     is_dark = theme == "dark"
#     bg_style = {
#         "fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
#         "minHeight":"100vh","padding":"0", "margin":"0",
#         "background": "#0a0a0a" if is_dark else "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
#         "color": "white" if is_dark else "#1e293b",
#         "transition": "background-color 0.3s ease, color 0.3s ease"
#     }
#     return navbar(theme), bg_style

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
#     Output("return-chart-drop", "figure"),
#     Output("bar-chart-drop", "figure"),
#     Output("stats-drop", "children"),
#     Output("trade-windows-drop", "children"),
#     # GAIN outputs
#     Output("analysis-output-gain", "children"),
#     Output("return-chart-gain", "figure"),
#     Output("bar-chart-gain", "figure"),
#     Output("stats-gain", "children"),
#     Output("trade-windows-gain", "children"),
#     # INDICATOR figure
#     Output("indicators-figure", "figure"),
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
#         return (no_update,) * 11
#     if not raw_payload:
#         msg = html.Div("Please upload a CSV first.", style={"color": "crimson"})
#         empty = go.Figure()
#         return msg, empty, empty, None, None, msg, empty, empty, None, None, empty

#     try:
#         csv_bytes = base64.b64decode(raw_payload["csv_b64"].encode())
#         df = pd.read_csv(io.BytesIO(csv_bytes))
#     except Exception as e:
#         msg = html.Div(f"Failed to load stored data: {e}", style={"color": "crimson"})
#         empty = go.Figure()
#         return msg, empty, empty, None, None, msg, empty, empty, None, None, empty

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
#         line_fig.update_layout(template="plotly_white", margin=dict(t=30, r=10, l=40, b=40),
#                                xaxis_title="Time", yaxis_title="% change",
#                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

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
#             template="plotly_white", title=bar_title + (f"  · N={N}" if N else ""),
#             margin=dict(t=50, r=10, l=40, b=40),
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#             bargap=0.2,
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
#         trade_table = build_trade_window_table(dff[["datetime","index"]], ws, limit=200)

#         return card, line_fig, bar_fig, stats_view, trade_table, dff

#     want_drop = "drop" in (analysis_types or [])
#     want_gain = "gain" in (analysis_types or [])

#     drop_out = build_outputs("drop",
#                              preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop) \
#                if want_drop else (html.Div("Drop disabled"), go.Figure(), go.Figure(), None, None, None)

#     gain_out = build_outputs("gain",
#                              preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain) \
#                if want_gain else (html.Div("Gain disabled"), go.Figure(), go.Figure(), None, None, None)

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

#     fig_ind.update_layout(
#         template="plotly_white",
#         margin=dict(t=40, r=10, l=40, b=40),
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         title="Indicators (weekend-aware where applicable)"
#     )

#     # Unpack results for return
#     drop_card, drop_line, drop_bar, drop_stats, drop_table, _dff_drop = drop_out
#     gain_card, gain_line, gain_bar, gain_stats, gain_table, _dff_gain = gain_out

#     return (drop_card, drop_line, drop_bar, drop_stats, drop_table,
#             gain_card, gain_line, gain_bar, gain_stats, gain_table,
#             fig_ind)

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
#     Output("x-line-levels", "figure"),
#     Output("x-scatter-returns", "figure"),
#     Output("x-line-returns", "figure"),
#     Output("x-stats", "children"),
#     Output("x-trade-windows", "children"),
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
#     empty = go.Figure()
#     if not n_clicks:
#         return empty, empty, empty, None, None
#     if not rawA or not rawB:
#         msg = html.Div("Please upload both Index A and Index B CSVs.", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     # Load A & B
#     try:
#         dfA = pd.read_csv(io.BytesIO(base64.b64decode(rawA["csv_b64"].encode())))
#         dfB = pd.read_csv(io.BytesIO(base64.b64decode(rawB["csv_b64"].encode())))
#     except Exception as e:
#         msg = html.Div(f"Failed to load stored data: {e}", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     for df in (dfA, dfB):
#         df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
#         df["index"] = pd.to_numeric(df["index"], errors="coerce")
#     dfA = dfA.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)
#     dfB = dfB.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)

#     # Determine overall range intersection
#     data_min = max(dfA["datetime"].min(), dfB["datetime"].min())
#     data_max = min(dfA["datetime"].max(), dfB["datetime"].max())
#     if data_min >= data_max:
#         msg = html.Div("No overlapping dates between A and B.", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     snap = ("snap" in (snap_val or []))
#     start, end = compute_range(preset, sd, ed, data_min, data_max, snap)

#     # Slice to range and inner-join on dates for level chart
#     A_in = dfA[(dfA["datetime"]>=start) & (dfA["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"A"})
#     B_in = dfB[(dfB["datetime"]>=start) & (dfB["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"B"})
#     levels = pd.merge(A_in, B_in, on="datetime", how="inner")
#     if levels.empty:
#         msg = html.Div("No overlapping data inside the selected date range.", style={"color":"crimson"})
#         return empty, empty, empty, msg, None

#     # -------- Chart 1: Levels normalized to 100 at range start --------
#     baseA = levels["A"].iloc[0]
#     baseB = levels["B"].iloc[0]
#     normA = 100 * levels["A"] / baseA
#     normB = 100 * levels["B"] / baseB

#     fig_levels = go.Figure()
#     fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normA, mode="lines", name="Index A (norm. to 100)"))
#     fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normB, mode="lines", name="Index B (norm. to 100)"))
#     fig_levels.update_layout(
#         template="plotly_white", title=f"Both Indexes (normalized) · {start.date()} → {end.date()}",
#         margin=dict(t=50, r=10, l=40, b=40),
#         xaxis_title="Date", yaxis_title="Indexed level (start=100)",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
#         msg = html.Div("Not enough data to compute weekend-aware windowed returns in this range.", style={"color":"crimson"})
#         return fig_levels, empty, empty, msg, None

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
#         template="plotly_white", title=f"Correlation (windowed returns) — {subtitle}",
#         margin=dict(t=60, r=10, l=50, b=50),
#         xaxis_title=f"Index B {win}-day return (%)",
#         yaxis_title=f"Index A {win}-day return (%)"
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
#         template="plotly_white",
#         title=f"{win}-day Returns Over Time · {start.date()} → {end.date()}",
#         margin=dict(t=50, r=10, l=40, b=40),
#         xaxis_title="Date", yaxis_title=f"{win}-day return (%)",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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

#     # -------- Trade windows tables --------
#     tableA = build_trade_window_table(tmpA[["datetime","index"]], win, limit=200)
#     tableB = build_trade_window_table(tmpB[["datetime","index"]], win, limit=200)
#     twin = html.Div([
#         html.Div([html.H5("Index A trade windows"), tableA], style={"flex":1,"minWidth":"380px"}),
#         html.Div([html.H5("Index B trade windows"), tableB], style={"flex":1,"minWidth":"380px"}),
#     ], style={"display":"flex","gap":"16px","flexWrap":"wrap"})

#     return fig_levels, fig_scatter, fig_returns, stats_view, twin


# # Local run (useful for dev & Render health checks)
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8050))
#     app.run_server(host="0.0.0.0", port=port, debug=False)



# ================================================================================================================================================================================================================

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
        </style>
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

# Store (Theme)
STORE_THEME = "store_theme"
STORE_THEME_CLICKS = "store_theme_clicks"

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
    )
    return table

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

def navbar(theme="dark"):
    is_dark = theme == "dark"
    bg_color = "#0a0a0a" if is_dark else "#ffffff"
    text_color = "white" if is_dark else "#1e293b"
    border_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
    
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
            
            # Right side: Navigation elements and theme toggle
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
                html.Button(
                    "🌙" if is_dark else "☀️",
                    id="theme-toggle",
                    style={
                        "background": "transparent",
                        "border": f"1px solid {border_color}",
                        "color": text_color,
                        "fontSize": "18px",
                        "padding": "6px 12px",
                        "borderRadius": "6px",
                        "cursor": "pointer",
                        "transition": "all 0.2s",
                        "marginLeft": "10px"
                    }
                )
            ], style={"display": "flex", "alignItems": "center"})
        ],
        style={
            "padding": "14px 32px",
            "background": bg_color,
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.3)" if is_dark else "0 2px 8px rgba(0,0,0,0.1)",
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
                html.P("Choose a workflow to begin your analysis:", style={
                    "fontSize":"18px", "color":"#64748b", "marginBottom":"40px"
                }),
            ], style={"textAlign":"center", "marginBottom":"48px"}),
            html.Div(
                [
                    dcc.Link(
                        html.Div(
                            [
                                html.Div("📊", style={"fontSize":"48px", "marginBottom":"16px"}),
                                html.H3("Single Index", style={"margin":"0 0 8px 0", "fontSize":"24px", "fontWeight":600}),
                                html.P("Analyze one index with comprehensive indicators", style={
                                    "margin":0, "fontSize":"14px", "opacity":0.9
                                })
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
                                html.H3("Cross Index", style={"margin":"0 0 8px 0", "fontSize":"24px", "fontWeight":600}),
                                html.P("Compare two indexes side by side", style={
                                    "margin":0, "fontSize":"14px", "opacity":0.9
                                })
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
                    "alignItems":"center",
                    "flexWrap":"wrap",
                    "gap":"24px"
                }
            ),
        ],
        style={"maxWidth":"1200px","margin":"0 auto","padding":"48px 24px", "marginTop":"0"}
    )

# ---------- Single Index (FULL) ----------
def single_layout():
    return html.Div([
        html.Div([
            html.H1("Single Index Analysis", style={
                "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
                "color":"inherit"
            }),
            html.P("Upload a CSV with two columns: a date column and a numeric index column (headers can be anything).", style={
                "fontSize":"16px", "color":"inherit", "opacity":0.8, "marginBottom":"32px"
            }),
        ]),

        dcc.Upload(
            id="uploader",
            children=html.Div([
                html.Div([
                    html.Span("Drag and Drop or ", style={"fontSize":"16px", "color":"rgba(255,255,255,0.7)"}),
                    html.A("Select CSV File", style={"fontSize":"16px", "color":"#00c896", "fontWeight":600, "textDecoration":"underline"})
                ], style={"display":"flex", "alignItems":"center", "gap":"8px"}),
                html.Span("📁", style={"fontSize":"24px", "marginLeft":"12px", "opacity":0.8, "transition":"all 0.3s"}),
            ], style={"display":"flex", "alignItems":"center", "justifyContent":"center"}),
            style={
                "width":"100%","height":"100px",
                "borderWidth":"2px","borderStyle":"dashed","borderColor":"rgba(0,200,150,0.3)",
                "borderRadius":"16px","textAlign":"center","margin":"10px 0",
                "background":"rgba(0,200,150,0.05)",
                "transition":"all 0.3s", "cursor":"pointer",
                "display":"flex", "flexDirection":"row", "justifyContent":"center", "alignItems":"center"
            },
            multiple=False, accept=".csv",
        ),

        html.Div(id="file-msg", style={"marginBottom": "8px"}),
        html.Div(id="warn-msg", style={"marginBottom": "8px"}),

        html.Div([
            html.Label("Analysis Type(s)", style={
                "fontWeight": "600", "fontSize":"16px", "color":"inherit",
                "marginBottom":"12px", "display":"block"
            }),
            dcc.Checklist(
                id="analysis-types",
                options=[{"label": " Drop", "value": "drop"},
                         {"label": " Gain", "value": "gain"}],
                value=["drop", "gain"], inline=True,
                inputStyle={"marginRight": "8px", "cursor":"pointer"},
                labelStyle={
                    "display": "inline-block", "marginRight": "24px",
                    "fontSize":"15px", "color":"#475569", "cursor":"pointer"
                },
            ),
        ], style={
            "marginBottom": "24px", "padding":"20px",
            "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
            "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
            "border":"1px solid rgba(255,255,255,0.1)"
        }),

        # Controls row: Drop (left) & Gain (right)
        html.Div([

            # -------------------- DROP CONTROLS --------------------
            html.Div([
                html.H3("Drop Options", style={
                    "marginBottom": "16px", "fontSize":"22px",
                    "fontWeight":600, "color":"#ef4444"
                }),

                # Date range + Jump to
                html.Div([
                    html.Label("Date Range", style={"fontWeight": "600"}),
                    dcc.Dropdown(
                        id="preset-drop",
                        options=[
                            {"label":"All","value":"all"},
                            {"label":"YTD","value":"ytd"},
                            {"label":"Last 1Y","value":"1y"},
                            {"label":"Last 3Y","value":"3y"},
                            {"label":"Last 6M","value":"6m"},
                            {"label":"Custom","value":"custom"},
                        ],
                        value="all", clearable=False,
                        style={"width":"180px","marginRight":"8px","display":"inline-block"}
                    ),
                    dcc.DatePickerRange(
                        id="date-range-drop",
                        display_format="YYYY-MM-DD",
                        minimum_nights=0, clearable=True, persistence=True,
                        style={"display":"inline-block"}
                    ),
                    dcc.Checklist(
                        id="snap-month-drop",
                        options=[{"label":" Snap to month", "value":"snap"}],
                        value=["snap"], inline=True,
                        style={"marginLeft":"10px", "display":"inline-block"}
                    ),
                ], style={"margin":"6px 4px 4px 0"}),

                html.Div([
                    html.Span("Jump to:", style={"marginRight":"6px"}),
                    dcc.Dropdown(id="jump-year-drop", options=[], placeholder="Year",
                                 style={"width":"100px","display":"inline-block","marginRight":"6px"}),
                    dcc.Dropdown(id="jump-month-drop", options=MONTH_OPTIONS, placeholder="Month",
                                 style={"width":"120px","display":"inline-block"}),
                ], style={"marginBottom":"8px"}),

                html.Div([
                    html.Label("Change over (days)", style={"fontWeight": "600"}),
                    dcc.RadioItems(
                        id="window-size-drop",
                        options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
                                 {"label": "7", "value": 7}, {"label": "10", "value": 10}],
                        value=5, inline=True
                    ),
                    dcc.Input(
                        id="window-size-input-drop", type="number", min=1, step=1,
                        placeholder="custom", style={"marginLeft":"8px","width":"100px"}
                    )
                ], style={"margin":"6px 0"}),

                html.Div([
                    html.Label("Min % Threshold", style={"fontWeight": "600"}),
                    dcc.RadioItems(
                        id="min-threshold-drop",
                        options=[{"label":"1%","value":1},{"label":"3%","value":3},
                                 {"label":"5%","value":5},{"label":"10%","value":10}],
                        value=3, inline=True
                    ),
                    dcc.Input(
                        id="min-threshold-input-drop", type="number", min=0, max=100, step=0.01,
                        placeholder="e.g. 2.7", style={"marginLeft":"8px","width":"120px"}
                    )
                ], style={"margin":"6px 0"}),
            ], style={
                "flex":1, "minWidth":"420px", "padding":"24px",
                "background":"rgba(239,68,68,0.08)", "borderRadius":"16px",
                "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                "border":"1px solid rgba(239,68,68,0.3)"
            }),

            # -------------------- GAIN CONTROLS --------------------
            html.Div([
                html.H3("Gain Options", style={
                    "marginBottom": "16px", "fontSize":"22px",
                    "fontWeight":600, "color":"#22c55e"
                }),

                html.Div([
                    html.Label("Date Range", style={"fontWeight": "600"}),
                    dcc.Dropdown(
                        id="preset-gain",
                        options=[
                            {"label":"All","value":"all"},
                            {"label":"YTD","value":"ytd"},
                            {"label":"Last 1Y","value":"1y"},
                            {"label":"Last 3Y","value":"3y"},
                            {"label":"Last 6M","value":"6m"},
                            {"label":"Custom","value":"custom"},
                        ],
                        value="all", clearable=False,
                        style={"width":"180px","marginRight":"8px","display":"inline-block"}
                    ),
                    dcc.DatePickerRange(
                        id="date-range-gain",
                        display_format="YYYY-MM-DD",
                        minimum_nights=0, clearable=True, persistence=True,
                        style={"display":"inline-block"}
                    ),
                    dcc.Checklist(
                        id="snap-month-gain",
                        options=[{"label":" Snap to month", "value":"snap"}],
                        value=["snap"], inline=True,
                        style={"marginLeft":"10px", "display":"inline-block"}
                    )
                ], style={"margin":"6px 4px 4px 0"}),

                html.Div([
                    html.Span("Jump to:", style={"marginRight":"6px"}),
                    dcc.Dropdown(id="jump-year-gain", options=[], placeholder="Year",
                                 style={"width":"100px","display":"inline-block","marginRight":"6px"}),
                    dcc.Dropdown(id="jump-month-gain", options=MONTH_OPTIONS, placeholder="Month",
                                 style={"width":"120px","display":"inline-block"}),
                ], style={"marginBottom":"8px"}),

                html.Div([
                    html.Label("Change over (days)", style={"fontWeight": "600"}),
                    dcc.RadioItems(
                        id="window-size-gain",
                        options=[{"label": "3", "value": 3}, {"label": "5", "value": 5},
                                 {"label": "7", "value": 7}, {"label": "10", "value": 10}],
                        value=5, inline=True
                    ),
                    dcc.Input(
                        id="window-size-input-gain", type="number", min=1, step=1,
                        placeholder="custom", style={"marginLeft":"8px","width":"100px"}
                    )
                ], style={"margin":"6px 0"}),

                html.Div([
                    html.Label("Min % Threshold", style={"fontWeight": "600"}),
                    dcc.RadioItems(
                        id="min-threshold-gain",
                        options=[{"label":"1%","value":1},{"label":"3%","value":3},
                                 {"label":"5%","value":5},{"label":"10%","value":10}],
                        value=3, inline=True
                    ),
                    dcc.Input(
                        id="min-threshold-input-gain", type="number", min=0, max=100, step=0.01,
                        placeholder="e.g. 2.7", style={"marginLeft":"8px","width":"120px"}
                    )
                ], style={"margin":"6px 0"}),
            ], style={
                "flex":1, "minWidth":"420px", "padding":"24px",
                "background":"rgba(34,197,94,0.08)", "borderRadius":"16px",
                "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                "border":"1px solid rgba(34,197,94,0.3)"
            }),

        ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"8px"}),

        # -------------------- INDICATORS TOGGLES --------------------
        html.Div([
            html.H3("Indicators", style={
                "marginBottom":"16px", "fontSize":"22px",
                "fontWeight":600, "color":"#1e293b"
            }),
            dcc.Checklist(
                id="indicators-select",
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
                inline=True,
                inputStyle={"marginRight":"8px", "cursor":"pointer"},
                labelStyle={
                    "display":"inline-block","marginRight":"16px",
                    "fontSize":"14px", "color":"#475569", "cursor":"pointer"
                }
            ),
        ], style={
            "margin":"24px 0", "padding":"24px",
            "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
            "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
            "border":"1px solid rgba(255,255,255,0.1)"
        }),

        html.Div([
            html.Button(
                "Analyze", id="analyze", n_clicks=0,
                style={
                    "padding":"14px 32px","borderRadius":"12px","border":"none",
                    "fontWeight":600,"cursor":"pointer",
                    "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "color":"white", "fontSize":"16px",
                    "boxShadow":"0 4px 12px rgba(102, 126, 234, 0.4)",
                    "transition":"all 0.3s"
                }
            )
        ], style={"textAlign":"right","margin":"24px 0 32px"}),

        # ---------- Results (Drop / Gain) ----------
        html.Div([
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
                html.Div([
                dcc.Graph(id="return-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
                ], style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
                    "padding":"16px", "marginBottom":"16px",
                    "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
                html.Div([
                dcc.Graph(id="bar-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
                ], style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
                    "padding":"16px", "marginBottom":"16px",
                    "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
                html.Div(id="stats-drop", style={"margin": "24px 0"}),
                html.H4("Trade windows (first and last day)", style={
                    "fontSize":"20px", "fontWeight":600, "color":"inherit",
                    "marginTop":"32px", "marginBottom":"16px"
                }),
                html.Div(id="trade-windows-drop", style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
                    "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
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
                html.Div([
                dcc.Graph(id="return-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
                ], style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
                    "padding":"16px", "marginBottom":"16px",
                    "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
                html.Div([
                dcc.Graph(id="bar-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
                ], style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
                    "padding":"16px", "marginBottom":"16px",
                    "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
                html.Div(id="stats-gain", style={"margin": "24px 0"}),
                html.H4("Trade windows (first and last day)", style={
                    "fontSize":"20px", "fontWeight":600, "color":"inherit",
                    "marginTop":"32px", "marginBottom":"16px"
                }),
                html.Div(id="trade-windows-gain", style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"12px",
                    "padding":"20px", "boxShadow":"0 2px 8px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
            ], style={"flex": 1, "minWidth": "420px"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),

        # ---------- Indicators figure ----------
        html.H3("Indicator Charts", style={
            "fontSize":"28px", "fontWeight":700, "color":"inherit",
            "marginTop":"40px", "marginBottom":"20px"
        }),
        html.Div([
        dcc.Graph(id="indicators-figure", config={"displayModeBar": False}, style={"height":"540px"}),
        ], style={
            "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
            "padding":"20px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
            "border":"1px solid rgba(255,255,255,0.1)"
        }),

        html.Hr(),
        html.Div(id="preview", style={
            "marginTop":"40px", "padding":"24px",
            "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
            "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
            "border":"1px solid rgba(255,255,255,0.1)"
        }),  # <<< Data Preview lives here (first 10 rows)

        dcc.Store(id=STORE_RAW),
        dcc.Store(id=STORE_META),
    ],
    style={"maxWidth":"1400px","margin":"0 auto","padding":"32px 24px", "marginTop":"0"})

# ---------- Cross Index ----------
def cross_layout():
    return html.Div(
        [
            html.Div([
                html.H1("Cross Index Analysis", style={
                    "fontSize":"36px", "fontWeight":700, "marginBottom":"12px",
                    "color":"inherit"
                }),
                html.P("Compare two indexes side by side with correlation analysis", style={
                    "fontSize":"16px", "color":"inherit", "opacity":0.8, "marginBottom":"32px"
                }),
            ]),

            html.Div([
                html.Div([
                html.H3("Upload Index A (CSV)", style={
                    "fontSize":"20px", "fontWeight":600, "color":"inherit",
                    "marginBottom":"16px"
                }),
                    dcc.Upload(
                        id="uploader-a",
                        children=html.Div([
                            html.Div([
                                html.Span("Drag & drop or ", style={"fontSize":"15px", "color":"rgba(255,255,255,0.7)"}),
                                html.A("Select CSV", style={"fontSize":"15px", "color":"#00c896", "fontWeight":600, "textDecoration":"underline"})
                            ], style={"display":"flex", "alignItems":"center", "gap":"8px"}),
                            html.Span("📁", style={"fontSize":"24px", "marginLeft":"12px", "opacity":0.8, "transition":"all 0.3s"}),
                        ], style={"display":"flex", "alignItems":"center", "justifyContent":"center"}),
                        style={
                            "width":"100%","height":"100px",
                            "borderWidth":"2px","borderStyle":"dashed","borderColor":"rgba(0,200,150,0.3)",
                            "borderRadius":"16px","textAlign":"center",
                            "margin":"10px 0",
                            "background":"rgba(0,200,150,0.05)",
                            "display":"flex", "flexDirection":"row", "justifyContent":"center", "alignItems":"center",
                            "cursor":"pointer", "transition":"all 0.3s"
                        },
                        multiple=False, accept=".csv",
                    ),
                    html.Div(id="file-msg-a", style={"marginBottom": "6px"}),
                    html.Div(id="warn-msg-a", style={"marginBottom": "6px"}),
                    html.Div(id="preview-a"),
                ], style={
                    "flex":1, "minWidth":"420px", "padding":"24px",
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
                    "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),

                html.Div([
                html.H3("Upload Index B (CSV)", style={
                    "fontSize":"20px", "fontWeight":600, "color":"inherit",
                    "marginBottom":"16px"
                }),
                    dcc.Upload(
                        id="uploader-b",
                        children=html.Div([
                            html.Div([
                                html.Span("Drag & drop or ", style={"fontSize":"15px", "color":"rgba(255,255,255,0.7)"}),
                                html.A("Select CSV", style={"fontSize":"15px", "color":"#00c896", "fontWeight":600, "textDecoration":"underline"})
                            ], style={"display":"flex", "alignItems":"center", "gap":"8px"}),
                            html.Span("📁", style={"fontSize":"24px", "marginLeft":"12px", "opacity":0.8, "transition":"all 0.3s"}),
                        ], style={"display":"flex", "alignItems":"center", "justifyContent":"center"}),
                        style={
                            "width":"100%","height":"100px",
                            "borderWidth":"2px","borderStyle":"dashed","borderColor":"rgba(0,200,150,0.3)",
                            "borderRadius":"16px","textAlign":"center",
                            "margin":"10px 0",
                            "background":"rgba(0,200,150,0.05)",
                            "display":"flex", "flexDirection":"row", "justifyContent":"center", "alignItems":"center",
                            "cursor":"pointer", "transition":"all 0.3s"
                        },
                        multiple=False, accept=".csv",
                    ),
                    html.Div(id="file-msg-b", style={"marginBottom": "6px"}),
                    html.Div(id="warn-msg-b", style={"marginBottom": "6px"}),
                    html.Div(id="preview-b"),
                ], style={
                    "flex":1, "minWidth":"420px", "padding":"24px",
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
                    "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
            ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"32px"}),

            html.Hr(),

            html.Div([
                html.H3("Analysis Settings", style={
                    "fontSize":"24px", "fontWeight":600, "color":"inherit",
                    "marginBottom":"20px"
                }),
                html.Div([
                    html.Label("Date Range", style={"fontWeight":"600","marginRight":"8px"}),
                    dcc.Dropdown(
                        id="preset-cross",
                        options=[
                            {"label":"All","value":"all"},
                            {"label":"YTD","value":"ytd"},
                            {"label":"Last 1Y","value":"1y"},
                            {"label":"Last 3Y","value":"3y"},
                            {"label":"Last 6M","value":"6m"},
                            {"label":"Custom","value":"custom"},
                        ],
                        value="all", clearable=False,
                        style={"width":"160px","display":"inline-block","marginRight":"8px"}
                    ),
                    dcc.DatePickerRange(
                        id="date-range-cross",
                        display_format="YYYY-MM-DD",
                        minimum_nights=0, clearable=True, persistence=True,
                        style={"display":"inline-block","marginRight":"8px"}
                    ),
                    dcc.Checklist(
                        id="snap-month-cross",
                        options=[{"label":" Snap to month", "value":"snap"}],
                        value=["snap"], inline=True,
                        style={"display":"inline-block"}
                    ),
                ], style={"marginBottom":"8px"}),

                html.Div([
                    html.Span("Jump to:", style={"marginRight":"6px"}),
                    dcc.Dropdown(id="jump-year-cross", options=[], placeholder="Year",
                                 style={"width":"100px","display":"inline-block","marginRight":"6px"}),
                    dcc.Dropdown(id="jump-month-cross", options=MONTH_OPTIONS, placeholder="Month",
                                 style={"width":"120px","display":"inline-block"}),
                ], style={"marginBottom":"12px"}),

                html.Div([
                    html.Label("Window size (days) for returns", style={"fontWeight":"600","marginRight":"8px"}),
                    dcc.Input(id="x-window", type="number", min=1, step=1, value=5,
                              style={"width":"140px"}),
                ], style={"marginBottom":"6px"}),

                html.Div([
                    html.Button(
                        "Analyze", id="x-analyze", n_clicks=0,
                        style={
                            "padding":"14px 32px","borderRadius":"12px","border":"none",
                            "fontWeight":600,"cursor":"pointer",
                            "background":"linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "color":"white", "fontSize":"16px",
                            "boxShadow":"0 4px 12px rgba(102, 126, 234, 0.4)",
                            "transition":"all 0.3s"
                        }
                    )
                ], style={"textAlign":"right","margin":"24px 0 12px"}),
            ], style={
                "background":"rgba(255,255,255,0.05)","border":"1px solid rgba(255,255,255,0.1)",
                "borderRadius":"16px","padding":"24px",
                "boxShadow":"0 4px 12px rgba(0,0,0,0.3)"
            }),

            # ---- Results ----
            html.Div([
            html.Div([
                dcc.Graph(id="x-line-levels", config={"displayModeBar": False}, style={"height":"360px"}),
                ], style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
                    "padding":"20px", "marginBottom":"24px",
                    "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
                html.Div([
                dcc.Graph(id="x-scatter-returns", config={"displayModeBar": False}, style={"height":"360px"}),
                ], style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
                    "padding":"20px", "marginBottom":"24px",
                    "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
                html.Div([
                dcc.Graph(id="x-line-returns", config={"displayModeBar": False}, style={"height":"360px"}),
                ], style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
                    "padding":"20px", "marginBottom":"24px",
                    "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
                html.Div(id="x-stats", style={"margin":"24px 0"}),
                html.H4("Trade windows (first and last day)", style={
                    "fontSize":"22px", "fontWeight":600, "color":"inherit",
                    "marginTop":"32px", "marginBottom":"16px"
                }),
                html.Div(id="x-trade-windows", style={
                    "background":"rgba(255,255,255,0.05)", "borderRadius":"16px",
                    "padding":"24px", "boxShadow":"0 4px 12px rgba(0,0,0,0.3)",
                    "border":"1px solid rgba(255,255,255,0.1)"
                }),
            ], style={"marginTop":"32px"}),

            dcc.Store(id=STORE_A),
            dcc.Store(id=STORE_B),

            html.Div(dcc.Link("← Back to Home", href="/", style={
                "textDecoration":"none", "color":"#00c896", "fontWeight":500,
                "fontSize":"16px", "marginTop":"32px", "display":"inline-block"
            }))
        ],
        style={"maxWidth":"1400px","margin":"0 auto","padding":"32px 24px"}
    )

# -----------------------------
# Top-level app layout with router
# -----------------------------
app.layout = html.Div(
    [
        html.Div(id="navbar-container"),
        dcc.Location(id="url"),
        html.Div(id="page-content"),
        dcc.Store(id=STORE_THEME, data="dark"),
        dcc.Store(id=STORE_THEME_CLICKS, data=0)
    ],
    id="app-container",
    style={"fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
           "minHeight":"100vh","padding":"0", "margin":"0",
           "transition": "background-color 0.3s ease, color 0.3s ease"}
)

# Theme toggle callback - handles button clicks directly
# Use a pattern that works even when button is recreated
@app.callback(
    [Output(STORE_THEME, "data", allow_duplicate=True),
     Output(STORE_THEME_CLICKS, "data", allow_duplicate=True)],
    Input("theme-toggle", "n_clicks"),
    [State(STORE_THEME, "data"),
     State(STORE_THEME_CLICKS, "data")],
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme, prev_click_count):
    # When button is clicked, n_clicks will be 1, 2, 3, etc.
    # We need to detect if this is a new click (n_clicks > prev_click_count)
    
    # Handle first click
    if prev_click_count is None:
        prev_click_count = 0
    
    # If n_clicks hasn't changed or is None, don't update
    if n_clicks is None or n_clicks == prev_click_count:
        return no_update, no_update
    
    # This is a new click - toggle the theme
    if current_theme is None or current_theme == "":
        current_theme = "dark"
    
    # Toggle between dark and light
    new_theme = "light" if current_theme == "dark" else "dark"
    
    # Return both the new theme and the updated click count
    return new_theme, n_clicks

# Theme and Navbar callbacks - updates UI based on theme store
@app.callback(
    Output("navbar-container", "children"),
    Output("app-container", "style"),
    Input(STORE_THEME, "data"),
    prevent_initial_call=False
)
def update_navbar_and_theme(theme):
    if theme is None:
        theme = "dark"  # Default to dark if theme is None
    is_dark = theme == "dark"
    bg_style = {
        "fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
        "minHeight":"100vh","padding":"0", "margin":"0",
        "background": "#0a0a0a" if is_dark else "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
        "color": "white" if is_dark else "#1e293b",
        "transition": "background-color 0.3s ease, color 0.3s ease"
    }
    return navbar(theme), bg_style


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
    else:
        return home_layout()

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
    Output("return-chart-drop", "figure"),
    Output("bar-chart-drop", "figure"),
    Output("stats-drop", "children"),
    Output("trade-windows-drop", "children"),
    # GAIN outputs
    Output("analysis-output-gain", "children"),
    Output("return-chart-gain", "figure"),
    Output("bar-chart-gain", "figure"),
    Output("stats-gain", "children"),
    Output("trade-windows-gain", "children"),
    # INDICATOR figure
    Output("indicators-figure", "figure"),
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
        return (no_update,) * 11
    if not raw_payload:
        msg = html.Div("Please upload a CSV first.", style={"color": "crimson"})
        empty = go.Figure()
        return msg, empty, empty, None, None, msg, empty, empty, None, None, empty

    try:
        csv_bytes = base64.b64decode(raw_payload["csv_b64"].encode())
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        msg = html.Div(f"Failed to load stored data: {e}", style={"color": "crimson"})
        empty = go.Figure()
        return msg, empty, empty, None, None, msg, empty, empty, None, None, empty

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
        line_fig.update_layout(template="plotly_white", margin=dict(t=30, r=10, l=40, b=40),
                               xaxis_title="Time", yaxis_title="% change",
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

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
            template="plotly_white", title=bar_title + (f"  · N={N}" if N else ""),
            margin=dict(t=50, r=10, l=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            bargap=0.2,
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
        trade_table = build_trade_window_table(dff[["datetime","index"]], ws, limit=200)

        return card, line_fig, bar_fig, stats_view, trade_table, dff

    want_drop = "drop" in (analysis_types or [])
    want_gain = "gain" in (analysis_types or [])

    drop_out = build_outputs("drop",
                             preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop) \
               if want_drop else (html.Div("Drop disabled"), go.Figure(), go.Figure(), None, None, None)

    gain_out = build_outputs("gain",
                             preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain) \
               if want_gain else (html.Div("Gain disabled"), go.Figure(), go.Figure(), None, None, None)

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

    fig_ind.update_layout(
        template="plotly_white",
        margin=dict(t=40, r=10, l=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        title="Indicators (weekend-aware where applicable)"
    )

    # Unpack results for return
    drop_card, drop_line, drop_bar, drop_stats, drop_table, _dff_drop = drop_out
    gain_card, gain_line, gain_bar, gain_stats, gain_table, _dff_gain = gain_out

    return (drop_card, drop_line, drop_bar, drop_stats, drop_table,
            gain_card, gain_line, gain_bar, gain_stats, gain_table,
            fig_ind)

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
    Output("x-line-levels", "figure"),
    Output("x-scatter-returns", "figure"),
    Output("x-line-returns", "figure"),
    Output("x-stats", "children"),
    Output("x-trade-windows", "children"),
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
    empty = go.Figure()
    if not n_clicks:
        return empty, empty, empty, None, None
    if not rawA or not rawB:
        msg = html.Div("Please upload both Index A and Index B CSVs.", style={"color":"crimson"})
        return empty, empty, empty, msg, None

    # Load A & B
    try:
        dfA = pd.read_csv(io.BytesIO(base64.b64decode(rawA["csv_b64"].encode())))
        dfB = pd.read_csv(io.BytesIO(base64.b64decode(rawB["csv_b64"].encode())))
    except Exception as e:
        msg = html.Div(f"Failed to load stored data: {e}", style={"color":"crimson"})
        return empty, empty, empty, msg, None

    for df in (dfA, dfB):
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["index"] = pd.to_numeric(df["index"], errors="coerce")
    dfA = dfA.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)
    dfB = dfB.dropna(subset=["datetime","index"]).sort_values("datetime").reset_index(drop=True)

    # Determine overall range intersection
    data_min = max(dfA["datetime"].min(), dfB["datetime"].min())
    data_max = min(dfA["datetime"].max(), dfB["datetime"].max())
    if data_min >= data_max:
        msg = html.Div("No overlapping dates between A and B.", style={"color":"crimson"})
        return empty, empty, empty, msg, None

    snap = ("snap" in (snap_val or []))
    start, end = compute_range(preset, sd, ed, data_min, data_max, snap)

    # Slice to range and inner-join on dates for level chart
    A_in = dfA[(dfA["datetime"]>=start) & (dfA["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"A"})
    B_in = dfB[(dfB["datetime"]>=start) & (dfB["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"B"})
    levels = pd.merge(A_in, B_in, on="datetime", how="inner")
    if levels.empty:
        msg = html.Div("No overlapping data inside the selected date range.", style={"color":"crimson"})
        return empty, empty, empty, msg, None

    # -------- Chart 1: Levels normalized to 100 at range start --------
    baseA = levels["A"].iloc[0]
    baseB = levels["B"].iloc[0]
    normA = 100 * levels["A"] / baseA
    normB = 100 * levels["B"] / baseB

    fig_levels = go.Figure()
    fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normA, mode="lines", name="Index A (norm. to 100)"))
    fig_levels.add_trace(go.Scatter(x=levels["datetime"], y=normB, mode="lines", name="Index B (norm. to 100)"))
    fig_levels.update_layout(
        template="plotly_white", title=f"Both Indexes (normalized) · {start.date()} → {end.date()}",
        margin=dict(t=50, r=10, l=40, b=40),
        xaxis_title="Date", yaxis_title="Indexed level (start=100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
        msg = html.Div("Not enough data to compute weekend-aware windowed returns in this range.", style={"color":"crimson"})
        return fig_levels, empty, empty, msg, None

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
        template="plotly_white", title=f"Correlation (windowed returns) — {subtitle}",
        margin=dict(t=60, r=10, l=50, b=50),
        xaxis_title=f"Index B {win}-day return (%)",
        yaxis_title=f"Index A {win}-day return (%)"
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
        template="plotly_white",
        title=f"{win}-day Returns Over Time · {start.date()} → {end.date()}",
        margin=dict(t=50, r=10, l=40, b=40),
        xaxis_title="Date", yaxis_title=f"{win}-day return (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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

    # -------- Trade windows tables --------
    tableA = build_trade_window_table(tmpA[["datetime","index"]], win, limit=200)
    tableB = build_trade_window_table(tmpB[["datetime","index"]], win, limit=200)
    twin = html.Div([
        html.Div([html.H5("Index A trade windows"), tableA], style={"flex":1,"minWidth":"380px"}),
        html.Div([html.H5("Index B trade windows"), tableB], style={"flex":1,"minWidth":"380px"}),
    ], style={"display":"flex","gap":"16px","flexWrap":"wrap"})

    return fig_levels, fig_scatter, fig_returns, stats_view, twin


# Local run (useful for dev & Render health checks)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)





