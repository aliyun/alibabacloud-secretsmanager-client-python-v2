# coding=utf-8


class CredentialsProperties:
    """
    凭据属性类
    用于存储和管理凭据相关配置信息
    """

    def __init__(self,
                 credentials_provider=None,
                 region_info_list=None,
                 source_properties=None):
        """
        初始化凭据属性
        
        :param credentials_provider: 凭据提供者
        :param region_info_list: 区域信息列表
        :param source_properties: 源属性
        """
        self.credentials_provider = credentials_provider
        self.region_info_list = region_info_list
        self.source_properties = source_properties