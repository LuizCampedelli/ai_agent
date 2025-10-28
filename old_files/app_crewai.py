import streamlit as st
import json
import datetime
from dental_crew import DentalCrewAI

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {
        "name": "",
        "age": "",
        "phone": "",
        "email": "",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
if 'dental_crew' not in st.session_state:
    st.session_state.dental_crew = DentalCrewAI()
if 'symptom_analysis' not in st.session_state:
    st.session_state.symptom_analysis = {}

# Streamlit app layout
def main():
    st.set_page_config(
        page_title="Dental AI Assistant with CrewAI",
        page_icon="🦷",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar
    render_sidebar()

    # Main area
    st.title("🦷 Dental Health Assistant with CrewAI")
    st.markdown("""
    **Advanced AI-powered dental anamnesis system** using multi-agent AI technology
    for comprehensive patient assessment.
    """)

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 AI Anamnesis",
        "📋 Symptom Analysis",
        "🖼️ Dental Imaging",
        "📊 Medical Records"
    ])

    with tab1:
        render_chat_interface()

    with tab2:
        render_analysis_interface()

    with tab3:
        render_imaging_interface()

    with tab4:
        render_records_interface()

def render_sidebar():
    """Render the sidebar"""
    with st.sidebar:
        st.header("👤 Patient Information")

        st.session_state.patient_data["name"] = st.text_input(
            "Full Name",
            value=st.session_state.patient_data["name"],
            placeholder="Patient name"
        )

        st.session_state.patient_data["age"] = st.text_input(
            "Age",
            value=st.session_state.patient_data["age"],
            placeholder="Age"
        )

        st.session_state.patient_data["phone"] = st.text_input(
            "Phone",
            value=st.session_state.patient_data["phone"],
            placeholder="Phone number"
        )

        st.session_state.patient_data["email"] = st.text_input(
            "Email",
            value=st.session_state.patient_data["email"],
            placeholder="Email address"
        )

        st.divider()
        st.header("🤖 AI Configuration")

        ai_mode = st.selectbox(
            "AI Mode:",
            ["CrewAI Multi-Agent", "Single Agent", "Rule-Based"]
        )

        # Show AI status
        st.success("✅ CrewAI System Active")
        st.info("3 specialized AI agents working together")

        st.divider()
        st.header("📊 Detected Symptoms")

        if st.session_state.symptom_analysis:
            for symptom, details in st.session_state.symptom_analysis.items():
                st.write(f"• **{symptom.capitalize()}**")
                if 'urgency' in details:
                    st.caption(f"Urgency: {details['urgency']}")

        st.divider()

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Conversation", use_container_width=True):
                reset_conversation()

        with col2:
            if st.button("📈 Analyze Case", use_container_width=True):
                analyze_full_case()

def render_chat_interface():
    """Main chat interface with CrewAI"""
    st.header("💬 AI Dental Anamnesis")
    st.markdown("""
    *Specialized AI agents are conducting your dental health assessment.
    Describe your symptoms in detail for comprehensive analysis.*
    """)

    # Display conversation
    for message in st.session_state.conversation:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**Patient**: {message['content']}")
                if message.get('timestamp'):
                    st.caption(f"({message['timestamp']})")
        else:
            with st.chat_message("assistant"):
                st.write(f"**Dental AI**: {message['content']}")
                if message.get('timestamp'):
                    st.caption(f"({message['timestamp']})")
                if message.get('agent_type'):
                    st.caption(f"👨‍⚕️ {message['agent_type']}")

    # Quick symptom prompts
    st.subheader("🚨 Common Dental Issues")
    cols = st.columns(4)

    with cols[0]:
        if st.button("Tooth Pain", use_container_width=True):
            process_user_input("I have tooth pain")

    with cols[1]:
        if st.button("Bleeding Gums", use_container_width=True):
            process_user_input("My gums are bleeding")

    with cols[2]:
        if st.button("Swelling", use_container_width=True):
            process_user_input("I have swelling in my mouth")

    with cols[3]:
        if st.button("Sensitivity", use_container_width=True):
            process_user_input("My teeth are sensitive")

    # Chat input
    user_input = st.chat_input("Describe your dental symptoms in detail...")

    if user_input:
        process_user_input(user_input)

def render_analysis_interface():
    """Symptom analysis interface"""
    st.header("📋 AI Symptom Analysis")

    if st.session_state.symptom_analysis:
        st.success("🤖 AI Analysis Complete")

        for symptom, analysis in st.session_state.symptom_analysis.items():
            with st.expander(f"🔍 {symptom.capitalize()} Analysis", expanded=True):
                if 'description' in analysis:
                    st.write(f"**Description**: {analysis['description']}")
                if 'urgency' in analysis:
                    urgency_color = "🔴" if "urgent" in analysis['urgency'].lower() else "🟡"
                    st.write(f"**Urgency**: {urgency_color} {analysis['urgency']}")
                if 'recommendations' in analysis:
                    st.write("**Recommendations**:")
                    for rec in analysis['recommendations']:
                        st.write(f"• {rec}")
    else:
        st.info("💬 Start a conversation in the chat tab to generate AI analysis")

        # Sample analysis preview
        st.subheader("Example AI Analysis")
        st.json({
            "tooth_pain": {
                "description": "Localized pain in posterior region, intermittent",
                "urgency": "Moderate - Schedule dental appointment",
                "recommendations": [
                    "Avoid hard foods on affected side",
                    "Use over-the-counter pain relief if needed",
                    "Schedule dental evaluation within 1-2 weeks"
                ]
            }
        })

def render_imaging_interface():
    """Dental imaging interface"""
    st.header("🖼️ Dental Imaging Analysis")
    st.info("""
    **Coming Soon**: AI-powered analysis of dental radiographs and intraoral photos.
    Our imaging specialist agent will analyze uploaded dental images.
    """)

    uploaded_file = st.file_uploader(
        "Upload dental images for AI analysis",
        type=['png', 'jpg', 'jpeg', 'dcm'],
        help="Panoramic X-rays, periapical films, intraoral photos"
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded dental image", use_container_width=True)
        st.warning("🦷 Dental image analysis feature in development")

def render_records_interface():
    """Medical records interface"""
    st.header("📊 Medical Records & Export")

    if st.session_state.conversation:
        # Summary card
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Conversation Length", f"{len(st.session_state.conversation)} messages")

        with col2:
            symptoms_count = len(st.session_state.symptom_analysis)
            st.metric("Symptoms Detected", symptoms_count)

        with col3:
            st.metric("AI Agents", "3 specialized")

        # Export options
        st.subheader("📤 Export Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Export JSON", use_container_width=True):
                export_to_json()

        with col2:
            if st.button("📄 Medical Report", use_container_width=True):
                generate_medical_report()

        with col3:
            if st.button("🤖 AI Analysis Report", use_container_width=True):
                generate_ai_report()

        # Conversation transcript
        st.subheader("🗣️ Conversation Transcript")
        for i, message in enumerate(st.session_state.conversation):
            if message["role"] == "user":
                st.info(f"**Patient**: {message['content']}")
            else:
                st.success(f"**AI Assistant**: {message['content']}")
    else:
        st.info("💬 No conversation data available. Start a chat to generate records.")

def process_user_input(user_input):
    """Process user input with CrewAI"""
    # Add user message
    st.session_state.conversation.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

    # Generate AI response using CrewAI
    with st.spinner("🤔 Multiple AI agents analyzing your symptoms..."):
        response = st.session_state.dental_crew.conduct_anamnesis(
            user_input,
            st.session_state.conversation
        )

    # Add AI response
    st.session_state.conversation.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent_type": "Dental Anamnesis Specialist"
    })

    # Update symptom analysis
    update_symptom_analysis()

    st.rerun()

def update_symptom_analysis():
    """Update symptom analysis based on conversation"""
    # Simple symptom detection from conversation
    symptoms_detected = set()
    for message in st.session_state.conversation:
        content = message['content'].lower()

        if any(word in content for word in ['dor', 'dói', 'pain', 'hurt']):
            symptoms_detected.add('tooth_pain')
        if any(word in content for word in ['sangramento', 'sangra', 'bleeding']):
            symptoms_detected.add('bleeding_gums')
        if any(word in content for word in ['inchaço', 'inchado', 'swelling']):
            symptoms_detected.add('swelling')
        if any(word in content for word in ['sensibilidade', 'sensível', 'sensitivity']):
            symptoms_detected.add('sensitivity')

    # Update analysis
    for symptom in symptoms_detected:
        if symptom not in st.session_state.symptom_analysis:
            st.session_state.symptom_analysis[symptom] = {
                'description': 'Detected in conversation',
                'urgency': 'Evaluation recommended',
                'recommendations': ['Consult with dental professional']
            }

def analyze_full_case():
    """Analyze the full case with CrewAI"""
    if not st.session_state.conversation:
        st.sidebar.warning("No conversation to analyze")
        return

    with st.sidebar:
        with st.spinner("🧠 Multiple AI agents conducting comprehensive analysis..."):
            analysis = st.session_state.dental_crew.analyze_complex_case(
                st.session_state.conversation
            )

        st.success("Comprehensive analysis complete!")
        st.text_area("AI Case Analysis", analysis, height=200)

def reset_conversation():
    """Reset the conversation"""
    st.session_state.conversation = []
    st.session_state.symptom_analysis = {}
    st.rerun()

def export_to_json():
    """Export data to JSON"""
    export_data = {
        "patient_info": st.session_state.patient_data,
        "ai_analysis": {
            "symptoms_detected": st.session_state.symptom_analysis,
            "conversation_summary": f"AI-anamnesis with {len(st.session_state.conversation)} messages",
            "ai_system": "CrewAI Multi-Agent Dental System"
        },
        "conversation_history": st.session_state.conversation,
        "export_metadata": {
            "export_date": datetime.datetime.now().isoformat(),
            "total_messages": len(st.session_state.conversation),
            "ai_agents_used": 3
        }
    }

    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

    st.download_button(
        label="📥 Download Complete Analysis (JSON)",
        data=json_str,
        file_name=f"dental_ai_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

def generate_medical_report():
    """Generate medical report"""
    st.info("📊 Medical report generation in development")

def generate_ai_report():
    """Generate AI analysis report"""
    st.info("🤖 AI analysis report generation in development")

if __name__ == "__main__":
    main()