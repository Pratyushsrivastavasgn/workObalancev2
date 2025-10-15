import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np

class Analytics:
    def __init__(self, database):
        self.db = database

    def get_posture_trends(self, user_id, days=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        records = self.db.posture_records.find({
            'user_id': user_id,
            'timestamp': {'$gte': start_date, '$lte': end_date}
        }).sort('timestamp', 1)

        records_list = list(records)

        timestamps = [r['timestamp'] for r in records_list]
        scores = [r['posture_score'] for r in records_list]

        return timestamps, scores

    def get_daily_averages(self, user_id, days=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        records = self.db.posture_records.find({
            'user_id': user_id,
            'timestamp': {'$gte': start_date, '$lte': end_date}
        })

        daily_data = {}
        for record in records:
            date = record['timestamp'].date()
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(record['posture_score'])

        dates = sorted(daily_data.keys())
        averages = [np.mean(daily_data[date]) for date in dates]

        return dates, averages

    def get_statistics(self, user_id):
        records = list(self.db.get_posture_history(user_id, limit=1000))

        if not records:
            return {
                'average_score': 0,
                'best_score': 0,
                'worst_score': 0,
                'total_sessions': 0,
                'good_posture_percentage': 0
            }

        scores = [r['posture_score'] for r in records]

        return {
            'average_score': np.mean(scores),
            'best_score': max(scores),
            'worst_score': min(scores),
            'total_sessions': len(records),
            'good_posture_percentage': (sum(1 for s in scores if s >= 70) / len(scores)) * 100
        }

    def create_posture_chart(self, user_id, parent_frame, days=7):
        dates, averages = self.get_daily_averages(user_id, days)

        fig, ax = plt.subplots(figsize=(8, 4), facecolor='white')

        if dates and averages:
            date_labels = [d.strftime('%m/%d') for d in dates]
            ax.plot(date_labels, averages, marker='o', linewidth=2, markersize=8, color='#4CAF50')
            ax.fill_between(range(len(averages)), averages, alpha=0.3, color='#4CAF50')

            ax.axhline(y=70, color='orange', linestyle='--', linewidth=1, label='Good Posture Threshold')

            ax.set_xlabel('Date', fontsize=10, fontweight='bold')
            ax.set_ylabel('Average Posture Score', fontsize=10, fontweight='bold')
            ax.set_title(f'Posture Trends - Last {days} Days', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

            ax.set_ylim([0, 100])
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()

        return canvas.get_tk_widget()

    def create_score_distribution(self, user_id, parent_frame):
        records = list(self.db.get_posture_history(user_id, limit=500))

        fig, ax = plt.subplots(figsize=(6, 4), facecolor='white')

        if records:
            scores = [r['posture_score'] for r in records]

            bins = [0, 30, 50, 70, 85, 100]
            labels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']

            hist, _ = np.histogram(scores, bins=bins)

            colors = ['#f44336', '#ff9800', '#ffeb3b', '#8bc34a', '#4caf50']

            ax.bar(labels, hist, color=colors, alpha=0.7, edgecolor='black')

            ax.set_xlabel('Posture Category', fontsize=10, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=10, fontweight='bold')
            ax.set_title('Posture Score Distribution', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()

        return canvas.get_tk_widget()

    def generate_insights(self, user_id):
        stats = self.get_statistics(user_id)
        insights = []

        if stats['average_score'] >= 80:
            insights.append("Excellent work! Your average posture is outstanding.")
        elif stats['average_score'] >= 70:
            insights.append("Good job! Your posture is above average.")
        elif stats['average_score'] >= 50:
            insights.append("Fair posture. Consider taking more frequent breaks.")
        else:
            insights.append("Your posture needs improvement. Focus on sitting upright.")

        if stats['good_posture_percentage'] >= 75:
            insights.append(f"You maintain good posture {stats['good_posture_percentage']:.1f}% of the time!")
        else:
            insights.append(f"Try to increase your good posture percentage (currently {stats['good_posture_percentage']:.1f}%).")

        return insights
