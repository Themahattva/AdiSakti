import tkinter as tk
import time
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
from geopy.geocoders import Nominatim
import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"
import tkinter as tk


# Initialize Firebase
cred = credentials.Certificate("adisakti-59fbe-firebase-adminsdk-fbsvc-c7c5ce2498.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Twilio Credentials (Replace with actual credentials)
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_number"

def send_sos_message():
    user_data = db.collection("users").document("user1").get().to_dict()
    if user_data:
        emergency_contacts = user_data.get("emergency_contacts", [])
        location = get_location()
        message = f"🚨 SOS Alert! Last known location: {location} 🚨"
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        for contact in emergency_contacts:
            client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=contact)
        status_label.config(text="🚨 SOS Sent! 🚨", fg="red")

def get_location():
    geolocator = Nominatim(user_agent="safety_app")
    location = geolocator.geocode("Your Address or Use GPS API Here")
    return location.address if location else "Location Not Found"

def check_in():
    global last_checkin_time
    last_checkin_time = time.time()
    status_label.config(text="✅ Checked In - You're Safe!", fg="green")

def periodic_check():
    while True:
        time.sleep(60)  # Check every 60 seconds
        if time.time() - last_checkin_time > 300:  # If no response for 5 minutes
            send_sos_message()

def panic_button():
    send_sos_message()

# GUI
root = tk.Tk()
root.title("Women's Safety App")
root.geometry("300x200")

title_label = tk.Label(root, text="Women's Safety Alert", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

status_label = tk.Label(root, text="Press Check-In Regularly", fg="blue")
status_label.pack(pady=5)

checkin_button = tk.Button(root, text="I'm Safe ✅", command=check_in, bg="green", fg="white")
checkin_button.pack(pady=5)

panic_button = tk.Button(root, text="SOS 🚨", command=panic_button, bg="red", fg="white")
panic_button.pack(pady=5)

last_checkin_time = time.time()
threading.Thread(target=periodic_check, daemon=True).start()

root.mainloop()
