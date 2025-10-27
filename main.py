# 2025-10-27 - 스마트 단어장 Phase 1 통합 테스트
# 파일 위치: word/main.py

"""
Phase 1 통합 테스트 스크립트

목적:
- Model 계층 전체 동작 확인
- 기본 CRUD 동작 테스트
- 학습/시험 흐름 테스트
- 통계 업데이트 확인

실행 방법:
    python main.py
"""

import sys
from datetime import datetime

from database.db_connection import DBConnection
from models.word_model import WordModel
from models.learning_model import LearningModel
from models.exam_model import ExamModel
from models.statistics_model import StatisticsModel
from models.settings_model import SettingsModel
from utils.logger import get_logger

logger = get_logger(__name__)


def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_word_operations():
    """단어 CRUD 테스트"""
    print_section("1. 단어 관리 테스트")
    
    word_model = WordModel()
    
    # 1-1. 단어 추가
    print("\n[1-1] 단어 추가 테스트")
    test_words = [
        ("apple", "사과", "빨간색 과일"),
        ("book", "책", "지식의 보고"),
        ("computer", "컴퓨터", "전자 계산기"),
        ("door", "문", "출입구"),
        ("elephant", "코끼리", "큰 동물")
    ]
    
    added_count = 0
    for english, korean, memo in test_words:
        word_id = word_model.add_word(english, korean, memo)
        if word_id:
            print(f"  ✓ 단어 추가 성공: {english} = {korean} (ID: {word_id})")
            added_count += 1
        else:
            print(f"  ✗ 단어 추가 실패: {english}")
    
    print(f"\n총 {added_count}개 단어 추가 완료")
    
    # 1-2. 단어 조회
    print("\n[1-2] 단어 조회 테스트")
    all_words = word_model.get_all_words()
    print(f"  전체 단어 수: {len(all_words)}개")
    
    # 1-3. 검색 테스트
    print("\n[1-3] 단어 검색 테스트")
    search_results = word_model.search_words("apple")
    if search_results:
        print(f"  'apple' 검색 결과: {len(search_results)}개")
        for word in search_results:
            print(f"    - {word['english']}: {word['korean']}")
    
    # 1-4. 즐겨찾기 테스트
    print("\n[1-4] 즐겨찾기 테스트")
    if all_words:
        first_word_id = all_words[0]['word_id']
        word_model.toggle_favorite(first_word_id)
        print(f"  ✓ 단어 ID {first_word_id} 즐겨찾기 설정")
    
    return all_words


def test_learning_session(words):
    """학습 세션 테스트"""
    print_section("2. 학습 세션 테스트")
    
    learning_model = LearningModel()
    statistics_model = StatisticsModel()
    
    if not words or len(words) < 3:
        print("  ✗ 테스트할 단어가 부족합니다.")
        return None
    
    # 2-1. 세션 생성
    print("\n[2-1] 학습 세션 생성")
    session_id = learning_model.create_session(
        session_type='flashcard',
        study_mode='sequential'
    )
    print(f"  ✓ 세션 생성 완료 (ID: {session_id})")
    
    # 2-2. 학습 이력 추가 (정답 2개, 오답 1개)
    print("\n[2-2] 학습 이력 추가")
    results = [
        (words[0]['word_id'], True, 5),   # apple - 정답 (5초)
        (words[1]['word_id'], True, 3),   # book - 정답 (3초)
        (words[2]['word_id'], False, 8),  # computer - 오답 (8초)
    ]
    
    for word_id, is_correct, response_time in results:
        word = next(w for w in words if w['word_id'] == word_id)
        success = learning_model.add_learning_history(
            session_id=session_id,
            word_id=word_id,
            study_mode='flashcard_ko_en',
            is_correct=is_correct,
            response_time=response_time
        )
        
        if success:
            result_text = "정답" if is_correct else "오답"
            print(f"  ✓ {word['english']}: {result_text} ({response_time}초)")
            
            # 통계 업데이트
            statistics_model.update_word_statistics(word_id, is_correct)
    
    # 2-3. 세션 종료
    print("\n[2-3] 세션 종료")
    # 통계 계산
    total_words = len(results)
    correct_count = sum(1 for _, is_correct, _ in results if is_correct)
    wrong_count = total_words - correct_count
    
    success = learning_model.end_session(
        session_id=session_id,
        total_words=total_words,
        correct_count=correct_count,
        wrong_count=wrong_count
    )
    
    if success:
        print(f"  ✓ 세션 종료 완료")
        print(f"    - 학습 단어 수: {total_words}개")
        print(f"    - 정답: {correct_count}개")
        print(f"    - 오답: {wrong_count}개")
        print(f"    - 정답률: {(correct_count/total_words*100):.1f}%")
    
    return session_id


def test_exam_flow(words):
    """시험 흐름 테스트"""
    print_section("3. 시험 흐름 테스트")
    
    exam_model = ExamModel()
    statistics_model = StatisticsModel()
    
    if not words or len(words) < 3:
        print("  ✗ 테스트할 단어가 부족합니다.")
        return None
    
    # 3-1. 시험 생성
    print("\n[3-1] 시험 생성")
    exam_id = exam_model.create_exam(
        exam_type='short_answer',
        question_mode='ko_to_en',
        total_questions=3
    )
    print(f"  ✓ 시험 생성 완료 (ID: {exam_id})")
    
    # 3-2. 문제 저장 및 답안 작성
    print("\n[3-2] 문제 및 답안 작성")
    answers = [
        (words[0]['word_id'], "apple", True),      # 정답
        (words[1]['word_id'], "book", True),       # 정답
        (words[2]['word_id'], "laptop", False),    # 오답 (정답: computer)
    ]
    
    for idx, (word_id, user_answer, is_correct) in enumerate(answers, 1):
        word = next(w for w in words if w['word_id'] == word_id)
        
        # 문제 저장 (답안 포함)
        exam_model.save_exam_question(
            exam_id=exam_id,
            word_id=word_id,
            question_number=idx,
            correct_answer=word['english'],
            user_answer=user_answer,
            is_correct=1 if is_correct else 0
        )
        
        result_text = "정답" if is_correct else "오답"
        print(f"  문제 {idx}: {word['korean']} → {user_answer} ({result_text})")
    
    # 3-3. 시험 종료 및 채점
    print("\n[3-3] 시험 종료 및 채점")
    # 점수 계산
    total_questions = len(answers)
    correct_count = sum(1 for _, _, is_correct in answers if is_correct)
    score = (correct_count / total_questions) * 100
    time_taken = 30  # 가상의 소요 시간 (초)
    
    success = exam_model.finish_exam(
        exam_id=exam_id,
        score=score,
        time_taken=time_taken
    )
    
    if success:
        print(f"  ✓ 시험 종료 완료")
        print(f"    - 총 문항: {total_questions}개")
        print(f"    - 정답: {correct_count}개")
        print(f"    - 오답: {total_questions - correct_count}개")
        print(f"    - 점수: {score:.1f}점")
    
    return exam_id


def test_statistics():
    """통계 조회 테스트"""
    print_section("4. 통계 조회 테스트")
    
    statistics_model = StatisticsModel()
    
    # 4-1. 오늘의 통계
    print("\n[4-1] 오늘의 학습 통계")
    today_stats = statistics_model.get_today_statistics()
    if today_stats and today_stats['total_words'] > 0:
        print(f"  ✓ 오늘 학습한 단어 수: {today_stats['total_words']}개")
        print(f"  ✓ 학습 세션 수: {today_stats['sessions']}회")
        print(f"  ✓ 정답률: {today_stats['accuracy']:.1f}%")
    else:
        print("  학습 기록이 없습니다.")
    
    # 4-2. 오답률 높은 단어
    print("\n[4-2] 오답률 높은 단어 Top 3")
    top_wrong = statistics_model.get_top_wrong_words(limit=3)
    if top_wrong:
        for idx, word in enumerate(top_wrong, 1):
            print(f"  {idx}. {word['english']} ({word['korean']})")
            print(f"     오답률: {word['wrong_rate']:.1f}%, 오답 횟수: {word['wrong_count']}회")
    else:
        print("  오답 단어가 없습니다.")
    
    # 4-3. 숙지도 분포
    print("\n[4-3] 숙지도 레벨 분포")
    mastery_dist = statistics_model.get_mastery_distribution()
    if mastery_dist:
        for level, count in mastery_dist.items():
            print(f"  레벨 {level}: {count}개")


def test_settings():
    """설정 관리 테스트"""
    print_section("5. 설정 관리 테스트")
    
    settings_model = SettingsModel()
    
    # 5-1. 설정 조회
    print("\n[5-1] 전체 설정 조회")
    all_settings = settings_model.get_all_settings()
    for key, value in all_settings.items():
        print(f"  {key}: {value}")
    
    # 5-2. 설정 변경
    print("\n[5-2] 설정 변경 테스트")
    original_goal = settings_model.get_setting('daily_word_goal')
    print(f"  현재 일일 목표: {original_goal}개")
    
    settings_model.set_setting('daily_word_goal', 100)
    new_goal = settings_model.get_setting('daily_word_goal')
    print(f"  변경된 일일 목표: {new_goal}개")
    
    # 원래 값으로 복원
    settings_model.set_setting('daily_word_goal', original_goal)
    print(f"  ✓ 원래 값으로 복원 완료")


def run_integration_test():
    """통합 테스트 실행"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Phase 1 통합 테스트 시작".center(56) + "  *")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print(f"\n시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # 1. 단어 관리 테스트
        words = test_word_operations()
        
        # 2. 학습 세션 테스트
        if words:
            test_learning_session(words)
        
        # 3. 시험 흐름 테스트
        if words:
            test_exam_flow(words)
        
        # 4. 통계 조회 테스트
        test_statistics()
        
        # 5. 설정 관리 테스트
        test_settings()
        
        # 완료 메시지
        print_section("✓ Phase 1 통합 테스트 완료!")
        print(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n모든 Model 계층이 정상적으로 동작합니다.")
        print("Phase 2 (Controller 계층) 구현을 시작할 수 있습니다.\n")
        
        return True
        
    except Exception as e:
        print_section("✗ 테스트 실패")
        print(f"\n오류 발생: {str(e)}")
        logger.error(f"통합 테스트 실패: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    print("\n")
    success = run_integration_test()
    sys.exit(0 if success else 1)