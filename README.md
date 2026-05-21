# Customer Segmentation & Retention Analytics

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

> Behavioral analytics and customer lifetime modeling using real transactional e-commerce data.

> (PT) Análise comportamental e modelagem do ciclo de vida do cliente usando dados transacionais reais de comércio eletrônico.

---

## Table of Contents

- [Business Problem](#business-problem)
- [Objectives](#objectives)
- [Reproducibility](#reproducibility)
- [Dataset](#dataset)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Cleaning](#data-cleaning)
- [Feature Engineering](#feature-engineering)
- [Customer Segmentation](#customer-segmentation)
- [Churn Definition](#churn-definition)
- [CLTV Modeling](#cltv-modeling)
- [SQL Analytics Layer](#sql-analytics-layer)
- [Tech Stack](#tech-stack)
- [Key Insights](#key-insights)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Business Problem

E-commerce companies need to answer questions like:

- Which customers generate the most value?
- Who presents the highest risk of churn?
- Which segments should receive different campaigns?
- How much revenue is each customer likely to generate in the future?
- How to transform raw transactional data into actionable business decisions?

This project builds a complete analytical layer to answer these questions using real and imperfect data.

---

## Objectives

### Analytics
- Build RFM segmentation from raw transactional data
- Detect behavioral groups via unsupervised clustering
- Define churn behaviorally (no explicit churn column)
- Estimate Customer Lifetime Value (CLTV) using probabilistic models

### Data Engineering
- Excel ingestion and type normalization
- Automated cleaning and validation
- Parquet persistence for fast downstream reads
- Load into PostgreSQL warehouse
- Analytical queries in pure SQL

---

## Reproducibility

### Requirements
- [Pixi](https://pixi.prefix.dev/latest/)
- PostgreSQL instance (for the reporting phase)

### Setup

```bash
git clone https://github.com/CaesarDuarte/Customer-Clustering-and-Segmentation
cd Customer-Clustering-and-Segmentation

pixi install
pixi shell
```

### Download the dataset

```
Place 'online_retail_II.xlsx' in data/raw/
Download from: https://archive.ics.uci.edu/dataset/502/online+retail+ii
```

### Run pipeline

```bash
pixi run python src/ingestion/loader.py
pixi run python src/ingestion/validation.py
```

---

## Dataset

**Online Retail II** — UCI Machine Learning Repository
[https://archive.ics.uci.edu/dataset/502/online+retail+ii](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

| Attribute        | Detail                              |
|------------------|-------------------------------------|
| Rows             | ~1 million transactions             |
| Period           | December 2009 – December 2011       |
| Source           | Real UK-based online retailer       |
| Format           | Excel (.xlsx), two sheets by year   |

This dataset is not pre-cleaned. It contains cancellations, invalid prices, missing customer IDs, and reversed invoices (making it a realistic proxy for production data environments).

---

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Excel Raw  │--->│  Ingestion   │--->│   Validation    │
│  (~1M rows) │    │  loader.py   │    │  validation.py  │
└─────────────┘    └──────────────┘    └────────┬────────┘
                                                │
                   ┌──────────────┐    ┌────────▼────────┐
                   │  PostgreSQL  │<---|   Cleaning &    |
                   │  Warehouse   │    │ Feature Eng.    │
                   └──────┬───────┘    └─────────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          RFM +       Churn        CLTV
       Clustering   Prediction   BG/NBD
```

---

## Project Structure

```
Customer-Clustering-and-Segmentation/
│
├── data/
│   ├── raw/            # original .xlsx (gitignored)
│   └── processed/      # parquet files (gitignored)
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_rfm_segmentation.ipynb
│   ├── 03_clustering.ipynb
│   ├── 04_churn_prediction.ipynb
│   └── 05_cltv.ipynb
│
├── src/
│   ├── ingestion/
│   │   ├── loader.py       # reads Excel, casts types, saves parquet
│   │   └── validation.py   # integrity checks on processed data
│   ├── features/
│   │   ├── cleaning.py     # cancellations, negatives, missing IDs
│   │   ├── rfm.py          # Recency, Frequency, Monetary calculation
│   │   └── cltv.py         # feature preparation for BG/NBD
│   ├── models/
│   │   ├── segmentation.py # K-Means, HDBSCAN, cluster evaluation
│   │   ├── churn.py        # churn labeling + LightGBM/XGBoost
│   │   └── cltv_model.py   # BG/NBD, Gamma-Gamma, LTV projection
│   └── reporting/
│       └── db.py           # PostgreSQL load via SQLAlchemy
│
├── sql/
│   ├── schema.sql
│   ├── rfm_segments.sql
│   ├── churn_rate_by_segment.sql
│   └── ltv_ranking.sql
│
├── environment.yml
├── pyproject.toml
└── README.md
```

---

## Data Cleaning

The pipeline handles common issues found in real transactional data:

- Invoices starting with `C` are cancellations and treated separately
- Negative or zero prices are removed
- Negative quantities outside cancellations are flagged
- Rows without `Customer ID` are excluded from behavioral modeling
- Duplicate rows are dropped
- Inconsistent date parsing is normalized at ingestion

---

## Feature Engineering

### RFM Features

| Feature   | Definition                                      |
|-----------|-------------------------------------------------|
| Recency   | Days since the customer's last purchase         |
| Frequency | Number of distinct invoices                     |
| Monetary  | Total revenue attributed to the customer        |

RFM scores are used for segmentation, retention prioritization, and churn risk ranking.

---

## Customer Segmentation

### Techniques
- **K-Means**: interpretable clusters, tuned via elbow method and silhouette score
- **HDBSCAN**: density-based, captures irregular shapes and isolates outliers naturally

### Cluster Evaluation
- Silhouette Score
- Davies-Bouldin Index
- Business interpretability (segments must map to actionable strategies)

Example segments identified:
- High-value loyal customers
- Seasonal buyers
- At-risk customers
- One-time purchasers

---

## Churn Definition

The dataset has no explicit churn column. Churn is defined behaviorally:

```
A customer is considered churned if they remain inactive for more than 90 days.
```

This threshold can be adjusted by segment or historical purchase frequency. Defining churn from behavior (rather than consuming a pre-labeled column) approximates real business scenarios where this decision belongs to the data scientist.

---

## CLTV Modeling
> **Status:** Planned (to be implemented after segmentation and churn phases are complete).

### Models
- **BG/NBD**: estimates expected future number of transactions
- **Gamma-Gamma**: estimates expected monetary value per transaction

### Output
- Projected number of purchases in the next 90/180/365 days
- Expected revenue per customer
- Ranked lifetime value for budget allocation decisions

---

## SQL Analytics Layer

Analytical queries written in pure SQL against the PostgreSQL warehouse:

- Cohort retention analysis
- Churn rate by segment
- LTV ranking
- Monthly revenue trend
- Repeat purchase rate
- Segment migration over time

Example:

```sql
SELECT
    segment,
    COUNT(*)       AS customers,
    ROUND(AVG(cltv)::numeric, 2) AS avg_cltv,
    ROUND(AVG(churn_probability)::numeric, 4) AS avg_churn_prob
FROM customer_segments
GROUP BY segment
ORDER BY avg_cltv DESC;
```

---

## Tech Stack

| Layer            | Tools                                      |
|------------------|--------------------------------------------|
| Data wrangling   | Pandas, NumPy, PyArrow                     |
| Machine Learning | Scikit-learn, XGBoost, LightGBM, HDBSCAN   |
| CLTV Modeling    | PYMC-Marketing (BG/NBD + Gamma-Gamma)      |
| Data Engineering | PostgreSQL, SQLAlchemy                     |
| Visualization    | Matplotlib, Seaborn, Plotly                |
| Environment      | Conda (Miniforge), pip                     |

---

## Key Insights

> *To be updated as the project progresses.*

---

## Future Improvements

- Orchestration with Airflow
- dbt transformations on top of PostgreSQL
- Docker deployment
- Streamlit/Nicegui dashboard
- MLflow experiment tracking

---

## License

MIT © César Duarte

Liked it? Have questions? Reach me on [LinkedIn](https://www.linkedin.com/in/caesar-duarte/).
