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


def drop_event_analysis(df: pd.DataFrame, minimum_per_drop: float, windows_size: int):
    _df = df.copy()
    _df["index_return"] = _df["index"].pct_change(periods=windows_size)
    _df = _df.dropna()
    crossings = (_df["index_return"] <= -minimum_per_drop)
    total_events = int(crossings.sum())
    denom = max(len(_df["index_return"]), 1)
    prob = total_events / denom
    key = f"{windows_size} days and {minimum_per_drop * 100:.0f}% minimum percentage drop"
    return {key: {"events": total_events, "probability": f"{prob:.2%}"}}


def gain_event_analysis(df: pd.DataFrame, minimum_per_gain: float, windows_size: int):
    _df = df.copy()
    _df["index_return"] = _df["index"].pct_change(periods=windows_size)
    _df = _df.dropna()
    crossings = (_df["index_return"] >= minimum_per_gain)
    total_events = int(crossings.sum())
    denom = max(len(_df["index_return"]), 1)
    prob = total_events / denom
    key = f"{windows_size} days and {minimum_per_gain * 100:.0f}% minimum percentage gain"
    return {key: {"events": total_events, "probability": f"{prob:.2%}"}}


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
# Layouts: Home / Single / Cross
# -----------------------------

card_style = {
    "display": "inline-block",
    "padding": "24px 28px",
    "borderRadius": "16px",
    "border": "1px solid #e6e6e6",
    "boxShadow": "0 3px 12px rgba(0,0,0,0.06)",
    "background": "white",
    "textDecoration": "none",
    "color": "#0f172a",
    "width": "320px",
    "transition": "transform .08s ease",
}

def navbar():
    return html.Div(
        [
            dcc.Link("Home", href="/", style={"marginRight":"16px", "fontWeight":600, "textDecoration":"none"}),
            dcc.Link("Single Index", href="/single", style={"marginRight":"16px", "textDecoration":"none"}),
            dcc.Link("Cross Index", href="/cross", style={"textDecoration":"none"}),
        ],
        style={"padding":"12px 0", "borderBottom":"1px solid #eee", "marginBottom":"16px"}
    )

def home_layout():
    return html.Div(
        [
            html.H1("Index Data Analysis"),
            html.P("Choose a workflow:"),
            html.Div(
                [
                    dcc.Link(
                        html.Div(
                            [html.H3("Single Index"),
                             html.P("Analyze one index")],
                            style=card_style
                        ),
                        href="/single",
                        style={"marginRight": "20px"}
                    ),
                    dcc.Link(
                        html.Div(
                            [html.H3("Cross Index"),
                             html.P("Compare two indexes")],
                            style=card_style
                        ),
                        href="/cross"
                    ),
                ],
                style={"marginTop": "12px"}
            ),
        ],
        style={"maxWidth":"1100px","margin":"0 auto","padding":"8px 12px"}
    )

# ---------- Single Index (FULL) ----------
def single_layout():
    return html.Div([
        html.H1("Single Index — Analysis"),
        html.P("Upload a CSV with two columns: a date column and a numeric index column (headers can be anything)."),

        dcc.Upload(
            id="uploader",
            children=html.Div(["Drag and Drop or ", html.A("Select CSV File")]),
            style={"width":"100%","height":"80px","lineHeight":"80px","borderWidth":"1px",
                   "borderStyle":"dashed","borderRadius":"12px","textAlign":"center",
                   "margin":"10px 0","background":"#fafafa"},
            multiple=False, accept=".csv",
        ),

        html.Div(id="file-msg", style={"marginBottom": "8px"}),
        html.Div(id="warn-msg", style={"marginBottom": "8px"}),

        html.Div([
            html.Label("Analysis Type(s)", style={"fontWeight": "600"}),
            dcc.Checklist(
                id="analysis-types",
                options=[{"label": " Drop", "value": "drop"},
                         {"label": " Gain", "value": "gain"}],
                value=["drop", "gain"], inline=True,
                inputStyle={"marginRight": "6px"},
                labelStyle={"display": "inline-block", "marginRight": "10px"},
            ),
        ], style={"marginBottom": "6px"}),

        # Controls row: Drop (left) & Gain (right)
        html.Div([

            # -------------------- DROP CONTROLS --------------------
            html.Div([
                html.H3("Drop Options", style={"marginBottom": "6px"}),

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
            ], style={"flex":1, "minWidth":"420px"}),

            # -------------------- GAIN CONTROLS --------------------
            html.Div([
                html.H3("Gain Options", style={"marginBottom": "6px"}),

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
            ], style={"flex":1, "minWidth":"420px"}),

        ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"8px"}),

        html.Div([
            html.Button(
                "Analyze", id="analyze", n_clicks=0,
                style={"padding":"10px 16px","borderRadius":"10px","border":"1px solid #ddd",
                       "fontWeight":600,"cursor":"pointer","background":"#0d6efd","color":"white"}
            )
        ], style={"textAlign":"right","margin":"6px 0 12px"}),

        # ---------- Results (Drop / Gain) ----------
        html.Div([
            html.Div([
                html.H2("Drop Analysis"),
                html.Div(id="analysis-output-drop", style={
                    "border": "1px solid #e6e6e6", "borderRadius": "12px",
                    "padding": "12px", "margin": "10px 0",
                    "background": "#ffffff", "boxShadow": "0 2px 6px rgba(0,0,0,0.04)"
                }),
                dcc.Graph(id="return-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
                dcc.Graph(id="bar-chart-drop", config={"displayModeBar": False}, style={"height": "320px"}),
                html.Div(id="stats-drop", style={"margin": "6px 0 14px"}),
            ], style={"flex": 1, "minWidth": "420px"}),

            html.Div([
                html.H2("Gain Analysis"),
                html.Div(id="analysis-output-gain", style={
                    "border": "1px solid #e6e6e6", "borderRadius": "12px",
                    "padding": "12px", "margin": "10px 0",
                    "background": "#ffffff", "boxShadow": "0 2px 6px rgba(0,0,0,0.04)"
                }),
                dcc.Graph(id="return-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
                dcc.Graph(id="bar-chart-gain", config={"displayModeBar": False}, style={"height": "320px"}),
                html.Div(id="stats-gain", style={"margin": "6px 0 14px"}),
            ], style={"flex": 1, "minWidth": "420px"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),

        html.Hr(),
        html.Div(id="preview"),

        dcc.Store(id=STORE_RAW),
        dcc.Store(id=STORE_META),
    ],
    style={"maxWidth":"1200px","margin":"0 auto","padding":"8px 12px"})

# ---------- Cross Index (UPLOAD TWO + SIMPLE ANALYSIS) ----------
def cross_layout():
    return html.Div(
        [
            html.H1("Cross Index — Compare Two Indexes"),

            html.Div([
                html.Div([
                    html.H3("Upload Index A (CSV)"),
                    dcc.Upload(
                        id="uploader-a",
                        children=html.Div(["Drag & drop or ", html.A("Select CSV")]),
                        style={"width":"100%","height":"70px","lineHeight":"70px","borderWidth":"1px",
                               "borderStyle":"dashed","borderRadius":"12px","textAlign":"center",
                               "margin":"10px 0","background":"#fafafa"},
                        multiple=False, accept=".csv",
                    ),
                    html.Div(id="file-msg-a", style={"marginBottom": "6px"}),
                    html.Div(id="warn-msg-a", style={"marginBottom": "6px"}),
                    html.Div(id="preview-a"),
                ], style={"flex":1, "minWidth":"420px"}),

                html.Div([
                    html.H3("Upload Index B (CSV)"),
                    dcc.Upload(
                        id="uploader-b",
                        children=html.Div(["Drag & drop or ", html.A("Select CSV")]),
                        style={"width":"100%","height":"70px","lineHeight":"70px","borderWidth":"1px",
                               "borderStyle":"dashed","borderRadius":"12px","textAlign":"center",
                               "margin":"10px 0","background":"#fafafa"},
                        multiple=False, accept=".csv",
                    ),
                    html.Div(id="file-msg-b", style={"marginBottom": "6px"}),
                    html.Div(id="warn-msg-b", style={"marginBottom": "6px"}),
                    html.Div(id="preview-b"),
                ], style={"flex":1, "minWidth":"420px"}),
            ], style={"display":"flex","gap":"24px","flexWrap":"wrap","marginBottom":"10px"}),

            html.Hr(),

            html.Div([
                html.H3("Analysis Settings"),
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
                        style={"padding":"10px 16px","borderRadius":"10px","border":"1px solid #ddd",
                               "fontWeight":600,"cursor":"pointer","background":"#0d6efd","color":"white"}
                    )
                ], style={"textAlign":"right","margin":"8px 0 12px"}),
            ], style={"background":"#fff","border":"1px solid #eee","borderRadius":"12px","padding":"12px"}),

            # ---- Results ----
            html.Div([
                dcc.Graph(id="x-line-levels", config={"displayModeBar": False}, style={"height":"360px"}),
                dcc.Graph(id="x-scatter-returns", config={"displayModeBar": False}, style={"height":"360px"}),
                dcc.Graph(id="x-line-returns", config={"displayModeBar": False}, style={"height":"360px"}),
                html.Div(id="x-stats", style={"margin":"8px 0 16px"}),
            ], style={"marginTop":"10px"}),

            dcc.Store(id=STORE_A),
            dcc.Store(id=STORE_B),

            html.Div(dcc.Link("← Back to Home", href="/", style={"textDecoration":"none", "color":"#0d6efd"}))
        ],
        style={"maxWidth":"1200px","margin":"0 auto","padding":"8px 12px"}
    )

# -----------------------------
# Top-level app layout with router
# -----------------------------
app.layout = html.Div(
    [
        navbar(),
        dcc.Location(id="url"),
        html.Div(id="page-content")
    ],
    style={"fontFamily":"system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
           "background":"#f6f7fb","minHeight":"100vh","padding":"0 18px"}
)

# Router
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
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
    Output("preview", "children"),
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

    table = dash_table.DataTable(
        data=df.head(10).to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=10, style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "minWidth": "120px"},
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
    # GAIN outputs
    Output("analysis-output-gain", "children"),
    Output("return-chart-gain", "figure"),
    Output("bar-chart-gain", "figure"),
    Output("stats-gain", "children"),
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
    prevent_initial_call=True,
)
def run_analysis_single(n_clicks, raw_payload, analysis_types,
                 preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop,
                 preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain):
    if not n_clicks:
        return (no_update,) * 8
    if not raw_payload:
        msg = html.Div("Please upload a CSV first.", style={"color": "crimson"})
        empty = go.Figure()
        return msg, empty, empty, None, msg, empty, empty, None

    try:
        csv_bytes = base64.b64decode(raw_payload["csv_b64"].encode())
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        msg = html.Div(f"Failed to load stored data: {e}", style={"color": "crimson"})
        empty = go.Figure()
        return msg, empty, empty, None, msg, empty, empty, None

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
            return msg, empty, empty, None

        ws = int(ws_custom) if ws_custom else int(ws_radio)
        th_pct = float(th_custom) if th_custom is not None else float(th_radio)
        th_frac = th_pct / 100.0

        if mode == "gain":
            summary = gain_event_analysis(dff, minimum_per_gain=th_frac, windows_size=ws)
            title = "Gain Event Analysis"
            label = "Min Gain: "
            sign = +1
            color = "#3b82f6"
        else:
            summary = drop_event_analysis(dff, minimum_per_drop=th_frac, windows_size=ws)
            title = "Drop Event Analysis"
            label = "Min Drop: "
            sign = -1
            color = "#ef4444"

        (k, v), = summary.items()
        card = html.Div([
            html.H3(title, style={"marginTop": 0}),
            html.P([
                html.Strong("Change over: "), f"{ws} days ",
                html.Span(" · "),
                html.Strong("Range: "), f"{start.date()} → {end.date()} ",
                html.Span(" · "),
                html.Strong(label), f"{th_pct:.2f}%",
            ]),
            html.Div([
                html.Div([
                    html.Div("Events", style={"color": "#6b7280", "fontSize": "12px"}),
                    html.Div(str(v["events"]), style={"fontSize": "28px", "fontWeight": 700}),
                ], style={"flex": 1, "textAlign": "center"}),
                html.Div([
                    html.Div("Probability", style={"color": "#6b7280", "fontSize": "12px"}),
                    html.Div(v["probability"], style={"fontSize": "28px", "fontWeight": 700}),
                ], style={"flex": 1, "textAlign": "center"}),
            ], style={"display": "flex", "gap": "12px"}),
        ], style={"border": "1px solid #e6e6e6", "borderRadius": "12px", "padding": "12px", "background": "#f8fafc"})

        # Return chart
        ret = dff["index"].pct_change(ws)
        mask = ~ret.isna()
        x_time = dff.loc[mask, "datetime"]
        y_pct = ret.loc[mask].values * 100.0

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

        # Bar chart
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
                x=labels, y=counts, name="Count", marker_color=color,
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
            html.H4("Change summary", style={"margin": "6px 0"}),
            html.Ul([html.Li(html.Span([html.Strong(k + ": "), v])) for k, v in stats_list])
        ], style={"background": "#f8fafc", "border": "1px solid #e6e6e6",
                  "borderRadius": "10px", "padding": "10px"})

        return card, line_fig, bar_fig, stats_view

    want_drop = "drop" in (analysis_types or [])
    want_gain = "gain" in (analysis_types or [])

    drop_out = build_outputs("drop",
                             preset_drop, sd_drop, ed_drop, snap_drop, ws_drop, ws_in_drop, th_drop, th_in_drop) \
               if want_drop else (html.Div("Drop disabled"), go.Figure(), go.Figure(), None)

    gain_out = build_outputs("gain",
                             preset_gain, sd_gain, ed_gain, snap_gain, ws_gain, ws_in_gain, th_gain, th_in_gain) \
               if want_gain else (html.Div("Gain disabled"), go.Figure(), go.Figure(), None)

    return (*drop_out, *gain_out)

# -----------------------------
# Upload callback (CROSS page) — BOTH uploads + date bounds
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
                page_size=10, style_table={"overflowX":"auto"},
                style_cell={"textAlign":"left","minWidth":"120px"}
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
                page_size=10, style_table={"overflowX":"auto"},
                style_cell={"textAlign":"left","minWidth":"120px"}
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
        return empty, empty, empty, None
    if not rawA or not rawB:
        msg = html.Div("Please upload both Index A and Index B CSVs.", style={"color":"crimson"})
        return empty, empty, empty, msg

    # Load A & B
    try:
        dfA = pd.read_csv(io.BytesIO(base64.b64decode(rawA["csv_b64"].encode())))
        dfB = pd.read_csv(io.BytesIO(base64.b64decode(rawB["csv_b64"].encode())))
    except Exception as e:
        msg = html.Div(f"Failed to load stored data: {e}", style={"color":"crimson"})
        return empty, empty, empty, msg

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
        return empty, empty, empty, msg

    snap = ("snap" in (snap_val or []))
    start, end = compute_range(preset, sd, ed, data_min, data_max, snap)

    # Slice to range and inner-join on dates for level chart
    A_in = dfA[(dfA["datetime"]>=start) & (dfA["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"A"})
    B_in = dfB[(dfB["datetime"]>=start) & (dfB["datetime"]<=end)][["datetime","index"]].rename(columns={"index":"B"})
    levels = pd.merge(A_in, B_in, on="datetime", how="inner")
    if levels.empty:
        msg = html.Div("No overlapping data inside the selected date range.", style={"color":"crimson"})
        return empty, empty, empty, msg

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

    # -------- Returns (window) --------
    win = max(int(win or 1), 1)
    retA = dfA.set_index("datetime")["index"].pct_change(win).rename("retA")
    retB = dfB.set_index("datetime")["index"].pct_change(win).rename("retB")
    # Keep only range
    retA = retA[(retA.index>=start) & (retA.index<=end)]
    retB = retB[(retB.index>=start) & (retB.index<=end)]
    rets = pd.concat([retA, retB], axis=1, join="inner").dropna()
    if rets.empty:
        msg = html.Div("Not enough data to compute windowed returns in this range.", style={"color":"crimson"})
        return fig_levels, empty, empty, msg

    # -------- Chart 2: Correlation scatter (windowed returns) --------
    x = rets["retB"].values * 100.0
    y = rets["retA"].values * 100.0
    # Pearson correlation
    if len(x) >= 2:
        corr = float(np.corrcoef(x, y)[0,1])
    else:
        corr = float("nan")

    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=x, y=y, mode="markers", name=f"{win}-day returns",
        hovertemplate="B: %{x:.2f}%<br>A: %{y:.2f}%<extra></extra>"
    ))
    # Add best-fit line (if enough points)
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
    ret_time = rets.reset_index().rename(columns={"index":"datetime"})
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

    # -------- Stats card (windowed returns) --------
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
            html.H4(name, style={"margin":"4px 0"}),
            html.Ul([html.Li(html.Span([html.Strong(k + ": "), v])) for k, v in items])
        ], style={"flex":1, "background":"#f8fafc","border":"1px solid #e6e6e6",
                  "borderRadius":"10px","padding":"10px"})

    corr_text = html.Div([
        html.H4("Relationship", style={"margin":"4px 0"}),
        html.P(f"Pearson correlation (windowed returns): {corr:.2f}" if np.isfinite(corr) else
               "Pearson correlation (windowed returns): n/a")
    ], style={"flex":1, "background":"#fff7ed","border":"1px solid #fde68a",
              "borderRadius":"10px","padding":"10px"})

    stats_view = html.Div([
        html.Div([
            stats_block("Index A — Stats", rets["retA"]),
            stats_block("Index B — Stats", rets["retB"]),
            corr_text
        ], style={"display":"flex","gap":"12px","flexWrap":"wrap"})
    ])

    return fig_levels, fig_scatter, fig_returns, stats_view


# Local run (useful for dev & Render health checks)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)



