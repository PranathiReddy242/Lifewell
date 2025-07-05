import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import datetime
import random
import json
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="LifeWell - AI Wellness Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #4CAF50, #2196F3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
}

.mood-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.productivity-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.quote-card {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    font-style: italic;
}

.stTextArea textarea {
    border-radius: 10px;
    border: 2px solid #e0e0e0;
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #4CAF50;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = []

if 'daily_entries' not in st.session_state:
    st.session_state.daily_entries = {}

# Motivational quotes database
QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Life is what happens to you while you're busy making other plans. - John Lennon",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "The only impossible journey is the one you never begin. - Tony Robbins",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Your limitation—it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones."
]

# AI Image prompts based on mood
IMAGE_PROMPTS = {
    "positive": [
        "A vibrant sunrise over mountains, digital art, inspiring and uplifting",
        "A person reaching the summit of a mountain, golden hour lighting, triumphant",
        "Colorful hot air balloons floating in a clear blue sky, dreamlike",
        "A path through a lush green forest with sunlight filtering through trees"
    ],
    "negative": [
        "A calm ocean at sunset, peaceful and serene, digital art",
        "A cozy reading nook with soft lighting and plants, comforting",
        "A gentle rain on a window with a warm cup of tea, soothing",
        "A lighthouse standing strong against gentle waves, hopeful"
    ],
    "neutral": [
        "A minimalist zen garden with smooth stones, peaceful",
        "A quiet lake with perfect reflections, serene and balanced",
        "A simple desk setup with plants and natural light, focused",
        "A winding path through rolling hills, journey and possibility"
    ]
}

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        return "positive", "😊", polarity
    elif polarity < -0.1:
        return "negative", "😔", polarity
    else:
        return "neutral", "😐", polarity

def get_productivity_advice(mood, polarity_score):
    """Get productivity advice based on mood"""
    advice = {
        "positive": [
            "🚀 You're feeling great! This is the perfect time to tackle your biggest, most challenging task.",
            "💪 Channel this positive energy into your most important project. You've got this!",
            "🎯 Your mood is perfect for deep work. Focus on one major goal today.",
            "⚡ Strike while the iron is hot! Use this momentum to make significant progress."
        ],
        "negative": [
            "🌱 It's okay to feel down sometimes. Break your tasks into tiny, 5-minute chunks.",
            "🤗 Be gentle with yourself today. Focus on small wins and celebrate them.",
            "🧘 Take a few deep breaths. Start with the easiest task to build momentum.",
            "💚 Remember: progress, not perfection. Every small step counts."
        ],
        "neutral": [
            "🎯 You're in a balanced state. Perfect for steady, consistent work.",
            "📝 Make a simple to-do list with 3 main priorities for today.",
            "⏰ Use the Pomodoro technique: 25 minutes work, 5 minutes break.",
            "🌟 Neutral can be powerful. Focus on building good habits today."
        ]
    }
    
    return random.choice(advice[mood])

def create_mood_chart(mood_data):
    """Create a mood trend chart"""
    if not mood_data:
        return None
    
    df = pd.DataFrame(mood_data)
    df['date'] = pd.to_datetime(df['date'])
    
    fig = px.line(df, x='date', y='polarity_score', 
                  title='Your Mood Journey Over Time',
                  labels={'polarity_score': 'Mood Score', 'date': 'Date'},
                  color_discrete_sequence=['#4CAF50'])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        title_font_size=20,
        title_x=0.5
    )
    
    # Add mood zones
    fig.add_hline(y=0.1, line_dash="dash", line_color="green", 
                  annotation_text="Positive Zone", annotation_position="bottom right")
    fig.add_hline(y=-0.1, line_dash="dash", line_color="red", 
                  annotation_text="Negative Zone", annotation_position="top right")
    
    return fig

def export_to_csv(mood_data):
    """Export mood data to CSV"""
    if not mood_data:
        return None
    
    df = pd.DataFrame(mood_data)
    csv = df.to_csv(index=False)
    return csv

def main():
    # Header
    st.markdown('<h1 class="main-header">🌱 LifeWell</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Your AI-Powered Wellness & Productivity Companion</p>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 📝 Daily Check-In")
        st.markdown("Share how you're feeling today. Your AI companion will analyze your mood and provide personalized support.")
        
        # Journal input
        journal_entry = st.text_area(
            "How are you feeling today?",
            placeholder="Express your thoughts, feelings, and experiences here...",
            height=150,
            help="Be honest about your emotions. This helps me provide better support."
        )
        
        if st.button("✨ Analyze My Mood", type="primary"):
            if journal_entry:
                # Analyze sentiment
                mood, emoji, polarity = analyze_sentiment(journal_entry)
                
                # Store the entry
                today = datetime.date.today().isoformat()
                entry_data = {
                    'date': today,
                    'entry': journal_entry,
                    'mood': mood,
                    'emoji': emoji,
                    'polarity_score': polarity,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                st.session_state.mood_data.append(entry_data)
                st.session_state.daily_entries[today] = entry_data
                
                # Display results
                st.markdown("---")
                
                # Mood Analysis Card
                st.markdown(f"""
                <div class="mood-card">
                    <h3>🧠 Mood Analysis</h3>
                    <p><strong>Detected Mood:</strong> {mood.title()} {emoji}</p>
                    <p><strong>Emotional Intensity:</strong> {abs(polarity):.2f}/1.0</p>
                    <p><strong>Analysis:</strong> Your journal entry shows a {mood} emotional tone with a polarity score of {polarity:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Productivity Advice Card
                advice = get_productivity_advice(mood, polarity)
                st.markdown(f"""
                <div class="productivity-card">
                    <h3>🎯 Personalized Productivity Advice</h3>
                    <p>{advice}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Motivational Quote Card
                quote = random.choice(QUOTES)
                st.markdown(f"""
                <div class="quote-card">
                    <h3>💭 Daily Inspiration</h3>
                    <p>"{quote}"</p>
                </div>
                """, unsafe_allow_html=True)
                
                # AI Image Prompt
                image_prompt = random.choice(IMAGE_PROMPTS[mood])
                st.markdown("### 🎨 AI Image Inspiration")
                st.info(f"**Copy this prompt to Bing Image Creator or DALL-E:**\n\n{image_prompt}")
                
                st.success("✅ Your daily check-in has been recorded!")
                
            else:
                st.warning("Please write something in your journal first.")
    
    with col2:
        # Sidebar content
        st.markdown("## 📊 Your Wellness Dashboard")
        
        # Quick stats
        if st.session_state.mood_data:
            total_entries = len(st.session_state.mood_data)
            recent_mood = st.session_state.mood_data[-1]['mood']
            recent_emoji = st.session_state.mood_data[-1]['emoji']
            
            avg_polarity = sum(entry['polarity_score'] for entry in st.session_state.mood_data) / total_entries
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Entries", total_entries)
            with col_b:
                st.metric("Recent Mood", f"{recent_mood.title()} {recent_emoji}")
            
            st.metric("Average Mood Score", f"{avg_polarity:.2f}")
            
            # Mood distribution
            mood_counts = {}
            for entry in st.session_state.mood_data:
                mood = entry['mood']
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            if mood_counts:
                st.markdown("### 📈 Mood Distribution")
                mood_df = pd.DataFrame(list(mood_counts.items()), columns=['Mood', 'Count'])
                fig_pie = px.pie(mood_df, values='Count', names='Mood', 
                                color_discrete_map={'positive': '#4CAF50', 'negative': '#f44336', 'neutral': '#ff9800'})
                fig_pie.update_layout(height=300)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        else:
            st.info("Start your wellness journey by writing your first journal entry!")
        
        # Export functionality
        st.markdown("### 📁 Export Your Data")
        if st.session_state.mood_data:
            csv_data = export_to_csv(st.session_state.mood_data)
            st.download_button(
                label="📥 Download Mood Report (CSV)",
                data=csv_data,
                file_name=f"lifewell_mood_report_{datetime.date.today().isoformat()}.csv",
                mime="text/csv"
            )
        
        # Reset data option
        if st.session_state.mood_data:
            st.markdown("### 🔄 Reset Data")
            if st.button("Clear All Data", type="secondary"):
                st.session_state.mood_data = []
                st.session_state.daily_entries = {}
                st.success("All data cleared!")
                st.rerun()

    # Mood trend chart (full width)
    if st.session_state.mood_data:
        st.markdown("---")
        st.markdown("## 📈 Your Mood Journey")
        
        chart = create_mood_chart(st.session_state.mood_data)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # Recent entries
        st.markdown("## 📜 Recent Entries")
        recent_entries = st.session_state.mood_data[-5:]  # Last 5 entries
        for entry in reversed(recent_entries):
            with st.expander(f"{entry['date']} - {entry['mood'].title()} {entry['emoji']}"):
                st.write(f"**Entry:** {entry['entry']}")
                st.write(f"**Mood Score:** {entry['polarity_score']:.2f}")
                st.write(f"**Timestamp:** {entry['timestamp']}")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🌱 LifeWell - Powered by AI for Your Wellness Journey</p>
        <p>Built with ❤️ using Streamlit, TextBlob, and Plotly</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()