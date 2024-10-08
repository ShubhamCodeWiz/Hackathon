import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from groq import Groq
from collections import Counter
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback_secret_key")

GROQ_API_KEY = os.environ.get("HIDE_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=GROQ_API_KEY)

# In-memory storage for simplicity. In a production app, use a database.
reviews = []

def get_code_review(code):
    prompt = f"""
    As an experienced software engineer, please review the following code and provide feedback:
    ```
    {code}
    ```
    Analyze the code for:
    1. Code style and formatting
    2. Potential bugs or errors
    3. Performance issues
    4. Security vulnerabilities
    5. Best practices and design patterns

    For each category, provide a brief explanation and a severity rating (Low, Medium, High).
    Format your response as JSON with the following structure:
    {{
        "overall_summary": "Brief overall summary",
        "categories": [
            {{
                "name": "Category name",
                "issues": [
                    {{
                        "description": "Issue description",
                        "severity": "Low/Medium/High"
                    }}
                ]
            }}
        ]
    }}
    """

    completion = client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[
            {"role": "system", "content": "You are an experienced software engineer performing code reviews."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=2048,
        top_p=0.95,
        stream=False,
        stop=None
    )

    return completion.choices[0].message.content

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form['code']
        review_result = get_code_review(code)
        review_data = json.loads(review_result)
        review_data['timestamp'] = datetime.now().isoformat()
        review_data['code'] = code
        reviews.append(review_data)
        return jsonify(review_result)
    return render_template('index.html')

@app.route('/past-reviews')
def past_reviews():
    return render_template('past_reviews.html', reviews=reviews)

@app.route('/review/<int:review_id>')
def view_review(review_id):
    if 0 <= review_id < len(reviews):
        return render_template('view_review.html', review=reviews[review_id])
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)