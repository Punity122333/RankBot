import sqlite3
from typing import List, Tuple, Optional

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('rankbot.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                pdf_url TEXT NOT NULL,
                posted_by INTEGER NOT NULL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cp_problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                problem_url TEXT NOT NULL,
                platform TEXT NOT NULL,
                difficulty TEXT DEFAULT '',
                posted_by INTEGER NOT NULL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                user_id INTEGER NOT NULL,
                pdf_url TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                score INTEGER DEFAULT 0,
                reviewed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                score INTEGER DEFAULT 0,
                reviewed BOOLEAN DEFAULT FALSE,
                completeness_score INTEGER DEFAULT 0,
                elegance_score INTEGER DEFAULT 0,
                speed_score INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def add_problem(self, title: str, pdf_url: str, posted_by: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO problems (title, pdf_url, posted_by) VALUES (?, ?, ?)',
                      (title, pdf_url, posted_by))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def add_cp_problem(self, title: str, problem_url: str, platform: str, difficulty: str, posted_by: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO cp_problems (title, problem_url, platform, difficulty, posted_by) VALUES (?, ?, ?, ?, ?)',
                      (title, problem_url, platform, difficulty, posted_by))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def add_solution(self, problem_id: int, user_id: int, pdf_url: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO solutions (problem_id, user_id, pdf_url) VALUES (?, ?, ?)',
                      (problem_id, user_id, pdf_url))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def add_submission(self, user_id: int, code: str, language: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO submissions (user_id, code, language) VALUES (?, ?, ?)',
                      (user_id, code, language))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def update_solution_score(self, solution_id: int, score: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute('UPDATE solutions SET score = ?, reviewed = TRUE WHERE id = ?',
                      (score, solution_id))
        self.conn.commit()
    
    def update_submission_scores(self, submission_id: int, completeness: int, elegance: int, speed: int) -> None:
        cursor = self.conn.cursor()
        total_score = completeness + elegance + speed
        cursor.execute('''UPDATE submissions SET completeness_score = ?, elegance_score = ?, 
                         speed_score = ?, score = ?, reviewed = TRUE WHERE id = ?''',
                      (completeness, elegance, speed, total_score, submission_id))
        self.conn.commit()
    
    def get_leaderboard(self) -> List[Tuple[int, int]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, SUM(score) as total_score FROM (
                SELECT user_id, score FROM solutions WHERE reviewed = TRUE
                UNION ALL
                SELECT user_id, score FROM submissions WHERE reviewed = TRUE
            ) GROUP BY user_id ORDER BY total_score DESC LIMIT 10
        ''')
        return cursor.fetchall()
    
    def get_unreviewed_solutions(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.id, s.user_id, s.pdf_url, p.title, s.submitted_at 
            FROM solutions s 
            JOIN problems p ON s.problem_id = p.id 
            WHERE s.reviewed = FALSE
        ''')
        return cursor.fetchall()
    
    def get_unreviewed_submissions(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, user_id, code, language, submitted_at 
            FROM submissions 
            WHERE reviewed = FALSE
        ''')
        return cursor.fetchall()
    
    def get_cp_problems(self, limit: int):
        cursor = self.conn.execute(
            "SELECT id, title, problem_url, platform, difficulty, posted_by, posted_at FROM cp_problems ORDER BY posted_at DESC LIMIT ?", (limit,)
        )
        return cursor.fetchall()
