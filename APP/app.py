from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ১. আপনার গুগল শিট লিঙ্ক (CSV ফরম্যাটে)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1i0_no4OOa68oOi3tjCUlAZzG2FrIIiX790IL29_jgaA/export?format=csv"

def get_data_from_sheet(raw_token):
    try:
        df = pd.read_csv(SHEET_URL)
        df['Ref No'] = df['Ref No'].astype(str).str.strip()
        
        # যদি আইডির আগে কোলন থাকে (যেমন :95NCGXV), তবে কোলন বাদ দিয়ে শুধু আইডি নেওয়া
        clean_id = str(raw_token).split(':')[-1].strip()
        
        found_data = df[df['Ref No'] == clean_id]
        
        if not found_data.empty:
            row = found_data.iloc[0].to_dict()
            # পুলিশ স্টেশন এবং ডিস্ট্রিক্ট টাইটেল কেস করা
            if 'Police Station' in row and pd.notnull(row['Police Station']):
                row['Police Station'] = str(row['Police Station']).title()
            if 'District' in row and pd.notnull(row['District']):
                row['District'] = str(row['District']).title()
            return row
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def home():
    return "Verification Server is Online"

@app.route('/ords/f')
def verify():
    # ইউআরএল থেকে ডাটা নেওয়ার চেষ্টা
    token_id = None
    
    # পদ্ধতি ১: সরাসরি চাবি খোঁজা
    if 'P50_TOKEN_ID' in request.args:
        token_id = request.args.get('P50_TOKEN_ID')
    
    # পদ্ধতি ২: যদি কিউআর কোডে কোলনসহ থাকে (যেমন :95NCGXV)
    if not token_id or token_id == "":
        for key, value in request.args.items():
            if 'P50_TOKEN_ID' in key:
                # যদি কি-র ভেতরেই আইডি থাকে (যেমন 'P50_TOKEN_ID:95NCGXV')
                if ':' in key:
                    token_id = key.split(':')[-1]
                else:
                    token_id = value
                break

    if not token_id:
        return "INVALID REQUEST: NO TOKEN ID PROVIDED.", 400
    
    data_row = get_data_from_sheet(token_id)
    
    if data_row:
        return render_template('index.html', d=data_row)
    else:
        # আইডি ক্লিন করে এরর মেসেজে দেখানো
        display_id = str(token_id).split(':')[-1]
        return f"No record found for ID: {display_id}", 404

if __name__ == '__main__':
    app.run(debug=True)
