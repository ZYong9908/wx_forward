# -*- coding: utf-8 -*-
from queue import Empty
from threading import Thread
from wcferry import Wcf, WxMsg
from job_mgmt import Job
from send_bark import Bark
import time
import xml.etree.ElementTree as ET
import logging
import re
import importlib
import config

__version__ = "39.3.3.0"


class Robot(Job):
    """个性化自己的机器人"""

    def __init__(self, wcf: Wcf) -> None:
        super().__init__()
        self.wcf = wcf
        self.bark = Bark()
        self.wxid = self.wcf.get_self_wxid()
        self.LOG = logging.getLogger("Robot")
        self.last_get_all_contacts_time = 0
        self.silent_notice, self.allContacts = [], {}
        self.getAllContacts()
        self.msg_type_dict = {}
        self.type_49_dict = {}
        self.get_message_type()

    @staticmethod
    def value_check(args: dict) -> bool:
        if args:
            return all(value is not None for key, value in args.items() if key != 'proxy')
        return False

    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    self.processMsg(msg)
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    print(f"Receiving message error: {e}")
                    self.LOG.error(f"Receiving message error: {e}")

        self.wcf.enable_receiving_msg()
        Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()

    def getAllContacts(self) -> tuple:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        current_time = time.time()
        if current_time - self.last_get_all_contacts_time < 60:
            return self.allContacts, self.silent_notice
        self.last_get_all_contacts_time = current_time
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName, Remark, ChatRoomNotify FROM Contact;")
        self.LOG.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - 获取联系人: {len(contacts)}")
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - 获取联系人: {len(contacts)}")
        id_name = {}
        notify_0 = []
        for contact in contacts:
            if contact["ChatRoomNotify"] == 0 and contact["UserName"].endswith("@chatroom"):
                notify_0.append(contact["UserName"])
            id_name[contact["UserName"]] = contact["Remark"] if contact["Remark"] else contact["NickName"]
        self.allContacts, self.silent_notice = id_name, notify_0

    def get_message_type(self):
        importlib.reload(config)
        self.msg_type_dict = config.WxMessageType
        self.type_49_dict = config.Wx49MessageType
        print('更新消息类型')
        self.LOG.info('更新消息类型')

    def get_msg_sender(self, sender):
        """
        获取消息发送者的名称。如果allContacts中获取不到，则更新allContacts并再次尝试获取。
        参数：
            sender (str): 消息发送者的标识。
        返回：
            str: 消息发送者的名称或标识。
        """
        msg_sender = self.allContacts.get(sender)
        if not msg_sender:
            self.getAllContacts()
            msg_sender = self.allContacts.get(sender, sender)
        return msg_sender

    def is_at(self, msg) -> bool:
        """是否被 @：群消息，在 @ 名单里"""
        if not msg.from_group():
            return False  # 只有群消息才能 @
        if not re.findall(f"<atuserlist>[\s|\S]*({self.wxid})[\s|\S]*</atuserlist>", msg.xml):
            return False  # 不在 @ 清单里
        return True

    def processMsg(self, msg: WxMsg) -> None:
        if msg.from_self() or msg.sender.startswith("gh_") or (msg.from_group() and msg.roomid in self.silent_notice and not self.is_at(msg)):
            return
        content = self.extract_content(msg)
        group_msg = f'群聊：{self.get_msg_sender(msg.roomid)}\n' if msg.from_group() else ''
        msg_sender = f'{self.get_msg_sender(msg.sender)}\n' if msg.sender else ''
        send_msg = f'{content}\n{group_msg}{msg_sender}{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}'
        self.bark.send(send_msg)

    def extract_content(self, msg: WxMsg) -> str:
        if msg.type == 0x01:  # 文本消息
            return msg.content
        if msg.type == 10000:
            return f'[{msg.content}]'
        if msg.type == 49:
            return self.extract_type_49_content(msg.content)
        content = self.msg_type_dict.get(msg.type, '其他消息类型')
        if content == '其他消息类型':
            self.LOG.warning(f'未识别的消息类型: {msg.type}')
            self.LOG.warning(f'未识别的消息类型: {msg.type}: {msg.content}')
        return content

    def extract_type_49_content(self, content: str) -> str:
        try:
            root = ET.fromstring(content)
            msg_type = root.find('.//appmsg/type').text
            if msg_type == '57':
                return root.find(".//appmsg/title").text
            elif msg_type in self.type_49_dict:
                return self.type_49_dict[msg_type]
            else:
                self.LOG.warning(f'未识别的49: {content}')
                self.LOG.warning(f'未识别的49, type: {msg_type}')
                return '[其他] type: 49'
        except ET.ParseError as e:
            self.LOG.error(f'XML解析错误: {e}')
            return '[解析错误]'

    def keepRunningAndBlockProcess(self) -> None:
        """
        保持机器人运行，不让进程退出
        """
        while True:
            self.runPendingJobs()
            time.sleep(1)
