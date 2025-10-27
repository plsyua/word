-- 2025-10-20 - 스마트 단어장 - 초기 설정 데이터
-- 파일 위치: C:\dev\word\database\init_data.sql - v1.0

-- ============================================================
-- user_settings 테이블 기본값 삽입
-- ============================================================

-- INSERT OR IGNORE: 이미 존재하면 건너뛰기 (중복 방지)

INSERT OR IGNORE INTO user_settings 
    (setting_key, setting_value, setting_type, description, modified_date) 
VALUES
    ('daily_word_goal', '50', 'integer', '일일 학습 목표 단어 수', datetime('now')),
    ('daily_time_goal', '30', 'integer', '일일 학습 목표 시간 (분)', datetime('now')),
    ('flashcard_time_limit', '0', 'integer', '플래시카드 제한 시간 (초, 0=무제한)', datetime('now')),
    ('exam_time_limit', '0', 'integer', '시험 전체 제한 시간 (초, 0=무제한)', datetime('now')),
    ('question_time_limit', '30', 'integer', '문제당 제한 시간 (초)', datetime('now')),
    ('theme_mode', 'light', 'string', 'UI 테마 (light/dark)', datetime('now')),
    ('font_size', '14', 'integer', '폰트 크기', datetime('now')),
    ('show_pronunciation', 'false', 'boolean', '발음 기호 표시 여부', datetime('now')),
    ('auto_save_enabled', 'true', 'boolean', '자동 저장 활성화', datetime('now')),
    ('auto_backup_enabled', 'true', 'boolean', '자동 백업 활성화', datetime('now'));