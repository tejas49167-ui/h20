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
    if "girl" in user_message :
        return jsonify({"reply": "Varsha is a good girl and THANGAALIYAL ENDU song queen for me\nPeople call me Harshith because im happy about her"})
    elif "what" in user_message : 
        return jsonify({"reply": "\nI'm Harshith\nfor your question it's gods wish"})
    elif "hi" in user_message : 
        return jsonify({"reply": "\nHelo machi"})
    elif "how" in user_message : 
        return jsonify({"reply": "\nI'm Fine how are you machi?"})
    elif "friend" in user_message:
        return jsonify({"reply": "\nNan friends yalaru but some are\n1.Vishwas(Best Friend)\n2.Jeevan(Polite friend)\n3.Nandan(best friend)\n4.Ankitha(Tution friend)\n5.Tejas Gowda S"})
    elif "name" in user_message or "who" in user_message:
        return jsonify({"reply": "It's me Harshith"})

   
    
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