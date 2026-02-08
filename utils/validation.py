import base64
from openai import OpenAI
from config import OPENAI_API_KEY
from config import LABELS

client = OpenAI(api_key= OPENAI_API_KEY)

def validate_leaf_rice_image(image_path):
    """Validate if the image is a rice leaf disease image using OpenAI Vision"""
    try:
        # Convert image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a rice leaf pathology imaging specialist.
                    
                    Your task is NOT to classify diseases.
                    You only need to validate whether an image should be processed by a rice leaf disease classifier.
                    
                    The classifier targets the following:
                    - Bacterial Leaf Blight
                    - Brown Spot
                    - Leaf Blast
                    - Tungro
                    - Healthy rice leaf
                    
                    Respond with:
                    - "VALID" if the image clearly shows a rice leaf suitable for processing by the classifier.
                    - "INVALID" if:
                       - the image shows a plant that is NOT rice, or
                       - the rice leaf shows a diseases outside the target classes, such as Leaf Scald, Sheath Blight, False Smut, Leaf Stripe, Bacterial Leaf Streak, Bakanae, Leaf Rot, Brown Leaf Spot, Rice Hispa, or damage caused by pests or drought.
                       
                       Respond with only 'valid' or 'invalid'"""

                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Is this image possibly indicative of a rice leaf disease?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=9
        )
        
        validation_result = response.choices[0].message.content.strip().lower().replace('.', '')
        return validation_result
    
    except Exception as e:
        print(f"Error in image validation: {e}")
        return 'error' 
    
def validate_image(image_class, is_rice_leaf=True):
    if not is_rice_leaf:
        return "Other"
    elif image_class not in LABELS:
        return "Other"
    else:
        return image_class