# -*- coding: UTF-8 -*-
from dataclasses import dataclass


@dataclass
class BarkConfig:
    api_serve = "https://api.day.app/"
    api_id = ""
    aes_key = b''
    aes_iv = b''
    params = {
        "title": '',
        "body": None,
        "badge": 1,
        "url": "",
        "group": "",
        "level": 'active',
        "icon": ''
    }


WxMessageType = {
    0: '[朋友圈消息]',
    3: '[图片]',
    37: '[好友请求]',
    34: '[语音]',
    47: '[表情]',
    48: '[位置]',
    50: '[通话]',
    42: '[名片]',
    43: '[视频]',
    62: '[小视频]',
    66: '[微信红包]',
}
Wx49MessageType = {
    '2000': '[转账]',
    '6': '[文件]',
    '36': '[分享]',
    '5': '[链接]',
    '19': '[合并消息]',
    '17': '[位置共享]',
    '63': '[视频号直播]',
    '51': '[视频号视频]',
    '57': '[引用消息]',
    '24': '[笔记]'
}
