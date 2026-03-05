from flask import Flask, render_template, request, jsonify
import requests
import os


app = Flask(__name__)

API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"].lower()
    u = user_message.split() 

    print("User typed:", user_message)  
    if "girl" in u or "gf" in u :
        return jsonify({"reply": "I'm harshith(gay)"})
    elif "ai" in u or "chatgpt" in u or "gemini" in u or "build" in u : 
        return jsonify({"reply": "\nI'm not any any ai model like anything \nI'm Harshith\n"})
    elif "lowde" in u or "gandu" in u or "nkn" in u or "nmn" in u : 
        return jsonify({"reply": "No bad words"})
    elif "where" in u : 
        return jsonify({"reply":"bumi mele akashad keligia \n"})
    elif "what" in u : 
        return jsonify({"reply": "\nI'm Harshith\nfor your question it's gods wish"})
    elif "hi" in u : 
        return jsonify({"reply": "\nHelu\n"})
    elif "how" in u : 
        return jsonify({"reply": "\nI'm Fine how are you ?"})
    elif "friend" in u:
        return jsonify({"reply": "\nNan friends yalaru but some are\n1.Modi\n2.elon musk\n"})
    elif "name" in u or "who" in u:
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
                {"role": "user", "content": u}
            ]
        }
    )

    reply = response.json()["choices"][0]["message"]["content"]

    return jsonify({"reply": reply})
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)