import sqlite3
from typing import List, Tuple, Optional

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('rankbot.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS math_problems (
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
            CREATE TABLE IF NOT EXISTS math_solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                pdf_url TEXT NOT NULL,
                score INTEGER DEFAULT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES math_problems (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cp_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER DEFAULT NULL,
                user_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                file_url TEXT DEFAULT NULL,
                completeness_score INTEGER DEFAULT NULL,
                elegance_score INTEGER DEFAULT NULL,
                speed_score INTEGER DEFAULT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES cp_problems (id)
            )
        ''')
        
        self.conn.commit()

    def add_math_problem(self, title: str, pdf_url: str, posted_by: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO math_problems (title, pdf_url, posted_by) VALUES (?, ?, ?)',
                      (title, pdf_url, posted_by))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def add_cp_problem(self, title: str, problem_url: str, platform: str, difficulty: str, posted_by: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO cp_problems (title, problem_url, platform, difficulty, posted_by) VALUES (?, ?, ?, ?, ?)',
                      (title, problem_url, platform, difficulty, posted_by))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def add_math_solution(self, problem_id: int, user_id: int, pdf_url: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO math_solutions (problem_id, user_id, pdf_url) VALUES (?, ?, ?)',
                      (problem_id, user_id, pdf_url))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def add_cp_submission(self, user_id: int, code: Optional[str] = None, language: Optional[str] = None, file_url: Optional[str] = None, problem_id: Optional[int] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO cp_submissions (user_id, code, language, file_url, problem_id) VALUES (?, ?, ?, ?, ?)',
                      (user_id, code or "", language or "", file_url, problem_id))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def update_math_solution_score(self, solution_id: int, score: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute('UPDATE math_solutions SET score = ? WHERE id = ?',
                      (score, solution_id))
        self.conn.commit()
    
    def update_cp_submission_scores(self, submission_id: int, completeness: int, elegance: int, speed: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute('UPDATE cp_submissions SET completeness_score = ?, elegance_score = ?, speed_score = ? WHERE id = ?',
                      (completeness, elegance, speed, submission_id))
        self.conn.commit()
    
    def get_math_leaderboard(self) -> List[Tuple[int, int]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, SUM(score) as total_score 
            FROM math_solutions 
            WHERE score IS NOT NULL 
            GROUP BY user_id 
            ORDER BY total_score DESC 
            LIMIT 10
        ''')
        return cursor.fetchall()
    
    def get_cp_leaderboard(self) -> List[Tuple[int, int]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, 
                   SUM(COALESCE(completeness_score, 0) + COALESCE(elegance_score, 0) + COALESCE(speed_score, 0)) as total_score 
            FROM cp_submissions 
            WHERE completeness_score IS NOT NULL 
            GROUP BY user_id 
            ORDER BY total_score DESC 
            LIMIT 10
        ''')
        return cursor.fetchall()
    
    def get_unreviewed_math_solutions(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.id, s.user_id, s.pdf_url, p.title, s.submitted_at 
            FROM math_solutions s
            JOIN math_problems p ON s.problem_id = p.id
            WHERE s.score IS NULL
            ORDER BY s.submitted_at ASC
        ''')
        return cursor.fetchall()
    
    def get_unreviewed_cp_submissions(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, user_id, code, language, file_url, submitted_at 
            FROM cp_submissions 
            WHERE completeness_score IS NULL 
            ORDER BY submitted_at ASC
        ''')
        return cursor.fetchall()
    
    def get_cp_problems(self, limit: int = 10) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cp_problems ORDER BY posted_at DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    
    def get_math_problems(self, limit: int = 10) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM math_problems ORDER BY posted_at DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    
    def get_cp_problem_by_id(self, problem_id: int) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cp_problems WHERE id = ?', (problem_id,))
        return cursor.fetchone()
    
    def get_math_problem_by_id(self, problem_id: int) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM math_problems WHERE id = ?', (problem_id,))
        return cursor.fetchone()
    
    def update_cp_problem(self, problem_id: int, title: Optional[str] = None, difficulty: Optional[str] = None) -> bool:
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        if difficulty is not None:
            updates.append('difficulty = ?')
            params.append(difficulty)
        
        if not updates:
            return False
        
        params.append(problem_id)
        query = f'UPDATE cp_problems SET {", ".join(updates)} WHERE id = ?'
        
        try:
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_cp_problem(self, problem_id: int) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM cp_problems WHERE id = ?', (problem_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def get_math_user_stats(self, user_id: int) -> Optional[Tuple[int, int, float, int]]:
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                COALESCE(SUM(score), 0) as total_score,
                COUNT(*) as total_count
            FROM math_solutions 
            WHERE user_id = ? AND score IS NOT NULL
        ''', (user_id,))
        
        result = cursor.fetchone()
        if not result or result[1] == 0:
            return None
        
        total_score, total_solutions = result
        avg_score = total_score / total_solutions if total_solutions > 0 else 0.0
        
        cursor.execute('''
            SELECT COUNT(*) + 1 
            FROM (
                SELECT user_id, SUM(score) as user_total 
                FROM math_solutions 
                WHERE score IS NOT NULL 
                GROUP BY user_id 
                HAVING user_total > ?
            )
        ''', (total_score,))
        
        rank = cursor.fetchone()[0]
        return (total_score, total_solutions, avg_score, rank)
    
    def get_cp_user_stats(self, user_id: int) -> Optional[Tuple[int, int, float, int]]:
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                COALESCE(SUM(completeness_score + elegance_score + speed_score), 0) as total_score,
                COUNT(*) as total_count
            FROM cp_submissions 
            WHERE user_id = ? AND completeness_score IS NOT NULL
        ''', (user_id,))
        
        result = cursor.fetchone()
        if not result or result[1] == 0:
            return None
        
        total_score, total_submissions = result
        avg_score = total_score / total_submissions if total_submissions > 0 else 0.0
        
        cursor.execute('''
            SELECT COUNT(*) + 1 
            FROM (
                SELECT user_id, SUM(completeness_score + elegance_score + speed_score) as user_total 
                FROM cp_submissions 
                WHERE completeness_score IS NOT NULL 
                GROUP BY user_id 
                HAVING user_total > ?
            )
        ''', (total_score,))
        
        rank = cursor.fetchone()[0]
        return (total_score, total_submissions, avg_score, rank)
    
    def get_math_leaderboard_paginated(self, offset: int, limit: int) -> List[Tuple[int, int]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, SUM(score) as total_score 
            FROM math_solutions 
            WHERE score IS NOT NULL 
            GROUP BY user_id 
            ORDER BY total_score DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return cursor.fetchall()
    
    def get_cp_leaderboard_paginated(self, offset: int, limit: int) -> List[Tuple[int, int]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, 
                   SUM(COALESCE(completeness_score, 0) + COALESCE(elegance_score, 0) + COALESCE(speed_score, 0)) as total_score 
            FROM cp_submissions 
            WHERE completeness_score IS NOT NULL 
            GROUP BY user_id 
            ORDER BY total_score DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return cursor.fetchall()
    
    def get_total_math_users_with_scores(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) 
            FROM math_solutions 
            WHERE score IS NOT NULL
        ''')
        return cursor.fetchone()[0]
    
    def get_total_cp_users_with_scores(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) 
            FROM cp_submissions 
            WHERE completeness_score IS NOT NULL
        ''')
        return cursor.fetchone()[0]

    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
