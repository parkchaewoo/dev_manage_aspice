"""YAML 유틸리티"""
import os
import yaml


def load_yaml(file_path):
    """YAML 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def dump_yaml(data, file_path):
    """YAML 파일 저장"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_yaml_string(yaml_string):
    """YAML 문자열 파싱"""
    return yaml.safe_load(yaml_string)


def dump_yaml_string(data):
    """데이터를 YAML 문자열로 변환"""
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
