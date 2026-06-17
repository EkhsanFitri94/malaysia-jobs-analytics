# 🇲🇾 Malaysia Jobs Analytics Dashboard

**Full-stack data pipeline: scrape → clean → analyze → visualize Malayisan job market data.**

Built by [Ekhsan Fitri](https://github.com/EkhsanFitri94) — demonstrating end-to-end data engineering with real-world Malaysian data.

---

## ✨ Features

- 🔍 **Live job scraping** — multi-source (JobStreet, Hiredly) with rate limiting
- 🧹 **Auto data cleaning** — salary parsing, location normalization, job categorization
- 📊 **Interactive dashboard** — salary trends, skill demand, hiring patterns
- 💰 **Salary benchmarking** — by role, experience, location
- 🔧 **Skill demand analysis** — what employers are actually asking for
- 🎓 **Fresh grad insights** — entry-level opportunities & starting salaries
- 📦 **Sample data mode** — 200 realistic Malaysian job listings for instant demo
- 📥 **Export** — download filtered results as CSV

## 🚀 Quick Start

```bash
git clone https://github.com/EkhsanFitri94/malaysia-jobs-analytics.git
cd malaysia-jobs-analytics
pip install -r requirements.txt
streamlit run app.py
```

## 📸 Dashboard Pages

| Tab | Description |
|---|---|
| 🧠 **Market Insights** | Auto-generated market intelligence, top hiring companies, weekly trends |
| 💰 **Salary Analysis** | Salary by category, experience, location; distribution charts |
| 🔧 **Skill Demand** | Top 20 in-demand skills, job category breakdown, experience demand |
| 📋 **Listings** | Filterable job listing table with CSV export |

## 🛠️ Tech Stack

- **Scraping:** BeautifulSoup4, requests, lxml
- **Data Processing:** pandas, numpy
- **Visualization:** Plotly (interactive charts)
- **Dashboard:** Streamlit
- **Pipeline:** scrape → clean → analyze → visualize

## 📂 Project Structure

```
malaysia-jobs-analytics/
├── app.py              # Streamlit dashboard
├── scraper.py          # Multi-source job scraper
├── analyzer.py         # Data cleaning + analytics engine
├── requirements.txt
├── data/               # Scraped/sample data
├── .gitignore
└── README.md
```

## 🎯 Skills Demonstrated

- Web scraping with ethical rate limiting
- Data cleaning & normalization (salary text → numeric, location → state mapping)
- Feature engineering (job categorization, experience level normalization)
- Interactive data visualization (Plotly)
- Full-stack dashboard development (Streamlit)

---

*Part of Ekhsan Fitri's AI, Analytics & Procurement portfolio · [More projects](https://github.com/EkhsanFitri94)*
