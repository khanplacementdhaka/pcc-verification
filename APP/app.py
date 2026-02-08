from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ১. আপনার গুগল শিট লিঙ্ক (CSV ফরম্যাটে)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1i0_no4OOa68oOi3tjCUlAZzG2FrIIiX790IL29_jgaA/export?format=csv"

def get_data_from_sheet(ref_no):
    try:
        # গুগল শিট থেকে ডেটা পড়া
        df = pd.read_csv(SHEET_URL)
        
        # শিটের Ref No কলামের ডেটা পরিষ্কার করা
        df['Ref No'] = df['Ref No'].astype(str).str.strip()
        
        # ইনপুট আইডি পরিষ্কার করা (যদি কোলন বা স্পেস থাকে)
        clean_ref_no = str(ref_no).strip().split(':')[-1]
        
        # ডেটা ফিল্টার করা
        found_data = df[df['Ref No'] == clean_ref_no]
        
        if not found_data.empty:
            row = found_data.iloc[0].to_dict()
            
            # পুলিশ স্টেশন এবং ডিস্ট্রিক্ট "Title Case" এ রূপান্তর (DHAKA -> Dhaka)
            if 'Police Station' in row and pd.notnull(row['Police Station']):
                row['Police Station'] = str(row['Police Station']).title()
            if 'District' in row and pd.notnull(row['District']):
                row['District'] = str(row['District']).title()
            
            return row
        return None
    except Exception as e:
        print(f"Error reading sheet: {e}")
        return None

@app.route('/')
def home():
    return "Verification Server is Running..."

# ২. মূল ভেরিফিকেশন রুট
@app.route('/ords/f')
def verify():
    # ইউআরএল থেকে P50_TOKEN_ID প্যারামিটারটি নেওয়া
    token_id = request.args.get('P50_TOKEN_ID')
    
    # যদি সরাসরি না পাওয়া যায়, তবে পুরো ইউআরএল আর্গুমেন্ট চেক করা (লিঙ্ক এরর হ্যান্ডলিং)
    if not token_id:
        all_args = request.args.to_dict()
        for key, value in all_args.items():
            if 'P50_TOKEN_ID' in key:
                # যদি কিউআর কোডের লিঙ্কে P50_TOKEN_ID:62VNQVI এমন থাকে
                token_id = value if value else key.split(':')[-1]
                break

    if not token_id:
        return "INVALID REQUEST: NO TOKEN ID PROVIDED. Please check your QR link format.", 400
    
    # শিট থেকে ডেটা আনা
    data_row = get_data_from_sheet(token_id)
    
    if data_row:
        # ডেটা পাওয়া গেলে index.html দেখানো
        return render_template('index.html', d=data_row)
    else:
        # আইডি না পাওয়া গেলে
        clean_id = str(token_id).split(':')[-1]
        return f"No record found for ID: {clean_id}", 404

if __name__ == '__main__':
    app.run(debug=True)
