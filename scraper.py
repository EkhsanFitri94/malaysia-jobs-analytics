"""
Malaysia Jobs Scraper
Scrapes job listings from Malaysian job portals.
Respectful scraping with rate limiting and proper headers.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
import os
from datetime import datetime
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
]


def get_headers() -> dict:
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ms;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
    }


def scrape_jobstreet(keyword: str = "data analyst", pages: int = 3) -> list:
    """
    Scrape JobStreet Malaysia listings.
    NOTE: Real JobStreet uses dynamic loading — this is a reference implementation.
    For production use, consider Selenium or their API.
    """
    jobs = []
    base_url = "https://www.jobstreet.com.my"

    for page in range(1, pages + 1):
        try:
            url = f"{base_url}/{keyword}-jobs?page={page}"
            resp = requests.get(url, headers=get_headers(), timeout=15)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            cards = soup.find_all('article', {'data-automation': 'normalJob'})

            for card in cards:
                try:
                    title_el = card.find('a', {'data-automation': 'jobTitle'})
                    company_el = card.find('a', {'data-automation': 'jobCompany'})
                    location_el = card.find('a', {'data-automation': 'jobLocation'})
                    salary_el = card.find('span', {'data-automation': 'jobSalary'})

                    jobs.append({
                        'title': title_el.text.strip() if title_el else 'N/A',
                        'company': company_el.text.strip() if company_el else 'N/A',
                        'location': location_el.text.strip() if location_el else 'Malaysia',
                        'salary': salary_el.text.strip() if salary_el else 'Not disclosed',
                        'source': 'JobStreet',
                        'keyword': keyword,
                        'scraped_at': datetime.now().isoformat(),
                    })
                except Exception:
                    continue

            time.sleep(random.uniform(2, 4))  # Be respectful
        except Exception:
            continue

    return jobs


def scrape_hh_malaysia(keyword: str = "data analyst", pages: int = 2) -> list:
    """
    Scrape Hiredly (formerly WOBB) Malaysia.
    """
    jobs = []
    base_url = "https://www.hiredly.com"

    for page in range(pages):
        try:
            url = f"{base_url}/jobs?keywords={keyword}&page={page}"
            resp = requests.get(url, headers=get_headers(), timeout=15)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            cards = soup.find_all('div', class_='job-card')

            for card in cards:
                try:
                    title = card.find('h3') or card.find('a', class_='job-title')
                    company = card.find('span', class_='company-name') or card.find('p', class_='company')
                    location = card.find('span', class_='location') or card.find('p', class_='location')

                    jobs.append({
                        'title': title.text.strip() if title else 'N/A',
                        'company': company.text.strip() if company else 'N/A',
                        'location': location.text.strip() if location else 'Malaysia',
                        'salary': 'Not disclosed',
                        'source': 'Hiredly',
                        'keyword': keyword,
                        'scraped_at': datetime.now().isoformat(),
                    })
                except Exception:
                    continue

            time.sleep(random.uniform(2, 4))
        except Exception:
            continue

    return jobs


def load_sample_data() -> pd.DataFrame:
    """Load or generate sample Malaysian job market data for demo."""
    sample_path = os.path.join(DATA_DIR, 'sample_jobs.csv')
    if os.path.exists(sample_path):
        return pd.read_csv(sample_path)

    import numpy as np
    np.random.seed(2026)

    titles = [
        'Data Analyst', 'Data Scientist', 'Business Analyst', 'AI Engineer',
        'Machine Learning Engineer', 'Data Engineer', 'BI Developer',
        'Python Developer', 'Software Engineer', 'Data Analytics Manager',
        'Junior Data Analyst', 'Senior Data Scientist', 'Analytics Consultant',
        'Procurement Analyst', 'Supply Chain Analyst', 'Digital Marketing Analyst',
        'Financial Analyst', 'Operations Analyst', 'Market Research Analyst',
    ]

    companies = [
        'Petronas', 'Maybank', 'CIMB Group', 'Top Glove', 'AirAsia',
        'Grab Malaysia', 'Shopee Malaysia', 'Lazada Malaysia', 'Maxis',
        'CelcomDigi', 'TM (Telekom Malaysia)', 'Sunway Group', 'Genting Malaysia',
        'Gamuda Berhad', 'IOI Group', 'MISC Berhad', 'Dialog Group',
        'Public Bank', 'Hong Leong Bank', 'JobStreet Malaysia',
    ]

    locations = [
        'Kuala Lumpur', 'Selangor', 'Penang', 'Johor', 'Kuala Lumpur',
        'Selangor', 'Penang', 'Kuala Lumpur', 'Selangor', 'Remote',
        'Cyberjaya', 'Petaling Jaya', 'Kuala Lumpur', 'Penang', 'Johor',
    ]

    skills_pool = [
        'Python, SQL, Tableau', 'Python, R, Machine Learning', 'SQL, Excel, Power BI',
        'Python, TensorFlow, NLP', 'Python, scikit-learn, Deep Learning',
        'SQL, ETL, Apache Spark', 'Power BI, SQL, DAX',
        'Python, Django, PostgreSQL', 'Java, Spring Boot, AWS',
        'Python, Tableau, BigQuery', 'SQL, Excel, Data Visualization',
        'Python, PyTorch, MLOps', 'R, SAS, Statistical Modeling',
        'Excel, SAP, Power BI', 'Python, SQL, Supply Chain Analytics',
        'Google Analytics, SQL, Excel', 'Excel, Bloomberg, Python',
        'SQL, Python, Process Mining', 'SPSS, Excel, Survey Design',
    ]

    salary_ranges = [
        (3000, 5000), (4000, 7000), (5000, 9000), (6000, 10000),
        (7000, 12000), (8000, 14000), (9000, 15000), (3500, 5500),
        (4500, 8000), (10000, 18000), (12000, 22000),
    ]

    n = 200
    data = []
    for _ in range(n):
        title = np.random.choice(titles)
        idx = np.random.choice(len(salary_ranges), p=[0.25, 0.2, 0.15, 0.12, 0.10, 0.08, 0.05, 0.2, 0.12, 0.03, 0.02])
        salary_range = salary_ranges[idx]
        data.append({
            'title': title,
            'company': np.random.choice(companies),
            'location': np.random.choice(locations),
            'salary_min': np.random.randint(salary_range[0], salary_range[0] + 2000),
            'salary_max': np.random.randint(salary_range[1] - 2000, salary_range[1]),
            'skills': np.random.choice(skills_pool),
            'experience': np.random.choice(['Fresh Graduate', '1-3 years', '3-5 years', '5+ years']),
            'source': np.random.choice(['JobStreet', 'Hiredly', 'LinkedIn', 'MauKerja']),
            'posted_date': (datetime.now() - pd.Timedelta(days=np.random.randint(1, 60))).strftime('%Y-%m-%d'),
        })

    df = pd.DataFrame(data)
    df.to_csv(sample_path, index=False)
    return df


def fetch_jobs(keywords: list = None, pages_per_keyword: int = 2) -> pd.DataFrame:
    """
    Main function: scrape jobs for given keywords and return as DataFrame.
    Falls back to sample data for demo if live scraping fails.
    """
    keywords = keywords or ['data analyst', 'data scientist', 'business analyst']
    all_jobs = []

    for kw in keywords:
        try:
            jobs = scrape_hh_malaysia(kw, pages_per_keyword)
            if not jobs:
                jobs = scrape_jobstreet(kw, pages_per_keyword)
            all_jobs.extend(jobs)
        except Exception:
            continue

    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.to_csv(os.path.join(DATA_DIR, f'jobs_{datetime.now().strftime("%Y%m%d")}.csv'), index=False)
        return df

    # Fallback to sample data
    return load_sample_data()


if __name__ == '__main__':
    df = fetch_jobs(['data analyst'])
    print(f"Found {len(df)} jobs")
    print(df.head())
