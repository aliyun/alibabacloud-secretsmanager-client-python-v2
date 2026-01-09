# coding=utf-8
"""
凭证属性工具类
"""

from alibabacloud_secretsmanager_client_v2.model.credentials_properties import CredentialsProperties
from alibabacloud_secretsmanager_client_v2.utils import config_utils, const, variable_const, \
    credentials_provider_utils


def load_credentials_properties(file_name):
    """
    加载凭证属性配置文件
    
    :param file_name: 配置文件名
    :return: 凭证属性对象
    """
    if file_name is None or file_name == "":
        file_name = const.DEFAULT_CONFIG_NAME

    credential_properties = CredentialsProperties()
    config_dict = config_utils.Properties(file_name).get_properties()
    credential_properties.source_properties = config_dict
    if config_dict is not None and len(config_dict) > 0:
        init_secrets_regions_from_config(config_dict, credential_properties)
        init_credentials_provider_from_config(config_dict, credential_properties)
        return credential_properties
    return None


def init_secrets_regions_from_config(config_dict, credential_properties):
    """
    从配置中初始化密钥区域信息
    
    :param config_dict: 配置字典
    :param credential_properties: 凭证属性对象
    """
    credential_properties.region_info_list = credentials_provider_utils.init_kms_regions(
        config_dict, variable_const.SOURCE_TYPE_CONFIG)


def init_credentials_provider_from_config(config_dict, credential_properties):
    """
    从配置中初始化凭证信息
    
    :param config_dict: 配置字典
    :param credential_properties: 凭证属性对象
    """
    credential_properties.credentials_provider = credentials_provider_utils.init_credentials_provider_from_config(
        config_dict)
