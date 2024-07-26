# -*- coding: UTF-8 -*-
import time
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import logging
import requests
from config import BarkConfig


class Bark:
    def __init__(self):
        self.url = f"{BarkConfig.api_serve}{BarkConfig.api_id}"
        self.aes_key = BarkConfig.aes_key
        self.aes_iv = BarkConfig.aes_iv
        self.LOG = logging.getLogger("Robot")
        self.last_sent_time = 0
        self.params = json.loads(json.dumps(BarkConfig.params))

    def send(self, content):
        current_time = time.time()
        if current_time - self.last_sent_time < 10:
            self.LOG.info(f"节流,10秒内不重复发送：\n{content}")
            print(f"节流,10秒内不重复发送：\n{content}")
            return
        self.params['body'] = content

        aes_data = self.crypt(self.params)
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(self.url, data=aes_data).json()
                if response.get('code') == 200:
                    self.LOG.info(f"bark 发送成功：\n{content}")
                    print(f"bark 发送成功：\n{content}")
                    self.last_sent_time = current_time
                    return
                else:
                    self.LOG.error(f"bark 发送失败 {attempt}/5，返回码：{response.get('code')}")
                    print(f"bark 发送失败 {attempt}/5，返回码：{response.get('code')}")
            except requests.RequestException as e:
                self.LOG.error(f"bark 发送失败 {attempt}/5，请检查配置：{e}")
                print(f"bark 发送失败 {attempt}/5，请检查配置：{e}")
            time.sleep(1)

    def crypt(self, content):
        json_payload = json.dumps(content).encode('utf-8')
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(json_payload) + padder.finalize()
        cipher = Cipher(algorithms.AES128(self.aes_key), modes.CBC(self.aes_iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
        return {'ciphertext': encoded_ciphertext}


if __name__ == '__main__':
    bark = Bark()
    bark.send(f'msg.sender\nmsg.content\n{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
