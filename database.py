import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        try:
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            database_name = os.getenv('DATABASE_NAME', 'mindful_work_desk')

            self.client = MongoClient(mongodb_uri)
            self.db = self.client[database_name]

            self.users = self.db.users
            self.posture_records = self.db.posture_records
            self.wellness_metrics = self.db.wellness_metrics
            self.gamification = self.db.gamification
            self.achievements = self.db.achievements

            print("Database connected successfully!")

        except Exception as e:
            print(f"Database connection error: {e}")
            self.client = None
            self.db = None

    def save_posture_record(self, user_id, posture_score, status, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        record = {
            'user_id': user_id,
            'posture_score': posture_score,
            'status': status,
            'timestamp': timestamp
        }
        return self.posture_records.insert_one(record)

    def save_wellness_metric(self, user_id, metric_type, value, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        metric = {
            'user_id': user_id,
            'metric_type': metric_type,
            'value': value,
            'timestamp': timestamp
        }
        return self.wellness_metrics.insert_one(metric)

    def update_gamification_score(self, user_id, points, action):
        existing = self.gamification.find_one({'user_id': user_id})

        if existing:
            new_points = existing.get('total_points', 0) + points
            self.gamification.update_one(
                {'user_id': user_id},
                {'$set': {
                    'total_points': new_points,
                    'last_updated': datetime.now()
                },
                '$push': {
                    'history': {
                        'action': action,
                        'points': points,
                        'timestamp': datetime.now()
                    }
                }}
            )
        else:
            self.gamification.insert_one({
                'user_id': user_id,
                'total_points': points,
                'last_updated': datetime.now(),
                'history': [{
                    'action': action,
                    'points': points,
                    'timestamp': datetime.now()
                }]
            })

    def get_user_gamification_data(self, user_id):
        return self.gamification.find_one({'user_id': user_id})

    def award_badge(self, user_id, badge_name, badge_description):
        badge = {
            'user_id': user_id,
            'badge_name': badge_name,
            'description': badge_description,
            'awarded_at': datetime.now()
        }
        return self.achievements.insert_one(badge)

    def get_user_badges(self, user_id):
        return list(self.achievements.find({'user_id': user_id}))

    def get_posture_history(self, user_id, limit=100):
        return list(self.posture_records.find({'user_id': user_id})
                   .sort('timestamp', -1)
                   .limit(limit))

    def get_wellness_trends(self, user_id, metric_type=None):
        query = {'user_id': user_id}
        if metric_type:
            query['metric_type'] = metric_type
        return list(self.wellness_metrics.find(query).sort('timestamp', -1))

    def create_or_get_user(self, username):
        user = self.users.find_one({'username': username})
        if not user:
            user = {
                'username': username,
                'created_at': datetime.now(),
                'settings': {
                    'break_interval': 30,
                    'posture_check_interval': 5
                }
            }
            result = self.users.insert_one(user)
            user['_id'] = result.inserted_id
        return user

    def close(self):
        if self.client:
            self.client.close()
