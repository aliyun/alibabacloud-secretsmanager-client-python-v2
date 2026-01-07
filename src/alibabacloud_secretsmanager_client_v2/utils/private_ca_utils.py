# coding=utf-8
"""
Private CA utilities for Alibaba Cloud KMS
"""

import os
from typing import Union
from datetime import date

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_CURRENT_DIR)

# 内置CA region map
REGION_ID_AND_CA_MAP = {
    "cn-hangzhou": os.path.join(_ROOT_DIR, "ca", "hz.pem"),
    "ap-southeast-1": os.path.join(_ROOT_DIR, "ca", "sgp.pem"),
    "cn-shanghai": os.path.join(_ROOT_DIR, "ca", "sh.pem"),
    "cn-beijing": os.path.join(_ROOT_DIR, "ca", "bj.pem"),
    "cn-shenzhen": os.path.join(_ROOT_DIR, "ca", "sz.pem"),
    "ap-northeast-1": os.path.join(_ROOT_DIR, "ca", "jp.pem"),
    "cn-shanghai-finance-1": os.path.join(_ROOT_DIR, "ca", "shf.pem"),
    "eu-central-1": os.path.join(_ROOT_DIR, "ca", "de.pem"),
    "cn-hongkong": os.path.join(_ROOT_DIR, "ca", "hk.pem"),
    "cn-zhangjiakou": os.path.join(_ROOT_DIR, "ca", "zjk.pem"),
    "cn-qingdao": os.path.join(_ROOT_DIR, "ca", "qd.pem"),
    "ap-southeast-3": os.path.join(_ROOT_DIR, "ca", "my.pem"),
    "cn-huhehaote": os.path.join(_ROOT_DIR, "ca", "hhht.pem"),
    "us-east-1": os.path.join(_ROOT_DIR, "ca", "usf.pem"),
    "us-west-1": os.path.join(_ROOT_DIR, "ca", "usv.pem"),
    "ap-southeast-5": os.path.join(_ROOT_DIR, "ca", "id.pem"),
    "cn-chengdu": os.path.join(_ROOT_DIR, "ca", "cd.pem"),
    "eu-west-1": os.path.join(_ROOT_DIR, "ca", "gb.pem"),
    "cn-heyuan": os.path.join(_ROOT_DIR, "ca", "hy.pem"),
    "cn-wulanchabu": os.path.join(_ROOT_DIR, "ca", "wlcb.pem"),
    "cn-guangzhou": os.path.join(_ROOT_DIR, "ca", "gz.pem"),
    "me-central-1": os.path.join(_ROOT_DIR, "ca", "mec.pem"),
    "ap-southeast-6": os.path.join(_ROOT_DIR, "ca", "php.pem"),
    "cn-beijing-finance-1": os.path.join(_ROOT_DIR, "ca", "bjf.pem"),
    "ap-southeast-7": os.path.join(_ROOT_DIR, "ca", "tha.pem"),
    "cn-heyuan-acdr-1": os.path.join(_ROOT_DIR, "ca", "hya.pem"),
    "pre-env": os.path.join(_ROOT_DIR, "ca", "pre_env.pem"),
}


def get_ca_expiration_utc_date(ca_source: Union[str, bytes, None]) -> Union[date, None]:
    """
    获取CA证书链中最后一个证书的过期时间
    
    Args:
        ca_source: CA证书源，可以是文件路径、证书内容或None
        
    Returns:
        CA证书链中最后一个证书的过期日期(仅年月日)，如果无法解析则返回None
    """
    if ca_source is None:
        return None

    try:
        if isinstance(ca_source, str) and os.path.isfile(ca_source):
            with open(ca_source, "rb") as f:
                cert_data = f.read()
        else:
            return None
        cert_chain = x509.load_pem_x509_certificates(cert_data)
        if cert_chain:
            last_cert = cert_chain[-1]
            return last_cert.not_valid_after_utc.date()
        else:
            return None
    except Exception:
        return None
