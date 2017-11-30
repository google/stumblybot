#!/usr/bin/env python3

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import socket
import time
import json
from executor import Execute
import traceback

while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('999.999.999.999', 1109))   # Address of the "router" server.
    print('Connected')
    sock_file = sock.makefile('rw')
    for line in sock_file:
        cmd = json.loads(line)
        #print('Received command: %s' % json.dumps(cmd, indent=2))
        request_id = cmd['id']
        del cmd['id']
        try:
            response = Execute(
                cmd['result']['metadata'].get('intentName'),
                cmd['result']['parameters'],
                cmd['result']['resolvedQuery'], cmd)
        except Exception as e:
            traceback.print_exc()
            response = 'Sorry, something went wrong: %s' % repr(e)
        response = str(response)
        print('Sending response: %s' % response)
        sock_file.write('%s\n' % json.dumps({
            'id': request_id,
            'speech': response,
            'displayText': response,
        }))
        sock_file.flush()

    sock.close()
    time.sleep(1)
