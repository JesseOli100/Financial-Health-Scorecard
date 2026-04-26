# Financial-Health-Scorecard

# Contact Info

Want to hire me? Check out my LinkedIn here: https://www.linkedin.com/in/jesse-o-03476a102/

# Counterparty Financial Health Scoring App
# Overview

This is a lightweight Flask web application that analyzes counterparty financial statements and produces:

Key credit ratios

A composite health score

Tier classification (Tier 1–4)

Structured analyst-style memo commentary

The application is designed to demonstrate programmatic credit analysis logic using deterministic ratio-based scoring instead of manual spreadsheet review.

# Purpose

In underwriting and counterparty risk environments, financial health assessment is often:

Performed manually

Inconsistent across analysts

Weakly documented

This application formalizes ratio computation and scoring logic into code, providing:

Reproducibility

Transparent logic

Structured memo generation

Tier-based classification

The system is intended as an internal analytical support tool — not as a standalone credit approval system.

# Input Format

Upload a .csv or Excel file containing one or more counterparties with the following required columns:

counterparty  
current_assets  
current_liabilities  
total_debt  
ebit  
interest_expense  
revenue_current  
revenue_prior  
total_assets  


See: sample_financials.csv

# Ratios Computed

From the uploaded financial data, the application computes:

Current Ratio
current_assets / current_liabilities

Leverage Ratio
total_debt / total_assets

Interest Coverage Ratio
EBIT / interest_expense

Revenue Growth (YoY)
(revenue_current - revenue_prior) / revenue_prior

Return on Assets (ROA)
EBIT / total_assets

All division logic includes safe guards to prevent zero-division errors 

# Scoring Framework

Each ratio contributes positive or negative points based on heuristic thresholds.

Example Logic:
Metric	Strong	Moderate	Weak
Current Ratio	≥ 2	1–2	< 1
Leverage	≤ 40%	40–70%	> 70%
Interest Coverage	≥ 5x	2–5x	< 2x
Revenue Growth	≥ 10%	0–10%	Negative
ROA	≥ 8%	3–8%	< 3%

Scores are aggregated and mapped to tiers:

Tier 1 – Strong

Tier 2 – Stable

Tier 3 – Negative Outlook

Tier 4 – High Risk

This mimics internal credit grading logic in simplified form 

# Analyst Memo Generation

The system automatically generates a structured underwriting-style memo including:

Counterparty name

Overall health score

Ratio breakdown

Interpretive commentary

Risk outlook

Usage disclaimer

This transforms quantitative assessment into explainable narrative output.

# Web Application Features

CSV or Excel upload

Automatic column normalization

Input validation (missing column detection)

Safe numeric coercion

Deterministic ratio scoring

Structured memo rendering

The application runs locally using Flask.

# How to Run

Install dependencies:

pip install flask pandas openpyxl


Run the application:

python app.py


Navigate to:

http://127.0.0.1:5000


Upload a properly formatted financial file to generate results.

📂 Project Structure
project/
│
├── app.py
├── sample_financials.csv
├── templates/
│    └── index.html
└── README.md

# Institutional Relevance

This project demonstrates:

Ratio-based credit analysis

Heuristic financial scoring

Automated memo generation

Deterministic underwriting logic

Structured financial data validation

It reflects simplified workflows used in:

Corporate credit underwriting

Counterparty risk assessment

Structured finance analysis

Private credit review

Energy / commodities trading risk

# Potential Extensions

Future expansions could include:

Multi-counterparty batch scoring

Historical financial trend tracking

Persistence layer (SQL storage)

Weight calibration of ratio scoring

Integration with exposure limits

Stress scenario overlays

Probability-of-default modeling

# Disclaimer

This tool is designed as an analytical aid and educational demonstration of structured credit evaluation logic. It is not intended as a standalone approval or investment decision engine.

# Author

Jesse Olivarez
Credit Risk | Financial Analytics | Data Analytics
