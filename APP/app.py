from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1i0_no4OOa68oOi3tjCUlAZzG2FrIIiX790IL29_jgaA/export?format=csv"

def get_data_from_sheet(raw_id):
    try:
        df = pd.read_csv(SHEET_URL)
        df['Ref No'] = df['Ref No'].astype(str).str.strip()
        
        # লিঙ্ক থেকে আইডি পরিষ্কার করা
        clean_id = str(raw_id).split(':')[-1].strip()
        
        found_data = df[df['Ref No'] == clean_id]
        
        if not found_data.empty:
            row = found_data.iloc[0].to_dict()
            
            # ডেটা ফরম্যাটিং
            if 'Police Station' in row: row['Police Station'] = str(row['Police Station']).title()
            if 'District' in row: row['District'] = str(row['District']).title()
            
            # নিশ্চিত করা যে DATED কলামটি আছে, না থাকলে খালি দেখাবে
            if 'DATED' not in row:
                row['DATED'] = "N/A"
                
            return row
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/ords/f')
def verify():
    full_query = request.query_string.decode('utf-8')
    token_id = None

    if 'P50_TOKEN_ID' in full_query:
        token_id = full_query.split('P50_TOKEN_ID:')[-1]
    
    if not token_id:
        token_id = request.args.get('P50_TOKEN_ID')

    if not token_id:
        return "INVALID REQUEST: NO TOKEN ID PROVIDED.", 400
    
    data_row = get_data_from_sheet(token_id)
    
    if data_row:
        return render_template('index.html', d=data_row)
    else:
        return f"No record found for ID: {token_id}", 404

if __name__ == '__main__':
    app.run(debug=True)
