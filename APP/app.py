from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# আপনার গুগল শিটের লিঙ্ক
SHEET_URL = "https://docs.google.com/spreadsheets/d/1i0_no4OOa68oOi3tjCUlAZzG2FrIIiX790IL29_jgaA/export?format=csv"

@app.route('/ords/f')
def verify():
    # কোলন (:) যুক্ত লিঙ্ক হ্যান্ডেল করার জন্য
    full_query = request.query_string.decode('utf-8')
    token_id = None
    
    if 'P50_TOKEN_ID:' in full_query:
        token_id = full_query.split('P50_TOKEN_ID:')[-1]
    else:
        token_id = request.args.get('P50_TOKEN_ID')

    if not token_id:
        return "<h1>Invalid Request!</h1>", 400

    try:
        df = pd.read_csv(SHEET_URL)
        # শিটের Ref No কলামের সাথে টোকেন আইডি মেলানো
        match = df[df['Ref No'].astype(str) == str(token_id)]
        
        if not match.empty:
            data = match.iloc[0].to_dict()
            return render_template('index.html', d=data)
        else:
            return f"<h1>No data found for ID: {token_id}</h1>", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)