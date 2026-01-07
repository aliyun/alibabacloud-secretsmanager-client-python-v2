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

import platform
import re
import subprocess

windows_pattern = ".*=([0-9]+)ms.*"
linux_pattern = ".*time=([0-9]+)(.[0-9]+) ms.*"


def ping_host(hostname, timeout=2):
    """
    ping指定主机并返回响应时间
    
    :param hostname: 主机名或IP地址
    :param timeout: 超时时间（秒）
    :return: 响应时间（毫秒），如果失败则返回-1
    """
    if platform.system() == "Windows":
        command = "ping " + hostname + " -n 1 -w " + str(timeout * 1000)
    else:
        command = "ping -i " + str(timeout) + " -c 1 " + hostname
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        pattern = linux_pattern
        if platform.system() == "Windows":
            pattern = windows_pattern
        output = process.stdout.read()
        matches = re.match(pattern.encode("utf-8"), output, re.DOTALL)
        if matches:
            return int(matches.group(1))
        else:
            return -1
    except Exception as e:
        # Handle any exception during ping process
        return -1
    finally:
        if 'process' in locals() and process.stdout:
            try:
                process.stdout.close()
            except:
                # Ignore exceptions during close
                pass
