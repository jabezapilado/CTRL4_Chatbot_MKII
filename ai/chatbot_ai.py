import re
import string
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ---------------------------------------------------------
# LAYER 1: INGESTING GOEMOTIONS SCHEMA & MACRO-GROUPING
# ---------------------------------------------------------
def load_goemotions_dataset(file_path):
    print("\n" + "="*60)
    print(" 📊 INGESTING GOEMOTIONS CSV DATABASE")
    print("="*60)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing file: '{file_path}'. Please ensure it is in the same folder.")
        
    # Read the GoEmotions dataset via Pandas
    df = pd.read_csv(file_path)
    print(f"✅ SUCCESS: Loaded '{file_path}' containing {len(df)} lines.")
    
    # Specify target metrics from your exact dataset columns
    negative_emotion_columns = ['anger', 'annoyance', 'disappointment', 'sadness']
    
    # Safety Check: Drop rows marked 'example_very_unclear' to maintain clean training data
    if 'example_very_unclear' in df.columns:
        initial_count = len(df)
        df = df[df['example_very_unclear'] == False]
        print(f"🧹 Cleaned data: Dropped {initial_count - len(df)} unclear rater records.")
    
    # Macro-Grouping Rule: If ANY of the target negative columns contain 1, label as Distress (1)
    df['target_label'] = df[negative_emotion_columns].max(axis=1)
    
    # Calculate dataset label distribution balances
    distribution = df['target_label'].value_counts().to_dict()
    print(f"⚙️  Macro-grouped target classes based on: {negative_emotion_columns}")
    print(f"   └── Distribution Matrix: {distribution}")
    print("="*60 + "\n")
    
    return df['text'].tolist(), df['target_label'].tolist()

# ---------------------------------------------------------
# LAYER 2: TEXT PREPROCESSING CORNERSTONE
# ---------------------------------------------------------
STOPWORDS = {"the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "po", "lang", "kasi"}

def clean_and_preprocess(text):
    text = str(text).lower()
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    tokens = text.split()
    filtered = [word for word in tokens if word not in STOPWORDS]
    return " ".join(filtered)

# ---------------------------------------------------------
# LAYER 3: CORE AI ENGINE ARCHITECTURE
# ---------------------------------------------------------
class GuidanceChatbotAI:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        # Using class_weight='balanced' ensures the model treats rare distress rows fairly
        self.emotion_model = LogisticRegression(class_weight='balanced', max_iter=1000)
        
    def train_model(self, texts, labels):
        cleaned_texts = [clean_and_preprocess(t) for t in texts]
        X = self.vectorizer.fit_transform(cleaned_texts)
        self.emotion_model.fit(X, labels)
        
    def test_live_query(self, message):
        processed = clean_and_preprocess(message)
        vec = self.vectorizer.transform([processed])
        prob = self.emotion_model.predict_proba(vec)[0][1]
        
        print(f"📥 Message Input: \"{message}\"")
        print(f"📊 Calculated Distress Rating: {prob * 100:.1f}%")
        if prob >= 0.55:
            print("🚨 ROUTING STATUS: [HUMAN ESCALATION SEVERE RISK WARNING]")
        else:
            print("🟢 ROUTING STATUS: [AUTOMATED FAQ STANDARD RESPONSE]")
        print("-" * 60)

# --- PIPELINE INITIALIZATION ---
if __name__ == "__main__":
    # Ingest directly from your target file name
    file_name = "goemotions_1.csv"
    
    try:
        corpus_texts, target_labels = load_goemotions_dataset(file_name)
        
        # Initialize and build pipeline
        bot_ai = GuidanceChatbotAI()
        print("🧠 Training Logistic Regression model... please wait...")
        bot_ai.train_model(corpus_texts, target_labels)
        print("✅ Training complete!\n")
        
        # Live System Validation Runs
        bot_ai.test_live_query("I WANT TO FUCKING KILL MYSELF")
        bot_ai.test_live_query("FUCK THIS SHIT BRO I HATE EVERYTHING!!!!!!")
        bot_ai.test_live_query("I'm looking forward for my day, I feel great.")

        
    except Exception as e:
        print(f"❌ Error during execution pipeline step: {e}")