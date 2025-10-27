# 2025-10-27 - 스마트 단어장 - 설정 컨트롤러
# 파일 위치: word/controllers/settings_controller.py - v1.0

"""
설정 관리 컨트롤러

주요 기능:
- 설정 조회/변경
- 설정 검증
- 카테고리별 설정 관리
- 기본값 초기화
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.settings_model import SettingsModel
from utils.logger import get_logger
from utils.validators import validate_positive_integer, validate_setting_value

logger = get_logger(__name__)


class SettingsController:
    """설정 관리 컨트롤러"""
    
    # 설정 카테고리 분류
    CATEGORIES = {
        'learning': ['daily_word_goal', 'daily_time_goal'],
        'exam': ['flashcard_time_limit', 'exam_time_limit'],
        'ui': ['theme_mode', 'font_size', 'show_pronunciation']
    }
    
    def __init__(self):
        """컨트롤러 초기화"""
        self.settings_model = SettingsModel()
        self.logger = logger
    
    # === 설정 조회 ===
    
    def get_all_settings(self):
        """
        전체 설정 조회
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 설정 딕셔너리)
        """
        try:
            settings = self.settings_model.get_all_settings()
            
            if settings:
                self.logger.debug(f"전체 설정 조회 완료: {len(settings)}개")
                return (True, "설정 조회 완료", settings)
            else:
                self.logger.warning("설정이 비어있음")
                return (False, "설정을 찾을 수 없습니다.", None)
                
        except Exception as e:
            self.logger.error(f"설정 조회 실패: {e}", exc_info=True)
            return (False, "설정 조회 중 오류가 발생했습니다.", None)
    
    def get_setting(self, key):
        """
        특정 설정 조회
        
        Args:
            key (str): 설정 키
        
        Returns:
            Tuple[bool, str, Any]: (성공여부, 메시지, 설정 값)
        """
        try:
            if not key or not isinstance(key, str):
                return (False, "유효하지 않은 설정 키입니다.", None)
            
            value = self.settings_model.get_setting(key)
            
            if value is not None:
                self.logger.debug(f"설정 조회: {key}={value}")
                return (True, "설정 조회 완료", value)
            else:
                self.logger.warning(f"존재하지 않는 설정 키: {key}")
                return (False, f"'{key}' 설정을 찾을 수 없습니다.", None)
                
        except Exception as e:
            self.logger.error(f"설정 조회 실패 ({key}): {e}", exc_info=True)
            return (False, "설정 조회 중 오류가 발생했습니다.", None)
    
    def get_settings_by_category(self):
        """
        카테고리별 설정 조회
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 카테고리별 설정)
            예: {
                'learning': {'daily_word_goal': 50, ...},
                'exam': {'flashcard_time_limit': 0, ...},
                'ui': {'theme_mode': 'light', ...}
            }
        """
        try:
            all_settings = self.settings_model.get_all_settings()
            
            if not all_settings:
                return (False, "설정을 찾을 수 없습니다.", None)
            
            # 카테고리별로 분류
            categorized = {}
            for category, keys in self.CATEGORIES.items():
                categorized[category] = {}
                for key in keys:
                    if key in all_settings:
                        categorized[category][key] = all_settings[key]
            
            self.logger.debug(f"카테고리별 설정 조회 완료: {len(categorized)}개 카테고리")
            return (True, "설정 조회 완료", categorized)
            
        except Exception as e:
            self.logger.error(f"카테고리별 설정 조회 실패: {e}", exc_info=True)
            return (False, "설정 조회 중 오류가 발생했습니다.", None)
    
    # === 설정 변경 ===
    
    def update_setting(self, key, value):
        """
        설정 변경
        
        Args:
            key (str): 설정 키
            value: 새 값
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            # 1. 키 유효성 확인
            if not key or not isinstance(key, str):
                return (False, "유효하지 않은 설정 키입니다.")
            
            # 2. 설정 존재 여부 확인
            setting_info = self.settings_model.get_setting_info(key)
            if not setting_info:
                return (False, f"'{key}' 설정을 찾을 수 없습니다.")
            
            # 3. 값 검증
            setting_type = setting_info['setting_type']
            is_valid, error_msg = validate_setting_value(key, value, setting_type)
            if not is_valid:
                self.logger.warning(f"설정 검증 실패 ({key}={value}): {error_msg}")
                return (False, error_msg)
            
            # 4. 설정 변경
            success = self.settings_model.set_setting(key, value)
            
            if success:
                self.logger.info(f"설정 변경 완료: {key}={value}")
                return (True, f"'{key}' 설정이 변경되었습니다.")
            else:
                self.logger.error(f"설정 변경 실패: {key}={value}")
                return (False, "설정 변경에 실패했습니다.")
                
        except Exception as e:
            self.logger.error(f"설정 변경 실패 ({key}={value}): {e}", exc_info=True)
            return (False, "설정 변경 중 오류가 발생했습니다.")
    
    def update_multiple_settings(self, settings_dict):
        """
        여러 설정 한번에 변경
        
        Args:
            settings_dict (Dict): {key: value, ...}
        
        Returns:
            Tuple[bool, str, List]: (성공여부, 메시지, 실패한 키 목록)
        """
        try:
            if not settings_dict or not isinstance(settings_dict, dict):
                return (False, "유효하지 않은 설정 데이터입니다.", [])
            
            failed_keys = []
            success_count = 0
            
            for key, value in settings_dict.items():
                success, message = self.update_setting(key, value)
                if success:
                    success_count += 1
                else:
                    failed_keys.append(key)
                    self.logger.warning(f"설정 변경 실패: {key} - {message}")
            
            total_count = len(settings_dict)
            
            if success_count == total_count:
                self.logger.info(f"모든 설정 변경 완료: {success_count}개")
                return (True, f"{success_count}개 설정이 변경되었습니다.", [])
            elif success_count > 0:
                self.logger.warning(
                    f"일부 설정 변경: 성공 {success_count}개, 실패 {len(failed_keys)}개"
                )
                return (
                    False, 
                    f"{success_count}개 설정 변경 완료, {len(failed_keys)}개 실패",
                    failed_keys
                )
            else:
                self.logger.error("모든 설정 변경 실패")
                return (False, "모든 설정 변경에 실패했습니다.", failed_keys)
                
        except Exception as e:
            self.logger.error(f"다중 설정 변경 실패: {e}", exc_info=True)
            return (False, "설정 변경 중 오류가 발생했습니다.", [])
    
    def reset_to_default(self, key=None):
        """
        기본값으로 초기화
        
        Args:
            key (str, optional): 특정 설정 키 (None이면 전체 초기화)
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            success = self.settings_model.reset_to_default(key)
            
            if success:
                if key:
                    self.logger.info(f"설정 초기화 완료: {key}")
                    return (True, f"'{key}' 설정이 기본값으로 초기화되었습니다.")
                else:
                    self.logger.info("전체 설정 초기화 완료")
                    return (True, "모든 설정이 기본값으로 초기화되었습니다.")
            else:
                self.logger.error(f"설정 초기화 실패: {key}")
                return (False, "설정 초기화에 실패했습니다.")
                
        except Exception as e:
            self.logger.error(f"설정 초기화 실패 ({key}): {e}", exc_info=True)
            return (False, "설정 초기화 중 오류가 발생했습니다.")
    
    # === 설정 검증 ===
    
    def validate_setting(self, key, value):
        """
        설정 값 검증 (실제 변경 없이 검증만)
        
        Args:
            key (str): 설정 키
            value: 검증할 값
        
        Returns:
            Tuple[bool, str]: (유효여부, 에러 메시지 or 성공 메시지)
        """
        try:
            # 1. 설정 존재 여부 확인
            setting_info = self.settings_model.get_setting_info(key)
            if not setting_info:
                return (False, f"'{key}' 설정을 찾을 수 없습니다.")
            
            # 2. 타입별 검증
            setting_type = setting_info['setting_type']
            is_valid, error_msg = validate_setting_value(key, value, setting_type)
            
            if is_valid:
                return (True, "유효한 설정 값입니다.")
            else:
                return (False, error_msg)
                
        except Exception as e:
            self.logger.error(f"설정 검증 실패 ({key}={value}): {e}", exc_info=True)
            return (False, "설정 검증 중 오류가 발생했습니다.")
    
    # === 유틸리티 ===
    
    def get_setting_info(self, key):
        """
        설정 상세 정보 조회 (키, 값, 타입, 설명)
        
        Args:
            key (str): 설정 키
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 설정 정보)
        """
        try:
            info = self.settings_model.get_setting_info(key)
            
            if info:
                return (True, "설정 정보 조회 완료", info)
            else:
                return (False, f"'{key}' 설정을 찾을 수 없습니다.", None)
                
        except Exception as e:
            self.logger.error(f"설정 정보 조회 실패 ({key}): {e}", exc_info=True)
            return (False, "설정 정보 조회 중 오류가 발생했습니다.", None)
    
    def get_category_for_key(self, key):
        """
        설정 키의 카테고리 조회
        
        Args:
            key (str): 설정 키
        
        Returns:
            str or None: 카테고리 이름
        """
        for category, keys in self.CATEGORIES.items():
            if key in keys:
                return category
        return None