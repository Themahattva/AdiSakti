from flask import Flask, render_template, request, redirect, url_for
import time
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("adisakti-59fbe-firebase-adminsdk-fbsvc-c7c5ce2498.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Twilio Credentials (Replace with actual credentials)
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_number"

last_checkin_time = time.time()

def send_sos_message():
    user_data = db.collection("users").document("user1").get().to_dict()
    if user_data:
        emergency_contacts = user_data.get("emergency_contacts", [])
        location = get_location()
        message = f"🚨 SOS Alert! Last known location: {location} 🚨"
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        for contact in emergency_contacts:
            client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=contact)

def get_location():
    geolocator = Nominatim(user_agent="safety_app")
    location = geolocator.geocode("Your Address or Use GPS API Here")
    return location.address if location else "Location Not Found"

def periodic_check():
    global last_checkin_time
    while True:
        time.sleep(60)  # Check every 60 seconds
        if time.time() - last_checkin_time > 300:  # If no response for 5 minutes
            send_sos_message()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/checkin', methods=['POST'])
def checkin():
    global last_checkin_time
    last_checkin_time = time.time()
    return redirect(url_for('index'))

@app.route('/sos', methods=['POST'])
def sos():
    send_sos_message()
    return redirect(url_for('index'))

if __name__ == '__main__':
    threading.Thread(target=periodic_check, daemon=True).start()
    app.run(debug=True)
