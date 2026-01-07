# coding=utf-8
import os


class Properties(object):
    """
    属性配置文件处理类
    用于读取和解析属性配置文件
    """

    def __init__(self, file_name):
        """
        初始化属性配置文件处理器
        
        :param file_name: 配置文件名
        """
        self.file_name = file_name
        self.properties = {}

    def __get_dict(self, str_name, dict_name, value):
        """
        递归解析属性键值对并存入字典
        
        :param str_name: 属性键名
        :param dict_name: 目标字典
        :param value: 属性值
        :return: None
        """
        if str_name.find('.') > 0:
            k = str_name.split('.')[0]
            dict_name.setdefault(k, {})
            return self.__get_dict(str_name[len(k) + 1:], dict_name[k], value)
        else:
            dict_name[str_name] = value
            return

    def get_properties(self):
        """
        获取配置文件中的所有属性
        
        :return: 属性字典
        """
        pro_file = None
        try:
            if not os.path.exists(self.file_name):
                return None
            pro_file = open(self.file_name, 'r')
            for line in pro_file.readlines():
                line = line.strip().replace('\n', '').replace('\r', '')
                if line.find("#") != -1:
                    line = line[0:line.find('#')]
                if line.find('=') > 0:
                    strs = line.split('=')
                    strs[1] = line[len(strs[0]) + 1:]
                    self.__get_dict(strs[0].strip(), self.properties, strs[1].strip())
        except Exception as e:
            raise e
        finally:
            if pro_file is not None:
                pro_file.close()
        return self.properties
