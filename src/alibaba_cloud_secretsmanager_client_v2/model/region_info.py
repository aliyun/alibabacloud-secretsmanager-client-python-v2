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


class RegionInfo:

    def __init__(self, region_id, vpc=False, endpoint=None, ca_file_path=None):
        """"""
        self.region_id = region_id
        self.vpc = vpc
        self.endpoint = endpoint
        self.ca_file_path = ca_file_path

    def __str__(self):
        return 'region_id:%s vpc:%s endpoint:%s ca_file_path:%s' % (self.region_id, str(self.vpc), self.endpoint,
                                                                    self.ca_file_path)

    def __hash__(self):
        if self.endpoint is None:
            return hash((self.region_id, self.vpc))
        return hash(self.endpoint)

    def __eq__(self, other):
        """
        比较两个RegionInfo对象是否相等
        如果endpoint相同则返回True
        否则比较vpc和region_id是否相等
        """
        if self is other:
            return True
        if other is None or type(self) != type(other):
            return False
        that = other
        if self.endpoint is not None and that.endpoint is not None:
            if self.endpoint == that.endpoint:
                return True
        return self.vpc == that.vpc and self.region_id == that.region_id
