from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ১. আপনার গুগল শিট লিঙ্ক (CSV ফরম্যাটে)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1i0_no4OOa68oOi3tjCUlAZzG2FrIIiX790IL29_jgaA/export?format=csv"

def get_data_from_sheet(raw_id):
    try:
        df = pd.read_csv(SHEET_URL)
        # শিটের Ref No কলাম থেকে স্পেস মুছে ফেলা
        df['Ref No'] = df['Ref No'].astype(str).str.strip()
        
        # যদি আইডির আগে কোলন থাকে (:95NCGXV), সেটা পরিষ্কার করা
        clean_id = str(raw_id).split(':')[-1].strip()
        
        found_data = df[df['Ref No'] == clean_id]
        
        if not found_data.empty:
            row = found_data.iloc[0].to_dict()
            # পুলিশ স্টেশন এবং ডিস্ট্রিক্ট টাইটেল কেস করা
            if 'Police Station' in row:
                row['Police Station'] = str(row['Police Station']).title()
            if 'District' in row:
                row['District'] = str(row['District']).title()
            return row
        return None
    except Exception as e:
        print(f"Error reading sheet: {e}")
        return None

@app.route('/')
def home():
    return "Verification Server is Running..."

@app.route('/ords/f')
def verify():
    # সম্পূর্ণ URL কুয়েরি স্ট্রিং চেক করা
    full_query = request.query_string.decode('utf-8')
    token_id = None

    # যদি ইউআরএলে P50_TOKEN_ID থাকে, তার পরের অংশটুকু নেওয়া
    if 'P50_TOKEN_ID' in full_query:
        # P50_TOKEN_ID: এর পর যা আছে সবটুকুই আমাদের আইডি
        token_id = full_query.split('P50_TOKEN_ID:')[-1]
    
    # যদি উপরে কাজ না করে তবে সাধারণ পদ্ধতিতে খোঁজা
    if not token_id:
        token_id = request.args.get('P50_TOKEN_ID')

    if not token_id:
        return "INVALID REQUEST: NO TOKEN ID PROVIDED. Please check your QR link format.", 400
    
    # শিট থেকে ডেটা আনা
    data_row = get_data_from_sheet(token_id)
    
    if data_row:
        return render_template('index.html', d=data_row)
    else:
        # আইডি ক্লিন করে এরর মেসেজ দেখানো
        display_id = str(token_id).split(':')[-1]
        return f"No record found for ID: {display_id} in Google Sheet.", 404

if __name__ == '__main__':
    app.run(debug=True)
