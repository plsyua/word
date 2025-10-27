# 2025-10-20 - 스마트 단어장 - 설정 모델
# 파일 위치: C:\dev\word\models\settings_model.py - v1.0

"""
사용자 설정 관리
- 설정 조회/변경
- 타입 변환
- 기본값 초기화
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.base_model import BaseModel
from utils.datetime_helper import get_current_datetime
from utils.validators import validate_setting_value


class SettingsModel(BaseModel):
    """
    설정 모델 클래스
    user_settings 테이블 관리
    """
    
    def get_setting(self, key):
        """
        설정 값 조회 (타입 변환 적용)
        
        Args:
            key (str): 설정 키
        
        Returns:
            타입 변환된 값 또는 None (없으면)
        """
        query = "SELECT * FROM user_settings WHERE setting_key = ?"
        result = self.execute_query(query, (key,))
        
        if not result:
            self.logger.warning(f"설정 키 없음: {key}")
            return None
        
        setting = result[0]
        value = setting['setting_value']
        setting_type = setting['setting_type']
        
        # 타입 변환
        converted_value = self._convert_type(value, setting_type)
        
        return converted_value
    
    def set_setting(self, key, value):
        """
        설정 값 변경
        
        Args:
            key (str): 설정 키
            value: 설정 값
        
        Returns:
            bool: 성공 여부
        """
        # 설정 존재 확인
        query = "SELECT setting_type FROM user_settings WHERE setting_key = ?"
        result = self.execute_query(query, (key,))
        
        if not result:
            self.logger.warning(f"설정 키 없음: {key}")
            return False
        
        setting_type = result[0]['setting_type']
        
        # 값 검증
        is_valid, error_msg = validate_setting_value(key, str(value), setting_type)
        if not is_valid:
            self.logger.warning(f"설정 값 검증 실패: {error_msg}")
            return False
        
        # 값 업데이트
        update_query = """
            UPDATE user_settings 
            SET setting_value = ?, modified_date = ?
            WHERE setting_key = ?
        """
        params = (str(value), get_current_datetime(), key)
        
        result = self.execute_update(update_query, params)
        
        if result and result > 0:
            self.logger.info(f"설정 변경: {key} = {value}")
            return True
        else:
            return False
    
    def get_all_settings(self):
        """
        전체 설정 조회 (타입 변환 적용)
        
        Returns:
            dict: {key: value} 형태의 설정 딕셔너리
        """
        query = "SELECT * FROM user_settings ORDER BY setting_key"
        result = self.execute_query(query)
        
        settings = {}
        for row in result:
            key = row['setting_key']
            value = row['setting_value']
            setting_type = row['setting_type']
            
            # 타입 변환
            settings[key] = self._convert_type(value, setting_type)
        
        self.logger.info(f"전체 설정 조회: {len(settings)}개")
        return settings
    
    def get_settings_by_type(self, setting_type):
        """
        타입별 설정 조회
        
        Args:
            setting_type (str): 'string', 'integer', 'boolean', 'float'
        
        Returns:
            dict: {key: value} 형태의 설정 딕셔너리
        """
        query = "SELECT * FROM user_settings WHERE setting_type = ? ORDER BY setting_key"
        result = self.execute_query(query, (setting_type,))
        
        settings = {}
        for row in result:
            key = row['setting_key']
            value = row['setting_value']
            settings[key] = self._convert_type(value, setting_type)
        
        return settings
    
    def reset_to_default(self, key=None):
        """
        기본값으로 초기화
        
        Args:
            key (str, optional): 설정 키. None이면 전체 초기화
        
        Returns:
            bool: 성공 여부
        """
        # 기본값 정의 (init_data.sql과 동일)
        default_settings = {
            'daily_word_goal': '50',
            'daily_time_goal': '30',
            'flashcard_time_limit': '0',
            'exam_time_limit': '0',
            'question_time_limit': '30',
            'theme_mode': 'light',
            'font_size': '14',
            'show_pronunciation': 'false',
            'auto_save_enabled': 'true',
            'auto_backup_enabled': 'true'
        }
        
        if key:
            # 특정 키만 초기화
            if key not in default_settings:
                self.logger.warning(f"기본값 없음: {key}")
                return False
            
            return self.set_setting(key, default_settings[key])
        else:
            # 전체 초기화
            success_count = 0
            for k, v in default_settings.items():
                if self.set_setting(k, v):
                    success_count += 1
            
            self.logger.info(f"설정 초기화 완료: {success_count}개")
            return success_count == len(default_settings)
    
    def add_setting(self, key, value, setting_type, description=None):
        """
        새 설정 추가
        
        Args:
            key (str): 설정 키
            value: 설정 값
            setting_type (str): 'string', 'integer', 'boolean', 'float'
            description (str, optional): 설명
        
        Returns:
            bool: 성공 여부
        """
        # 중복 확인
        if self.get_setting(key) is not None:
            self.logger.warning(f"설정 키 중복: {key}")
            return False
        
        # 값 검증
        is_valid, error_msg = validate_setting_value(key, str(value), setting_type)
        if not is_valid:
            self.logger.warning(f"설정 값 검증 실패: {error_msg}")
            return False
        
        # 추가
        query = """
            INSERT INTO user_settings 
                (setting_key, setting_value, setting_type, description, modified_date)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (key, str(value), setting_type, description, get_current_datetime())
        
        result = self.execute_update(query, params)
        
        if result:
            self.logger.info(f"설정 추가: {key} = {value}")
            return True
        else:
            return False
    
    def delete_setting(self, key):
        """
        설정 삭제
        
        Args:
            key (str): 설정 키
        
        Returns:
            bool: 성공 여부
        """
        query = "DELETE FROM user_settings WHERE setting_key = ?"
        result = self.execute_update(query, (key,))
        
        if result and result > 0:
            self.logger.info(f"설정 삭제: {key}")
            return True
        else:
            self.logger.warning(f"설정 삭제 실패: {key} (존재하지 않음)")
            return False
    
    def get_setting_info(self, key):
        """
        설정 상세 정보 조회 (타입, 설명 포함)
        
        Args:
            key (str): 설정 키
        
        Returns:
            dict: 설정 정보 또는 None
        """
        query = "SELECT * FROM user_settings WHERE setting_key = ?"
        result = self.execute_query(query, (key,))
        return result[0] if result else None
    
    def _convert_type(self, value, setting_type):
        """
        문자열을 실제 타입으로 변환
        
        Args:
            value (str): 문자열 값
            setting_type (str): 'string', 'integer', 'boolean', 'float'
        
        Returns:
            변환된 값
        """
        if value is None:
            return None
        
        try:
            if setting_type == 'integer':
                return int(value)
            elif setting_type == 'float':
                return float(value)
            elif setting_type == 'boolean':
                return value.lower() in ('true', '1', 'yes')
            else:  # 'string'
                return str(value)
        except (ValueError, TypeError) as e:
            self.logger.warning(f"타입 변환 실패: {value} -> {setting_type} ({e})")
            return value


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("SettingsModel 테스트")
    print("=" * 50)
    
    model = SettingsModel()
    
    # 전체 설정 조회
    print("\n[전체 설정 조회]")
    all_settings = model.get_all_settings()
    print(f"✓ 총 {len(all_settings)}개 설정")
    for key, value in list(all_settings.items())[:5]:
        print(f"  - {key}: {value} ({type(value).__name__})")
    
    # 개별 설정 조회
    print("\n[개별 설정 조회]")
    daily_goal = model.get_setting('daily_word_goal')
    print(f"✓ daily_word_goal: {daily_goal} ({type(daily_goal).__name__})")
    
    theme = model.get_setting('theme_mode')
    print(f"✓ theme_mode: {theme} ({type(theme).__name__})")
    
    show_pronunciation = model.get_setting('show_pronunciation')
    print(f"✓ show_pronunciation: {show_pronunciation} ({type(show_pronunciation).__name__})")
    
    # 설정 변경
    print("\n[설정 변경]")
    success = model.set_setting('daily_word_goal', 100)
    if success:
        new_value = model.get_setting('daily_word_goal')
        print(f"✓ daily_word_goal 변경: {new_value}")
    
    # 타입별 조회
    print("\n[타입별 설정 조회]")
    integer_settings = model.get_settings_by_type('integer')
    print(f"✓ integer 타입: {len(integer_settings)}개")
    for key, value in integer_settings.items():
        print(f"  - {key}: {value}")
    
    # 설정 정보 조회
    print("\n[설정 정보 조회]")
    info = model.get_setting_info('daily_word_goal')
    if info:
        print(f"✓ 키: {info['setting_key']}")
        print(f"  값: {info['setting_value']}")
        print(f"  타입: {info['setting_type']}")
        print(f"  설명: {info['description']}")
    
    # 기본값으로 초기화
    print("\n[기본값으로 초기화]")
    success = model.reset_to_default('daily_word_goal')
    if success:
        reset_value = model.get_setting('daily_word_goal')
        print(f"✓ daily_word_goal 초기화: {reset_value}")
    
    # 새 설정 추가 테스트
    print("\n[새 설정 추가]")
    success = model.add_setting('test_setting', 'test_value', 'string', '테스트 설정')
    if success:
        print(f"✓ test_setting 추가 성공")
        # 삭제
        model.delete_setting('test_setting')
        print(f"✓ test_setting 삭제 완료")
    
    print("\n" + "=" * 50)
    print("SettingsModel 테스트 완료")
    print("=" * 50)