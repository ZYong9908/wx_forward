# PC微信消息转发
## 功能
- 转发pc微信消息到bark
## 主要工具
- [wcferry](https://github.com/lich0821/WeChatFerry)
- [bark](https://github.com/Finb/bark)
## 说明
1. bark加密：AES128 CBC pkcs7
2. [bark推送参数](https://bark.day.app/#/tutorial?id=请求参数)：
    ```
   {
            "title": 标题,
            "body": 推送内容,
            "badge": 角标,
            "url": 跳转链接,
            "group": 分组,
            "level": 通知类型,
            "icon": 通知图标
        }
   ```
3. 直接使用，修改`config.py`中`BarkConfig.api_id`,`BarkConfig.api_key`,`BarkConfig.aes_iv`以及`BarkConfig.params`
4. 修改消息类型无需重启：每8小时自动更新
## 运行：
```
start.bat
```