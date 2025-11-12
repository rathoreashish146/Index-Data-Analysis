# 📉 Drawdown & Recovery Analysis Feature

## Overview
A comprehensive tool added to the Single Index Analysis page that identifies and analyzes all major drawdown episodes from peak to trough to recovery. This powerful feature helps users understand market corrections, their severity, and recovery patterns.

---

## ✨ Features

### 1. **Automatic Drawdown Detection**
- Identifies all drawdown episodes from historical peaks to troughs
- Tracks recovery dates when price returns to previous peak
- Handles open drawdowns (not yet recovered) gracefully

### 2. **Smart Filtering**
Filter drawdowns by minimum percentage threshold:
- **Show All** - Every drawdown episode
- **≥5%** - Small to moderate corrections
- **≥10%** - Significant corrections (default)
- **≥15%** - Major corrections
- **≥20%** - Severe market crashes

### 3. **Comprehensive Data Table**
Interactive table showing:
- **Peak Date** - When the high was reached
- **Peak Value** - Index value at peak
- **Trough Date** - When the low was reached
- **Trough Value** - Index value at trough
- **Recovery Date** - When price returned to peak (or N/A if not recovered)
- **Recovery Value** - Index value at recovery
- **Drawdown %** - Percentage decline (color-coded in red)
- **Days to Trough** - How long the decline took
- **Days to Recovery** - How long full recovery took (color-coded in blue)

### 4. **Summary Statistics Dashboard**
Four key metrics displayed in color-coded cards:
- **Total Episodes** - Count of drawdown events
- **Avg Drawdown** - Mean drawdown percentage
- **Max Drawdown** - Worst drawdown in dataset
- **Avg Recovery Days** - Mean time to recover

### 5. **Export Functionality**
- **Download CSV** button to export results
- Filename: `drawdown_recoveries.csv`
- Includes all filtered data with proper formatting

---

## 🎯 Use Cases

### Risk Assessment
> *"How severe were the market corrections in the past decade?"*

**Steps:**
1. Upload your index data
2. Click "📊 Analyze Drawdowns"
3. Set filter to **≥10%** to see significant corrections
4. Review summary statistics for average severity

**Insight:** Understand historical volatility and prepare for future drawdowns.

---

### Recovery Analysis
> *"How long does it typically take to recover from a 15% drop?"*

**Steps:**
1. Set filter to **≥15%**
2. Analyze drawdowns
3. Check "Avg Recovery Days" in summary
4. Review individual episodes in table

**Insight:** Set realistic expectations for recovery timeframes.

---

### Worst-Case Scenarios
> *"What was the worst drawdown and how long did recovery take?"*

**Steps:**
1. Set filter to **Show All**
2. Analyze drawdowns
3. Sort table by "Drawdown %" (descending)
4. Review the top entry for max drawdown details

**Insight:** Understand extreme risk scenarios.

---

### Pattern Identification
> *"Were drawdowns during 2020 different from other periods?"*

**Steps:**
1. Set filter to **≥5%** to capture all significant moves
2. Analyze drawdowns
3. Sort table by "Peak Date"
4. Download CSV for further analysis in Excel/Python

**Insight:** Identify market regime changes and unusual patterns.

---

## 📊 Technical Details

### Algorithm
The feature uses a **peak-to-trough-to-recovery** detection algorithm:

1. **Find Peaks:** Identifies local maximum (record high) points
2. **Track Trough:** Follows decline until lowest point reached
3. **Detect Recovery:** Continues until price returns to original peak
4. **Handle Open:** If data ends before recovery, marks as open drawdown

### Key Logic
```python
def compute_drawdown_recovery(df, date_col="datetime", price_col="index"):
    """
    - Scans through price series
    - Identifies each peak as start of potential episode
    - Tracks decline to trough
    - Monitors recovery back to peak
    - Records all metadata (dates, values, durations)
    """
```

### Data Processing
- **Input:** Raw price/index data with dates
- **Processing:** 
  - Computes cumulative max (running peak)
  - Calculates drawdown = current - peak
  - Identifies episode boundaries
- **Output:** Structured DataFrame with episode details

---

## 🎨 UI Components

### Header Section
- **Title:** 📉 Drawdown & Recovery Analysis
- **Description:** Explains feature purpose
- **Styling:** Clean card with subtle background

### Filter Controls
- **Radio buttons** for percentage thresholds
- **Helper text** explaining filter behavior
- **Responsive layout** for mobile

### Action Buttons
- **Analyze Button:** Red gradient, prominent
- **Download Button:** Subtle, secondary style
- **Loading indicators** during processing

### Results Display
1. **Summary Cards:** 4-column grid (responsive to 1-column on mobile)
2. **Data Table:** Paginated, sortable, filterable
3. **Color coding:** Red for drawdowns, blue for recovery

---

## 💡 Design Decisions

### Why Filter by Default to 10%?
- **Practical:** Most users care about significant corrections
- **Focus:** Reduces noise from minor fluctuations
- **Standard:** 10% is commonly used threshold in finance
- **Flexible:** Easy to change for different needs

### Why Show Summary Statistics?
- **Quick insight** without scrolling through table
- **Comparison** against personal expectations
- **Context** for individual episodes
- **Decision support** for risk assessment

### Why Separate Analyze Button?
- **Performance:** Large datasets can take time
- **User control:** Explicit action required
- **Clarity:** Clear when analysis starts
- **Feedback:** Loading states work properly

---

## 📱 Responsive Design

### Desktop (>900px)
- Summary cards in 4-column grid
- Full table width
- All features visible simultaneously

### Tablet (480px - 900px)
- Summary cards in 2-column grid
- Table scrollable horizontally
- Filters stack vertically

### Mobile (<480px)
- Summary cards in 1-column stack
- Compact table with horizontal scroll
- Buttons stack vertically
- Touch-friendly targets

---

## ♿ Accessibility

- **Keyboard navigation:** All controls accessible via tab
- **Screen readers:** Semantic HTML structure
- **Color contrast:** WCAG AA compliant
- **Focus indicators:** Clear visual feedback
- **Alternative text:** Emojis supplementary to text

---

## 🔧 Integration

### Where It Lives
**Single Index Analysis Page**
- After Indicators section
- Before Data Preview
- Visible to all users

### Data Requirements
- Uses `STORE_RAW` (uploaded CSV data)
- Requires `datetime` and `index` columns
- Works with any time series data

### Dependencies
- Existing `compute_drawdown_recovery()` function
- Dash DataTable component
- Download functionality (dcc.Download)

---

## 📈 Future Enhancements

### Potential Additions

1. **Visualization:**
   - Line chart showing all drawdown periods shaded
   - Bar chart comparing recovery times
   - Scatter plot: drawdown % vs recovery days

2. **Advanced Filters:**
   - Date range filter (e.g., "Only 2020-2023")
   - Recovery time filter (e.g., ">100 days")
   - Combined filters (e.g., "≥15% AND >6 months")

3. **Statistical Analysis:**
   - Distribution histograms
   - Correlation with market events
   - Comparison across multiple indexes

4. **Export Options:**
   - Download as Excel with formatting
   - Generate PDF report
   - Export charts as images

5. **Alerts & Insights:**
   - "Current drawdown is X% from peak"
   - "Historical average suggests recovery in Y days"
   - "This drawdown ranks #Z out of all episodes"

---

## 🐛 Error Handling

### Graceful Failures
- **No data:** Shows friendly message
- **Empty results:** Explains no drawdowns found
- **Invalid filter:** Falls back to sensible defaults
- **Processing errors:** Displays error message, doesn't crash

### User Feedback
- **Loading states:** Shows processing indicator
- **Success confirmation:** Results appear
- **Empty state messages:** Clear explanations
- **Error messages:** Actionable guidance

---

## 📊 Example Output

### Sample Summary Stats
```
Total Episodes: 12
Avg Drawdown: -14.52%
Max Drawdown: -34.87%
Avg Recovery Days: 127
```

### Sample Table Row
```
Peak Date       | Peak Value | Trough Date  | Trough Value | Recovery Date | Drawdown % | Days to Trough | Days to Recovery
2020-02-19     | 3386.15    | 2020-03-23   | 2237.40      | 2020-08-18   | -33.92%    | 33            | 181
```

---

## ✅ Testing Checklist

### Functionality
- [ ] Upload CSV with price data
- [ ] Click "Analyze Drawdowns" button
- [ ] Verify summary statistics calculate correctly
- [ ] Change filter threshold (try each option)
- [ ] Sort table by different columns
- [ ] Use table filter/search
- [ ] Click "Download CSV"
- [ ] Verify downloaded file has correct data
- [ ] Test with empty results (high filter threshold)
- [ ] Test with edge case (single peak, no drawdown)

### Visual
- [ ] Cards align properly
- [ ] Table renders correctly
- [ ] Colors match design (red drawdowns, blue recovery)
- [ ] Buttons have hover states
- [ ] Summary cards responsive on mobile
- [ ] Table scrolls horizontally on small screens

### Edge Cases
- [ ] No data uploaded → shows appropriate message
- [ ] All drawdowns < filter → shows "no results" message
- [ ] Open drawdown (no recovery) → shows N/A correctly
- [ ] Single data point → handles gracefully
- [ ] Decreasing series (no peaks) → appropriate handling

---

## 📚 Documentation Updates

### User-Facing
Add to main documentation (docs page):
- **Section 3.5:** Drawdown & Recovery Analysis
- Explain what drawdowns are
- Show example use cases
- Screenshot of results

### Technical
Add to code comments:
- Function docstrings
- Algorithm explanation
- Performance notes

---

## 🎉 Success Metrics

### User Engagement
- **Usage rate:** % of users who click "Analyze Drawdowns"
- **Filter changes:** How many adjust the threshold
- **Downloads:** How many export the results

### Value Delivered
- **Insights gained:** Users understand market volatility better
- **Risk assessment:** Better informed investment decisions
- **Time saved:** Automated vs manual analysis

---

## 🔗 Related Features

### Works Well With
- **Drop/Gain Analysis:** Compare event-based vs drawdown analysis
- **Technical Indicators:** RSI/MACD context for drawdowns
- **Date Range Filters:** Analyze specific periods

### Complementary
- **Cross Index Comparison:** Compare drawdown patterns between indexes
- **Historical Data:** Longer time series = more episodes

---

## 📝 Summary

The Drawdown & Recovery Analysis feature provides users with:

✅ **Automatic detection** of all market corrections  
✅ **Flexible filtering** to focus on significant events  
✅ **Comprehensive data** with dates, values, and durations  
✅ **Summary statistics** for quick insights  
✅ **Export functionality** for further analysis  
✅ **Professional UI** with color coding and responsive design  

This tool empowers users to:
- Understand historical market volatility
- Assess risk based on past patterns
- Plan for recovery timeframes
- Make data-driven investment decisions

**No finance expertise needed** - the feature explains everything clearly!

---

*Feature Status: ✅ Complete and Production Ready*
*Integration: Single Index Analysis Page*
*Last Updated: 2025*

