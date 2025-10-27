# Dental Health Assistant - AI-Powered Odontological Anamnesis System

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Medical-FF6B6B?style=for-the-badge)

A sophisticated AI-powered dental health assistant that performs intelligent anamnesis through natural conversation. The system uses advanced symptom detection and follow-up questioning to gather comprehensive dental health information.

## 🦷 Features

### 🤖 Intelligent AI Assistant
- **Smart Symptom Detection**: Automatically identifies dental symptoms from patient descriptions
- **Contextual Follow-up**: Asks relevant questions based on detected symptoms
- **Multi-symptom Tracking**: Handles multiple symptoms simultaneously
- **Urgency Assessment**: Evaluates case urgency based on symptoms

### 💬 Interactive Chat Interface
- **Natural Conversation**: Chat-based interface for comfortable patient interaction
- **Quick Symptom Buttons**: One-click access to common dental issues
- **Real-time Analysis**: Instant AI responses with symptom analysis
- **Conversation History**: Complete record of all interactions

### 📊 Professional Features
- **Patient Management**: Comprehensive patient data collection
- **Medical History Tracking**: Symptom and conversation logging
- **Export Capabilities**: JSON export for medical records
- **Responsive Design**: Works on desktop and mobile devices

### 🎯 Supported Symptoms
- **Tooth Pain** 😣 - Location, intensity, duration, triggers
- **Bleeding Gums** 🩸 - Timing, frequency, associated factors
- **Swelling** 📈 - Location, size, progression, associated pain
- **Sensitivity** ❄️ - Triggers (cold, hot, sweet, pressure)
- **Bad Breath** 👃 - Duration, persistence, associated factors

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/LuizCampedelli/ai_agent.git
cd ai_agent
```

2. **Create virtual environment (recommended)**
```bash
python -m venv dental_agent_env
source dental_agent_env/bin/activate  # Linux/Mac
# dental_env\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app_enhanced.py
```

5. **Access the application**
   - Open your browser and go to: `http://localhost:8501`

### Deployment to Streamlit Cloud

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy Dental Agent Asistence"
git push origin main
```

1. **Your app will be live at**: `https://aiaiaimeudente.streamlit.app
```

## 🛠️ Technical Details

### Core Components

#### DentalKnowledgeBase Class
- **Symptom Detection**: NLP-based symptom identification from patient input
- **Question Flow**: Dynamic question sequencing based on symptom context
- **Urgency Assessment**: Intelligent triage based on symptom severity
- **Medical Context**: Comprehensive dental medical knowledge base

#### EnhancedDentalAgent Class
- **Conversation Management**: Maintains context across multiple interactions
- **Response Generation**: AI-powered response generation
- **Symptom Tracking**: Real-time symptom detection and categorization
- **API Integration Ready**: Prepared for LLM API integration

### Key Algorithms

1. **Symptom Pattern Matching**
   ```python
   # Detects symptoms from natural language input
   symptoms = knowledge_base.detect_symptoms(user_input)
   ```

2. **Dynamic Question Sequencing**
   ```python
   # Generates context-aware follow-up questions
   next_question = knowledge_base.get_next_question(symptom, history)
   ```

3. **Urgency Evaluation**
   ```python
   # Assesses case urgency based on symptoms and responses
   urgency = knowledge_base.assess_urgency(symptoms, responses)
   ```

## 📋 Usage Guide

### For Patients
1. **Enter Patient Information** in the sidebar
2. **Describe Symptoms** in the chat interface
3. **Answer Follow-up Questions** prompted by the AI
4. **Review Summary** in the medical record tab
5. **Export Data** for your dental professional

### For Dental Professionals
1. **Patient Intake**: Use as pre-consultation screening tool
2. **Symptom Documentation**: Automated symptom tracking and recording
3. **Case Prioritization**: Urgency assessment for appointment scheduling
4. **Medical Records**: Exportable JSON format for integration with EMR systems

## 🎨 Interface Overview

### Main Tabs
- **💬 Chat with AI**: Primary interaction interface
- **🖼️ Image Analysis**: Future feature for dental image upload
- **📊 Medical Record**: Patient data management and export

### Sidebar Features
- Patient demographic information
- Detected symptoms overview
- Conversation management controls
- Data export functionality

## 🔧 Configuration

### Environment Variables
The application can be configured using environment variables:

```bash
# Optional: API keys for enhanced AI features
export HUGGINGFACE_API_KEY=your_api_key_here
export OPENAI_API_KEY=your_api_key_here
```

### Customization
Modify `dental_knowledge.py` to:
- Add new symptom categories
- Customize question flows
- Adjust urgency assessment criteria
- Add localization for different languages

## 📈 Future Enhancements

### Planned Features
- [ ] **Image Analysis**: AI-powered dental radiograph analysis
- [ ] **Voice Input**: Speech-to-text for symptom description
- [ ] **Multi-language Support**: Additional language interfaces
- [ ] **EMR Integration**: Direct integration with dental practice software
- [ ] **Advanced AI**: Integration with larger language models
- [ ] **Analytics Dashboard**: Practice analytics and insights

### API Integration Ready
The system is prepared for integration with:
- **Hugging Face Inference API**
- **OpenAI GPT models**
- **Custom LLM deployments**
- **Medical knowledge databases**

## 🤝 Contributing

We welcome contributions from the dental and developer communities!

### Areas for Contribution
- **Medical Knowledge**: Expand symptom databases and question flows
- **UI/UX Improvements**: Enhance patient and practitioner experience
- **AI Enhancements**: Improve natural language understanding
- **Integration Features**: Connect with dental practice software

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏥 Medical Disclaimer

**Important**: This application is designed as a dental health assistant and screening tool. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your dentist or other qualified health provider with any questions you may have regarding a dental or medical condition.

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/dental-health-assistant/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/dental-health-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/dental-health-assistant/discussions)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Dental medical knowledge based on standard dental practice guidelines
- AI components designed for ethical and responsible use in healthcare

---

<div align="center">

**Made with ❤️ for better dental healthcare**

*Improving patient care through intelligent technology*

</div>