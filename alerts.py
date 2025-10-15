import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import time

class AlertSystem:
    def __init__(self, root):
        self.root = root
        self.break_interval = 30 * 60
        self.posture_check_interval = 5 * 60
        self.last_break_time = datetime.now()
        self.last_posture_alert = datetime.now()
        self.poor_posture_count = 0
        self.alert_enabled = True

    def check_break_reminder(self):
        if not self.alert_enabled:
            return False

        elapsed = (datetime.now() - self.last_break_time).total_seconds()
        if elapsed >= self.break_interval:
            self.show_break_reminder()
            self.last_break_time = datetime.now()
            return True
        return False

    def check_posture_alert(self, posture_score):
        if not self.alert_enabled:
            return False

        if posture_score < 50:
            self.poor_posture_count += 1

            elapsed = (datetime.now() - self.last_posture_alert).total_seconds()
            if self.poor_posture_count >= 3 and elapsed >= self.posture_check_interval:
                self.show_posture_alert()
                self.last_posture_alert = datetime.now()
                self.poor_posture_count = 0
                return True
        else:
            self.poor_posture_count = 0

        return False

    def show_break_reminder(self):
        self.show_notification(
            "Break Time!",
            "You've been working for 30 minutes.\nTime to take a short break!\n\nStretch, walk around, and rest your eyes.",
            duration=5000
        )

    def show_posture_alert(self):
        self.show_notification(
            "Posture Alert!",
            "Poor posture detected!\n\nPlease adjust your sitting position:\n- Sit up straight\n- Keep shoulders relaxed\n- Align your ears with your shoulders",
            duration=5000
        )

    def show_achievement_notification(self, badge_name):
        self.show_notification(
            "Achievement Unlocked!",
            f"Congratulations! You earned:\n{badge_name}",
            duration=4000
        )

    def show_notification(self, title, message, duration=3000):
        notification = tk.Toplevel(self.root)
        notification.title(title)
        notification.geometry("350x200")
        notification.resizable(False, False)

        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        x = screen_width - 370
        y = screen_height - 250
        notification.geometry(f"+{x}+{y}")

        notification.attributes('-topmost', True)

        title_frame = tk.Frame(notification, bg='#2196F3', height=40)
        title_frame.pack(fill='x')

        title_label = tk.Label(
            title_frame,
            text=title,
            font=('Arial', 14, 'bold'),
            bg='#2196F3',
            fg='white'
        )
        title_label.pack(pady=10)

        message_frame = tk.Frame(notification, bg='white')
        message_frame.pack(fill='both', expand=True, padx=10, pady=10)

        message_label = tk.Label(
            message_frame,
            text=message,
            font=('Arial', 10),
            bg='white',
            justify='left',
            wraplength=300
        )
        message_label.pack(pady=10)

        close_button = tk.Button(
            message_frame,
            text="OK",
            command=notification.destroy,
            bg='#2196F3',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2'
        )
        close_button.pack(pady=5)

        notification.after(duration, notification.destroy)

    def reset_break_timer(self):
        self.last_break_time = datetime.now()

    def set_break_interval(self, minutes):
        self.break_interval = minutes * 60

    def set_posture_check_interval(self, minutes):
        self.posture_check_interval = minutes * 60

    def toggle_alerts(self):
        self.alert_enabled = not self.alert_enabled
        return self.alert_enabled
