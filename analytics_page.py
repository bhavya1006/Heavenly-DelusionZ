"""
Mental Health Analytics Dashboard
Streamlit page for displaying comprehensive mental health analytics and insights.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from analytics_engine import get_mental_health_analytics, get_session_analytics
from analytics_schema import MentalHealthAnalytics, SeverityLevel
from database import get_sessions

def show_analytics_page():
    """Main analytics dashboard page"""
    
    # Apply mobile CSS
    add_mobile_css()
    
    st.title("🧠 Mental Health Analytics Dashboard")
    st.markdown("### Comprehensive Youth Mental Wellness Insights")
    
    # Check if user is authenticated
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.warning("Please log in to view your mental health analytics.")
        return
    
    username = st.session_state["username"]
    
    # Sidebar for analytics options
    st.sidebar.markdown("## 📊 Analytics Options")
    
    analysis_type = st.sidebar.radio(
        "Select Analysis Type:",
        ["Overall Mental Health", "Session-Specific Analysis", "Progress Tracking"]
    )
    
    # Get user sessions for session-specific analysis
    user_sessions = get_sessions(username)
    
    if analysis_type == "Overall Mental Health":
        show_overall_analytics(username)
    elif analysis_type == "Session-Specific Analysis":
        show_session_analytics(username, user_sessions)
    else:
        show_progress_tracking(username, user_sessions)

def show_overall_analytics(username: str):
    """Display overall mental health analytics"""
    
    st.markdown("## 🌟 Overall Mental Health Assessment")
    
    # Generate analytics
    with st.spinner("🧠 Analyzing your mental health patterns..."):
        try:
            analytics = get_mental_health_analytics(username)
        except Exception as e:
            st.error(f"Error generating analytics: {e}")
            st.info("This might be because you haven't had enough conversations yet. Please have at least one chat session to generate meaningful analytics.")
            return
    
    # Create main dashboard layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Overall Mental Health Score
        st.markdown("### 🎯 Overall Mental Health Score")
        score_color = get_score_color(analytics.overall_mental_health_score)
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background-color: {score_color}20; border-radius: 10px; border: 2px solid {score_color};'>
            <h1 style='color: {score_color}; margin: 0;'>{analytics.overall_mental_health_score:.1f}/10</h1>
            <p style='margin: 0; font-size: 18px;'>{get_score_interpretation(analytics.overall_mental_health_score)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Risk Level
        st.markdown("### ⚠️ Risk Level")
        risk_color = get_risk_color(analytics.risk_level)
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: {risk_color}20; border-radius: 10px; border: 2px solid {risk_color};'>
            <h3 style='color: {risk_color}; margin: 0;'>{analytics.risk_level.value.replace('_', ' ').title()}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Assessment Confidence
        st.markdown("### 🎯 Confidence")
        confidence_percent = analytics.assessment_confidence * 100
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: #00838f20; border-radius: 10px; border: 2px solid #00838f;'>
            <h3 style='color: #00838f; margin: 0;'>{confidence_percent:.1f}%</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Mental Health Parameters Radar Chart
    st.markdown("## 📊 Mental Health Parameters")
    create_mental_health_radar(analytics)
    
    # Detailed Parameter Analysis
    st.markdown("## 📈 Detailed Parameter Analysis")
    create_parameter_bars(analytics)
    
    # Emotional State Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 😊 Emotional State")
        create_emotional_state_chart(analytics.emotional_state)
    
    with col2:
        st.markdown("### 🧠 Cognitive Patterns")
        create_cognitive_patterns_chart(analytics.cognitive_patterns)
    
    # Social and Coping Assessment
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Social Connections")
        create_social_connections_chart(analytics.social_connections)
    
    with col2:
        st.markdown("### 🛡️ Coping Mechanisms")
        create_coping_mechanisms_chart(analytics.coping_mechanisms)
    
    # Insights and Recommendations
    show_insights_and_recommendations(analytics)

def show_session_analytics(username: str, user_sessions):
    """Display session-specific analytics"""
    
    st.markdown("## 🎪 Session-Specific Analysis")
    
    if not user_sessions:
        st.info("No chat sessions found. Start a conversation to generate session analytics!")
        return
    
    # Session selector
    session_options = {session_name: session_id for session_id, session_name in user_sessions}
    selected_session_name = st.selectbox("Select a session to analyze:", list(session_options.keys()))
    selected_session_id = session_options[selected_session_name]
    
    # Generate session analytics
    with st.spinner(f"Analyzing session: {selected_session_name}..."):
        try:
            analytics = get_session_analytics(selected_session_id, username)
        except Exception as e:
            st.error(f"Error analyzing session: {e}")
            return
    
    # Session summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{analytics.overall_mental_health_score:.1f}/10")
    
    with col2:
        st.metric("Assessment Confidence", f"{analytics.assessment_confidence*100:.1f}%")
    
    with col3:
        st.metric("Risk Level", analytics.risk_level.value.replace('_', ' ').title())
    
    # Session-specific insights
    create_session_parameter_comparison(analytics)
    
    # Show session recommendations
    st.markdown("### 💡 Session-Specific Insights")
    if analytics.immediate_concerns:
        st.markdown("**🚨 Immediate Concerns:**")
        for concern in analytics.immediate_concerns:
            st.markdown(f"- {concern}")
    
    if analytics.strengths:
        st.markdown("**💪 Identified Strengths:**")
        for strength in analytics.strengths:
            st.markdown(f"- {strength}")

def show_progress_tracking(username: str, user_sessions):
    """Display progress tracking across sessions"""
    
    st.markdown("## 📈 Progress Tracking")
    
    if len(user_sessions) < 2:
        st.info("You need at least 2 chat sessions to track progress. Keep chatting to see your mental health journey!")
        return
    
    st.markdown("### 🌟 Mental Health Journey")
    
    # Simulate progress data (in a real app, you'd store historical analytics)
    progress_data = simulate_progress_data(user_sessions)
    create_progress_charts(progress_data)
    
    # Show trend analysis
    st.markdown("### 📊 Trend Analysis")
    show_trend_analysis(progress_data)

def create_mental_health_radar(analytics: MentalHealthAnalytics):
    """Create radar chart for mental health parameters"""
    
    categories = [
        'Anxiety Level',
        'Depression Indicators', 
        'Stress Level',
        'Self Esteem',
        'Emotional Regulation',
        'Motivation Level',
        'Sleep Quality'
    ]
    
    # Invert anxiety, depression, and stress scores for better visualization
    values = [
        10 - analytics.anxiety_level.score,  # Lower anxiety is better
        10 - analytics.depression_indicators.score,  # Lower depression is better
        10 - analytics.stress_level.score,  # Lower stress is better
        analytics.self_esteem.score,
        analytics.emotional_regulation.score,
        analytics.motivation_level.score,
        analytics.sleep_quality.score
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Mental Health Profile',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_parameter_bars(analytics: MentalHealthAnalytics):
    """Create horizontal bar chart for parameters"""
    
    parameters = [
        ('Anxiety Level', 10 - analytics.anxiety_level.score, analytics.anxiety_level.confidence),
        ('Depression', 10 - analytics.depression_indicators.score, analytics.depression_indicators.confidence),
        ('Stress Level', 10 - analytics.stress_level.score, analytics.stress_level.confidence),
        ('Self Esteem', analytics.self_esteem.score, analytics.self_esteem.confidence),
        ('Emotional Regulation', analytics.emotional_regulation.score, analytics.emotional_regulation.confidence),
        ('Motivation', analytics.motivation_level.score, analytics.motivation_level.confidence),
        ('Sleep Quality', analytics.sleep_quality.score, analytics.sleep_quality.confidence)
    ]
    
    df = pd.DataFrame(parameters, columns=['Parameter', 'Score', 'Confidence'])
    
    fig = px.bar(
        df, 
        x='Score', 
        y='Parameter',
        orientation='h',
        color='Confidence',
        color_continuous_scale='Viridis',
        title='Mental Health Parameters (Higher is Better)'
    )
    
    fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

def create_emotional_state_chart(emotional_state):
    """Create emotional state visualization"""
    
    # Emotion intensity gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = emotional_state.emotion_intensity,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Intensity: {emotional_state.dominant_emotion.title()}"},
        delta = {'reference': 5},
        gauge = {
            'axis': {'range': [None, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "lightgray"},
                {'range': [3, 7], 'color': "gray"},
                {'range': [7, 10], 'color': "darkgray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8}}))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional emotional metrics
    st.markdown(f"**Dominant Emotion:** {emotional_state.dominant_emotion.title()}")
    st.markdown(f"**Emotional Stability:** {emotional_state.emotional_stability:.1f}/10")
    st.markdown(f"**Emotional Awareness:** {emotional_state.emotional_awareness:.1f}/10")

def create_cognitive_patterns_chart(cognitive_patterns):
    """Create cognitive patterns visualization"""
    
    # Thinking patterns pie chart
    if cognitive_patterns.thought_patterns:
        labels = list(cognitive_patterns.thought_patterns.keys())
        values = list(cognitive_patterns.thought_patterns.values())
        
        fig = px.pie(
            values=values, 
            names=labels, 
            title='Thinking Patterns Distribution'
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cognitive metrics
    st.markdown(f"**Problem Solving:** {cognitive_patterns.problem_solving_ability:.1f}/10")
    st.markdown(f"**Self Awareness:** {cognitive_patterns.self_awareness:.1f}/10")
    
    if cognitive_patterns.cognitive_distortions:
        st.markdown("**Identified Cognitive Distortions:**")
        for distortion in cognitive_patterns.cognitive_distortions:
            st.markdown(f"- {distortion}")

def create_social_connections_chart(social_connections):
    """Create social connections visualization"""
    
    social_metrics = {
        'Support Quality': social_connections.social_support_quality,
        'Relationship Satisfaction': social_connections.relationship_satisfaction,
        'Social Connection': 10 - social_connections.social_isolation_level,  # Invert isolation
        'Communication Skills': social_connections.communication_skills
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(social_metrics.keys()),
            y=list(social_metrics.values()),
            marker_color=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        )
    ])
    
    fig.update_layout(
        title='Social Connection Metrics',
        yaxis_title='Score (0-10)',
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_coping_mechanisms_chart(coping_mechanisms):
    """Create coping mechanisms visualization"""
    
    # Coping effectiveness
    coping_metrics = {
        'Stress Management': coping_mechanisms.stress_management,
        'Resilience Level': coping_mechanisms.resilience_level
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(coping_metrics.keys()),
            y=list(coping_metrics.values()),
            marker_color=['#1f77b4', '#ff7f0e']
        )
    ])
    
    fig.update_layout(
        title='Coping Effectiveness',
        yaxis_title='Score (0-10)',
        height=250
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # List coping strategies
    if coping_mechanisms.healthy_coping_strategies:
        st.markdown("**💚 Healthy Coping Strategies:**")
        for strategy in coping_mechanisms.healthy_coping_strategies:
            st.markdown(f"- {strategy}")
    
    if coping_mechanisms.unhealthy_coping_patterns:
        st.markdown("**⚠️ Areas for Improvement:**")
        for pattern in coping_mechanisms.unhealthy_coping_patterns:
            st.markdown(f"- {pattern}")

def show_insights_and_recommendations(analytics: MentalHealthAnalytics):
    """Display insights and recommendations"""
    
    st.markdown("## 💡 Insights & Recommendations")
    
    # Create tabs for different types of insights
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Priority Actions", "💪 Strengths", "⚕️ Interventions", "📊 Progress Tracking"])
    
    with tab1:
        if analytics.priority_recommendations:
            st.markdown("### 🎯 Priority Recommendations")
            for i, rec in enumerate(analytics.priority_recommendations, 1):
                st.markdown(f"**{i}.** {rec}")
        
        if analytics.immediate_concerns:
            st.markdown("### 🚨 Areas Needing Attention")
            for concern in analytics.immediate_concerns:
                st.error(f"⚠️ {concern}")
    
    with tab2:
        if analytics.strengths:
            st.markdown("### 💪 Your Mental Health Strengths")
            for strength in analytics.strengths:
                st.success(f"✅ {strength}")
    
    with tab3:
        if analytics.suggested_interventions:
            st.markdown("### ⚕️ Suggested Interventions")
            for intervention in analytics.suggested_interventions:
                st.markdown(f"- {intervention}")
        
        if analytics.follow_up_needed:
            st.warning("🩺 Professional follow-up recommended. Consider speaking with a mental health professional.")
    
    with tab4:
        if analytics.progress_indicators:
            st.markdown("### 📊 Key Metrics to Track")
            for indicator in analytics.progress_indicators:
                st.markdown(f"- {indicator}")

def create_session_parameter_comparison(analytics: MentalHealthAnalytics):
    """Create comparison chart for session parameters"""
    
    parameters = [
        'Anxiety', 'Depression', 'Stress', 'Self Esteem', 
        'Emotional Regulation', 'Motivation', 'Sleep Quality'
    ]
    
    scores = [
        10 - analytics.anxiety_level.score,
        10 - analytics.depression_indicators.score,
        10 - analytics.stress_level.score,
        analytics.self_esteem.score,
        analytics.emotional_regulation.score,
        analytics.motivation_level.score,
        analytics.sleep_quality.score
    ]
    
    fig = px.bar(
        x=parameters,
        y=scores,
        title='Session Mental Health Snapshot',
        color=scores,
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def simulate_progress_data(user_sessions):
    """Simulate progress data for demonstration"""
    
    # In a real app, you would store historical analytics data
    dates = []
    scores = []
    sessions = []
    
    for i, (session_id, session_name) in enumerate(user_sessions[-5:]):  # Last 5 sessions
        dates.append(datetime.now() - timedelta(days=(len(user_sessions) - i)))
        scores.append(5.0 + np.random.normal(0, 1.5))  # Simulate some progress
        sessions.append(session_name)
    
    return pd.DataFrame({
        'Date': dates,
        'Overall_Score': scores,
        'Session': sessions
    })

def create_progress_charts(progress_data):
    """Create progress tracking charts"""
    
    fig = px.line(
        progress_data,
        x='Date',
        y='Overall_Score',
        title='Mental Health Progress Over Time',
        markers=True
    )
    
    fig.update_layout(
        yaxis_title='Overall Mental Health Score',
        yaxis_range=[0, 10],
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_trend_analysis(progress_data):
    """Show trend analysis"""
    
    if len(progress_data) >= 2:
        recent_trend = progress_data['Overall_Score'].iloc[-1] - progress_data['Overall_Score'].iloc[-2]
        
        if recent_trend > 0.5:
            st.success(f"📈 Positive trend: Your mental health score improved by {recent_trend:.1f} points!")
        elif recent_trend < -0.5:
            st.warning(f"📉 Declining trend: Your score decreased by {abs(recent_trend):.1f} points. Consider additional support.")
        else:
            st.info("📊 Stable trend: Your mental health score is relatively stable.")

def get_score_color(score):
    """Get color based on score"""
    if score >= 8:
        return "#4CAF50"  # Green
    elif score >= 6:
        return "#FF9800"  # Orange
    elif score >= 4:
        return "#FF5722"  # Red-Orange
    else:
        return "#F44336"  # Red

def get_risk_color(risk_level):
    """Get color based on risk level"""
    colors = {
        SeverityLevel.VERY_LOW: "#4CAF50",
        SeverityLevel.LOW: "#8BC34A", 
        SeverityLevel.MODERATE: "#FF9800",
        SeverityLevel.HIGH: "#FF5722",
        SeverityLevel.VERY_HIGH: "#F44336"
    }
    return colors.get(risk_level, "#FF9800")

def get_score_interpretation(score):
    """Get interpretation of score"""
    if score >= 8:
        return "Excellent Mental Health"
    elif score >= 6:
        return "Good Mental Health"
    elif score >= 4:
        return "Moderate Concerns"
    else:
        return "Significant Concerns"

# Mobile responsive CSS
def add_mobile_css():
    """Add mobile responsive CSS for analytics page"""
    st.markdown("""
    <style>
        /* Mobile responsive adjustments for analytics */
        @media (max-width: 768px) {
            .stPlotlyChart {
                height: 300px !important;
            }
            
            .metric-container {
                padding: 10px !important;
                margin: 5px 0 !important;
            }
            
            h1 {
                font-size: 1.5rem !important;
            }
            
            h2 {
                font-size: 1.3rem !important;
            }
            
            h3 {
                font-size: 1.1rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)