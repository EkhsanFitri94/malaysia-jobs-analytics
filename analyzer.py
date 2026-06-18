"""
Malaysia Jobs Analyzer
Advanced analytics for job market data — trends, skills, salaries, insights.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter


def clean_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize job listings data."""
    df = df.copy()
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]

    # Clean salary text → numeric
    if 'salary' in df.columns and df['salary'].dtype == object:
        df = _parse_salary_text(df)

    # Ensure numeric salary columns
    for col in ['salary_min', 'salary_max']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate avg salary
    if 'salary_min' in df.columns and 'salary_max' in df.columns:
        df['salary_avg'] = (df['salary_min'] + df['salary_max']) / 2

    # Clean location
    if 'location' in df.columns:
        df['location'] = df['location'].astype(str).str.strip()
        df['state'] = df['location'].apply(_extract_state)

    # Parse posted_date
    if 'posted_date' in df.columns:
        df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce')

    # Categorize job titles
    if 'title' in df.columns:
        df['category'] = df['title'].apply(_categorize_title)

    # Normalize experience
    if 'experience' in df.columns:
        df['experience_level'] = df['experience'].apply(_normalize_experience)

    return df


def _parse_salary_text(df: pd.DataFrame) -> pd.DataFrame:
    """Parse salary strings like 'RM 3,000 - RM 5,000 per month'."""
    import re
    mins, maxs = [], []

    for s in df['salary']:
        numbers = re.findall(r'[\d,]+', str(s))
        numbers = [int(n.replace(',', '')) for n in numbers]
        if len(numbers) >= 2:
            mins.append(min(numbers[:2]))
            maxs.append(max(numbers[:2]))
        elif len(numbers) == 1:
            mins.append(numbers[0])
            maxs.append(numbers[0])
        else:
            mins.append(np.nan)
            maxs.append(np.nan)

    df['salary_min'] = mins
    df['salary_max'] = maxs
    return df


def _extract_state(location: str) -> str:
    """Extract Malaysian state from location string."""
    location = location.lower()
    state_map = {
        'kuala lumpur': 'Kuala Lumpur', 'kl': 'Kuala Lumpur',
        'selangor': 'Selangor', 'petaling jaya': 'Selangor', 'pj': 'Selangor',
        'shah alam': 'Selangor', 'subang': 'Selangor', 'cyberjaya': 'Selangor',
        'penang': 'Penang', 'pulau pinang': 'Penang', 'georgetown': 'Penang',
        'johor': 'Johor', 'johor bahru': 'Johor', 'jb': 'Johor',
        'melaka': 'Melaka', 'malacca': 'Melaka',
        'negeri sembilan': 'Negeri Sembilan', 'seremban': 'Negeri Sembilan',
        'perak': 'Perak', 'ipoh': 'Perak',
        'kedah': 'Kedah', 'alor setar': 'Kedah',
        'pahang': 'Pahang', 'kuantan': 'Pahang',
        'terengganu': 'Terengganu',
        'kelantan': 'Kelantan',
        'sabah': 'Sabah', 'kota kinabalu': 'Sabah', 'kk': 'Sabah',
        'sarawak': 'Sarawak', 'kuching': 'Sarawak',
        'remote': 'Remote',
    }
    for key, state in state_map.items():
        if key in location:
            return state
    return 'Other'


def _categorize_title(title: str) -> str:
    """Categorize job title into broad groups."""
    title = title.lower()
    if any(k in title for k in ['data scientist', 'ml engineer', 'machine learning', 'ai engineer', 'artificial intelligence']):
        return 'AI & Machine Learning'
    if any(k in title for k in ['data analyst', 'analytics', 'bi ', 'business intelligence', 'data']):
        return 'Data & Analytics'
    if any(k in title for k in ['data engineer', 'etl', 'big data']):
        return 'Data Engineering'
    if any(k in title for k in ['software', 'developer', 'python dev', 'backend', 'frontend', 'full stack', 'web dev', 'java dev', 'engineer']):
        return 'Software & IT'
    if any(k in title for k in ['procurement', 'supply chain', 'logistics', 'inventory', 'warehouse', 'shipping']):
        return 'Supply Chain & Logistics'
    if any(k in title for k in ['financial', 'finance', 'accounting', 'accountant', 'auditor', 'tax', 'bookkeeping']):
        return 'Finance & Accounting'
    if any(k in title for k in ['marketing', 'digital market', 'brand', 'social media', 'content', 'seo', 'sem']):
        return 'Marketing & Creative'
    if any(k in title for k in ['telecommunication', 'telco', 'network', 'wireless', 'fiber', 'broadband', 'rf ', 'radio']):
        return 'Telecommunications'
    if any(k in title for k in ['human resource', 'hr ', 'recruitment', 'recruiter', 'talent', 'payroll', 'compensation']):
        return 'Human Resources'
    if any(k in title for k in ['admin', 'administrative', 'office', 'clerical', 'secretary', 'reception', 'personal assistant', 'executive assistant']):
        return 'Administration'
    if any(k in title for k in ['nurse', 'doctor', 'medical', 'pharmacist', 'healthcare', 'clinic', 'hospital']):
        return 'Healthcare'
    if any(k in title for k in ['teacher', 'lecturer', 'education', 'trainer', 'tutor', 'academic']):
        return 'Education & Training'
    if any(k in title for k in ['sales', 'business dev', 'account manager', 'retail', 'merchandising']):
        return 'Sales & Business Development'
    if any(k in title for k in ['customer service', 'support', 'call center', 'helpdesk']):
        return 'Customer Service'
    if any(k in title for k in ['construction', 'civil engineer', 'architect', 'site ', 'project manager', 'quantity survey', 'm&e', 'mechanical', 'electrical']):
        return 'Construction & Engineering'
    if any(k in title for k in ['design', 'graphic', 'ui ', 'ux ', 'video', 'photographer', 'multimedia']):
        return 'Design & Multimedia'
    if any(k in title for k in ['legal', 'lawyer', 'compliance', 'regulatory', 'paralegal']):
        return 'Legal & Compliance'
    if any(k in title for k in ['security', 'guard', 'safety', 'hse', 'occupational health']):
        return 'Safety & Security'
    if any(k in title for k in ['quality', 'qa ', 'qc ', 'testing', 'inspector']):
        return 'Quality Assurance'
    if any(k in title for k in ['manager', 'director', 'head of', 'vp ', 'chief ', 'ceo', 'coo', 'president']):
        return 'Management & Executive'
    return 'Other'


def _normalize_experience(exp: str) -> str:
    """Normalize experience level strings."""
    exp = str(exp).lower()
    if any(k in exp for k in ['fresh', 'entry', 'junior', '0-1', 'graduate']):
        return 'Entry Level'
    if any(k in exp for k in ['1-3', '2-3', 'associate']):
        return 'Junior (1-3 yrs)'
    if any(k in exp for k in ['3-5', '4-5', 'mid', 'senior']):
        return 'Mid-Level (3-5 yrs)'
    if any(k in exp for k in ['5+', '6+', 'lead', 'manager', 'head']):
        return 'Senior (5+ yrs)'
    return exp.title()


def salary_analysis(df: pd.DataFrame) -> dict:
    """Comprehensive salary analysis."""
    analysis = {}

    if 'salary_avg' not in df.columns:
        return analysis

    analysis['overall_median'] = df['salary_avg'].median()
    analysis['overall_mean'] = df['salary_avg'].mean()
    analysis['salary_range'] = (df['salary_avg'].min(), df['salary_avg'].max())

    # By category
    if 'category' in df.columns:
        analysis['by_category'] = (
            df.groupby('category')['salary_avg']
            .agg(['mean', 'median', 'count'])
            .round(0)
            .sort_values('median', ascending=False)
        )

    # By experience
    if 'experience_level' in df.columns:
        analysis['by_experience'] = (
            df.groupby('experience_level')['salary_avg']
            .agg(['mean', 'median', 'count'])
            .round(0)
        )

    # By location
    if 'state' in df.columns:
        analysis['by_state'] = (
            df.groupby('state')['salary_avg']
            .agg(['mean', 'median', 'count'])
            .round(0)
            .sort_values('count', ascending=False)
        )

    # Salary distribution
    analysis['distribution'] = _salary_bins(df)

    return analysis


def _salary_bins(df: pd.DataFrame) -> pd.DataFrame:
    """Create salary distribution bins."""
    if 'salary_avg' not in df.columns:
        return pd.DataFrame()

    bins = [0, 3000, 5000, 7000, 10000, 15000, 999999]
    labels = ['<RM3k', 'RM3k-5k', 'RM5k-7k', 'RM7k-10k', 'RM10k-15k', 'RM15k+']
    df['salary_bin'] = pd.cut(df['salary_avg'], bins=bins, labels=labels)
    return df['salary_bin'].value_counts().sort_index().reset_index()
# ^ FIX: added missing closing parenthesis for value_counts chain


def skill_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze most in-demand skills from job listings."""
    if 'skills' not in df.columns:
        return pd.DataFrame()

    all_skills = []
    for skills_str in df['skills'].dropna():
        for skill in str(skills_str).split(','):
            skill = skill.strip()
            if skill:
                all_skills.append(skill)

    counter = Counter(all_skills)
    skill_df = pd.DataFrame(
        counter.most_common(20),
        columns=['skill', 'count'],
    )
    skill_df['pct'] = (skill_df['count'] / len(df) * 100).round(1)
    return skill_df


def hiring_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze hiring trends over time."""
    if 'posted_date' not in df.columns:
        return pd.DataFrame()

    if not pd.api.types.is_datetime64_any_dtype(df['posted_date']):
        df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce')

    df['week'] = df['posted_date'].dt.to_period('W').astype(str)
    weekly = df.groupby('week').agg(
        job_count=('title', 'count'),
        avg_salary=('salary_avg', 'mean') if 'salary_avg' in df.columns else pd.Series(dtype=float),
    ).reset_index()
    weekly['avg_salary'] = weekly['avg_salary'].round(0)
    return weekly


def top_companies(df: pd.DataFrame) -> pd.DataFrame:
    """Top hiring companies."""
    if 'company' not in df.columns:
        return pd.DataFrame()

    company_stats = df.groupby('company').agg(
        openings=('title', 'count'),
        avg_salary=('salary_avg', 'mean') if 'salary_avg' in df.columns else pd.Series(dtype=float),
    ).reset_index()
    company_stats['avg_salary'] = company_stats['avg_salary'].round(0)
    return company_stats.sort_values('openings', ascending=False).head(15)


def generate_insights(df: pd.DataFrame) -> list:
    """Generate smart market insights."""
    insights = []
    salary = salary_analysis(df)

    # Insight 1: Salary benchmark
    if 'overall_median' in salary:
        insights.append({
            'icon': '💰',
            'title': 'Market Salary Benchmark',
            'detail': (
                f'Median salary for data roles in Malaysia is **RM{salary["overall_median"]:,.0f}** '
                f'(avg RM{salary["overall_mean"]:,.0f}). '
                f'Range: RM{salary["salary_range"][0]:,.0f} – RM{salary["salary_range"][1]:,.0f}.'
            ),
            'severity': 'info',
        })

    # Insight 2: Top category
    if 'by_category' in salary and not salary['by_category'].empty:
        top_cat = salary['by_category'].index[0]
        top_sal = salary['by_category'].iloc[0]['median']
        insights.append({
            'icon': '🏆',
            'title': f'Highest-Paying Category: {top_cat}',
            'detail': (
                f'**{top_cat}** roles command the highest median salary at '
                f'**RM{top_sal:,.0f}**. {int(salary["by_category"].iloc[0]["count"])} openings available.'
            ),
            'severity': 'info',
        })

    # Insight 3: Location concentration
    if 'state' in df.columns:
        top_state = df['state'].value_counts().index[0]
        state_pct = (df['state'].value_counts().iloc[0] / len(df)) * 100
        kl = df[df['state'] == 'Kuala Lumpur']
        kl_pct = (len(kl) / len(df)) * 100 if len(kl) > 0 else 0
        insights.append({
            'icon': '📍',
            'title': 'Job Concentration',
            'detail': (
                f'**{top_state}** dominates with {state_pct:.0f}% of listings. '
                f'Kuala Lumpur alone accounts for {kl_pct:.0f}%. '
                'Remote roles are growing but remain a small fraction.'
            ),
            'severity': 'info',
        })

    # Insight 4: Skill demand
    skills = skill_demand(df)
    if not skills.empty:
        top_3 = skills.head(3)['skill'].tolist()
        insights.append({
            'icon': '🔧',
            'title': 'Most In-Demand Skills',
            'detail': (
                f'**{top_3[0]}**, **{top_3[1]}**, and **{top_3[2]}** '
                f'appear in the most job listings. Python + SQL is the baseline expectation.'
            ),
            'severity': 'info',
        })

    # Insight 5: Entry level opportunity
    if 'experience_level' in df.columns:
        entry = df[df['experience_level'] == 'Entry Level']
        if len(entry) > 0:
            entry_pct = (len(entry) / len(df)) * 100
            entry_sal = entry['salary_avg'].mean() if 'salary_avg' in entry.columns else 0
            insights.append({
                'icon': '🎓',
                'title': 'Fresh Graduate Opportunity',
                'detail': (
                    f'**{int(entry_pct)}%** of listings are entry-level. '
                    f'Average starting salary: **RM{entry_sal:,.0f}**. '
                    'Strong demand for fresh grads with data skills.'
                ),
                'severity': 'info',
            })

    # Insight 6: Remote work
    if 'location' in df.columns:
        remote = df[df['location'].str.lower().str.contains('remote', na=False)]
        remote_pct = (len(remote) / len(df)) * 100
        insights.append({
            'icon': '🏠',
            'title': 'Remote Work Availability',
            'detail': (
                f'**{len(remote)} roles** ({remote_pct:.1f}%) offer remote work. '
                f'{"Growing trend — remote options are expanding." if remote_pct > 5 else "Still limited — most roles require on-site presence."}'
            ),
            'severity': 'info',
        })

    return insights
