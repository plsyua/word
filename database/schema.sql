-- 2025-10-20 - 스마트 단어장 - 데이터베이스 스키마
-- 파일 위치: C:\dev\word\database\schema.sql - v1.0
-- 외래키 제약조건 활성화
PRAGMA foreign_keys = ON;
-- ============================================================
-- 1. words 테이블 (단어 정보)
-- ============================================================
CREATE TABLE IF NOT EXISTS words (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    english TEXT NOT NULL,
    korean TEXT NOT NULL,
    memo TEXT,
    is_favorite INTEGER DEFAULT 0 CHECK(is_favorite IN (0, 1)),
    pronunciation TEXT,
    example_sentence TEXT,
    created_date TEXT NOT NULL,
    modified_date TEXT,
    UNIQUE(english, korean)
);
CREATE INDEX IF NOT EXISTS idx_words_english ON words(english);
CREATE INDEX IF NOT EXISTS idx_words_favorite ON words(is_favorite);
-- ============================================================
-- 2. learning_sessions 테이블 (학습 세션)
-- ============================================================
CREATE TABLE IF NOT EXISTS learning_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_type TEXT NOT NULL CHECK(session_type IN ('flashcard', 'exam')),
    start_time TEXT NOT NULL,
    end_time TEXT,
    total_words INTEGER DEFAULT 0 CHECK(total_words >= 0),
    correct_count INTEGER DEFAULT 0 CHECK(correct_count >= 0),
    wrong_count INTEGER DEFAULT 0 CHECK(wrong_count >= 0),
    accuracy_rate REAL DEFAULT 0.0 CHECK(accuracy_rate >= 0.0 AND accuracy_rate <= 100.0),
    study_mode TEXT CHECK(study_mode IN ('sequential', 'random', 'personalized'))
);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON learning_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_type ON learning_sessions(session_type);
-- ============================================================
-- 3. learning_history 테이블 (학습 이력)
-- ============================================================
CREATE TABLE IF NOT EXISTS learning_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    study_date TEXT NOT NULL,
    study_mode TEXT NOT NULL CHECK(study_mode IN ('flashcard_en_ko', 'flashcard_ko_en', 'exam_en_ko', 'exam_ko_en')),
    is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
    response_time REAL,
    user_answer TEXT,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (word_id) REFERENCES words(word_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_history_word_id ON learning_history(word_id);
CREATE INDEX IF NOT EXISTS idx_history_study_date ON learning_history(study_date);
CREATE INDEX IF NOT EXISTS idx_history_session_id ON learning_history(session_id);
-- ============================================================
-- 4. word_statistics 테이블 (단어별 통계)
-- ============================================================
CREATE TABLE IF NOT EXISTS word_statistics (
    word_id INTEGER PRIMARY KEY,
    total_attempts INTEGER DEFAULT 0 CHECK(total_attempts >= 0),
    correct_count INTEGER DEFAULT 0 CHECK(correct_count >= 0),
    wrong_count INTEGER DEFAULT 0 CHECK(wrong_count >= 0),
    wrong_rate REAL DEFAULT 0.0 CHECK(wrong_rate >= 0.0 AND wrong_rate <= 100.0),
    last_study_date TEXT,
    next_review_date TEXT,
    mastery_level INTEGER DEFAULT 0 CHECK(mastery_level >= 0 AND mastery_level <= 5),
    consecutive_correct INTEGER DEFAULT 0 CHECK(consecutive_correct >= 0),
    FOREIGN KEY (word_id) REFERENCES words(word_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_stats_wrong_rate ON word_statistics(wrong_rate DESC);
CREATE INDEX IF NOT EXISTS idx_stats_last_study ON word_statistics(last_study_date);
CREATE INDEX IF NOT EXISTS idx_stats_mastery ON word_statistics(mastery_level);
-- ============================================================
-- 5. exam_history 테이블 (시험 이력)
-- ============================================================
CREATE TABLE IF NOT EXISTS exam_history (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_date TEXT NOT NULL,
    exam_type TEXT NOT NULL CHECK(exam_type IN ('short_answer', 'multiple_choice')),
    question_mode TEXT NOT NULL CHECK(question_mode IN ('en_to_ko', 'ko_to_en', 'mixed')),
    total_questions INTEGER NOT NULL CHECK(total_questions > 0),
    correct_count INTEGER DEFAULT 0 CHECK(correct_count >= 0),
    wrong_count INTEGER DEFAULT 0 CHECK(wrong_count >= 0),
    score REAL NOT NULL CHECK(score >= 0.0 AND score <= 100.0),
    time_taken INTEGER CHECK(time_taken >= 0),
    time_limit INTEGER
);
CREATE INDEX IF NOT EXISTS idx_exam_date ON exam_history(exam_date);
CREATE INDEX IF NOT EXISTS idx_exam_score ON exam_history(score DESC);
-- ============================================================
-- 6. exam_questions 테이블 (시험 문제 상세)
-- ============================================================
CREATE TABLE IF NOT EXISTS exam_questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    question_number INTEGER NOT NULL CHECK(question_number > 0),
    user_answer TEXT,
    correct_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
    response_time REAL,
    choices TEXT,
    FOREIGN KEY (exam_id) REFERENCES exam_history(exam_id) ON DELETE CASCADE,
    FOREIGN KEY (word_id) REFERENCES words(word_id) ON DELETE CASCADE,
    UNIQUE(exam_id, question_number)
);
CREATE INDEX IF NOT EXISTS idx_questions_exam_id ON exam_questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_questions_word_id ON exam_questions(word_id);
CREATE INDEX IF NOT EXISTS idx_questions_correct ON exam_questions(is_correct);
-- ============================================================
-- 7. wrong_note 테이블 (오답 노트)
-- ============================================================
CREATE TABLE IF NOT EXISTS wrong_note (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    exam_id INTEGER,
    added_date TEXT NOT NULL,
    is_resolved INTEGER DEFAULT 0 CHECK(is_resolved IN (0, 1)),
    resolved_date TEXT,
    wrong_count INTEGER DEFAULT 1 CHECK(wrong_count > 0),
    FOREIGN KEY (word_id) REFERENCES words(word_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exam_history(exam_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_wrong_note_word_id ON wrong_note(word_id);
CREATE INDEX IF NOT EXISTS idx_wrong_note_resolved ON wrong_note(is_resolved);
CREATE INDEX IF NOT EXISTS idx_wrong_note_added_date ON wrong_note(added_date);
-- ============================================================
-- 8. user_settings 테이블 (사용자 설정)
-- ============================================================
CREATE TABLE IF NOT EXISTS user_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    setting_type TEXT NOT NULL CHECK(setting_type IN ('string', 'integer', 'boolean', 'float')),
    description TEXT,
    modified_date TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_settings_key ON user_settings(setting_key);