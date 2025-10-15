from datetime import datetime, timedelta

class GamificationSystem:
    def __init__(self, database):
        self.db = database

        self.badges = {
            'posture_novice': {'name': 'Posture Novice', 'description': 'Maintained good posture for 10 minutes', 'threshold': 10},
            'posture_pro': {'name': 'Posture Pro', 'description': 'Maintained good posture for 1 hour', 'threshold': 60},
            'posture_master': {'name': 'Posture Master', 'description': 'Maintained good posture for 4 hours', 'threshold': 240},
            'break_taker': {'name': 'Break Taker', 'description': 'Took 5 breaks in a day', 'threshold': 5},
            'wellness_warrior': {'name': 'Wellness Warrior', 'description': 'Scored 1000 total points', 'threshold': 1000},
            'streak_starter': {'name': 'Streak Starter', 'description': 'Maintained 3-day streak', 'threshold': 3},
            'streak_legend': {'name': 'Streak Legend', 'description': 'Maintained 7-day streak', 'threshold': 7},
        }

        self.point_actions = {
            'good_posture': 10,
            'excellent_posture': 20,
            'break_taken': 15,
            'session_completed': 50,
            'daily_goal_met': 100,
        }

    def award_points(self, user_id, action):
        points = self.point_actions.get(action, 0)
        if points > 0:
            self.db.update_gamification_score(user_id, points, action)
            return points
        return 0

    def check_and_award_badges(self, user_id):
        gamification_data = self.db.get_user_gamification_data(user_id)
        if not gamification_data:
            return []

        existing_badges = self.db.get_user_badges(user_id)
        existing_badge_names = [b['badge_name'] for b in existing_badges]

        new_badges = []
        total_points = gamification_data.get('total_points', 0)

        if total_points >= 1000 and 'Wellness Warrior' not in existing_badge_names:
            self.db.award_badge(user_id, 'Wellness Warrior',
                              self.badges['wellness_warrior']['description'])
            new_badges.append('Wellness Warrior')

        posture_records = self.db.get_posture_history(user_id, limit=500)
        good_posture_minutes = sum(1 for r in posture_records if r.get('posture_score', 0) >= 70)

        if good_posture_minutes >= 10 and 'Posture Novice' not in existing_badge_names:
            self.db.award_badge(user_id, 'Posture Novice',
                              self.badges['posture_novice']['description'])
            new_badges.append('Posture Novice')

        if good_posture_minutes >= 60 and 'Posture Pro' not in existing_badge_names:
            self.db.award_badge(user_id, 'Posture Pro',
                              self.badges['posture_pro']['description'])
            new_badges.append('Posture Pro')

        if good_posture_minutes >= 240 and 'Posture Master' not in existing_badge_names:
            self.db.award_badge(user_id, 'Posture Master',
                              self.badges['posture_master']['description'])
            new_badges.append('Posture Master')

        return new_badges

    def get_user_stats(self, user_id):
        gamification_data = self.db.get_user_gamification_data(user_id)
        badges = self.db.get_user_badges(user_id)

        stats = {
            'total_points': gamification_data.get('total_points', 0) if gamification_data else 0,
            'total_badges': len(badges),
            'badges': badges,
            'recent_activity': gamification_data.get('history', [])[-10:] if gamification_data else []
        }

        return stats

    def calculate_streak(self, user_id):
        posture_records = self.db.get_posture_history(user_id, limit=1000)

        if not posture_records:
            return 0

        dates_with_activity = set()
        for record in posture_records:
            date = record['timestamp'].date()
            dates_with_activity.add(date)

        sorted_dates = sorted(dates_with_activity, reverse=True)

        if not sorted_dates:
            return 0

        streak = 1
        for i in range(len(sorted_dates) - 1):
            diff = (sorted_dates[i] - sorted_dates[i + 1]).days
            if diff == 1:
                streak += 1
            else:
                break

        return streak

    def get_leaderboard_position(self, user_id):
        all_users = list(self.db.gamification.find().sort('total_points', -1))
        position = 1
        for idx, user in enumerate(all_users):
            if user['user_id'] == user_id:
                position = idx + 1
                break
        return position
