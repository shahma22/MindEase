# MindEase - AI Mental Wellness Website
# Author: Shahma Mohammed Salih | Student: 2527465

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from textblob import TextBlob
import sqlite3
import json
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mindease_secret_2026'

# ── Database Setup ─────────────────────────────────────────

def get_db():
    conn = sqlite3.connect('mindease.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            mood_type TEXT NOT NULL,
            date      TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            date    TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ── Fuzzy Logic Sentiment ──────────────────────────────────

def fuzzy_sentiment(polarity):
    if polarity >= 0.5:
        return {'label': 'Very Positive', 'emoji': '🌟', 'color': 'very-positive', 'level': 5}
    elif polarity >= 0.1:
        return {'label': 'Positive',      'emoji': '😊', 'color': 'positive',      'level': 4}
    elif polarity >= -0.1:
        return {'label': 'Neutral',       'emoji': '🌿', 'color': 'neutral',        'level': 3}
    elif polarity >= -0.4:
        return {'label': 'Negative',      'emoji': '💙', 'color': 'negative',       'level': 2}
    else:
        return {'label': 'Very Negative', 'emoji': '🫂', 'color': 'very-negative',  'level': 1}

# ── Keyword Detection ──────────────────────────────────────

def detect_keywords(text):
    text = text.lower()
    keywords = {
        'exam'       : ['exam', 'test', 'assignment', 'deadline', 'grade', 'fail', 'study', 'revision'],
        'sleep'      : ['sleep', 'tired', 'exhausted', 'insomnia', 'awake', 'rest', 'fatigue'],
        'lonely'     : ['lonely', 'alone', 'isolated', 'no friends', 'nobody', 'left out'],
        'family'     : ['family', 'parents', 'mum', 'dad', 'home', 'siblings', 'mother', 'father'],
        'anxiety'    : ['anxious', 'anxiety', 'panic', 'worry', 'nervous', 'scared', 'fear'],
        'money'      : ['money', 'financial', 'broke', 'debt', 'rent', 'fees', 'afford'],
        'work'       : ['work', 'job', 'boss', 'colleague', 'workplace', 'employed'],
        'overwhelmed': ['overwhelmed', 'too much', 'cannot cope', 'cant cope', 'everything', 'breaking'],
    }
    for topic, words in keywords.items():
        for word in words:
            if word in text:
                return topic
    return None

# ── Chatbot Response Engine ────────────────────────────────

def generate_response(user_text, polarity, fuzzy, keyword, turn):
    topic_responses = {
        'exam': [
            "Exam pressure is really common for students. Is it one specific subject or the overall workload that is getting to you?",
            "It sounds like the academic pressure is building up. Have you tried breaking your revision into 25-minute focused sessions with short breaks?",
            "Remember — your worth is not defined by your grades. What is one small step you could take today to feel more prepared?"
        ],
        'sleep': [
            "Not sleeping properly makes everything feel ten times harder. How long has this been going on?",
            "Poor sleep and stress often go hand in hand. Have you tried the 4-7-8 breathing technique before bed? Inhale 4 seconds, hold 7, exhale 8.",
            "A consistent sleep schedule can really help reset your body clock. Is there something specific keeping you awake at night?"
        ],
        'lonely': [
            "Feeling lonely at university is more common than people admit. Have you been able to connect with anyone on your course recently?",
            "Loneliness can feel very heavy. Are there any clubs or student groups at your university you have thought about joining?",
            "Even small connections matter. Is there one person you could reach out to today — even just a message?"
        ],
        'family': [
            "Family situations can add a lot of pressure on top of university life. Would you like to talk about what is happening?",
            "Being away from family or having difficult dynamics at home is genuinely hard. How are you managing day to day?",
            "It sounds like things at home are weighing on you. Have you spoken to your university student support service about this?"
        ],
        'anxiety': [
            "Anxiety can feel overwhelming but you are not alone in this. Can you describe what your anxiety feels like right now?",
            "When anxiety peaks, grounding techniques can help. Try naming 5 things you can see around you right now.",
            "Anxiety often feeds on uncertainty. Is there one specific thing triggering it most right now?"
        ],
        'money': [
            "Financial stress is one of the biggest pressures students face. Has your university hardship fund been something you have looked into?",
            "Money worries can affect everything else. Is this a short-term issue or something more ongoing?",
            "You do not have to manage financial stress alone. Most universities have a financial support team — have you spoken to anyone there?"
        ],
        'work': [
            "Balancing work and university is genuinely tough. How many hours are you working alongside your studies?",
            "Workplace stress on top of academic pressure can really take a toll. Is there a specific situation at work bothering you?",
            "It is important to protect your study time. Have you spoken to your employer about your university commitments?"
        ],
        'overwhelmed': [
            "When everything feels like too much, it helps to focus on just one thing at a time. What is the most pressing thing on your mind right now?",
            "Feeling overwhelmed is a signal that you need support — not a sign of weakness. Have you spoken to anyone about how you are feeling?",
            "Let us break this down together. What is one small thing you could do in the next 10 minutes to feel slightly more in control?"
        ]
    }

    sentiment_responses = {
        5: [
            "You seem to be in a really great place right now! What has been going well for you?",
            "That is wonderful to hear! How have you been keeping such a positive mindset?",
            "It is great that you are feeling so well. Is there anything you would like to reflect on today?"
        ],
        4: [
            "It sounds like things are going reasonably well. What has been the highlight of your day?",
            "Good to hear you are feeling positive! Is there anything on your mind you would like to talk through?",
            "Glad you are in a good headspace. How are you managing your workload at the moment?"
        ],
        3: [
            "It sounds like you are feeling fairly steady. Is there anything specific on your mind right now?",
            "Sometimes neutral is okay — not every day has to be amazing. What would make today a little better for you?",
            "I am here if you want to talk through anything. What has your day been like so far?"
        ],
        2: [
            "I am sorry you are feeling this way. You do not have to go through this alone. Can you tell me a bit more about what is happening?",
            "It sounds like things are tough right now. What has been the hardest part of your day?",
            "Thank you for sharing that with me. Have you been able to talk to anyone else about how you are feeling?"
        ],
        1: [
            "I can hear that you are really struggling right now and I want you to know that matters. Can you tell me what is going on?",
            "You are not alone in this, even when it feels that way. What has been happening that has brought you to this point?",
            "I am really glad you are talking about this. Please know that support is available — can you tell me more about what you are going through?"
        ]
    }

    if keyword and keyword in topic_responses:
        responses = topic_responses[keyword]
    else:
        responses = sentiment_responses[fuzzy['level']]

    return responses[turn % len(responses)]

# ── Routes ─────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/wellness', methods=['GET', 'POST'])
def wellness():
    result = None
    error  = None
    if request.method == 'POST':
        user_text = request.form.get('user_text', '').strip()
        if not user_text:
            error = "Please type how you are feeling before submitting."
        else:
            blob     = TextBlob(user_text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                label   = "Positive"
                emoji   = "😊"
                color   = "positive"
                message = "That's great to hear! It sounds like you're in a good headspace. Keep doing what's working for you — whether that's talking to friends, taking breaks, or simply being kind to yourself."
            elif polarity < -0.1:
                label   = "Negative"
                emoji   = "💙"
                color   = "negative"
                message = "It sounds like you're going through a tough time, and that's okay. Try a breathing exercise or a short walk. If things feel overwhelming please reach out — 800-HOPE (4673), available 24/7."
            else:
                label   = "Neutral"
                emoji   = "🌿"
                color   = "neutral"
                message = "You seem fairly balanced right now. Use this moment to check in with yourself — try journaling your thoughts or visiting the Resources page for calming techniques."
            result = {
                'label'    : label,
                'emoji'    : emoji,
                'color'    : color,
                'polarity' : round(polarity, 2),
                'message'  : message,
                'user_text': user_text
            }
    return render_template('wellness.html', result=result, error=error)

# ── Mood Tracker ───────────────────────────────────────────

# Quotes bank — one set per mood
MOOD_QUOTES = {
    'Happy': [
        {'text': 'Happiness is not something ready-made. It comes from your own actions.', 'author': 'Dalai Lama', 'emoji': '😊'},
        {'text': 'The most wasted of all days is one without laughter.', 'author': 'E.E. Cummings', 'emoji': '😄'},
        {'text': 'Joy is the simplest form of gratitude.', 'author': 'Karl Barth', 'emoji': '🌟'},
    ],
    'Excited': [
        {'text': 'Enthusiasm is the electricity of life.', 'author': 'Gordon Parks', 'emoji': '🤩'},
        {'text': 'The secret of getting ahead is getting started.', 'author': 'Mark Twain', 'emoji': '🚀'},
        {'text': 'Energy and persistence conquer all things.', 'author': 'Benjamin Franklin', 'emoji': '⚡'},
    ],
    'Grateful': [
        {'text': 'Gratitude turns what we have into enough.', 'author': 'Aesop', 'emoji': '🙏'},
        {'text': 'Appreciation is a wonderful thing. It makes what is excellent in others belong to us.', 'author': 'Voltaire', 'emoji': '💛'},
        {'text': 'The more grateful I am, the more beauty I see.', 'author': 'Mary Davis', 'emoji': '🌸'},
    ],
    'Neutral': [
        {'text': 'In the middle of every difficulty lies opportunity.', 'author': 'Albert Einstein', 'emoji': '🌿'},
        {'text': 'Peace is the result of retraining your mind to process life as it is.', 'author': 'Wayne Dyer', 'emoji': '☮️'},
        {'text': 'Calmness is the cradle of power.', 'author': 'Josiah Holland', 'emoji': '🌊'},
    ],
    'Tired': [
        {'text': 'Rest when you are weary. Refresh and renew yourself, your body, your mind.', 'author': 'Ralph Marston', 'emoji': '😴'},
        {'text': 'Almost everything will work again if you unplug it for a few minutes — including you.', 'author': 'Anne Lamott', 'emoji': '🔋'},
        {'text': 'Take rest. A field that has rested gives a bountiful crop.', 'author': 'Ovid', 'emoji': '🌾'},
    ],
    'Anxious': [
        {'text': 'You do not have to control your thoughts. You just have to stop letting them control you.', 'author': 'Dan Millman', 'emoji': '🌬️'},
        {'text': 'Nothing diminishes anxiety faster than action.', 'author': 'Walter Anderson', 'emoji': '💪'},
        {'text': 'Breathe. You are going to be okay.', 'author': 'Unknown', 'emoji': '🫁'},
    ],
    'Sad': [
        {'text': 'Even the darkest night will end and the sun will rise.', 'author': 'Victor Hugo', 'emoji': '🌅'},
        {'text': 'You are allowed to be both a masterpiece and a work in progress simultaneously.', 'author': 'Sophia Bush', 'emoji': '💙'},
        {'text': 'This too shall pass.', 'author': 'Persian Proverb', 'emoji': '🌧️'},
    ],
    'Stressed': [
        {'text': 'Do not anticipate trouble or worry about what may never happen. Keep in the sunlight.', 'author': 'Benjamin Franklin', 'emoji': '☀️'},
        {'text': 'You are braver than you believe, stronger than you seem.', 'author': 'A.A. Milne', 'emoji': '💛'},
        {'text': 'Take it one day at a time. Today, after all, is the tomorrow you worried about yesterday.', 'author': 'Dale Carnegie', 'emoji': '📅'},
    ],
    'Overwhelmed': [
        {'text': 'You do not have to see the whole staircase, just take the first step.', 'author': 'Martin Luther King Jr.', 'emoji': '🪜'},
        {'text': 'Start where you are. Use what you have. Do what you can.', 'author': 'Arthur Ashe', 'emoji': '🌱'},
        {'text': 'One small positive thought in the morning can change your whole day.', 'author': 'Dalai Lama', 'emoji': '🌄'},
    ],
}

@app.route('/mood', methods=['GET', 'POST'])
def mood():
    conn  = get_db()
    error = None
    quote = None

    if request.method == 'POST':
        mood_type = request.form.get('mood_type', '').strip()
        if mood_type not in ['Happy','Excited','Grateful','Neutral','Tired','Anxious','Sad','Stressed','Overwhelmed']:
            error = "Please select a mood first."
        else:
            date_now = datetime.now().strftime('%d %b %Y, %H:%M')
            conn.execute(
                'INSERT INTO moods (mood_type, date) VALUES (?, ?)',
                (mood_type, date_now)
            )
            conn.commit()

            # Pick a quote for this mood
            import random
            quotes     = MOOD_QUOTES.get(mood_type, MOOD_QUOTES['Neutral'])
            picked     = random.choice(quotes)
            quote      = {**picked, 'mood': mood_type}

    moods = conn.execute(
        'SELECT * FROM moods ORDER BY id DESC LIMIT 20'
    ).fetchall()
    conn.close()

    return render_template('mood.html', moods=moods, error=error, quote=quote)

@app.route('/mood/delete/<int:mood_id>', methods=['POST'])
def delete_mood(mood_id):
    conn = get_db()
    conn.execute('DELETE FROM moods WHERE id = ?', (mood_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('mood'))

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    conn    = get_db()
    error   = None
    entries = conn.execute('SELECT * FROM journal ORDER BY id DESC').fetchall()
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            error = "Please write something before saving."
        else:
            date_now = datetime.now().strftime('%d %b %Y, %H:%M')
            conn.execute('INSERT INTO journal (content, date) VALUES (?, ?)', (content, date_now))
            conn.commit()
            entries = conn.execute('SELECT * FROM journal ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('journal.html', entries=entries, error=error)

@app.route('/journal/delete/<int:entry_id>', methods=['POST'])
def delete_journal(entry_id):
    conn = get_db()
    conn.execute('DELETE FROM journal WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('journal'))

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/breathing')
def breathing():
    return render_template('breathing.html')

@app.route('/analytics')
def analytics():
    conn = get_db()
    mood_counts = conn.execute('''
        SELECT mood_type, COUNT(*) as count
        FROM moods GROUP BY mood_type ORDER BY count DESC
    ''').fetchall()
    journal_count = conn.execute('SELECT COUNT(*) as count FROM journal').fetchone()
    mood_total    = conn.execute('SELECT COUNT(*) as count FROM moods').fetchone()
    top_mood      = mood_counts[0] if mood_counts else None
    conn.close()
    return render_template('analytics.html',
        mood_counts   = [dict(row) for row in mood_counts],
        journal_count = journal_count['count'],
        mood_total    = mood_total['count'],
        top_mood      = dict(top_mood) if top_mood else None
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/chat')
def chat():
    session['conversation']        = []
    session['consecutive_negative'] = 0
    return render_template('chat.html')

@app.route('/chat/send', methods=['POST'])
def chat_send():
    try:
        data      = request.get_json(force=True)
        user_text = data.get('message', '').strip()

        if not user_text:
            return jsonify({'error': 'empty'})

        conversation = session.get('conversation', [])
        turn         = len(conversation)

        # Sentiment analysis
        blob     = TextBlob(user_text)
        polarity = round(blob.sentiment.polarity, 2)

        # Fuzzy logic
        fuzzy = fuzzy_sentiment(polarity)

        # Keyword detection
        keyword = detect_keywords(user_text)

        # Crisis detection
        consecutive_negative = session.get('consecutive_negative', 0)

        if fuzzy['level'] == 1:
            consecutive_negative += 1
        else:
            consecutive_negative = 0

        session['consecutive_negative'] = consecutive_negative
        session.modified = True

        crisis_alert = consecutive_negative >= 2

        # Generate response
        if crisis_alert:
            bot_response = (
                "I am really concerned about you right now. "
                "You have been sharing very difficult feelings and I want to make sure "
                "you get the right support. Please reach out — "
                "800-HOPE (4673) is free and available 24/7 across the UAE. "
                "You do not have to face this alone. 💙"
            )
        else:
            bot_response = generate_response(user_text, polarity, fuzzy, keyword, turn)

        conversation.append({
            'user'    : user_text,
            'bot'     : bot_response,
            'polarity': polarity,
            'fuzzy'   : fuzzy['label'],
            'keyword' : keyword
        })
        session['conversation'] = conversation
        session.modified = True

        return jsonify({
            'bot_response'        : bot_response,
            'polarity'            : polarity,
            'fuzzy_label'         : fuzzy['label'],
            'fuzzy_emoji'         : fuzzy['emoji'],
            'fuzzy_level'         : fuzzy['level'],
            'keyword'             : keyword,
            'crisis_alert'        : crisis_alert,
            'consecutive_negative': consecutive_negative
        })

    except Exception as e:
        return jsonify({'error': str(e), 'bot_response': 'Sorry something went wrong. Please try again.'})

@app.route('/chat/clear', methods=['POST'])
def chat_clear():
    session['conversation']         = []
    session['consecutive_negative'] = 0
    session.modified = True
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)