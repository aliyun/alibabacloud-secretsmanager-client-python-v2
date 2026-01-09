# coding=utf-8
import json

from alibabacloud_credentials import provider

from alibabacloud_secretsmanager_client_v2.model.region_info import RegionInfo
from alibabacloud_secretsmanager_client_v2.utils import variable_const


def init_credentials_provider(params_map, source_type):
    """
    根据参数映射初始化凭证提供者
    
    :param params_map: 参数映射字典
    :return: AlibabaCloudCredentialsProvider对象
    """
    credentials_type = params_map.get(variable_const.VARIABLE_CREDENTIALS_TYPE_KEY)
    if credentials_type:
        if credentials_type == "ak":
            access_key_id = params_map.get(variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY)
            access_secret = params_map.get(variable_const.VARIABLE_CREDENTIALS_ACCESS_SECRET_KEY)
            if not access_key_id:
                raise ValueError(
                    (variable_const.CHECK_PARAM_ERROR_MESSAGE % (
                        source_type, variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY)))
            if not access_secret:
                raise ValueError(
                    (variable_const.CHECK_PARAM_ERROR_MESSAGE % (
                        source_type, variable_const.VARIABLE_CREDENTIALS_ACCESS_SECRET_KEY)))
            return provider.StaticAKCredentialsProvider(access_key_id=access_key_id,
                                                        access_key_secret=access_secret)
        elif credentials_type == "ecs_ram_role":
            role_name = params_map.get(variable_const.VARIABLE_CREDENTIALS_ROLE_NAME_KEY)
            if not role_name:
                raise ValueError(
                    (variable_const.CHECK_PARAM_ERROR_MESSAGE % (
                        source_type, variable_const.VARIABLE_CREDENTIALS_ROLE_NAME_KEY)))
            return provider.EcsRamRoleCredentialsProvider(role_name=role_name)
        elif credentials_type == "oidc_role_arn":
            role_session_expiration = params_map.get(
                variable_const.VARIABLE_CREDENTIALS_OIDC_DURATION_SECONDS_KEY)
            role_session_name = params_map.get(variable_const.VARIABLE_CREDENTIALS_OIDC_ROLE_SESSION_NAME_KEY)
            role_arn = params_map.get(variable_const.VARIABLE_CREDENTIALS_OIDC_ROLE_ARN_KEY)
            oidc_provider_arn = params_map.get(variable_const.VARIABLE_CREDENTIALS_OIDC_PROVIDER_ARN_KEY)
            oidc_token_file_path = params_map.get(variable_const.VARIABLE_CREDENTIALS_OIDC_TOKEN_FILE_PATH_KEY)
            region_id = params_map.get(variable_const.VARIABLE_CREDENTIALS_OIDC_STS_REGION_ID_KEY)
            policy = params_map.get(variable_const.VARIABLE_CREDENTIALS_OIDC_POLICY_KEY)
            sts_endpoint = params_map.get(variable_const.VARIABLE_CREDENTIALS_OIDC_STS_ENDPOINT_KEY)
            return provider.OIDCRoleArnCredentialsProvider(role_arn=role_arn,
                                                           oidc_provider_arn=oidc_provider_arn,
                                                           oidc_token_file_path=oidc_token_file_path,
                                                           role_session_name=role_session_name,
                                                           duration_seconds=role_session_expiration,
                                                           policy=policy,
                                                           sts_region_id=region_id,
                                                           sts_endpoint=sts_endpoint)
        else:
            raise ValueError(("%s credentials type[%s] is illegal" % (source_type, credentials_type)))


def init_credentials_provider_from_env(env_map):
    """
    从环境变量初始化凭证信息
    
    :param env_map: 环境变量Map
    :return: AlibabaCloudCredentialsProvider对象
    """
    return init_credentials_provider(env_map, variable_const.SOURCE_TYPE_ENV)


def init_credentials_provider_from_config(properties):
    """
    从配置文件初始化凭证信息
    
    :param properties: 配置属性
    :return: AlibabaCloudCredentialsProvider对象
    """
    map = {}
    for key, value in properties.items():
        map[key] = value
    return init_credentials_provider(map, variable_const.SOURCE_TYPE_CONFIG)


def init_kms_regions(env_dict, source_type):
    """
    从配置属性或环境变量初始化KMS地域信息列表
    
    :param env_dict: 环境变量字典
    :param source_type: 配置属性来源("config" 或 "env")
    :return: 地域信息列表
    """
    region_info_list = []
    region_json = env_dict.get(variable_const.VARIABLE_CACHE_CLIENT_REGION_ID_KEY)
    if region_json:
        try:
            region_dict_list = json.loads(region_json)
            for region_dict in region_dict_list:
                region_info_list.append(RegionInfo(
                    region_dict.get(variable_const.VARIABLE_REGION_REGION_ID_NAME_KEY),
                    region_dict.get(variable_const.VARIABLE_REGION_VPC_NAME_KEY, False),
                    region_dict.get(variable_const.VARIABLE_REGION_ENDPOINT_NAME_KEY),
                    region_dict.get(variable_const.VARIABLE_REGION_CA_FILE_PATH_NAME_KEY)))
        except Exception:
            raise ValueError(
                ("%s credentials param[%s] is illegal" % (source_type,
                                                          variable_const.VARIABLE_CACHE_CLIENT_REGION_ID_KEY)))

    return region_info_list
