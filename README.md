# Mindful Work Desk

An advanced Python-based desktop application designed to promote both productivity and wellness in modern work environments. The application tracks posture, provides real-time feedback, awards gamification points, and presents detailed analytics.

## Features

- **Real-Time Posture Monitoring**: Uses OpenCV and MediaPipe to detect and analyze user posture through webcam
- **Instant Feedback & Alerts**: Notifies users about poor posture and reminds them to take breaks
- **Gamification System**: Awards points, badges, and tracks streaks for maintaining good posture
- **Analytics Dashboard**: Visualizes posture trends and score distributions over time
- **MongoDB Integration**: Securely stores all user data, posture records, and wellness metrics

## Requirements

- Python 3.8 or higher
- Webcam
- MongoDB Atlas account or local MongoDB instance

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up MongoDB:
   - Create a MongoDB Atlas account at https://www.mongodb.com/cloud/atlas
   - Create a new cluster
   - Get your connection string
   - Create a `.env` file based on `.env.example`:

```
MONGODB_URI=mongodb+srv://your_username:your_password@cluster.mongodb.net/
DATABASE_NAME=mindful_work_desk
```

## Usage

1. Make sure your webcam is connected
2. Run the application:

```bash
python main.py
```

3. Enter your username when prompted
4. Click "Start Monitoring" to begin posture tracking
5. The application will:

   - Show real-time video feed with posture detection overlay
   - Display current posture score and status
   - Award points for maintaining good posture
   - Send break reminders every 30 minutes
   - Alert you when poor posture is detected
   - Track your progress and show analytics

## Application Components

### Database Module (`database.py`)

- Manages MongoDB connections
- Handles user data, posture records, wellness metrics
- Manages gamification scores and achievements

### Posture Detector (`posture_detector.py`)

- Uses MediaPipe for pose estimation
- Analyzes neck angle and shoulder alignment
- Calculates posture score (0-100)
- Provides real-time feedback

### Gamification System (`gamification.py`)

- Awards points for healthy behaviors
- Tracks badges and achievements
- Calculates user streaks
- Manages leaderboard positions

### Analytics (`analytics.py`)

- Generates posture trend charts
- Creates score distribution visualizations
- Calculates statistics (average, best, worst scores)
- Provides personalized insights

### Alert System (`alerts.py`)

- Sends break reminders
- Alerts for poor posture
- Shows achievement notifications
- Customizable alert intervals

### Main Application (`main.py`)

- Tkinter-based GUI
- Real-time video display
- Dashboard with stats and achievements
- Analytics visualization

## Gamification Details

### Point System

- Good Posture (70-84): 10 points
- Excellent Posture (85+): 20 points
- Break Taken: 15 points
- Session Completed: 50 points
- Daily Goal Met: 100 points

### Badges

- **Posture Novice**: Maintain good posture for 10 minutes
- **Posture Pro**: Maintain good posture for 1 hour
- **Posture Master**: Maintain good posture for 4 hours
- **Break Taker**: Take 5 breaks in a day
- **Wellness Warrior**: Score 1000 total points
- **Streak Starter**: Maintain 3-day streak
- **Streak Legend**: Maintain 7-day streak

## Customization

You can customize the following settings:

- Break interval (default: 30 minutes)
- Posture check interval (default: 5 minutes)
- Posture score thresholds
- Point values for different actions

## Troubleshooting

**Camera not detected:**

- Ensure your webcam is properly connected
- Check if another application is using the camera
- Try restarting the application

**Database connection error:**

- Verify your MongoDB connection string in `.env`
- Check your internet connection (for MongoDB Atlas)
- Ensure MongoDB service is running (for local installation)

**Poor posture detection:**

- Ensure good lighting conditions
- Position yourself properly in front of the camera
- Keep your full upper body visible in the frame

## Future Enhancements

- Mobile app integration
- Smart device connectivity
- Voice assistance
- Cloud dashboard for multi-user support
- Export data to CSV/PDF reports
