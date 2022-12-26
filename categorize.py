from google.cloud import language_v1
import firebase_admin
from firebase_admin import firestore
from collections import defaultdict
import time
import random

app = firebase_admin.initialize_app()
db = firestore.client()
client = language_v1.LanguageServiceClient()
type_ = language_v1.Document.Type.PLAIN_TEXT
language = "en"
content_categories_version = (language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2)

categories = defaultdict(list)

def sample_classify_text(text_content):

    document = {"content": text_content, "type_": type_, "language": language}

    response = client.classify_text(request = {
        "document": document,
        "classification_model_options": {
            "v2_model": {
                "content_categories_version": content_categories_version
            }
        }
    })
    
    for category in response.categories:
        categories[category.name].append(category.confidence)

def find_max_confidence_and_filter(categories):
    filtered_categories = {}
    for category in categories:
        mx = max(categories[category]) 
        if(mx > 0.7):
            filtered_categories[category] = mx
    return filtered_categories
    
def save_categories_to_firestore(categories):
    tm = str(time.time())
    name = tm + max(0,18-len(tm))*"0"+"-"+str(random.randint(100000,1000000))
    db.collection('categorized-gundem').document(name).set(categories)

def hello_firestore(event, context):
    """Triggered by a change to a Firestore document.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    data = event['value']['fields']

    for key, values in data.items():
        values = values['arrayValue']['values']
        for val in values:
            val = val['stringValue']
            sample_classify_text(val)

    filtered_categories = find_max_confidence_and_filter(categories)
    save_categories_to_firestore(filtered_categories)
