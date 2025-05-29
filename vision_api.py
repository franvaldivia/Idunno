from google.cloud import vision
from io import BytesIO
from config import CREDENTIALS_VISION

def detect_texts(image):
    client = vision.ImageAnnotatorClient(credentials=CREDENTIALS_VISION)  
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return [text.description for text in texts]

def image_to_vision_image(image):
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    content = buffer.getvalue()
    return vision.Image(content=content)
