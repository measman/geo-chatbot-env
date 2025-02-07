from transformers import pipeline

# Load a pre-trained NLP model for entity recognition
nlp_ner = pipeline("ner", model="dslim/bert-base-NER")

def extract_entities(query):
    entities = nlp_ner(query)
    extracted = {
        "location": "",
        "place_type": ""
    }
    for entity in entities:
        if entity['entity'] == 'B-LOC' or entity['entity'] == 'I-LOC':
            extracted['location'] += entity['word'].replace("##", "") + " "
        elif entity['entity'] == 'B-ORG' and "hospital" in entity['word'].lower():
            extracted['place_type'] = "hospital"
    extracted['location'] = extracted['location'].strip()
    return extracted

# Test
test_query = "Show me hospitals near Mumbai."
print(extract_entities(test_query))  # Output: {'location': 'Mumbai', 'place_type': 'hospital'}