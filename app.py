"""
Malaysia Jobs Analytics Dashboard
Full-stack data pipeline: scrape → analyze → visualize
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from scraper import load_sample_data, fetch_jobs
from analyzer import (
    clean_jobs, salary_analysis, skill_demand,
    hiring_trends, top_companies, generate_insights,
)

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Malaysia Jobs Analytics",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; }
    .metric-box {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-box .val {
        font-size: 1.7rem;
        font-weight: 800;
        color: #1a202c;
        margin: 0.1rem 0;
    }
    .metric-box .lbl {
        font-size: 0.78rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .insight {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #3182ce;
        margin-bottom: 0.7rem;
    }
    .insight.high { border-left-color: #e53e3e; }
    .insight.medium { border-left-color: #ed8936; }
    .insight h4 { margin: 0 0 0.3rem; font-size: 0.95rem; }
    .insight p { margin: 0; font-size: 0.87rem; color: #4a5568; }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/malaysia.png", width=64)
    st.title("🇲🇾 Malaysia Jobs")
    st.caption("Analytics Dashboard")
    st.markdown("---")

    st.subheader("📂 Data Source")
    data_option = st.radio(
        "Choose data source",
        ["📦 Sample Data (200 listings)", "🔍 Live Scrape (slow)"],
        help="Sample data covers data/analytics roles across Malaysia",
    )

    if data_option.startswith("🔍"):
        keywords = st.text_input(
            "Job keywords",
            value="data analyst, data scientist, business analyst",
            help="Comma-separated keywords to search",
        )
        pages = st.slider("Pages per keyword", 1, 5, 2)

    st.markdown("---")

    # Filters
    with st.expander("🔍 Filters", expanded=True):
        if 'df' in st.session_state:
            df = st.session_state.df

            if 'state' in df.columns:
                states = ['All'] + sorted(df['state'].dropna().unique().tolist())
                st.session_state.state_filter = st.selectbox('Location', states)

            if 'category' in df.columns:
                cats = ['All'] + sorted(df['category'].dropna().unique().tolist())
                st.session_state.cat_filter = st.selectbox('Job Category', cats)

            if 'experience_level' in df.columns:
                exps = ['All'] + sorted(df['experience_level'].dropna().unique().tolist())
                st.session_state.exp_filter = st.selectbox('Experience Level', exps)

            if 'salary_avg' in df.columns:
                min_sal = int(df['salary_avg'].min())
                max_sal = int(df['salary_avg'].max())
                st.session_state.salary_range = st.slider(
                    'Salary Range (RM)',
                    min_sal, max_sal,
                    (min_sal, max_sal),
                    step=500,
                )

    st.markdown("---")
    
    # Refresh button
    if st.button('🔄 Refresh Data', use_container_width=True, help='Clear cache and reload'):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Built by Ekhsan Fitri · Data Pipeline Project")

# ── Data Loading ─────────────────────────────────────────
if 'df' not in st.session_state:
    with st.spinner('Loading job market data...'):
        if data_option.startswith("📦"):
            df = load_sample_data()
        else:
            kw_list = [k.strip() for k in keywords.split(',')]
            df = fetch_jobs(kw_list, pages)

        df = clean_jobs(df)
        st.session_state.df = df
        st.session_state.state_filter = 'All'
        st.session_state.cat_filter = 'All'
        st.session_state.exp_filter = 'All'

df = st.session_state.df

# ── Apply Filters ────────────────────────────────────────
df_view = df.copy()
if st.session_state.get('state_filter', 'All') != 'All' and 'state' in df_view.columns:
    df_view = df_view[df_view['state'] == st.session_state.state_filter]
if st.session_state.get('cat_filter', 'All') != 'All' and 'category' in df_view.columns:
    df_view = df_view[df_view['category'] == st.session_state.cat_filter]
if st.session_state.get('exp_filter', 'All') != 'All' and 'experience_level' in df_view.columns:
    df_view = df_view[df_view['experience_level'] == st.session_state.exp_filter]
if 'salary_avg' in df_view.columns and 'salary_range' in st.session_state:
    lo, hi = st.session_state.salary_range
    df_view = df_view[(df_view['salary_avg'] >= lo) & (df_view['salary_avg'] <= hi)]

# ── Header ───────────────────────────────────────────────
st.title("🇲🇾 Malaysia Jobs Analytics")
st.markdown(f"*Real-time data pipeline: scrape → clean → analyze · {len(df_view):,} listings shown*")

# ── KPI Row ──────────────────────────────────────────────
median_sal = df_view['salary_avg'].median() if 'salary_avg' in df_view.columns else 0
mean_sal = df_view['salary_avg'].mean() if 'salary_avg' in df_view.columns else 0
unique_companies = df_view['company'].nunique() if 'company' in df_view.columns else 0
unique_locations = df_view['state'].nunique() if 'state' in df_view.columns else 0

cols = st.columns(5)
cols[0].markdown(f'<div class="metric-box"><div class="lbl">Total Listings</div><div class="val">{len(df_view):,}</div></div>', unsafe_allow_html=True)
cols[1].markdown(f'<div class="metric-box"><div class="lbl">Median Salary</div><div class="val">RM{median_sal:,.0f}</div></div>', unsafe_allow_html=True)
cols[2].markdown(f'<div class="metric-box"><div class="lbl">Avg Salary</div><div class="val">RM{mean_sal:,.0f}</div></div>', unsafe_allow_html=True)
cols[3].markdown(f'<div class="metric-box"><div class="lbl">Companies Hiring</div><div class="val">{unique_companies}</div></div>', unsafe_allow_html=True)
cols[4].markdown(f'<div class="metric-box"><div class="lbl">Locations</div><div class="val">{unique_locations}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Market Insights", "💰 Salary Analysis", "🔧 Skill Demand", "📋 Listings",
])

# ── Tab 1: Insights ──────────────────────────────────────
with tab1:
    st.subheader("🧠 Key Market Insights")
    insights = generate_insights(df_view)

    if not insights:
        st.info("Upload richer data for AI-generated insights.")

    for ins in insights:
        sev = ins.get('severity', 'info')
        st.markdown(f"""
        <div class="insight {sev}">
            <h4>{ins['icon']} {ins['title']}</h4>
            <p>{ins['detail']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🏢 Who's Hiring?")
    top_co = top_companies(df_view)
    if not top_co.empty:
        fig = px.bar(
            top_co,
            x='openings',
            y='company',
            orientation='h',
            color='avg_salary',
            color_continuous_scale='Blues',
            title='Top Hiring Companies',
            labels={'openings': 'Job Openings', 'company': ''},
        )
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    # Hiring trend
    trend = hiring_trends(df_view)
    if not trend.empty:
        st.subheader("📅 Hiring Trend (Weekly)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend['week'], y=trend['job_count'],
            mode='lines+markers', fill='tozeroy',
            name='Job Count', line_color='#3182ce',
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: Salary Analysis ───────────────────────────────
with tab2:
    st.subheader("💰 Salary Analysis")
    salary = salary_analysis(df_view)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### By Job Category")
        if 'by_category' in salary and not salary['by_category'].empty:
            fig = px.bar(
                salary['by_category'].reset_index(),
                x='median', y='category',
                orientation='h',
                color='median',
                text='median',
                color_continuous_scale='Greens',
                labels={'median': 'Median Salary (RM)', 'category': ''},
            )
            fig.update_traces(
                texttemplate='RM%{text:,.0f}',
                textposition='outside',
            )
            fig.update_layout(height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### By Experience Level")
        if 'by_experience' in salary and not salary['by_experience'].empty:
            fig = px.bar(
                salary['by_experience'].reset_index(),
                x='experience_level', y='median',
                color='median',
                text='median',
                color_continuous_scale='Oranges',
                labels={'median': 'Median Salary (RM)', 'experience_level': ''},
            )
            fig.update_traces(texttemplate='RM%{text:,.0f}', textposition='outside')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    # Salary distribution
    st.markdown("#### Salary Distribution")
    if 'distribution' in salary and not salary['distribution'].empty:
        dist = salary['distribution']
        fig = px.bar(
            dist, x='salary_bin', y='count',
            color='count', color_continuous_scale='Blues',
            labels={'salary_bin': 'Salary Range', 'count': 'Number of Jobs'},
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # By state
    st.markdown("#### Salary by Location")
    if 'by_state' in salary and not salary['by_state'].empty:
        by_state = salary['by_state'].reset_index().head(10)
        fig = px.bar(
            by_state,
            x='state', y='median',
            color='count',
            text='median',
            color_continuous_scale='Blues',
            labels={'median': 'Median Salary (RM)', 'state': '', 'count': 'Jobs'},
        )
        fig.update_traces(texttemplate='RM%{text:,.0f}', textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Skill Demand ──────────────────────────────────
with tab3:
    st.subheader("🔧 Most In-Demand Skills")

    col1, col2 = st.columns([3, 2])

    with col1:
        skills = skill_demand(df_view)
        if not skills.empty:
            fig = px.bar(
                skills.head(15),
                x='count', y='skill',
                orientation='h',
                color='count',
                text='pct',
                color_continuous_scale='Blues',
                labels={'count': 'Job Listings', 'skill': '', 'pct': '% of Jobs'},
            )
            fig.update_traces(
                texttemplate='%{text}%',
                textposition='outside',
            )
            fig.update_layout(height=450, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🎯 Skill Takeaway")
        if not skills.empty:
            top_skills = skills.head(5)['skill'].tolist()

            st.markdown("**Must-Have Skills:**")
            for i, s in enumerate(top_skills, 1):
                st.markdown(f"{i}. **{s}**")

            # Category breakdown
            if 'category' in df_view.columns:
                st.markdown("---")
                st.markdown("#### 📊 Category Breakdown")
                cat_counts = df_view['category'].value_counts()
                fig = px.pie(
                    values=cat_counts.values,
                    names=cat_counts.index,
                    hole=0.5,
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    # Experience demand
    if 'experience_level' in df_view.columns:
        st.markdown("---")
        st.markdown("#### 🎓 Demand by Experience")
        exp_counts = df_view['experience_level'].value_counts().reset_index()
        exp_counts.columns = ['level', 'count']

        fig = px.bar(
            exp_counts,
            x='level', y='count',
            color='count',
            color_continuous_scale='Greens',
            labels={'level': '', 'count': 'Openings'},
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 4: Listings ──────────────────────────────────────
with tab4:
    st.subheader("📋 Job Listings")

    display_cols = [c for c in ['title', 'company', 'location', 'salary_avg', 'experience', 'skills', 'source', 'posted_date'] if c in df_view.columns]

    st.dataframe(
        df_view[display_cols].sort_values('posted_date', ascending=False) if 'posted_date' in display_cols else df_view[display_cols],
        use_container_width=True,
        height=500,
        column_config={
            'title': st.column_config.TextColumn('Job Title', width='medium'),
            'company': st.column_config.TextColumn('Company'),
            'location': st.column_config.TextColumn('Location'),
            'salary_avg': st.column_config.NumberColumn('Avg Salary', format='RM%.0f'),
            'skills': st.column_config.TextColumn('Skills', width='large'),
        },
    )

    csv = df_view.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Filtered Results (CSV)",
        csv,
        f"malaysia_jobs_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
    )

# ── Footer ───────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>🇲🇾 Malaysia Jobs Analytics · Data Pipeline Project · "
    "<a href='https://github.com/EkhsanFitri94'>Ekhsan Fitri</a></small></center>",
    unsafe_allow_html=True,
)
