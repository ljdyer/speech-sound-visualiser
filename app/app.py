from visualiser.main import save_plots
import speech_recognition as sr
from flask import Flask, render_template, request, jsonify, current_app
import os

app = Flask(__name__)

# ====================
@app.route('/')
def index():
    return render_template('index.html')


# ====================
@app.route('/visualiser/')
def audio_to_text():
    return render_template('visualiser.html')


# ====================
@app.route('/audio', methods=['POST'])
def audio():
    r = sr.Recognizer()
    with open('upload/audio.wav', 'wb') as f:
        f.write(request.data)
  
    with sr.AudioFile('upload/audio.wav') as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language='en-GB', show_all=True)
            transcription = text['alternative'][0]['transcript']
            confidence = text['alternative'][0]['confidence']
            return_text = f"""It sounds like you said <span class="said-text">'{transcription}'</span> (confidence: {confidence*100:.2f}%)"""
        except:
            return_text = "Google Web Speech API could not detect any speech."
    
    try:
        save_plots('upload/audio.wav', os.path.join(current_app.root_path + '/static/images'))
    except:
        return_text = "ERR"
        
    return str(return_text)


# ====================
if __name__ == "__main__":
    app.run(debug=True)
