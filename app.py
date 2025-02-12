from flask import Flask, request, render_template, jsonify
from PIL import Image
import numpy as np
import skin_cancer_detection as SCD
from collections import defaultdict
import re

app = Flask(__name__)

# Medical Chatbot Implementation
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
            ],
            'diagnosis': [
                f"Our system can detect several types of skin conditions including:",
                "- Actinic keratoses (pre-cancerous)",
                "- Basal cell carcinoma",
                "- Benign keratosis",
                "- Dermatofibroma",
                "- Melanocytic nevi",
                "- Pyogenic granulomas",
                "- Melanoma",
                "Please upload an image for analysis, but remember this is just a screening tool."
            ]
        }
        
        self.keywords = {
            'melanoma': ['melanoma', 'cancer type', 'serious', 'dangerous'],
            'prevention': ['prevent', 'protect', 'avoid', 'risk', 'sunscreen'],
            'symptoms': ['symptom', 'sign', 'indication', 'warning', 'look like'],
            'treatment': ['treat', 'cure', 'therapy', 'medicine', 'surgery'],
            'diagnosis': ['detect', 'diagnostic', 'analysis', 'test', 'scan', 'upload']
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
                "prevention, symptoms, diagnosis, or treatment options for skin cancer.")

# Initialize chatbot
chatbot = MedicalChatbot()

# Main route for home page
@app.route("/", methods=["GET", "POST"])
def runhome():
    return render_template("home.html")

# Chat page route
@app.route("/chat_page")
def chat_page():
    return render_template("chat.html")

# Chat message handling route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
        
    response = chatbot.get_response(user_message)
    return jsonify({'response': response})

# Image analysis route
@app.route("/showresult", methods=["GET", "POST"])
def show():
    try:
        pic = request.files["pic"]
        inputimg = Image.open(pic)
        inputimg = inputimg.resize((28, 28))
        img = np.array(inputimg).reshape(-1, 28, 28, 3)
        result = SCD.model.predict(img)

        result = result.tolist()
        print(result)
        max_prob = max(result[0])
        class_ind = result[0].index(max_prob)
        print(class_ind)
        result = SCD.classes[class_ind]

        if class_ind == 0:
            info = "Actinic keratosis also known as solar keratosis or senile keratosis are names given to intraepithelial keratinocyte dysplasia. As such they are a pre-malignant lesion or in situ squamous cell carcinomas and thus a malignant lesion."
        elif class_ind == 1:
            info = "Basal cell carcinoma is a type of skin cancer. Basal cell carcinoma begins in the basal cells — a type of cell within the skin that produces new skin cells as old ones die off.Basal cell carcinoma often appears as a slightly transparent bump on the skin, though it can take other forms. Basal cell carcinoma occurs most often on areas of the skin that are exposed to the sun, such as your head and neck"
        elif class_ind == 2:
            info = "Benign lichenoid keratosis (BLK) usually presents as a solitary lesion that occurs predominantly on the trunk and upper extremities in middle-aged women. The pathogenesis of BLK is unclear; however, it has been suggested that BLK may be associated with the inflammatory stage of regressing solar lentigo (SL)1"
        elif class_ind == 3:
            info = "Dermatofibromas are small, noncancerous (benign) skin growths that can develop anywhere on the body but most often appear on the lower legs, upper arms or upper back. These nodules are common in adults but are rare in children. They can be pink, gray, red or brown in color and may change color over the years. They are firm and often feel like a stone under the skin. "
        elif class_ind == 4:
            info = "A melanocytic nevus (also known as nevocytic nevus, nevus-cell nevus and commonly as a mole) is a type of melanocytic tumor that contains nevus cells. Some sources equate the term mole with 'melanocytic nevus', but there are also sources that equate the term mole with any nevus form."
        elif class_ind == 5:
            info = "Pyogenic granulomas are skin growths that are small, round, and usually bloody red in color. They tend to bleed because they contain a large number of blood vessels. They're also known as lobular capillary hemangioma or granuloma telangiectaticum."
        elif class_ind == 6:
            info = "Melanoma, the most serious type of skin cancer, develops in the cells (melanocytes) that produce melanin — the pigment that gives your skin its color. Melanoma can also form in your eyes and, rarely, inside your body, such as in your nose or throat. The exact cause of all melanomas isn't clear, but exposure to ultraviolet (UV) radiation from sunlight or tanning lamps and beds increases your risk of developing melanoma."

        return render_template("reults.html", result=result, info=info)
    except Exception as e:
        return render_template("home.html", error="Error processing image. Please try again.")

if __name__ == "__main__":
    app.run(debug=True)