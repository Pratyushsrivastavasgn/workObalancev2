import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import threading

from database import Database
from posture_detector import PostureDetector
from gamification import GamificationSystem
from analytics import Analytics
from alerts import AlertSystem

class MindfulWorkDesk:
    def __init__(self, root):
        self.root = root
        self.root.title("Mindful Work Desk")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f5f5f5')

        self.db = Database()
        self.posture_detector = PostureDetector()
        self.gamification = GamificationSystem(self.db)
        self.analytics = Analytics(self.db)
        self.alerts = AlertSystem(self.root)

        self.username = simpledialog.askstring("Login", "Enter your username:", parent=self.root)
        if not self.username:
            self.username = "default_user"

        self.user = self.db.create_or_get_user(self.username)
        self.user_id = str(self.user['_id'])

        self.cap = None
        self.is_monitoring = False
        self.current_posture_score = 0
        self.current_posture_status = "Not monitoring"

        self.setup_ui()

        self.update_thread = None
        self.monitoring_active = False

    def setup_ui(self):
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        header = tk.Frame(main_container, bg='#2196F3', height=80)
        header.pack(fill='x', pady=(0, 10))

        title = tk.Label(
            header,
            text="Mindful Work Desk",
            font=('Arial', 24, 'bold'),
            bg='#2196F3',
            fg='white'
        )
        title.pack(side='left', padx=20, pady=20)

        user_label = tk.Label(
            header,
            text=f"Welcome, {self.username}!",
            font=('Arial', 12),
            bg='#2196F3',
            fg='white'
        )
        user_label.pack(side='right', padx=20, pady=20)

        content_frame = tk.Frame(main_container, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        left_panel = tk.Frame(content_frame, bg='white', width=600)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        right_panel = tk.Frame(content_frame, bg='white', width=400)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        self.setup_monitoring_panel(left_panel)
        self.setup_stats_panel(right_panel)

        bottom_panel = tk.Frame(main_container, bg='white', height=300)
        bottom_panel.pack(fill='both', expand=True, pady=(10, 0))

        self.setup_analytics_panel(bottom_panel)

    def setup_monitoring_panel(self, parent):
        monitor_header = tk.Label(
            parent,
            text="Real-Time Posture Monitoring",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#333'
        )
        monitor_header.pack(pady=10)

        self.video_label = tk.Label(parent, bg='black')
        self.video_label.pack(pady=10, padx=10)

        controls_frame = tk.Frame(parent, bg='white')
        controls_frame.pack(pady=10)

        self.start_button = tk.Button(
            controls_frame,
            text="Start Monitoring",
            command=self.start_monitoring,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief='flat',
            cursor='hand2',
            width=15
        )
        self.start_button.pack(side='left', padx=5)

        self.stop_button = tk.Button(
            controls_frame,
            text="Stop Monitoring",
            command=self.stop_monitoring,
            bg='#f44336',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief='flat',
            cursor='hand2',
            width=15,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)

        status_frame = tk.Frame(parent, bg='#e3f2fd', relief='ridge', borderwidth=2)
        status_frame.pack(pady=10, padx=20, fill='x')

        tk.Label(
            status_frame,
            text="Current Status:",
            font=('Arial', 12, 'bold'),
            bg='#e3f2fd'
        ).pack(pady=5)

        self.status_label = tk.Label(
            status_frame,
            text=self.current_posture_status,
            font=('Arial', 14),
            bg='#e3f2fd',
            fg='#1976D2'
        )
        self.status_label.pack(pady=5)

        tk.Label(
            status_frame,
            text="Posture Score:",
            font=('Arial', 12, 'bold'),
            bg='#e3f2fd'
        ).pack(pady=5)

        self.score_label = tk.Label(
            status_frame,
            text=f"{self.current_posture_score}/100",
            font=('Arial', 18, 'bold'),
            bg='#e3f2fd',
            fg='#4CAF50'
        )
        self.score_label.pack(pady=5)

    def setup_stats_panel(self, parent):
        stats_header = tk.Label(
            parent,
            text="Your Stats & Achievements",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#333'
        )
        stats_header.pack(pady=10)

        self.stats_frame = tk.Frame(parent, bg='white')
        self.stats_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.update_stats_display()

        refresh_button = tk.Button(
            parent,
            text="Refresh Stats",
            command=self.update_stats_display,
            bg='#2196F3',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2'
        )
        refresh_button.pack(pady=10)

    def setup_analytics_panel(self, parent):
        analytics_header = tk.Label(
            parent,
            text="Analytics & Trends",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#333'
        )
        analytics_header.pack(pady=10)

        self.analytics_frame = tk.Frame(parent, bg='white')
        self.analytics_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.update_analytics_display()

    def start_monitoring(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot access camera!")
                return

            self.is_monitoring = True
            self.monitoring_active = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            self.update_thread = threading.Thread(target=self.update_video, daemon=True)
            self.update_thread.start()

            messagebox.showinfo("Success", "Monitoring started!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")

    def stop_monitoring(self):
        self.is_monitoring = False
        self.monitoring_active = False

        if self.cap:
            self.cap.release()

        self.video_label.config(image='')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

        messagebox.showinfo("Stopped", "Monitoring stopped!")

    def update_video(self):
        while self.monitoring_active:
            if not self.cap or not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret:
                continue

            frame, status, score = self.posture_detector.analyze_posture(frame)

            self.current_posture_status = status
            self.current_posture_score = score

            self.db.save_posture_record(
                self.user_id,
                score,
                status,
                datetime.now()
            )

            if score >= 85:
                self.gamification.award_points(self.user_id, 'excellent_posture')
            elif score >= 70:
                self.gamification.award_points(self.user_id, 'good_posture')

            new_badges = self.gamification.check_and_award_badges(self.user_id)
            for badge in new_badges:
                self.alerts.show_achievement_notification(badge)

            self.alerts.check_posture_alert(score)
            self.alerts.check_break_reminder()

            frame_resized = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            score_color = '#4CAF50' if score >= 70 else '#FF9800' if score >= 50 else '#f44336'

            self.status_label.config(text=status)
            self.score_label.config(text=f"{score}/100", fg=score_color)

    def update_stats_display(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = self.gamification.get_user_stats(self.user_id)
        general_stats = self.analytics.get_statistics(self.user_id)
        streak = self.gamification.calculate_streak(self.user_id)

        points_card = tk.Frame(self.stats_frame, bg='#e8f5e9', relief='raised', borderwidth=2)
        points_card.pack(fill='x', pady=5)

        tk.Label(
            points_card,
            text="Total Points",
            font=('Arial', 10, 'bold'),
            bg='#e8f5e9'
        ).pack(pady=5)

        tk.Label(
            points_card,
            text=str(stats['total_points']),
            font=('Arial', 20, 'bold'),
            bg='#e8f5e9',
            fg='#4CAF50'
        ).pack(pady=5)

        badges_card = tk.Frame(self.stats_frame, bg='#fff3e0', relief='raised', borderwidth=2)
        badges_card.pack(fill='x', pady=5)

        tk.Label(
            badges_card,
            text="Badges Earned",
            font=('Arial', 10, 'bold'),
            bg='#fff3e0'
        ).pack(pady=5)

        tk.Label(
            badges_card,
            text=str(stats['total_badges']),
            font=('Arial', 20, 'bold'),
            bg='#fff3e0',
            fg='#FF9800'
        ).pack(pady=5)

        streak_card = tk.Frame(self.stats_frame, bg='#e3f2fd', relief='raised', borderwidth=2)
        streak_card.pack(fill='x', pady=5)

        tk.Label(
            streak_card,
            text="Current Streak",
            font=('Arial', 10, 'bold'),
            bg='#e3f2fd'
        ).pack(pady=5)

        tk.Label(
            streak_card,
            text=f"{streak} days",
            font=('Arial', 20, 'bold'),
            bg='#e3f2fd',
            fg='#2196F3'
        ).pack(pady=5)

        avg_card = tk.Frame(self.stats_frame, bg='#f3e5f5', relief='raised', borderwidth=2)
        avg_card.pack(fill='x', pady=5)

        tk.Label(
            avg_card,
            text="Average Posture Score",
            font=('Arial', 10, 'bold'),
            bg='#f3e5f5'
        ).pack(pady=5)

        tk.Label(
            avg_card,
            text=f"{general_stats['average_score']:.1f}/100",
            font=('Arial', 20, 'bold'),
            bg='#f3e5f5',
            fg='#9C27B0'
        ).pack(pady=5)

        if stats['badges']:
            badges_list = tk.Frame(self.stats_frame, bg='white')
            badges_list.pack(fill='x', pady=10)

            tk.Label(
                badges_list,
                text="Recent Badges:",
                font=('Arial', 11, 'bold'),
                bg='white'
            ).pack(anchor='w', padx=5)

            for badge in stats['badges'][-5:]:
                badge_frame = tk.Frame(badges_list, bg='#fffde7', relief='solid', borderwidth=1)
                badge_frame.pack(fill='x', pady=2, padx=5)

                tk.Label(
                    badge_frame,
                    text=f"🏆 {badge['badge_name']}",
                    font=('Arial', 9),
                    bg='#fffde7'
                ).pack(anchor='w', padx=5, pady=2)

    def update_analytics_display(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        charts_frame = tk.Frame(self.analytics_frame, bg='white')
        charts_frame.pack(fill='both', expand=True)

        try:
            chart = self.analytics.create_posture_chart(self.user_id, charts_frame, days=7)
            chart.pack(side='left', fill='both', expand=True, padx=5)

            dist_chart = self.analytics.create_score_distribution(self.user_id, charts_frame)
            dist_chart.pack(side='right', fill='both', expand=True, padx=5)
        except Exception as e:
            print(f"Error creating charts: {e}")

        insights = self.analytics.generate_insights(self.user_id)
        if insights:
            insights_frame = tk.Frame(self.analytics_frame, bg='#e8f5e9', relief='ridge', borderwidth=2)
            insights_frame.pack(fill='x', pady=10, padx=10)

            tk.Label(
                insights_frame,
                text="Insights & Recommendations",
                font=('Arial', 12, 'bold'),
                bg='#e8f5e9'
            ).pack(pady=5)

            for insight in insights:
                tk.Label(
                    insights_frame,
                    text=f"• {insight}",
                    font=('Arial', 10),
                    bg='#e8f5e9',
                    wraplength=600,
                    justify='left'
                ).pack(anchor='w', padx=10, pady=2)

    def on_closing(self):
        self.stop_monitoring()
        if self.cap:
            self.cap.release()
        self.posture_detector.release()
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MindfulWorkDesk(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
