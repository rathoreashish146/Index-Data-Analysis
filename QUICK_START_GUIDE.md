# 🚀 Quick Start Guide - Index Data Analysis App

## 📋 What You Need

### Required Data Format
- **CSV file** with exactly **2 columns**:
  1. **Date column** (any date format: YYYY-MM-DD, MM/DD/YYYY, etc.)
  2. **Numeric column** (index value, price, level, etc.)
- Column names can be anything - the app auto-detects!

### Example Valid CSV:
```csv
Date,Index
2024-01-01,1000.5
2024-01-02,1005.2
2024-01-03,998.7
2024-01-04,1012.3
```

---

## 🎯 Choosing Your Analysis

### Single Index Analysis 📊
**When to use:** Analyzing one market index in depth

**What you get:**
- Drop events (when it fell significantly)
- Gain events (when it rose significantly)  
- Technical indicators (RSI, MACD, Bollinger Bands)
- Statistical analysis
- Visual charts and trends

**Best for:**
- Risk assessment
- Finding historical patterns
- Understanding volatility
- Technical analysis

---

### Cross Index Comparison 🔀
**When to use:** Comparing two different indexes

**What you get:**
- Correlation analysis (how they move together)
- Relative performance comparison
- Side-by-side visualizations
- Statistical relationship

**Best for:**
- Diversification decisions
- Understanding market relationships
- Portfolio analysis
- Comparative performance

---

## ⚙️ Key Settings Explained

### Analysis Period (days)
- **What:** Time window for measuring changes
- **Examples:**
  - 3 days = short-term movements
  - 5 days = weekly (most common)
  - 7 days = full week
  - 10 days = two weeks

### Minimum Threshold (%)
- **What:** Minimum change to count as significant
- **Examples:**
  - 1% = very sensitive (finds many small events)
  - 3% = moderate (standard risk measure)
  - 5% = significant movements only
  - 10% = major events only

### Date Range Presets
- **All** - Entire dataset
- **YTD** - Year-to-date (Jan 1 to now)
- **1Y** - Last 365 days
- **3Y** - Last 3 years
- **6M** - Last 6 months
- **Custom** - Pick your own dates

### Snap to Month
- ✅ **Enabled:** Analysis starts at month beginning, ends at month end
- ❌ **Disabled:** Uses exact dates selected
- **Use when:** You want clean monthly reporting

---

## 📊 Understanding Results

### Probability
- **Formula:** (Events Found / Total Windows) × 100
- **Example:** "8%" means 8 out of every 100 time periods had this event
- **Higher = More frequent**

### Correlation (Cross Index only)
- **+1.0** = Perfect sync (always move together)
- **+0.7 to +1.0** = Strong relationship
- **+0.3 to +0.7** = Moderate relationship
- **0.0** = No relationship
- **-0.3 to -0.7** = Moderate opposite
- **-0.7 to -1.0** = Strong opposite
- **-1.0** = Perfect opposite (one up = other down)

### Technical Indicators (Single Index)

#### RSI (Relative Strength Index)
- **0-30:** Oversold (may rise soon)
- **30-70:** Normal range
- **70-100:** Overbought (may drop soon)

#### MACD Signal
- **MACD above signal line:** Bullish (upward momentum)
- **MACD below signal line:** Bearish (downward momentum)
- **Crossover:** Potential trend change

#### Bollinger Bands
- **Price near upper band:** Potentially overvalued
- **Price near lower band:** Potentially undervalued
- **Bands narrowing:** Low volatility (breakout coming?)
- **Bands widening:** High volatility

---

## 💡 Pro Tips

### Starting Out
1. ✅ **Start simple:** Use 5-day period, 3% threshold, "All" date range
2. ✅ **Upload & click Analyze** - See what you get!
3. ✅ **Then experiment:** Try different settings to see how results change

### Getting Better Results
1. ✅ **Compare thresholds:** Run 3%, 5%, and 10% to see different risk levels
2. ✅ **Use YTD:** Great for current year performance
3. ✅ **Check indicators together:** RSI + MACD + Bollinger gives complete picture
4. ✅ **Look at Trade Windows table:** See exact dates of events

### Common Use Cases

#### "How risky is this investment?"
- Use **Drop Analysis**
- Set **7-day period**
- Set **5% threshold**
- Check **probability** - higher = more risky

#### "When does it usually gain?"
- Use **Gain Analysis**  
- Try **different thresholds** (3%, 5%, 10%)
- Check **Trade Windows** table for dates
- Look for seasonal patterns

#### "Do these two move together?"
- Use **Cross Index**
- Check **correlation number**
- Look at **scatter plot** (tight cluster = correlated)

---

## 🔍 Troubleshooting

### "My file won't upload"
- ✅ Make sure it's a CSV file (.csv extension)
- ✅ Check you have exactly 2 columns
- ✅ Verify date column has valid dates
- ✅ Verify numeric column has numbers (not text)

### "No results showing"
- ✅ Click the "Analyze" button
- ✅ Check you selected at least one analysis type (Drop or Gain)
- ✅ Make sure your date range has data
- ✅ Try a lower threshold (finds more events)

### "Numbers seem wrong"
- ✅ Check your date range is correct
- ✅ Verify threshold setting (3% = 0.03 not 3)
- ✅ Remember: App uses weekend-aware calculations
- ✅ Small datasets = higher variance

---

## 📖 Need More Help?

1. **Click "Documentation" in the navbar** - Comprehensive guide with examples
2. **Check the examples section** - Real-world scenarios with steps
3. **Read indicator explanations** - Understand what each metric means
4. **Start with preset options** - Then customize as you learn

---

## 🎓 Learning Path

### Week 1: Basics
- Upload a file
- Run with default settings
- Understand basic results

### Week 2: Configuration  
- Try different periods (3, 5, 7, 10 days)
- Experiment with thresholds
- Use date range presets

### Week 3: Analysis
- Read indicator explanations
- Understand correlation
- Compare different analyses

### Week 4: Advanced
- Custom date ranges
- Interpret technical indicators
- Make data-driven decisions

---

## 📞 Quick Reference Card

| Feature | Location | Purpose |
|---------|----------|---------|
| Single Index | Home → Single Index | Analyze one index |
| Cross Index | Home → Cross Index | Compare two indexes |
| Documentation | Navbar → 📖 Documentation | Full guide & examples |
| Date Range | Each analysis page | Select time period |
| Analysis Period | Drop/Gain options | Days for calculation |
| Threshold | Drop/Gain options | Minimum % change |
| Trade Windows | Results section | Exact event dates |
| Indicators | Results (Single only) | Technical analysis |

---

## ✨ Remember

**The app is designed to be self-explanatory!**

- 💡 Every field has help text
- 📖 Documentation is always one click away
- 🎯 Start simple, then explore
- 📊 Experiment with different settings
- 🔍 Results explain themselves

**You don't need to be a financial expert - just curious!**

---

*Generated for Index Data Analysis App | [View Full Documentation](/docs)*

