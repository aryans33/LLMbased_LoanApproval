# AI-Powered Loan Approval Chatbot

An intelligent loan approval assistant powered by Google's Gemini API that uses natural language processing to evaluate loan applications through conversational AI.

## 🚀 Features

### Core Capabilities

- **Natural Language Understanding**: Handles flexible user inputs with context awareness
- **Smart Entity Extraction**: Automatically extracts financial data from conversation
- **DTI Calculation**: Calculates Debt-to-Income ratio automatically
- **Intelligent Approval Logic**:
  - DTI ≤ 36%: Approved
  - DTI 36-43%: Conditional approval
  - DTI > 43%: Rejected
- **Context-Aware Conversations**: Maintains conversation history across multiple turns
- **PII Protection**: Automatically masks sensitive information before API calls

### Technical Features

- **Streamlit Interface**: Modern, interactive chat UI
- **Real-time Responses**: Live conversation with Gemini API
- **Metrics Tracking**: Comprehensive analytics on conversation performance
- **Error Handling**: Retry logic with exponential backoff for API failures
- **Security**: Built-in PII masking and safe data handling

## 📋 Requirements

- Python 3.8+
- Google Gemini API key

## 🛠️ Installation

### 1. Navigate to Project Directory

```cmd
cd d:\TechBaton\LLMbased_LoanApproval
```

### 2. Create Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```cmd
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```cmd
copy .env.example .env
```

Edit `.env` and add your credentials:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Get your Gemini API key:**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file

### 5. Run the Application

```cmd
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`

## 📖 Usage

### Starting a Conversation

1. The app opens automatically in your browser
2. The chatbot will greet you automatically
3. Start by saying something like:
   - "I want to apply for a loan"
   - "Can I qualify for a $200,000 mortgage?"
   - "I need help with a loan application"

### Example Conversation Flow

```
Bot: Hello! I'm your loan approval assistant...

You: Hi, I want to apply for a loan

Bot: Great! I'd be happy to help you. Let's start with your monthly income...

You: I make about $6000 per month

Bot: Thank you! And what are your total monthly debt payments?

You: Around $1500 for car, student loans, and credit cards

Bot: Got it! How much would you like to borrow?

You: I need $200,000

Bot: What's your employment status?

You: I work full-time

Bot: And finally, what's your credit score range?

You: It's good, around 720

Bot: [Provides approval decision with DTI calculation and next steps]
```

## 🎯 UI Features

### Main Chat Area

- **Interactive Chat**: Type and receive responses in real-time
- **Message History**: Scroll through entire conversation
- **Decision Formatting**: Approval/rejection displayed with color-coded boxes
- **Typing Indicator**: Visual feedback while bot is responding

### Sidebar Panel

- **Extracted Information**: See parsed financial data in real-time
  - Monthly Income
  - Monthly Debt
  - Loan Amount
  - Employment Status
  - Credit Score Range

- **Action Buttons**:
  - 🔄 Reset Chat: Start a new conversation
  - 📊 Metrics: View conversation analytics

- **Session Stats**: Track conversation duration and turn count

### Metrics Dashboard

Click "📊 Metrics" to view:

- Conversation turns
- Duration
- Intent recognition
- Entities extracted
- Data completeness
- Error count

## 🔒 Security & Privacy

### PII Protection

The system automatically masks:

- Social Security Numbers (SSN)
- Credit card numbers
- Phone numbers
- Email addresses
- Account numbers
- Routing numbers
- Physical addresses

Example:

```
Input:  "My SSN is 123-45-6789"
Masked: "My SSN is <SSN_1>"
```

### Data Privacy

- Conversations are session-based (cleared on browser refresh)
- No sensitive data is permanently stored
- Gemini API configured with safety settings
- PII masked before sending to API

## 🏗️ Project Structure

```
LLMbased_LoanApproval/
├── app.py                      # Streamlit application (main entry point)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── QUICKSTART.md              # Quick start guide
│
├── services/
│   ├── __init__.py
│   └── gemini_service.py      # Gemini API integration
│
├── utils/
│   ├── __init__.py
│   ├── pii_masker.py          # PII detection & masking
│   ├── loan_calculator.py     # DTI calculation & approval logic
│   └── metrics_tracker.py     # Metrics tracking system
│
└── logs/                      # Metrics logs (auto-created)
    ├── metrics.jsonl
    └── daily_stats.json
```

## 🧪 Testing

### Test Individual Components

```cmd
# Test PII Masking
python utils\pii_masker.py

# Test Loan Calculator
python utils\loan_calculator.py

# Test Gemini Integration (requires API key)
python services\gemini_service.py

# Test Metrics
python utils\metrics_tracker.py
```

## 🔧 Configuration

### Gemini Model Settings

Edit `services/gemini_service.py`:

```python
self.generation_config = {
    "temperature": 0.7,      # Creativity (0.0-1.0)
    "top_p": 0.95,           # Nucleus sampling
    "top_k": 40,             # Top-k sampling
    "max_output_tokens": 1024
}
```

### Approval Thresholds

Edit `utils/loan_calculator.py`:

```python
DTI_APPROVED_MAX = 36.0      # Change from 36%
DTI_CONDITIONAL_MAX = 43.0   # Change from 43%
```

## 📈 Performance Monitoring

### View Daily Report

```python
from utils.metrics_tracker import MetricsTracker

tracker = MetricsTracker()
print(tracker.generate_report())
```

### Access Logs

Logs are stored in `logs/` directory:

- `metrics.jsonl`: Individual conversation metrics
- `daily_stats.json`: Aggregated daily statistics

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"

**Solution**: Make sure you've:

1. Created `.env` file from `.env.example`
2. Added your actual API key
3. Restarted the application

### "Failed to start chat"

**Possible causes**:

- Invalid API key
- Network connectivity issues
- API quota exceeded

**Solution**: Check your API key and internet connection

### Module Import Errors

**Solution**: Ensure virtual environment is activated:

```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Port Already in Use

Streamlit will automatically use a different port if 8501 is busy.

## 🚀 Deployment

### Streamlit Cloud (Free)

1. Push code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Add `GEMINI_API_KEY` in Secrets
5. Deploy!

### Local Production

```cmd
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📝 Loan Approval Criteria

### DTI Calculation

```
DTI = (Total Monthly Debt / Gross Monthly Income) × 100
```

### Approval Rules

| DTI Ratio | Decision       | Notes                        |
| --------- | -------------- | ---------------------------- |
| ≤ 36%     | ✅ Approved    | Excellent financial position |
| 36-43%    | ⚠️ Conditional | Requires manual review       |
| > 43%     | ❌ Rejected    | Debt burden too high         |

### Additional Factors

- Minimum monthly income: $1,000
- Employment status considered
- Credit score influences final decision

## 🤝 Contributing

Suggestions for improvements:

1. Add voice input/output
2. Multi-language support
3. PDF report generation
4. Document upload functionality
5. Integration with real loan systems
6. Historical application tracking

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- **Google Gemini API**: For powerful language understanding
- **Streamlit**: For amazing web framework
- **Python Community**: For excellent libraries

---

**Built with ❤️ using Google Gemini API + Streamlit**

_Last updated: February 3, 2026_
