from flask import Flask, render_template, request, jsonify
import requests
import os


app = Flask(__name__)

API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"].lower()
    print("User typed:", user_message)   
    if "name" in user_message or "who" in user_message:
        return jsonify({"reply": "It's me Harshith"})

    elif "girl" in user_message :
        return jsonify({"reply": "Varsha"})

    elif "friend" in user_message:
        return jsonify({"reply": "1.Vishwas\n2.Jeevan\n3.Nandan\n4.Ankitha\n5.Tejas Gowda S"})

    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }
    )

    reply = response.json()["choices"][0]["message"]["content"]

    return jsonify({"reply": reply})
if __name__ == "__main__":
    app.run(debug=True)