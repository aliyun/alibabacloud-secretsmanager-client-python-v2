# coding=utf-8
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License


import abc


class CacheClientBuilder(object):
    """
    缓存客户端构建器抽象基类
    定义了构建缓存客户端的接口
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build(self):
        """
        构建对象，同时对对象实例进行初始化
        """
