# -*- coding: UTF-8 -*-
import signal
from robot import Robot
from wcferry import Wcf


def main():
    wcf = Wcf(debug=False)

    def handler(sig, frame):
        wcf.cleanup()  # 退出前清理环境
        exit(0)
    signal.signal(signal.SIGINT, handler)
    robot = Robot(wcf)
    # 接收消息
    robot.enableReceivingMsg()
    # 每12小时更新联系人
    robot.onEveryHours(12, robot.getAllContacts)
    # 每8小时更新消息类型
    robot.onEveryHours(8, robot.get_message_type)
    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()


if __name__ == "__main__":
    main()
