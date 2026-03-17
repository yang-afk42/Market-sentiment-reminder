# Market-sentiment-reminder
1.Description
This project aims to automate the tracking of market sentiment indicators—such as yield spreads and margin maintenance ratios—to provide actionable investment decision support. It addresses the critical investor pain point of synthesizing disparate macroeconomic and technical indicators in real-time.

2.Features 
Yield Spread Monitoring: Automates the calculation and tracking of U.S. Treasury yield curve fluctuations.
Positioning & Flow Analysis: Retrieves market-wide margin maintenance ratios in real-time to identify overbought or oversold zones, utilizing the 60-day (Quarterly) MA Bias and 5-day Moving Average for trend validation.
Sentiment Alerts: Leverages yfinance data to monitor the VIX Index and its deviation from historical moving averages to provide early risk warnings.

3. Tech Stack 
Data Processing: Python, Pandas, NumPy
Data Source: yfinance (Yahoo Finance API)
Infrastructure: Docker
Automation: GitHub Actions (Scheduled CI)

4. Installation & Usage 
