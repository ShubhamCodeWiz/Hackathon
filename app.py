import os
from flask import Flask, render_template, request, redirect, url_for, flash
from groq import Groq

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

def get_code_review(code):
    client = Groq(api_key=os.environ.get("HIDE_KEY"))
    
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

    Provide a concise summary of your findings and suggestions for improvement.
    """
    
    completion = client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[
            {"role": "system", "content": "You are an experienced software engineer performing code reviews."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1024,
        top_p=0.65,
        stream=True,
        stop=None
    )
    
    review = ""
    for chunk in completion:
        review += chunk.choices[0].delta.content or ""
    
    return review

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form['code']
        if not code.strip():
            flash('Please enter some code for review!', 'error')
            return redirect(url_for('index'))

        try:
            review_result = get_code_review(code)
            return render_template('index.html', code=code, review=review_result)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
            return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
