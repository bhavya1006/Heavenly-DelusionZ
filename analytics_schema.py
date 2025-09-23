"""
Mental Health Analytics Schema and Models
Defines the structure for analyzing youth mental health through AI-powered chat assessment.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
import datetime

class SeverityLevel(str, Enum):
    """Severity levels for mental health parameters"""
    VERY_LOW = "very_low"
    LOW = "low" 
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class MentalHealthParameter(BaseModel):
    """Individual mental health parameter assessment"""
    name: str = Field(description="Name of the mental health parameter")
    score: float = Field(ge=0, le=10, description="Score from 0-10 (0=very poor, 10=excellent)")
    severity: SeverityLevel = Field(description="Categorical severity level")
    confidence: float = Field(ge=0, le=1, description="AI confidence in this assessment (0-1)")
    indicators: List[str] = Field(description="Key phrases/behaviors that influenced this score")
    recommendations: List[str] = Field(description="Specific recommendations for improvement")

class EmotionalState(BaseModel):
    """Current emotional state assessment"""
    dominant_emotion: str = Field(description="Primary emotion detected (e.g., anxious, sad, hopeful)")
    emotion_intensity: float = Field(ge=0, le=10, description="Intensity of the dominant emotion (0-10)")
    emotional_stability: float = Field(ge=0, le=10, description="Emotional stability/volatility (0=very unstable, 10=very stable)")
    emotional_awareness: float = Field(ge=0, le=10, description="User's awareness of their emotions (0=unaware, 10=highly aware)")

class CognitivePatternsAssessment(BaseModel):
    """Assessment of cognitive patterns and thinking styles"""
    cognitive_distortions: List[str] = Field(description="Identified cognitive distortions (e.g., catastrophizing, all-or-nothing thinking)")
    thought_patterns: Dict[str, float] = Field(description="Thinking pattern scores (positive_thinking, rumination, etc.)")
    problem_solving_ability: float = Field(ge=0, le=10, description="Ability to think through problems constructively")
    self_awareness: float = Field(ge=0, le=10, description="Level of self-reflection and insight")

class SocialConnectionAssessment(BaseModel):
    """Assessment of social relationships and support systems"""
    social_support_quality: float = Field(ge=0, le=10, description="Quality of social support system")
    relationship_satisfaction: float = Field(ge=0, le=10, description="Satisfaction with relationships")
    social_isolation_level: float = Field(ge=0, le=10, description="Level of social isolation (0=very isolated, 10=well connected)")
    communication_skills: float = Field(ge=0, le=10, description="Effectiveness in communicating with others")

class CopingMechanismsAssessment(BaseModel):
    """Assessment of coping strategies and resilience"""
    healthy_coping_strategies: List[str] = Field(description="Identified healthy coping mechanisms")
    unhealthy_coping_patterns: List[str] = Field(description="Identified unhealthy coping patterns")
    stress_management: float = Field(ge=0, le=10, description="Effectiveness of stress management")
    resilience_level: float = Field(ge=0, le=10, description="Overall resilience and adaptability")

class MentalHealthAnalytics(BaseModel):
    """Comprehensive mental health analytics assessment"""
    assessment_timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    user_id: str = Field(description="User identifier")
    session_id: Optional[str] = Field(description="Chat session identifier")
    
    # Core mental health parameters
    anxiety_level: MentalHealthParameter = Field(description="Anxiety and worry assessment")
    depression_indicators: MentalHealthParameter = Field(description="Depression and mood assessment")
    stress_level: MentalHealthParameter = Field(description="Stress and pressure assessment")
    self_esteem: MentalHealthParameter = Field(description="Self-worth and confidence assessment")
    emotional_regulation: MentalHealthParameter = Field(description="Ability to manage emotions")
    motivation_level: MentalHealthParameter = Field(description="Drive and motivation assessment")
    sleep_quality: MentalHealthParameter = Field(description="Sleep patterns and quality")
    
    # Comprehensive assessments
    emotional_state: EmotionalState = Field(description="Current emotional state analysis")
    cognitive_patterns: CognitivePatternsAssessment = Field(description="Thinking patterns and cognitive health")
    social_connections: SocialConnectionAssessment = Field(description="Social relationships and support")
    coping_mechanisms: CopingMechanismsAssessment = Field(description="Coping strategies and resilience")
    
    # Overall assessment
    overall_mental_health_score: float = Field(ge=0, le=10, description="Comprehensive mental health score")
    risk_level: SeverityLevel = Field(description="Overall risk assessment")
    immediate_concerns: List[str] = Field(description="Areas requiring immediate attention")
    strengths: List[str] = Field(description="Identified mental health strengths")
    
    # Recommendations and insights
    priority_recommendations: List[str] = Field(description="Top 3-5 priority recommendations")
    suggested_interventions: List[str] = Field(description="Suggested therapeutic interventions")
    progress_indicators: List[str] = Field(description="Key metrics to track progress")
    
    # Confidence and metadata
    assessment_confidence: float = Field(ge=0, le=1, description="Overall confidence in this assessment")
    data_quality: str = Field(description="Quality of conversation data for analysis")
    follow_up_needed: bool = Field(description="Whether professional follow-up is recommended")

class ChatAnalysisContext(BaseModel):
    """Context information for analyzing a chat conversation"""
    total_messages: int = Field(description="Total number of messages in conversation")
    conversation_length_minutes: Optional[float] = Field(description="Estimated conversation duration")
    topics_discussed: List[str] = Field(description="Main topics covered in the conversation")
    emotional_journey: List[str] = Field(description="Emotional progression throughout conversation")
    user_engagement_level: float = Field(ge=0, le=10, description="Level of user engagement and openness")
    conversation_quality: float = Field(ge=0, le=10, description="Quality and depth of conversation")

# Parameter definitions for comprehensive assessment
MENTAL_HEALTH_PARAMETERS = {
    "anxiety_level": {
        "description": "Level of anxiety, worry, and nervousness",
        "indicators": ["worry", "nervous", "anxious", "panic", "fear", "overwhelmed", "racing thoughts"],
        "reverse_indicators": ["calm", "relaxed", "peaceful", "confident"]
    },
    "depression_indicators": {
        "description": "Signs of depression, sadness, and hopelessness", 
        "indicators": ["sad", "hopeless", "empty", "worthless", "depressed", "no energy", "no motivation"],
        "reverse_indicators": ["happy", "hopeful", "energetic", "motivated", "content"]
    },
    "stress_level": {
        "description": "Level of stress and pressure",
        "indicators": ["stressed", "pressure", "overwhelmed", "burned out", "exhausted"],
        "reverse_indicators": ["relaxed", "manageable", "balanced", "in control"]
    },
    "self_esteem": {
        "description": "Self-worth, confidence, and self-image",
        "indicators": ["confident", "proud", "capable", "worthy", "strong"],
        "reverse_indicators": ["worthless", "inadequate", "failure", "incompetent", "weak"]
    },
    "emotional_regulation": {
        "description": "Ability to manage and control emotions",
        "indicators": ["emotional control", "manage feelings", "stay calm", "regulate emotions"],
        "reverse_indicators": ["emotional outbursts", "can't control", "overwhelming emotions"]
    },
    "motivation_level": {
        "description": "Drive, enthusiasm, and goal-oriented behavior",
        "indicators": ["motivated", "driven", "enthusiastic", "goals", "ambitious"],
        "reverse_indicators": ["unmotivated", "apathetic", "no drive", "giving up", "listless"]
    },
    "sleep_quality": {
        "description": "Sleep patterns, quality, and rest",
        "indicators": ["good sleep", "well rested", "sleeping well", "refreshed"],
        "reverse_indicators": ["insomnia", "can't sleep", "tired", "exhausted", "sleep problems"]
    }
}