"""OEM 설정 관리 서비스"""
import os
import glob

from src.utils.yaml_helpers import load_yaml, load_yaml_string
from src.utils.constants import SWE_STAGES


def load_oem_config(config_yaml_string):
    """YAML 문자열을 파싱하여 OEM 설정 딕셔너리로 변환

    Args:
        config_yaml_string: OEM 설정이 담긴 YAML 문자열

    Returns:
        dict: 파싱된 OEM 설정 딕셔너리

    Raises:
        ValueError: YAML 파싱 실패 시
    """
    if not config_yaml_string or not config_yaml_string.strip():
        raise ValueError("Empty configuration YAML string")
    try:
        config = load_yaml_string(config_yaml_string)
    except Exception as e:
        raise ValueError(f"Failed to parse OEM configuration YAML: {e}")
    if config is None:
        raise ValueError("Configuration YAML parsed to None")
    return config


def validate_oem_config(config):
    """OEM 설정 구조를 검증

    필수 필드:
        - oem_name (str)
        - stages (dict) with at least one SWE.x entry
        - 각 stage에 enabled, required_documents, checklist

    Args:
        config: OEM 설정 딕셔너리

    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    errors = []

    if not isinstance(config, dict):
        return False, ["Configuration must be a dictionary"]

    # oem_name 확인
    if "oem_name" not in config:
        errors.append("Missing required field: 'oem_name'")
    elif not isinstance(config["oem_name"], str) or not config["oem_name"].strip():
        errors.append("'oem_name' must be a non-empty string")

    # stages 확인
    if "stages" not in config:
        errors.append("Missing required field: 'stages'")
        return len(errors) == 0, errors

    stages = config["stages"]
    if not isinstance(stages, dict):
        errors.append("'stages' must be a dictionary")
        return False, errors

    valid_swe_levels = set(SWE_STAGES.keys())
    found_stages = set()

    for stage_key, stage_data in stages.items():
        if stage_key not in valid_swe_levels:
            errors.append(f"Unknown stage key: '{stage_key}'. Valid keys: {sorted(valid_swe_levels)}")
            continue

        found_stages.add(stage_key)

        if not isinstance(stage_data, dict):
            errors.append(f"Stage '{stage_key}' must be a dictionary")
            continue

        # enabled 필드
        if "enabled" not in stage_data:
            errors.append(f"Stage '{stage_key}': missing 'enabled' field")

        # required_documents 필드
        if "required_documents" not in stage_data:
            errors.append(f"Stage '{stage_key}': missing 'required_documents' field")
        elif not isinstance(stage_data["required_documents"], list):
            errors.append(f"Stage '{stage_key}': 'required_documents' must be a list")
        else:
            for i, doc in enumerate(stage_data["required_documents"]):
                if not isinstance(doc, dict):
                    errors.append(f"Stage '{stage_key}': document [{i}] must be a dictionary")
                elif "name" not in doc:
                    errors.append(f"Stage '{stage_key}': document [{i}] missing 'name' field")

        # checklist 필드
        if "checklist" not in stage_data:
            errors.append(f"Stage '{stage_key}': missing 'checklist' field")
        elif not isinstance(stage_data["checklist"], list):
            errors.append(f"Stage '{stage_key}': 'checklist' must be a list")

    if not found_stages:
        errors.append("No valid SWE stages found in configuration")

    return len(errors) == 0, errors


def get_default_configs():
    """config/default_oem_configs/ 디렉토리에서 모든 YAML 설정 파일을 로드

    Returns:
        list[dict]: 각 항목은 {'filename': str, 'config': dict}
    """
    config_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "config", "default_oem_configs"
    )

    configs = []
    if not os.path.isdir(config_dir):
        return configs

    yaml_files = sorted(glob.glob(os.path.join(config_dir, "*.yaml")))
    for filepath in yaml_files:
        try:
            config = load_yaml(filepath)
            if config:
                configs.append({
                    "filename": os.path.basename(filepath),
                    "filepath": filepath,
                    "config": config,
                })
        except Exception:
            # 파싱 실패한 파일은 건너뜀
            continue

    return configs


def get_stage_config(oem_config, swe_level):
    """OEM 설정에서 특정 SWE 단계의 설정을 추출

    Args:
        oem_config: OEM 설정 딕셔너리 (load_oem_config 결과)
        swe_level: SWE 단계 키 (예: "SWE.1")

    Returns:
        dict or None: 해당 단계 설정, 없으면 None
    """
    if not oem_config or "stages" not in oem_config:
        return None

    stages = oem_config.get("stages", {})
    stage_config = stages.get(swe_level)

    if stage_config is None:
        return None

    # enabled가 False이면 None 반환
    if not stage_config.get("enabled", True):
        return None

    return stage_config
