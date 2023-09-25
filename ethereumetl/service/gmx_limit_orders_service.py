# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import logging
from builtins import map
import time
from ethereumetl.domain.gmx_execute_limit_orders import GmxExecuteLimitOrdersLogs
from ethereumetl.utils import chunk_string, hex_to_dec, to_normalized_address

# https://ethereum.stackexchange.com/questions/12553/understanding-logs-and-log-blooms
TOPICS_TO_LISTEN = ['0x7fb1c74d1ea6aa1c9c585e17ce8274c8ff98745e85e7459b73f87d784494f58e', # alfred_follow_event
                    '0x9a382661d6573da86db000471303be6f0b2b1bb66089b08e3c16a85d7b6e94f8', # alfred_unfollow_event
                    '0x2e1f85a64a2f22cf2f0c42584e7c919ed4abe8d53675cff0f62bf1e95a1c676f',
                    '0x137a44067c8961cd7e1d876f4754a5a3a75989b4552f1843fc69c3b372def160
]
logger = logging.getLogger(__name__)

class ExtractGmxLimitOrdersLogsJob(object):
    def extract_transfer_from_log(self, receipt_log):
        topics = receipt_log.topics
        topics_with_data = topics + split_to_words(receipt_log.data)
        if len(topics) < 1:
            return None
        if ((topics[0]).casefold()) in TOPICS_TO_LISTEN:
            filtered_logs = GmxExecuteLimitOrdersLogs()
            filtered_logs.address = to_normalized_address(receipt_log.address)
            filtered_logs.topics = receipt_log.topics
            filtered_logs.data = receipt_log.data
            filtered_logs.transaction_hash = receipt_log.transaction_hash
            filtered_logs.log_index = receipt_log.log_index
            filtered_logs.block_number = receipt_log.block_number
            filtered_logs.to_address = receipt_log.to_address
            filtered_logs.from_address = receipt_log.from_address
            filtered_logs.transaction_index = receipt_log.transaction_index
            return filtered_logs
        return None

def split_to_words(data):
    if data and len(data) > 2:
        data_without_0x = data[2:]
        words = list(chunk_string(data_without_0x, 64))
        words_with_0x = list(map(lambda word: '0x' + word, words))
        return words_with_0x
    return []


def word_to_address(param):
    if param is None:
        return None
    elif len(param) >= 40:
        return to_normalized_address('0x' + param[-40:])
    else:
        return to_normalized_address(param)
