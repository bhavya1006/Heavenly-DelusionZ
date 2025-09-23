"""
Mental Health Analytics Engine
Analyzes chat conversations using Gemini AI to generate comprehensive mental health insights.
"""

import os
import json
from typing import List, Dict, Tuple
import google.generativeai as genai
from dotenv import load_dotenv
from analytics_schema import (
    MentalHealthAnalytics, 
    ChatAnalysisContext,
    MENTAL_HEALTH_PARAMETERS,
    SeverityLevel
)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Set it in the .env file.")

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)

class MentalHealthAnalyzer:
    """Core analytics engine for mental health assessment"""
    
    def __init__(self):
        # Use Gemini 2.5 Flash for better structured outputs
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def analyze_conversation(self, username: str, conversation_history: List[Dict], 
                           session_id: str = None) -> MentalHealthAnalytics:
        """
        Analyze a complete conversation to generate mental health insights.
        
        Args:
            username: User identifier
            conversation_history: List of message dictionaries with 'role' and 'content'
            session_id: Optional session identifier
            
        Returns:
            MentalHealthAnalytics: Comprehensive mental health assessment
        """
        
        # Prepare conversation context
        context = self._prepare_conversation_context(conversation_history)
        
        # Generate comprehensive analysis using structured output
        analytics_prompt = self._create_analysis_prompt(conversation_history, context)
        
        try:
            # Use structured output for reliable parsing
            response = self.model.generate_content(
                analytics_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": MentalHealthAnalytics.model_json_schema()
                }
            )
            
            # Parse the structured response
            analytics_data = json.loads(response.text)
            
            # Add user and session information
            analytics_data['user_id'] = username
            analytics_data['session_id'] = session_id
            
            # Create and return the analytics object
            return MentalHealthAnalytics(**analytics_data)
            
        except Exception as e:
            # Fallback to basic analysis if structured output fails
            print(f"Structured output failed, using fallback: {e}")
            return self._fallback_analysis(username, conversation_history, session_id)
    
    def _prepare_conversation_context(self, conversation_history: List[Dict]) -> ChatAnalysisContext:
        """Prepare context information about the conversation"""
        
        user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        assistant_messages = [msg['content'] for msg in conversation_history if msg['role'] in ['assistant', 'model']]
        
        # Estimate conversation quality based on message length and depth
        avg_user_msg_length = sum(len(msg) for msg in user_messages) / max(len(user_messages), 1)
        conversation_quality = min(10, (avg_user_msg_length / 50) * 5 + 5)  # Scale based on message depth
        
        # Simple topic extraction
        all_text = ' '.join(user_messages).lower()
        topics = []
        topic_keywords = {
            'anxiety': ['anxious', 'worry', 'nervous', 'panic', 'fear'],
            'depression': ['sad', 'depressed', 'hopeless', 'empty', 'down'],
            'stress': ['stress', 'pressure', 'overwhelmed', 'burnout'],
            'relationships': ['friend', 'family', 'relationship', 'partner', 'social'],
            'work_school': ['work', 'school', 'job', 'study', 'career', 'college'],
            'sleep': ['sleep', 'tired', 'exhausted', 'insomnia', 'rest'],
            'self_esteem': ['confidence', 'self-worth', 'inadequate', 'capable', 'failure']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                topics.append(topic)
        
        return ChatAnalysisContext(
            total_messages=len(conversation_history),
            conversation_length_minutes=len(conversation_history) * 2,  # Estimate 2 minutes per exchange
            topics_discussed=topics,
            emotional_journey=["initial_state", "exploration", "insights"],  # Simplified
            user_engagement_level=min(10, len(user_messages) / 3 * 10),
            conversation_quality=conversation_quality
        )
    
    def _create_analysis_prompt(self, conversation_history: List[Dict], 
                              context: ChatAnalysisContext) -> str:
        """Create a comprehensive prompt for mental health analysis"""
        
        # Format conversation for analysis
        conversation_text = ""
        for msg in conversation_history:
            role = "User" if msg['role'] == 'user' else "AI Assistant"
            conversation_text += f"{role}: {msg['content']}\n\n"
        
        prompt = f"""
You are a highly skilled clinical psychologist and mental health expert with extensive experience in youth psychology. Analyze the following conversation between a young person and an AI mental health companion. Provide a comprehensive, evidence-based assessment of their mental health state.

CONVERSATION CONTEXT:
- Total messages: {context.total_messages}
- Topics discussed: {', '.join(context.topics_discussed)}
- User engagement level: {context.user_engagement_level}/10
- Conversation quality: {context.conversation_quality}/10

CONVERSATION TO ANALYZE:
{conversation_text}

ANALYSIS INSTRUCTIONS:
Please provide a comprehensive mental health assessment following these guidelines:

1. **EVIDENCE-BASED SCORING**: Use the 0-10 scale where:
   - 0-2: Severe concerns requiring immediate attention
   - 3-4: Significant challenges needing professional support
   - 5-6: Moderate concerns with room for improvement
   - 7-8: Good mental health with minor areas to address
   - 9-10: Excellent mental health and coping

2. **PARAMETER ASSESSMENT**: For each mental health parameter, analyze:
   - Direct statements and expressions of the user
   - Implicit emotional indicators
   - Behavioral patterns mentioned
   - Coping strategies used
   - Language patterns and emotional tone

3. **YOUTH-SPECIFIC CONSIDERATIONS**: Account for:
   - Developmental stage appropriate expectations
   - Common youth mental health challenges
   - Academic and social pressures
   - Identity formation issues
   - Technology and social media impacts

4. **RISK ASSESSMENT**: Identify:
   - Immediate safety concerns
   - Concerning patterns requiring attention
   - Protective factors and strengths
   - Support system quality

5. **RECOMMENDATIONS**: Provide:
   - Actionable, age-appropriate suggestions
   - Evidence-based interventions
   - Professional resources when needed
   - Specific skills to develop

6. **CONFIDENCE LEVELS**: Base confidence on:
   - Depth and quality of conversation
   - Consistency of indicators
   - Amount of relevant information shared
   - Clarity of emotional expression

CRITICAL ASSESSMENT AREAS:

**Anxiety Assessment**: Look for worry patterns, physical symptoms mentioned, avoidance behaviors, catastrophic thinking, fear expressions, and anxiety management strategies.

**Depression Indicators**: Analyze mood descriptions, energy levels, hopelessness, self-worth statements, interest in activities, and social withdrawal patterns.

**Stress Management**: Evaluate pressure handling, overwhelm indicators, coping strategies, time management, and stress responses.

**Self-Esteem**: Assess self-talk patterns, confidence expressions, self-worth statements, achievement orientation, and identity concerns.

**Emotional Regulation**: Look at emotional intensity, mood stability, impulse control, anger management, and emotional awareness.

**Social Connections**: Evaluate relationship descriptions, social support quality, communication patterns, and isolation indicators.

**Cognitive Patterns**: Identify thinking distortions, problem-solving approaches, rumination patterns, and cognitive flexibility.

**Coping Mechanisms**: Analyze stress responses, healthy vs. unhealthy coping, resilience indicators, and adaptation strategies.

Please provide your assessment in the exact JSON format specified by the schema, ensuring all required fields are included with appropriate data types and value ranges.
"""
        return prompt
    
    def _fallback_analysis(self, username: str, conversation_history: List[Dict], 
                          session_id: str = None) -> MentalHealthAnalytics:
        """Fallback analysis when structured output fails"""
        
        # Simple keyword-based analysis as fallback
        all_text = ' '.join([msg['content'] for msg in conversation_history if msg['role'] == 'user']).lower()
        
        # Basic parameter scoring based on keywords
        def score_parameter(param_name):
            param_info = MENTAL_HEALTH_PARAMETERS.get(param_name, {})
            indicators = param_info.get('indicators', [])
            reverse_indicators = param_info.get('reverse_indicators', [])
            
            positive_count = sum(1 for indicator in indicators if indicator in all_text)
            negative_count = sum(1 for indicator in reverse_indicators if indicator in all_text)
            
            # Simple scoring logic
            if positive_count > negative_count:
                return max(3, 7 - positive_count)  # Lower score for more negative indicators
            else:
                return min(7, 5 + negative_count)  # Higher score for more positive indicators
        
        # Create basic assessment structure
        from analytics_schema import (
            MentalHealthParameter, EmotionalState, CognitivePatternsAssessment,
            SocialConnectionAssessment, CopingMechanismsAssessment
        )
        import datetime
        
        # Basic parameter assessments
        def create_basic_parameter(name, score):
            return MentalHealthParameter(
                name=name,
                score=score,
                severity=SeverityLevel.MODERATE,
                confidence=0.5,
                indicators=["Limited data available"],
                recommendations=[f"Consider discussing {name} in more detail"]
            )
        
        return MentalHealthAnalytics(
            assessment_timestamp=datetime.datetime.now(),
            user_id=username,
            session_id=session_id,
            anxiety_level=create_basic_parameter("anxiety", score_parameter("anxiety_level")),
            depression_indicators=create_basic_parameter("depression", score_parameter("depression_indicators")),
            stress_level=create_basic_parameter("stress", score_parameter("stress_level")),
            self_esteem=create_basic_parameter("self_esteem", score_parameter("self_esteem")),
            emotional_regulation=create_basic_parameter("emotional_regulation", score_parameter("emotional_regulation")),
            motivation_level=create_basic_parameter("motivation", score_parameter("motivation_level")),
            sleep_quality=create_basic_parameter("sleep", score_parameter("sleep_quality")),
            emotional_state=EmotionalState(
                dominant_emotion="neutral",
                emotion_intensity=5.0,
                emotional_stability=5.0,
                emotional_awareness=5.0
            ),
            cognitive_patterns=CognitivePatternsAssessment(
                cognitive_distortions=[],
                thought_patterns={"positive_thinking": 5.0},
                problem_solving_ability=5.0,
                self_awareness=5.0
            ),
            social_connections=SocialConnectionAssessment(
                social_support_quality=5.0,
                relationship_satisfaction=5.0,
                social_isolation_level=5.0,
                communication_skills=5.0
            ),
            coping_mechanisms=CopingMechanismsAssessment(
                healthy_coping_strategies=["Seeking support"],
                unhealthy_coping_patterns=[],
                stress_management=5.0,
                resilience_level=5.0
            ),
            overall_mental_health_score=5.0,
            risk_level=SeverityLevel.MODERATE,
            immediate_concerns=["Need more conversation data for accurate assessment"],
            strengths=["Seeking help and support"],
            priority_recommendations=["Continue engaging in supportive conversations"],
            suggested_interventions=["Regular check-ins with mental health support"],
            progress_indicators=["Frequency of positive expressions", "Engagement level"],
            assessment_confidence=0.3,
            data_quality="Limited - insufficient conversation data",
            follow_up_needed=True
        )

# Global analyzer instance
analyzer = MentalHealthAnalyzer()

def get_mental_health_analytics(username: str, session_id: str = None) -> MentalHealthAnalytics:
    """
    Get mental health analytics for a user's conversation history.
    
    Args:
        username: User identifier
        session_id: Optional specific session to analyze
        
    Returns:
        MentalHealthAnalytics: Comprehensive assessment
    """
    
    # Import here to avoid circular imports
    from chatbot import get_memory_for_user
    from database import load_chat_history
    
    # Get conversation history
    if session_id:
        # Load specific session history
        chat_history = load_chat_history(session_id)
        conversation_history = []
        for message, response in chat_history:
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": response})
    else:
        # Use in-memory conversation history
        conversation_history = get_memory_for_user(username)
    
    if not conversation_history:
        # Return default assessment for new users
        return analyzer._fallback_analysis(username, [], session_id)
    
    # Generate analytics
    return analyzer.analyze_conversation(username, conversation_history, session_id)

def get_session_analytics(session_id: str, username: str) -> MentalHealthAnalytics:
    """Get analytics for a specific session"""
    return get_mental_health_analytics(username, session_id)

def get_user_overall_analytics(username: str) -> MentalHealthAnalytics:
    """Get overall analytics for a user across all sessions"""
    return get_mental_health_analytics(username)