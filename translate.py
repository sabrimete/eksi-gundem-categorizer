import asyncio
import re
import firebase_admin
from firebase_admin import firestore
from collections import defaultdict
import json
import six
from google.cloud import translate_v2 as translate

app = firebase_admin.initialize_app()
db = firestore.client()
translate_client = translate.Client()

def translate_text(target, text):

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    result = translate_client.translate(text, target_language=target, format_='html')
    return result["translatedText"]
def remove_urls(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)
def fix_quote(data):
    p = re.compile(r'&#39;')
    return p.sub('\'', data)
async def on_write(event: dict):
    # Get the data that was written to the Firestore database
    mp_gundem = defaultdict(list)
    for key, values in event.items():
        translated_baslik =  translate_text("en", key)
        translated_baslik = fix_quote(translated_baslik)
        values = values['arrayValue']['values']
        for val in values:
            val = val['stringValue']
            val = fix_quote(remove_urls(val))
            translated_entry = translate_text("en", val)
            translated_entry = fix_quote(translated_entry)
            mp_gundem[translated_baslik].append(translated_entry)
    db.collection("translated-gundem").add(mp_gundem)

def hello_firestore(event, context):
    """Triggered by a change to a Firestore document.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    data = event['value']['fields']
    asyncio.run(on_write(data))