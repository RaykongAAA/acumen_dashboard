import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from enum import Enum

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

st.set_page_config(
    page_title="Acumen Operations Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme colors matching Acumen Group branding
TRUST_BLUE = "#1f4788"
CONFIDENCE_GOLD = "#c4a574"
PROFESSIONAL_GREY = "#878c93"
ALERT_RED = "#d32f2f"
SUCCESS_GREEN = "#388e3c"
WARNING_ORANGE = "#f57c00"

# ============================================================================
# DATA MODELS & TEMPLATES
# ============================================================================

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    CLIENT = "client"

class ServiceType(Enum):
    BOOKKEEPING = "Bookkeeping"
    AUDIT = "Audit & Assurance"
    TAX = "Tax & Compliance"
    SECRETARIAL = "Corporate Secretarial"
    HR = "HR & Payroll"
    ADVISORY = "Advisory"

class DeadlineStatus(Enum):
    OVERDUE = "Overdue"
    CRITICAL = "Critical (< 7 days)"
    WARNING = "Warning (< 14 days)"
    ON_TRACK = "On Track"

# ============================================================================
# DATA LOADING & INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'selected_country' not in st.session_state:
        st.session_state.selected_country = 'Both'

def load_template_data():
    """Load or create template data structures"""
    
    # Template for Clients
    clients_template = pd.DataFrame({
        'client_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
        'client_name': ['ABC Trading Sdn Bhd', 'XYZ Technologies Pte Ltd', 'Global Services Co', 'Tech Startup Sdn Bhd', 'Finance Advisory Ltd'],
        'country': ['Malaysia', 'Singapore', 'Singapore', 'Malaysia', 'Malaysia'],
        'entity': ['AAASB', 'AAAPL', 'AAAL', 'ACSSB', 'AAT'],
        'main_contact': ['Tan Wei Ming', 'Raj Kumar', 'Sarah Johnson', 'Lim Huey Jen', 'Michael Chua'],
        'email': ['tan@abc.com', 'raj@xyz.sg', 'sarah@global.com', 'lim@tech.com', 'michael@finance.com'],
        'services': [
            'Bookkeeping, Tax',
            'Audit, Tax, Secretarial',
            'Payroll, HR Advisory',
            'Bookkeeping, Secretarial',
            'Audit, Advisory'
        ],
        'status': ['Active', 'Active', 'At Risk', 'Active', 'Active'],
        'annual_revenue': [45000, 120000, 85000, 35000, 95000],
        'last_contact_date': [
            (datetime.now() - timedelta(days=5)).date(),
            (datetime.now() - timedelta(days=2)).date(),
            (datetime.now() - timedelta(days=30)).date(),
            (datetime.now() - timedelta(days=10)).date(),
            (datetime.now() - timedelta(days=3)).date(),
        ]
    })
    
    # Template for Staff
    staff_template = pd.DataFrame({
        'staff_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 'S008'],
        'staff_name': ['Priya Sharma', 'Ahmad Hassan', 'Ng Wei Chen', 'Lisa Wong', 'Vikram Patel', 'Siti Fatimah', 'David Lee', 'Emma Thompson'],
        'country': ['Malaysia', 'Malaysia', 'Singapore', 'Singapore', 'Malaysia', 'Singapore', 'Malaysia', 'Singapore'],
        'role': ['Senior Accountant', 'Audit Manager', 'Tax Specialist', 'Bookkeeper', 'HR Manager', 'Compliance Officer', 'Partner/Director', 'Senior Manager'],
        'billable_hours_target': [32, 35, 30, 28, 20, 30, 15, 32],
        'billable_hours_current': [28, 38, 25, 26, 18, 32, 14, 30],
        'assigned_clients': ['C001,C005', 'C002,C003', 'C002', 'C001,C004', 'C003', 'C002,C004', 'Multiple', 'C001,C002,C003'],
        'utilization_pct': [87.5, 108.6, 83.3, 92.9, 90.0, 106.7, 93.3, 93.8],
        'quality_score': [4.8, 4.5, 4.9, 4.6, 4.7, 4.4, 4.9, 4.8],
        'tasks_completed': [12, 8, 15, 18, 6, 9, 4, 11],
        'tasks_pending': [2, 3, 1, 2, 1, 2, 0, 1],
    })
    
    # Template for Deadlines
    deadlines_template = pd.DataFrame({
        'deadline_id': ['D001', 'D002', 'D003', 'D004', 'D005', 'D006', 'D007', 'D008', 'D009', 'D010'],
        'client_id': ['C001', 'C002', 'C003', 'C001', 'C004', 'C002', 'C005', 'C003', 'C004', 'C005'],
        'client_name': ['ABC Trading Sdn Bhd', 'XYZ Technologies Pte Ltd', 'Global Services Co', 'ABC Trading Sdn Bhd', 'Tech Startup Sdn Bhd', 'XYZ Technologies Pte Ltd', 'Finance Advisory Ltd', 'Global Services Co', 'Tech Startup Sdn Bhd', 'Finance Advisory Ltd'],
        'country': ['Malaysia', 'Singapore', 'Singapore', 'Malaysia', 'Malaysia', 'Singapore', 'Malaysia', 'Singapore', 'Malaysia', 'Malaysia'],
        'service_type': ['Tax Filing', 'Audit Report', 'Payroll Compliance', 'SSM Filing', 'Tax Filing', 'ACRA Filing', 'Audit Report', 'Tax Filing', 'AGM Notice', 'Annual Report'],
        'deadline_date': [
            datetime.now() + timedelta(days=3),
            datetime.now() + timedelta(days=8),
            datetime.now() + timedelta(days=15),
            datetime.now() + timedelta(days=1),
            datetime.now() + timedelta(days=45),
            datetime.now() + timedelta(days=20),
            datetime.now() - timedelta(days=2),
            datetime.now() + timedelta(days=12),
            datetime.now() + timedelta(days=60),
            datetime.now() + timedelta(days=25),
        ],
        'assigned_staff': ['Priya Sharma', 'Ahmad Hassan', 'Lisa Wong', 'Priya Sharma', 'Vikram Patel', 'Ng Wei Chen', 'David Lee', 'Siti Fatimah', 'Ahmad Hassan', 'Ng Wei Chen'],
        'status': ['In Progress', 'In Progress', 'Pending', 'Urgent', 'Planning', 'In Progress', 'Overdue', 'In Progress', 'Planning', 'Not Started'],
        'completion_pct': [60, 45, 0, 20, 0, 55, 0, 35, 0, 0],
    })
    
    # Template for Tasks/Projects
    tasks_template = pd.DataFrame({
        'task_id': ['T001', 'T002', 'T003', 'T004', 'T005', 'T006'],
        'client_id': ['C001', 'C002', 'C003', 'C001', 'C004', 'C005'],
        'task_description': ['Monthly bookkeeping review', 'Quarterly audit fieldwork', 'Payroll processing & filing', 'Annual tax return prep', 'Secretarial AGM setup', 'Mid-year financial advisory'],
        'assigned_to': ['Priya Sharma', 'Ahmad Hassan', 'Lisa Wong', 'Priya Sharma', 'Siti Fatimah', 'David Lee'],
        'status': ['Completed', 'In Progress', 'In Progress', 'Pending', 'In Progress', 'Completed'],
        'hours_estimated': [8, 40, 6, 20, 5, 12],
        'hours_actual': [7, 32, 6, 0, 6, 13],
        'due_date': [
            (datetime.now() - timedelta(days=2)).date(),
            (datetime.now() + timedelta(days=5)).date(),
            (datetime.now() + timedelta(days=2)).date(),
            (datetime.now() + timedelta(days=10)).date(),
            (datetime.now() + timedelta(days=3)).date(),
            (datetime.now() - timedelta(days=1)).date(),
        ],
    })
    
    # Template for Client Communications
    comms_template = pd.DataFrame({
        'comm_id': ['CM001', 'CM002', 'CM003', 'CM004', 'CM005'],
        'client_id': ['C001', 'C002', 'C003', 'C001', 'C004'],
        'client_name': ['ABC Trading Sdn Bhd', 'XYZ Technologies Pte Ltd', 'Global Services Co', 'ABC Trading Sdn Bhd', 'Tech Startup Sdn Bhd'],
        'communication_type': ['Email', 'Meeting', 'Phone Call', 'Email', 'Meeting'],
        'subject': ['Monthly report delivered', 'Audit planning session', 'Payroll discrepancy discussion', 'Year-end planning', 'Service review'],
        'date': [
            (datetime.now() - timedelta(days=1)).date(),
            (datetime.now() - timedelta(days=3)).date(),
            (datetime.now() - timedelta(days=5)).date(),
            (datetime.now() - timedelta(days=10)).date(),
            (datetime.now() - timedelta(days=7)).date(),
        ],
        'notes': [
            'Client satisfied with reporting',
            'Planning Q1 audit procedures',
            'Resolved - payroll corrected',
            'Discussed 2024 tax strategy',
            'Client discussed expanding services'
        ],
    })
    
    return {
        'clients': clients_template,
        'staff': staff_template,
        'deadlines': deadlines_template,
        'tasks': tasks_template,
        'communications': comms_template
    }

def get_deadline_status(deadline_date):
    """Determine deadline status based on days remaining"""
    today = datetime.now().date()

    if deadline_date is None or (isinstance(deadline_date, str) and deadline_date.strip() == ""):
        return "No deadline", "grey"

    # Parse text dates safely
    if isinstance(deadline_date, str):
        try:
            deadline = datetime.strptime(deadline_date, "%Y-%m-%d").date()
        except ValueError:
            try:
                parsed = pd.to_datetime(deadline_date, errors="coerce")
                if pd.isna(parsed):
                    return "Invalid deadline", "grey"
                deadline = parsed.date()
            except Exception:
                return "Invalid deadline", "grey"
    elif isinstance(deadline_date, datetime):
        deadline = deadline_date.date()
    elif isinstance(deadline_date, date):
        deadline = deadline_date
    else:
        return "Invalid deadline", "grey"

    days_remaining = (deadline - today).days

    if days_remaining < 0:
        return DeadlineStatus.OVERDUE.value, ALERT_RED
    elif days_remaining == 0:
        return "Due today", WARNING_ORANGE
    elif days_remaining <= 7:
        return DeadlineStatus.CRITICAL.value, WARNING_ORANGE
    elif days_remaining <= 14:
        return DeadlineStatus.WARNING.value, "#FFA500"
    else:
        return DeadlineStatus.ON_TRACK.value, SUCCESS_GREEN

# ============================================================================
# AUTHENTICATION & ACCESS CONTROL
# ============================================================================

def login_interface():
    """Simple login interface for demo"""
    st.markdown(f"""
        <style>
            .login-container {{
                max-width: 400px;
                margin: 100px auto;
                padding: 40px;
                border: 2px solid {TRUST_BLUE};
                border-radius: 8px;
                background: linear-gradient(135deg, {TRUST_BLUE}10 0%, {CONFIDENCE_GOLD}05 100%);
            }}
            .login-title {{
                color: {TRUST_BLUE};
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 30px;
                text-align: center;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Acumen Operations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("👤 Internal User", use_container_width=True, key="btn_internal"):
            st.session_state.user_role = UserRole.MANAGER.value
            st.session_state.current_user = "Ray (Manager)"
            st.rerun()
    
    with col2:
        if st.button("👥 Client View", use_container_width=True, key="btn_client"):
            st.session_state.user_role = UserRole.CLIENT.value
            st.session_state.current_user = "Client User"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.info("👉 For demo: Click 'Internal User' to see full dashboard, or 'Client View' for client-only access")

# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

def show_header():
    """Display dashboard header"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"<h1 style='color: {TRUST_BLUE}'>📊 Acumen Operations Dashboard</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: {PROFESSIONAL_GREY}; font-size: 14px;'>Malaysia & Singapore | Multi-Entity Management</p>", unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_role = None
            st.session_state.current_user = None
            st.rerun()
    
    st.divider()

def deadline_dashboard(data):
    """Deadline Management Dashboard"""
    st.markdown(f"<h2 style='color: {TRUST_BLUE}'>⏰ Deadline Management</h2>", unsafe_allow_html=True)
    
    deadlines = data['deadlines'].copy()
    deadlines['deadline_date'] = pd.to_datetime(deadlines['deadline_date'])
    deadlines['days_remaining'] = (deadlines['deadline_date'] - datetime.now()).dt.days
    
    # Add status column
    deadline_statuses = []
    colors = []
    for deadline in deadlines['deadline_date']:
        status, color = get_deadline_status(deadline)
        deadline_statuses.append(status)
        colors.append(color)
    
    deadlines['deadline_status'] = deadline_statuses
    deadlines['color'] = colors
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country_filter = st.multiselect("Country", options=['Malaysia', 'Singapore', 'Both'], default=['Both'], key="deadline_country")
    
    with col2:
        service_filter = st.multiselect("Service Type", options=deadlines['service_type'].unique(), default=deadlines['service_type'].unique(), key="deadline_service")
    
    with col3:
        status_filter = st.multiselect(
            "Status",
            options=['Overdue', 'Due today', 'Critical (< 7 days)', 'Warning (< 14 days)', 'On Track', 'No deadline', 'Invalid deadline'],
            default=['Overdue', 'Due today', 'Critical (< 7 days)', 'Warning (< 14 days)', 'On Track'],
            key="deadline_status"
        )
    
    # Apply filters
    filtered_deadlines = deadlines[
        (deadlines['country'].isin(country_filter) if 'Both' not in country_filter else True) &
        (deadlines['service_type'].isin(service_filter)) &
        (deadlines['deadline_status'].isin(status_filter))
    ]
    
    # Display critical deadlines (Overdue + Critical)
    critical = filtered_deadlines[filtered_deadlines['deadline_status'].isin(['Overdue', 'Critical (< 7 days)'])]
    
    if len(critical) > 0:
        st.markdown("### 🚨 Critical & Overdue Deadlines")
        for idx, row in critical.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1])
            with col1:
                st.markdown(f"**{row['client_name']}**")
            with col2:
                st.markdown(f"{row['service_type']}")
            with col3:
                st.markdown(f"📅 {row['deadline_date'].strftime('%d %b %Y')}")
            with col4:
                st.markdown(f"⏱️ {row['days_remaining']} days")
            with col5:
                badge_color = ALERT_RED if row['deadline_status'] == 'Overdue' else WARNING_ORANGE
                st.markdown(f"<span style='background-color: {badge_color}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px;'>{row['deadline_status']}</span>", unsafe_allow_html=True)
        st.divider()
    
    # Deadline timeline chart
    st.markdown("### 📈 Deadline Timeline")
    
    # Sort by deadline date
    timeline_data = filtered_deadlines.sort_values('deadline_date').head(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timeline_data['deadline_date'],
        y=timeline_data['client_name'],
        mode='markers+text',
        marker=dict(
            size=12,
            color=timeline_data['color'],
            line=dict(width=2, color='white')
        ),
        text=timeline_data['service_type'],
        textposition='top center',
        hovertemplate='<b>%{y}</b><br>%{text}<br>Due: %{x|%d %b %Y}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Upcoming Deadlines (Next 15)",
        xaxis_title="Deadline Date",
        yaxis_title="Client",
        height=400,
        template="plotly_white",
        hovermode='closest',
        xaxis=dict(gridcolor='#f0f0f0'),
        yaxis=dict(gridcolor='#f0f0f0')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Deadline summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overdue_count = len(filtered_deadlines[filtered_deadlines['deadline_status'] == 'Overdue'])
        st.metric("Overdue", overdue_count, delta=None, delta_color="inverse")
    
    with col2:
        critical_count = len(filtered_deadlines[filtered_deadlines['deadline_status'] == 'Critical (< 7 days)'])
        st.metric("Critical (< 7 days)", critical_count, delta=None, delta_color="inverse")
    
    with col3:
        warning_count = len(filtered_deadlines[filtered_deadlines['deadline_status'] == 'Warning (< 14 days)'])
        st.metric("Warning (< 14 days)", warning_count, delta=None)
    
    with col4:
        ontrack_count = len(filtered_deadlines[filtered_deadlines['deadline_status'] == 'On Track'])
        st.metric("On Track", ontrack_count, delta=None, delta_color="off")

def staff_performance_dashboard(data):
    """Staff Performance & Workload Dashboard"""
    st.markdown(f"<h2 style='color: {TRUST_BLUE}'>👥 Staff Performance & Workload</h2>", unsafe_allow_html=True)
    
    staff = data['staff'].copy()
    tasks = data['tasks'].copy()
    
    # Filter by country
    col1, col2 = st.columns([2, 1])
    with col1:
        country_filter = st.multiselect("Filter by Country", options=['Malaysia', 'Singapore'], default=['Malaysia', 'Singapore'], key="staff_country")
    
    staff_filtered = staff[staff['country'].isin(country_filter)]
    
    # Utilization Overview
    st.markdown("### 📊 Utilization & Capacity")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_utilization = staff_filtered['utilization_pct'].mean()
        st.metric("Avg Utilization", f"{avg_utilization:.1f}%", delta="Target: 85-100%")
    
    with col2:
        overloaded = len(staff_filtered[staff_filtered['utilization_pct'] > 100])
        st.metric("Overloaded Staff", overloaded, delta="Above 100%", delta_color="inverse")
    
    with col3:
        underutilized = len(staff_filtered[staff_filtered['utilization_pct'] < 70])
        st.metric("Underutilized", underutilized, delta="Below 70%")
    
    with col4:
        avg_quality = staff_filtered['quality_score'].mean()
        st.metric("Avg Quality Score", f"{avg_quality:.2f}/5.0", delta="Target: 4.5+")
    
    st.divider()
    
    # Workload Distribution Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💼 Workload Distribution by Staff")
        
        fig_util = px.bar(
            staff_filtered.sort_values('utilization_pct', ascending=False),
            x='staff_name',
            y='utilization_pct',
            color='utilization_pct',
            color_continuous_scale=['#4CAF50', '#FFC107', '#F44336'],
            range_color=[60, 120],
            title="",
            labels={'utilization_pct': 'Utilization %', 'staff_name': 'Staff'}
        )
        
        fig_util.add_hline(y=85, line_dash="dash", line_color="blue", annotation_text="Target Min", annotation_position="right")
        fig_util.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target Max", annotation_position="right")
        fig_util.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_util, use_container_width=True)
    
    with col2:
        st.markdown("### ⭐ Quality Scores")
        
        fig_quality = px.scatter(
            staff_filtered,
            x='quality_score',
            y='billable_hours_current',
            size='utilization_pct',
            color='country',
            hover_name='staff_name',
            title="",
            labels={'quality_score': 'Quality Score (out of 5)', 'billable_hours_current': 'Current Billable Hours'},
        )
        
        fig_quality.update_layout(height=400)
        st.plotly_chart(fig_quality, use_container_width=True)
    
    st.divider()
    
    # Staff Detail Table
    st.markdown("### 📋 Staff Detail Report")
    
    display_staff = staff_filtered[[
        'staff_name', 'country', 'role', 'billable_hours_current', 'billable_hours_target',
        'utilization_pct', 'quality_score', 'tasks_completed', 'tasks_pending'
    ]].copy()
    
    display_staff['billable_hours_current'] = display_staff['billable_hours_current'].astype(int)
    display_staff['billable_hours_target'] = display_staff['billable_hours_target'].astype(int)
    display_staff['utilization_pct'] = display_staff['utilization_pct'].apply(lambda x: f"{x:.1f}%")
    display_staff['quality_score'] = display_staff['quality_score'].apply(lambda x: f"{x:.2f}/5.0")
    
    st.dataframe(display_staff, use_container_width=True, hide_index=True)

def client_management_dashboard(data):
    """Client Management & Health Dashboard"""
    st.markdown(f"<h2 style='color: {TRUST_BLUE}'>👔 Client Management</h2>", unsafe_allow_html=True)
    
    clients = data['clients'].copy()
    comms = data['communications'].copy()
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country_filter = st.multiselect("Country", options=['Malaysia', 'Singapore'], default=['Malaysia', 'Singapore'], key="client_country")
    
    with col2:
        status_filter = st.multiselect("Status", options=['Active', 'At Risk', 'Inactive'], default=['Active', 'At Risk'], key="client_status")
    
    with col3:
        min_revenue = st.slider("Min Annual Revenue", 0, 150000, 0, 5000, key="client_revenue")
    
    clients_filtered = clients[
        (clients['country'].isin(country_filter)) &
        (clients['status'].isin(status_filter)) &
        (clients['annual_revenue'] >= min_revenue)
    ]
    
    # Client Health Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clients", len(clients_filtered), delta=f"{len(clients_filtered)} shown")
    
    with col2:
        active_clients = len(clients_filtered[clients_filtered['status'] == 'Active'])
        st.metric("Active Clients", active_clients)
    
    with col3:
        at_risk = len(clients_filtered[clients_filtered['status'] == 'At Risk'])
        st.metric("At Risk", at_risk, delta="Needs attention", delta_color="inverse")
    
    with col4:
        total_revenue = clients_filtered['annual_revenue'].sum()
        st.metric("Total Annual Revenue", f"${total_revenue:,.0f}")
    
    st.divider()
    
    # Client Health Dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Revenue by Country")
        
        revenue_by_country = clients_filtered.groupby('country')['annual_revenue'].sum()
        
        fig_revenue = px.pie(
            values=revenue_by_country.values,
            names=revenue_by_country.index,
            title="",
            color_discrete_map={'Malaysia': TRUST_BLUE, 'Singapore': CONFIDENCE_GOLD}
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Client Status Distribution")
        
        status_counts = clients_filtered['status'].value_counts()
        
        fig_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="",
            labels={'x': 'Status', 'y': 'Count'},
            color=status_counts.index,
            color_discrete_map={'Active': SUCCESS_GREEN, 'At Risk': ALERT_RED, 'Inactive': PROFESSIONAL_GREY}
        )
        
        fig_status.update_layout(height=400, showlegend=False, xaxis_tickangle=0)
        st.plotly_chart(fig_status, use_container_width=True)
    
    st.divider()
    
    # At-Risk Clients
    at_risk_clients = clients_filtered[clients_filtered['status'] == 'At Risk']
    if len(at_risk_clients) > 0:
        st.markdown("### 🚨 At-Risk Clients (Require Proactive Outreach)")
        
        for idx, client in at_risk_clients.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1.5])
            
            with col1:
                st.markdown(f"**{client['client_name']}**")
                st.caption(f"{client['main_contact']} | {client['email']}")
            
            with col2:
                st.markdown(f"📍 {client['country']}")
            
            with col3:
                days_since = (datetime.now().date() - client['last_contact_date']).days
                st.markdown(f"⏱️ {days_since} days since contact")
            
            with col4:
                st.markdown(f"💰 ${client['annual_revenue']:,}")
        
        st.divider()
    
    # Client Detail Table
    st.markdown("### 📋 Client Directory")
    
    display_clients = clients_filtered[[
        'client_name', 'country', 'main_contact', 'services', 'status', 'annual_revenue'
    ]].copy()
    
    display_clients['annual_revenue'] = display_clients['annual_revenue'].apply(lambda x: f"${x:,}")
    
    st.dataframe(display_clients, use_container_width=True, hide_index=True)
    
    # Recent Communications
    st.markdown("### 💬 Recent Client Communications")
    
    comms_filtered = comms[comms['client_id'].isin(clients_filtered['client_id'])]
    comms_display = comms_filtered[[
        'date', 'client_name', 'communication_type', 'subject', 'notes'
    ]].copy()
    
    comms_display = comms_display.sort_values('date', ascending=False)
    st.dataframe(comms_display, use_container_width=True, hide_index=True)

def tasks_dashboard(data):
    """Tasks & Project Progress Dashboard"""
    st.markdown(f"<h2 style='color: {TRUST_BLUE}'>✅ Tasks & Projects</h2>", unsafe_allow_html=True)
    
    tasks = data['tasks'].copy()
    
    # Task Status Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completed = len(tasks[tasks['status'] == 'Completed'])
        st.metric("Completed", completed)
    
    with col2:
        in_progress = len(tasks[tasks['status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with col3:
        pending = len(tasks[tasks['status'] == 'Pending'])
        st.metric("Pending", pending, delta="Needs attention", delta_color="inverse")
    
    with col4:
        completion_rate = (completed / len(tasks) * 100) if len(tasks) > 0 else 0
        st.metric("Overall Completion", f"{completion_rate:.0f}%")
    
    st.divider()
    
    # Task Progress Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Tasks by Status")
        
        status_counts = tasks['status'].value_counts()
        fig_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="",
            labels={'x': 'Status', 'y': 'Count'},
            color=status_counts.index,
            color_discrete_map={'Completed': SUCCESS_GREEN, 'In Progress': CONFIDENCE_GOLD, 'Pending': ALERT_RED}
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        st.markdown("### ⏱️ Estimated vs Actual Hours")
        
        fig_hours = px.scatter(
            tasks,
            x='hours_estimated',
            y='hours_actual',
            color='status',
            hover_name='task_description',
            title="",
            labels={'hours_estimated': 'Estimated Hours', 'hours_actual': 'Actual Hours'},
            color_discrete_map={'Completed': SUCCESS_GREEN, 'In Progress': CONFIDENCE_GOLD, 'Pending': ALERT_RED}
        )
        
        # Add reference line (equal hours)
        max_hours = max(tasks['hours_estimated'].max(), tasks['hours_actual'].max())
        fig_hours.add_trace(go.Scatter(
            x=[0, max_hours],
            y=[0, max_hours],
            mode='lines',
            name='Perfect Match',
            line=dict(dash='dash', color='gray'),
            hoverinfo='skip'
        ))
        
        st.plotly_chart(fig_hours, use_container_width=True)
    
    st.divider()
    
    # Task Detail Table
    st.markdown("### 📋 Task Details")
    
    display_tasks = tasks[[
        'task_description', 'assigned_to', 'status', 'hours_estimated', 'hours_actual', 'due_date'
    ]].copy()
    
    st.dataframe(display_tasks, use_container_width=True, hide_index=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    initialize_session_state()
    
    # Check if user is logged in
    if st.session_state.user_role is None:
        login_interface()
        return
    
    # Load data
    data = load_template_data()
    
    # Show header
    show_header()
    
    # Navigation sidebar
    st.sidebar.markdown(f"<h3 style='color: {TRUST_BLUE}'>Navigation</h3>", unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select View",
        options=["Dashboard Overview", "⏰ Deadlines", "👥 Staff Performance", "👔 Clients", "✅ Tasks"],
        label_visibility="collapsed"
    )
    
    # User info
    st.sidebar.divider()
    st.sidebar.markdown(f"**User:** {st.session_state.current_user}")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role.capitalize()}")
    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%d %b %Y, %H:%M')}")
    
    # Show selected page
    if page == "Dashboard Overview":
        st.markdown(f"<h2 style='color: {TRUST_BLUE}'>📊 Operations Overview</h2>", unsafe_allow_html=True)
        st.markdown("Welcome to Acumen Operations Dashboard. Select a section below or use the navigation menu on the left.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("⏰ **Deadlines**\n\nTrack all deadlines across Malaysia & Singapore")
        
        with col2:
            st.info("👥 **Staff Performance**\n\nMonitor workload and capacity")
        
        with col3:
            st.info("👔 **Client Management**\n\nManage client relationships and revenue")
        
        # Quick Stats
        st.divider()
        st.markdown("### 📈 Quick Statistics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            deadlines = data['deadlines'].copy()
            deadlines['deadline_date'] = pd.to_datetime(deadlines['deadline_date'])
            critical_count = len(deadlines[deadlines['days_remaining'] < 7])
            st.metric("Critical Deadlines", critical_count)
        
        with col2:
            staff = data['staff']
            overloaded = len(staff[staff['utilization_pct'] > 100])
            st.metric("Overloaded Staff", overloaded)
        
        with col3:
            clients = data['clients']
            at_risk = len(clients[clients['status'] == 'At Risk'])
            st.metric("At-Risk Clients", at_risk)
        
        with col4:
            tasks = data['tasks']
            pending = len(tasks[tasks['status'] == 'Pending'])
            st.metric("Pending Tasks", pending)
        
        with col5:
            total_revenue = clients['annual_revenue'].sum()
            st.metric("Total Revenue", f"${total_revenue/1000:.0f}K")
    
    elif page == "⏰ Deadlines":
        deadline_dashboard(data)
    
    elif page == "👥 Staff Performance":
        staff_performance_dashboard(data)
    
    elif page == "👔 Clients":
        client_management_dashboard(data)
    
    elif page == "✅ Tasks":
        tasks_dashboard(data)
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #878c93; font-size: 12px; padding: 20px;'>
            <p>Acumen Group Operations Dashboard | Malaysia & Singapore Corporate Services</p>
            <p>Confidential - Internal Use Only</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
