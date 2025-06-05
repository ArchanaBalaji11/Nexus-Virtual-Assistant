# nexusassistant.py

import os
import json
import math
import time
import webbrowser
import random
import datetime
import threading
import pyttsx3
import wikipedia
import requests
import platform
import psutil
import pyautogui
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from youtubesearchpython import VideosSearch
from tkinter import *
from wikipedia.exceptions import WikipediaException
from bs4 import BeautifulSoup
import speech_recognition as sr
import openai

# ----------------- Load Settings ------------------
with open("commands.json", "r", encoding='utf-8') as f:
    COMMAND = json.load(f)
with open("config.json", "r") as f:
    config = json.load(f)

openai.api_key = config["openai_api_key"]
weather_api_key = config["weather_api_key"]
default_city = config["city"]

# ----------------- Initialization ------------------
root = Tk()
root.config(bg="light grey")
root.geometry('1000x550+100+100')
root.title('Nexus Virtual Assistant')

canvas = Canvas(root, bg="snow")
canvas.place(x=10, y=10, width=980, height=450)

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

messages, answers = [], []

# ----------------- Speech & Voice ------------------
def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio).lower()
    except Exception:
        put_answer("Sorry, I didn't catch that.")
        return ""

# ----------------- Assistant Logic ------------------
def put_answer(answer):
    assistant = Assistant(canvas, answer=answer)
    answers.append(assistant)
    canvas.move(ALL, 0, -110)
    canvas.update()
    threading.Thread(target=speak, args=(answer,)).start()

def wish_me():
    hour = datetime.datetime.now().hour
    if hour < 12:
        put_answer("Good Morning! How can I help?")
    elif hour < 18:
        put_answer("Good Afternoon! How can I help?")
    else:
        put_answer("Good Evening! How can I help?")

def Math_Operations(operation):
    ex = operation.replace("what is ", "").replace("calculate", "")
    try:
        if "sin" in ex:
            return math.sin(float(ex.replace("sin", "")))
        elif "cos" in ex:
            return math.cos(float(ex.replace("cos", "")))
        elif "factorial" in ex:
            return math.factorial(int(ex.replace("factorial", "")))
        elif "binary" in ex:
            return bin(int(ex.replace("binary", "")))[2:]
        else:
            return eval(ex)
    except:
        return "I don't understand."

def weather(message):
    city = message.split("in")[-1].strip()
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    res = requests.get(url)
    data = res.json()
    try:
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return temp, f"Weather in {city} is {description}."
    except:
        return None, "Couldn't fetch weather."

def Search(message):
    try:
        topic = message.replace("wikipedia", "").strip()
        summary = wikipedia.summary(topic, sentences=3)
        put_answer(summary)
    except WikipediaException:
        put_answer("I can't find that topic on Wikipedia.")

def Google(message):
    query = message.replace("google", "").strip().replace(" ", "+")
    url = f"https://www.google.com/search?q={query}"
    put_answer(f"Searching for {query} on Google.")
    webbrowser.open(url)

def find_video(message):
    video = message.replace("video", "").strip()
    results = VideosSearch(video, limit=1).result()
    url = f"https://www.youtube.com/watch?v={results['result'][0]['id']}"
    os.startfile(url)
    put_answer("Playing video on YouTube...")

def Note(message):
    note = message.replace("note", "").strip()
    root.clipboard_clear()
    root.clipboard_append(note)
    put_answer("Note copied to clipboard.")
    os.startfile("notepad.exe")

def Screenshot():
    filename = "screenshot.png"
    pyautogui.screenshot(filename)
    put_answer("Screenshot taken and saved.")

def SystemInfo():
    info = f"System: {platform.system()} {platform.release()}\n"
    info += f"Processor: {platform.processor()}\n"
    info += f"CPU Usage: {psutil.cpu_percent()}%\n"
    info += f"RAM: {round(psutil.virtual_memory().total / (1024*1024), 2)} MB"
    put_answer(info)

def ask_chatgpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response.choices[0].message["content"].strip()
        put_answer(reply)
    except Exception as e:
        put_answer("ChatGPT is not responding.")


def send_email(to_email, subject, body):
    from_email = "archuaji2096@gmail.com"
    app_password = "okikpogiadjhtcsh"
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, app_password)
        server.send_message(msg)
        server.quit()
        put_answer("Email sent successfully.")
    except Exception as e:
        put_answer("Failed to send email.")
        print("Error:", e)

def execute_command(message):
    if 'wikipedia' in message:
        Search(message)
    elif 'google' in message:
        Google(message)
    elif 'weather' in message:
        try:
            temp, desc = weather(message)
            put_answer(f"Temperature: {temp} °C")
            put_answer(desc)
        except:
            put_answer("Couldn't fetch weather.")
    elif 'video' in message:
        find_video(message)
    elif 'note' in message:
        Note(message)
    elif 'screenshot' in message:
        Screenshot()
    elif 'system info' in message:
        SystemInfo()
    elif 'send email' in message:
        put_answer("Who do you want to send the email to?")
        to = get_audio()
        put_answer("What should be the subject?")
        subject = get_audio()
        put_answer("What should I say in the email?")
        body = get_audio()
        send_email(to, subject, body)
    elif 'what is' in message or 'calculate' in message:
        result = Math_Operations(message)
        put_answer(str(result))
    elif 'time' in message:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        put_answer(f"Current time is {now}")
    elif 'joke' in message:
        put_answer(random.choice(["Why did the computer show up at work late? It had a hard drive!", "Debugging: Removing the needles from the haystack."]))
    elif message in COMMAND:
        cmds = COMMAND[message][0]
        if cmds:
            for cmd in cmds:
                os.startfile(cmd)
        put_answer(random.choice(COMMAND[message][1]))
    elif message in ["stop", "bye", "exit"]:
        put_answer("Goodbye!")
        root.quit()
    else:
        ask_chatgpt(message)

# ----------------- GUI Classes ------------------
class Me:
    def __init__(self, master, message=""):
        self.frame = Frame(master, bg="cyan")
        master.create_window(900, 200, window=self.frame, anchor="ne")
        Label(self.frame, text=message, font=("Segoe", 15), bg="cyan").pack()

class Assistant:
    def __init__(self, master, answer=""):
        self.frame = Frame(master, bg="dodger blue")
        master.create_window(20, 250, window=self.frame, anchor="nw")
        Label(self.frame, text=answer, font=("Segoe", 15), bg="dodger blue").pack()

# ----------------- Input Triggers ------------------
def send_message():
    canvas.move(ALL, 0, -110)
    msg = get_audio()
    if msg:
        Me(canvas, message=msg)
        execute_command(msg)

def write_message():
    canvas.move(ALL, 0, -110)
    msg = ask.get()
    if msg:
        Me(canvas, message=msg)
        execute_command(msg.lower())

ask = Entry(root, font=("Segoe", 14))
ask.place(x=10, y=470, width=800, height=40)
ask.bind('<Return>', lambda event: write_message())

Button(root, text="Speak", command=lambda: threading.Thread(target=send_message).start()).place(x=820, y=470, width=80, height=40)
Button(root, text="Send", command=write_message).place(x=910, y=470, width=80, height=40)

wish_me()
root.mainloop()
