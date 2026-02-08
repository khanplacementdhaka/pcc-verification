from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ১. আপনার গুগল শিট লিঙ্ক (CSV ফরম্যাটে)
# নিশ্চিত করুন যে শিটটি "Anyone with the link" মোডে ভিউয়ার হিসেবে পাবলিশ করা আছে
SHEET_URL = "https://docs.google.com/spreadsheets/d/1i0_no4OOa68oOi3tjCUlAZzG2FrIIiX790IL29_jgaA/export?format=csv"

def get_data_from_sheet(ref_no):
    try:
        # গুগল শিট থেকে ডেটা পড়া
        df = pd.read_csv(SHEET_URL)
        
        # Ref No কলামে ওই নির্দিষ্ট আইডিটি খোঁজা
        # আপনার শিটের কলামের নাম 'Ref No' হতে হবে
        found_data = df[df['Ref No'].astype(str).str.strip() == str(ref_no).strip()]
        
        if not found_data.empty:
            row = found_data.iloc[0].to_dict()
            
            # ডেটা ফরম্যাটিং: পুলিশ স্টেশন এবং ডিস্ট্রিক্ট "Title Case" এ রূপান্তর (যেমন: DHAKA -> Dhaka)
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

# ২. আপনার কাঙ্ক্ষিত ইউআরএল পাথ /ords/f
@app.route('/ords/f')
def verify():
    # ইউআরএল থেকে P50_TOKEN_ID প্যারামিটারটি নেওয়া
    token_id = request.args.get('P50_TOKEN_ID')
    
    if not token_id:
        return "Invalid Request: No Token ID provided.", 400
    
    # শিট থেকে ডেটা আনা
    data_row = get_data_from_sheet(token_id)
    
    if data_row:
        # যদি ডেটা পাওয়া যায়, তবে index.html ফাইলে সেটি পাঠানো
        return render_template('index.html', d=data_row)
    else:
        # যদি আইডি না পাওয়া যায়
        return f"No record found for ID: {token_id}", 404

if __name__ == '__main__':
    app.run(debug=True)
