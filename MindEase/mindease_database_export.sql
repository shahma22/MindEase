-- MindEase Database SQL Export
-- Project: AI-Powered Mental Health Wellness Website
-- Student: Shahma Mohammed Salih | 2527465
-- Module: SEC6201 Undergraduate Project
-- Generated: April 2026

-- NOTE: This file creates the database schema and inserts sample data.
-- The actual mindease.db file is auto-created when you run python app.py

-- ============================================================
-- TABLE: moods
-- ============================================================

CREATE TABLE IF NOT EXISTS moods (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    mood_type TEXT    NOT NULL,
    date      TEXT    NOT NULL
);

-- Sample mood data
INSERT INTO moods (id, mood_type, date) VALUES (1, 'Happy', '01 Apr 2026, 09:15');
INSERT INTO moods (id, mood_type, date) VALUES (2, 'Stressed', '02 Apr 2026, 14:30');
INSERT INTO moods (id, mood_type, date) VALUES (3, 'Anxious', '03 Apr 2026, 11:00');
INSERT INTO moods (id, mood_type, date) VALUES (4, 'Neutral', '04 Apr 2026, 16:45');
INSERT INTO moods (id, mood_type, date) VALUES (5, 'Tired', '05 Apr 2026, 08:20');

-- ============================================================
-- TABLE: journal
-- ============================================================

CREATE TABLE IF NOT EXISTS journal (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT    NOT NULL,
    date    TEXT    NOT NULL
);

-- Sample journal data
INSERT INTO journal (id, content, date) VALUES (1, 'Today was a good day. I managed to finish my assignment on time and felt really proud of myself.', '01 Apr 2026, 21:00');
INSERT INTO journal (id, content, date) VALUES (2, 'Feeling overwhelmed with deadlines but trying to take it one step at a time.', '03 Apr 2026, 22:15');
INSERT INTO journal (id, content, date) VALUES (3, 'Had a great conversation with my friend today. It really helped me feel less alone.', '05 Apr 2026, 20:30');
