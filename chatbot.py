# chatbot.py
from collections import defaultdict
import re

class MedicalChatbot:
    def __init__(self):
        self.responses = {
            'melanoma': [
                "Melanoma is the most serious type of skin cancer. Key warning signs include:",
                "- Asymmetrical shape",
                "- Border irregularity",
                "- Color variations",
                "- Diameter larger than 6mm",
                "- Evolution or changes over time",
                "Please consult a healthcare professional for proper diagnosis."
            ],
            'prevention': [
                "To reduce skin cancer risk:",
                "- Use sunscreen (SPF 30+)",
                "- Avoid peak sun hours (10am-4pm)",
                "- Wear protective clothing",
                "- Regular skin self-examinations",
                "- Annual professional skin checks"
            ],
            'symptoms': [
                "Common skin cancer symptoms include:",
                "- New growths or changes in existing moles",
                "- Sores that don't heal",
                "- Spread of pigment from spot border",
                "- Redness, swelling, or color changes",
                "- Changes in sensation (itchiness, tenderness)"
            ],
            'treatment': [
                "Treatment options may include:",
                "- Surgery",
                "- Radiation therapy",
                "- Chemotherapy",
                "- Immunotherapy",
                "Always follow your doctor's recommended treatment plan."
            ]
        }
        
        self.keywords = {
            'melanoma': ['melanoma', 'cancer type', 'serious', 'dangerous'],
            'prevention': ['prevent', 'protect', 'avoid', 'risk', 'sunscreen'],
            'symptoms': ['symptom', 'sign', 'indication', 'warning', 'look like'],
            'treatment': ['treat', 'cure', 'therapy', 'medicine', 'surgery']
        }

    def get_intent(self, user_input):
        user_input = user_input.lower()
        scores = defaultdict(int)
        
        for category, words in self.keywords.items():
            for word in words:
                if re.search(r'\b' + word + r'\b', user_input):
                    scores[category] += 1
                    
        if not scores:
            return None
        return max(scores.items(), key=lambda x: x[1])[0]

    def get_response(self, user_input):
        intent = self.get_intent(user_input)
        if intent:
            return '\n'.join(self.responses[intent])
        return ("I'm not sure about that. You can ask me about melanoma, "
                "prevention, symptoms, or treatment options for skin cancer.")

# Add this to your app.py
from flask import jsonify
from chatbot import MedicalChatbot

chatbot = MedicalChatbot()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
        
    response = chatbot.get_response(user_message)
    return jsonify({'response': response})