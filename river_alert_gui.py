
import tkinter as tk
from tkinter import messagebox
from email.message import EmailMessage
import smtplib
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# === CONFIG === #
DANGER_LEVEL = 80
CSV_FILE = "water_log.csv"

EMAIL_ADDRESS = "javeshkhosla@gmail.com"        # your Gmail
EMAIL_PASSWORD = ""        # App password
EMAIL_RECEIVER = ""# who gets alert

# === FUNCTIONS === #

def send_email_alert(level):
    msg = EmailMessage()
    msg['Subject'] = '🌊 River Water-Level Alert'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECEIVER
    msg.set_content(f"⚠️ ALERT: River water level is {level} cm. Possible flood risk.")

    # Optionally attach graph
    if os.path.exists("plot.png"):
        with open("plot.png", 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='png', filename='plot.png')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False

def log_level(level):
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), level])

def plot_graph():
    if not os.path.exists(CSV_FILE):
        return

    df = pd.read_csv(CSV_FILE, names=["Time", "Level"], parse_dates=["Time"])
    df = df[df["Time"] > datetime.now() - timedelta(days=7)]
    df.set_index("Time")["Level"].plot(title="7-Day Water Level", figsize=(8, 4))
    plt.ylabel("Level (cm)")
    plt.tight_layout()
    plt.savefig("plot.png")
    plt.close()

def submit_level():
    try:
        level = int(entry.get())
        log_level(level)
        plot_graph()

        if level > DANGER_LEVEL:
            success = send_email_alert(level)
            if success:
                messagebox.showwarning("🚨 ALERT", f"Danger! Level: {level} cm. Email Sent.")
            else:
                messagebox.showerror("Email Error", "Could not send email.")
        else:
            messagebox.showinfo("✅ Safe", f"Level: {level} cm. No alert.")
        entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# === GUI === #
app = tk.Tk()
app.title("🌊 River Water-Level Alert")

tk.Label(app, text="Enter Water Level (cm):").pack(pady=10)
entry = tk.Entry(app)
entry.pack()

tk.Button(app, text="Submit", command=submit_level).pack(pady=5)
tk.Button(app, text="Show Graph", command=plot_graph).pack(pady=5)

app.mainloop()
