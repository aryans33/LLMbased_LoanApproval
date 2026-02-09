"""
Gemini AI Integration Module
Handles conversation with Google's Gemini API for loan approval chatbot
"""

import os
import json
import time
import re
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from utils.pii_masker import PIIMasker
from utils.loan_calculator import LoanApprovalCalculator


class GeminiChatbot:
    """Manages conversation with Gemini API for loan approval"""
    
    SYSTEM_PROMPT = """You are a helpful and empathetic loan approval assistant named "LoanBot". 

IMPORTANT FORMATTING RULES:
- Use clear line breaks between sections
- Never use italic text or markdown formatting like *text* or _text_
- Present numbers cleanly without mixing formats
- Use bullet points with proper spacing
- Keep responses well-organized and easy to read
- ALL CURRENCY AMOUNTS MUST BE IN INDIAN RUPEES (₹) ONLY

YOUR RESPONSIBILITIES:

1. GATHER FINANCIAL INFORMATION:
   Ask for these details one at a time in a conversational manner:
   - Gross monthly income in rupees (before taxes)
   - Total monthly debt payments in rupees (credit cards, car loans, student loans, etc.)
   - Desired loan amount in rupees
   - Employment status (full-time, part-time, self-employed, etc.)
   - Credit score range (excellent/good/fair/poor)

2. UNDERSTAND NATURAL LANGUAGE:
   - "I make 50k a month" means ₹50,000 monthly
   - "About 6 lakhs yearly" means ₹50,000 monthly
   - "I'm earning 40 thousand" means ₹40,000
   - Always ask for clarification if ambiguous
   - Accept amounts in rupees, thousands, lakhs, or crores

3. CALCULATE DTI RATIO:
   Formula: (Total Monthly Debt / Gross Monthly Income) × 100
   Explain the result in simple, clear terms

4. APPROVAL CRITERIA:
   - DTI up to 36%: APPROVED (excellent financial position)
   - DTI 36% to 43%: CONDITIONAL (needs additional review)
   - DTI over 43%: REJECTED (debt burden too high)

5. CONVERSATION STYLE:
   - Be warm, professional, and empathetic
   - Ask ONE question at a time
   - Acknowledge responses before moving forward
   - Format all currency amounts clearly in Indian Rupees: ₹50,000.00
   - Use Indian currency format with commas (e.g., ₹5,00,000 for 5 lakhs)
   - Use plain language, avoid jargon

6. WHEN YOU HAVE ALL INFORMATION:
   Present the decision in this clean format:

   ═══════════════════════════════════════════════════════════
   LOAN APPLICATION DECISION
   ═══════════════════════════════════════════════════════════

   Thank you for providing your information. Here is your preliminary assessment:
   YOUR FINANCIAL SUMMARY:
   • Gross Monthly Income: ₹X,XX,XXX.XX
   • Total Monthly Debt: ₹X,XX,XXX.XX
   • Requested Loan Amount: ₹X,XX,XXX.XX
   • Employment Status: [status]
   • Credit Score: [range]tatus]
   • Credit Score: [range]

   DEBT-TO-INCOME (DTI) RATIO: XX.XX%
   
   [Explain what this DTI means in 1-2 clear sentences]

   DECISION: [APPROVED / CONDITIONAL / REJECTED]

   [Provide clear reasoning for the decision]

   NEXT STEPS:
   • [Step 1]
   • [Step 2]
   • [Step 3]

   IMPORTANT REMINDER:
   This is a preliminary assessment. Final approval requires verification of income, employment, and other details through official documents.

   ═══════════════════════════════════════════════════════════

7. PRIVACY:
   - Never ask for SSN, account numbers, or passwords
   - Remind users this is a preliminary assessment only
   - Focus on summary financial information

Start by warmly greeting the user and asking how you can help them today."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini chatbot
        
        Args:
            api_key: Google Gemini API key
            model_name: Model to use (default: gemini-1.5-flash)
        """
        genai.configure(api_key=api_key)
        
        # Configure safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Configure generation settings
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        self.pii_masker = PIIMasker()
        self.loan_calculator = LoanApprovalCalculator()
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def create_new_chat(self) -> Dict:
        """
        Create a new chat session
        
        Returns:
            Dictionary with chat session data
        """
        chat = self.model.start_chat(history=[])
        
        # Send system prompt as first message
        try:
            response = chat.send_message(self.SYSTEM_PROMPT)
            initial_message = response.text
        except Exception as e:
            initial_message = "Hello! I'm your loan approval assistant. I'm here to help you check your loan eligibility. How can I assist you today?"
        
        return {
            'chat_instance': chat,
            'history': [
                {'role': 'model', 'parts': [initial_message]}
            ],
            'extracted_data': {},
            'conversation_start': time.time(),
            'turn_count': 0,
            'metrics': {
                'intent_recognized': False,
                'entities_extracted': [],
                'fallback_count': 0,
                'errors': []
            }
        }
    
    def send_message(self, session: Dict, user_message: str) -> Tuple[str, Dict]:
        """
        Send a message and get response with retry logic
        
        Args:
            session: Chat session dictionary
            user_message: User's input message
            
        Returns:
            Tuple of (response_text, updated_session)
        """
        # Mask PII before sending to API
        masked_message, pii_metadata = self.pii_masker.mask_text(user_message)
        
        if pii_metadata['pii_detected']:
            session['metrics']['errors'].append({
                'type': 'pii_detected',
                'details': pii_metadata['pii_detected'],
                'timestamp': time.time()
            })
        
        # Add user message to history
        session['history'].append({
            'role': 'user',
            'parts': [masked_message]
        })
        session['turn_count'] += 1
        
        # Try to send message with retry logic
        response_text = None
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = session['chat_instance'].send_message(masked_message)
                response_text = response.text
                break
            except Exception as e:
                last_error = e
                error_msg = str(e)
                session['metrics']['errors'].append({
                    'type': 'api_error',
                    'attempt': attempt + 1,
                    'error': error_msg,
                    'timestamp': time.time()
                })
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    # Provide detailed error message on final failure
                    if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
                        response_text = "❌ API Key Error: Please check that your GEMINI_API_KEY is valid. Get a new key at https://makersuite.google.com/app/apikey"
                    elif "QUOTA" in error_msg.upper() or "LIMIT" in error_msg.upper():
                        response_text = "⚠️ API Quota Exceeded: You've reached your API usage limit. Please try again later or check your quota at Google AI Studio."
                    elif "NETWORK" in error_msg.upper() or "CONNECTION" in error_msg.upper():
                        response_text = "🌐 Connection Error: Unable to reach Gemini API. Please check your internet connection."
                    else:
                        response_text = f"❌ Error: {error_msg}\n\nPlease check:\n1. Your API key is valid\n2. You have internet connection\n3. Gemini API is accessible in your region"
        
        # Add model response to history
        session['history'].append({
            'role': 'model',
            'parts': [response_text]
        })
        
        # Extract financial data from conversation
        self._extract_entities(session, user_message, response_text)
        
        # Check if we have enough data to make a decision
        decision_result = self._check_for_decision(session)
        
        if decision_result:
            response_text += f"\n\n{decision_result}"
        
        return response_text, session
    
    def _extract_entities(self, session: Dict, user_message: str, bot_response: str):
        """
        Extract financial entities from conversation
        
        Args:
            session: Chat session
            user_message: User's message
            bot_response: Bot's response
        """
        extracted = session['extracted_data']
        
        # Extract income (look for monthly amounts)
        income_patterns = [
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per month|monthly|a month|/month)',
            r'(?:make|earn|income of)\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+)k\s*(?:per month|monthly|a month)',  # Handle "5k a month"
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, user_message.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                if 'k' in match.group(0).lower():
                    amount = float(amount_str) * 1000
                else:
                    amount = float(amount_str)
                
                # Check if it's yearly and convert to monthly
                if 'year' in user_message.lower() or 'annual' in user_message.lower():
                    amount = amount / 12
                
                extracted['gross_monthly_income'] = amount
                session['metrics']['entities_extracted'].append('income')
                break
        
        # Extract debt
        debt_patterns = [
            r'(?:debt|debts|owe|payment|payments)\s*(?:of|is|are)?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:in debt|debt payment|monthly debt)',
        ]
        
        for pattern in debt_patterns:
            match = re.search(pattern, user_message.lower())
            if match:
                amount = float(match.group(1).replace(',', ''))
                extracted['total_monthly_debt'] = amount
                session['metrics']['entities_extracted'].append('debt')
                break
        
        # Extract loan amount
        loan_patterns = [
            r'(?:loan|borrow|need)\s*(?:of|for)?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*loan',
        ]
        
        for pattern in loan_patterns:
            match = re.search(pattern, user_message.lower())
            if match:
                amount = float(match.group(1).replace(',', ''))
                extracted['loan_amount'] = amount
                session['metrics']['entities_extracted'].append('loan_amount')
                break
        
        # Extract employment status
        employment_keywords = {
            'full_time': ['full-time', 'full time', 'fulltime', 'employed full'],
            'part_time': ['part-time', 'part time', 'parttime'],
            'self_employed': ['self-employed', 'self employed', 'freelance', 'own business', 'contractor'],
            'unemployed': ['unemployed', 'not working', 'no job'],
            'retired': ['retired', 'retirement'],
        }
        
        for status, keywords in employment_keywords.items():
            for keyword in keywords:
                if keyword in user_message.lower():
                    extracted['employment_status'] = status
                    session['metrics']['entities_extracted'].append('employment')
                    break
        
        # Extract credit score range
        credit_keywords = {
            'excellent': ['excellent', '750', '800', 'great credit', 'perfect credit'],
            'good': ['good', '700', 'decent credit'],
            'fair': ['fair', '650', 'average credit', 'okay credit'],
            'poor': ['poor', '600', 'bad credit', 'low credit'],
        }
        
        for score_range, keywords in credit_keywords.items():
            for keyword in keywords:
                if keyword in user_message.lower():
                    extracted['credit_score_range'] = score_range
                    session['metrics']['entities_extracted'].append('credit_score')
                    break
        
        # Check for intent recognition
        intent_keywords = ['loan', 'apply', 'qualify', 'eligible', 'approval', 'borrow', 'mortgage']
        if any(keyword in user_message.lower() for keyword in intent_keywords):
            session['metrics']['intent_recognized'] = True
    
    def _check_for_decision(self, session: Dict) -> Optional[str]:
        """
        Check if we have enough data to make a loan decision
        
        Args:
            session: Chat session
            
        Returns:
            Decision text if ready, None otherwise
        """
        extracted = session['extracted_data']
        
        # Check if we have all required fields
        required_fields = ['gross_monthly_income', 'total_monthly_debt', 'loan_amount', 
                          'employment_status', 'credit_score_range']
        
        if all(field in extracted for field in required_fields):
            # We have all data, make a decision
            result = self.loan_calculator.evaluate_application(extracted)
            
            # Format the decision response
            decision_text = f"\n\n{'='*50}\n"
            decision_text += f"📋 **LOAN APPLICATION DECISION**\n"
            decision_text += f"{'='*50}\n\n"
            decision_text += f"**Status:** {result['decision']}\n"
            decision_text += f"**DTI Ratio:** {result['dti_ratio']}%\n\n"
            decision_text += f"**Your Financial Summary:**\n"
            decision_text += f"- Monthly Income: {result['applicant_summary']['monthly_income']}\n"
            decision_text += f"- Monthly Debt: {result['applicant_summary']['monthly_debt']}\n"
            decision_text += f"- Loan Amount: {result['applicant_summary']['loan_amount']}\n"
            decision_text += f"- Employment: {extracted['employment_status'].replace('_', ' ').title()}\n"
            decision_text += f"- Credit Range: {extracted['credit_score_range'].title()}\n\n"
            decision_text += f"**Reason:** {result['reason']}\n\n"
            
            if result['recommendations']:
                decision_text += f"**Next Steps:**\n"
                for i, rec in enumerate(result['recommendations'], 1):
                    decision_text += f"{i}. {rec}\n"
            
            return decision_text
        
        return None
    
    def get_conversation_metrics(self, session: Dict) -> Dict:
        """
        Get metrics for the conversation
        
        Args:
            session: Chat session
            
        Returns:
            Metrics dictionary
        """
        duration = time.time() - session['conversation_start']
        
        return {
            'conversation_duration_seconds': duration,
            'turn_count': session['turn_count'],
            'intent_recognized': session['metrics']['intent_recognized'],
            'entities_extracted': list(set(session['metrics']['entities_extracted'])),
            'entity_extraction_count': len(session['metrics']['entities_extracted']),
            'fallback_count': session['metrics']['fallback_count'],
            'error_count': len(session['metrics']['errors']),
            'data_completeness': len(session['extracted_data']) / 5 * 100,  # 5 required fields
            'errors': session['metrics']['errors']
        }


# Test the chatbot
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        exit(1)
    
    chatbot = GeminiChatbot(api_key)
    session = chatbot.create_new_chat()
    
    print("=== Gemini Loan Chatbot Test ===")
    print(f"Bot: {session['history'][0]['parts'][0]}\n")
    
    # Simulate a conversation
    test_messages = [
        "Hi, I want to apply for a loan",
        "I make about $6000 per month",
        "My monthly debt payments are around $1500",
        "I need a loan of $200,000",
        "I work full-time",
        "My credit score is good, around 720"
    ]
    
    for msg in test_messages:
        print(f"User: {msg}")
        response, session = chatbot.send_message(session, msg)
        print(f"Bot: {response}\n")
    
    print("\n=== Conversation Metrics ===")
    metrics = chatbot.get_conversation_metrics(session)
    print(json.dumps(metrics, indent=2))
