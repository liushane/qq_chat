"""
exercise
[1] 有人进入聊天室需要输入姓名，姓名不能重复
【2】 有人进入聊天室时，其他人会收到通知：xxx 进入了聊天室
【3】 一个人发消息，其他人会收到：xxx ： xxxxxxxxxxx
【4】 有人退出聊天室，则其他人也会收到通知:xxx退出了聊天室
【5】 扩展功能：服务器可以向所有用户发送公告:管理员消息： xxxxxxxxx
转发模型：ｃｌｉｅｎｔ　－－＞　ｓｅｒｖｅｒ
网络模型：ＵＤＰ通信
保存用户信息：[(,),(,)] {:}
收发关系处理：采用多进程分别进行收发操作
结构设计：　函数　or 类
协议：
    如果允许进入聊天室发送＂ＯＫ＂到ｃｌｉｅｎｔ
    请求类别：
    Ｌ　－－　进入聊天室
    Ｃ　－－　聊天信息
    Ｑ　－－　退出聊天
用户存储结构：｛name:addr｝
客户端：创建新的进程
    一个进程发送消息
    一个进程接受消息
服务端：
    接收请求
"""
from socket import *
import os,sys

#服务器地址
ADDR = ("0.0.0.0",8288)
user = {}
def do_login(s,name,addr):
    if name in user or "管理员" in name:
        s.sendto("已存在".encode(),addr)
        return
    s.sendto(b"OK",addr)

    #通知其他人
    msg = "欢迎%s来到王者荣耀"%name
    for i in user:
        s.sendto(msg.encode(),user[i])
    #将用户加入
    user[name] = addr

#聊天
def do_chat(s,name,text):
    msg = "%s : %s"%(name,text)
    for i in user:
        if i != name:
            s.sendto(msg.encode(),user[i])

#客户端退出
def do_quit(s,name):
    msg = "%s退出了聊天室"%name
    for i in user:
        if i != name:
            s.sendto(msg.encode(),user[i])
        else:
            s.sendto(b"EXIT",user[i])

#接收客户端请求
def do_request(s):
    while True:
        data,addr = s.recvfrom(1024)
        msg = data.decode().split(" ")
        if msg[0] == "L":
            do_login(s,msg[1],addr)
            print("\n%s加入战场"%(msg[1]))
        elif msg[0] == "C":
            text = " ".join(msg[2:])
            do_chat(s,msg[1],text)
            print("\n%s : %s"%(msg[1],text))
        elif msg[0] == "Q":
            if msg[1] not in user:
                s.sendto(b"EXIT",addr)
                continue
            do_quit(s,msg[1])

#创建网络连接
def main():
    #套接字
    s = socket(AF_INET,SOCK_DGRAM)
    s.bind(ADDR)

    pid = os.fork()
    if pid < 0:
        return
    elif pid == 0:
        while True:
            msg = input("管理员消息：")
            msg = "C 管理员消息 " + msg
    else:
        do_request(s)

    #请求处理
    do_request(s) #处理客户请求

if __name__ == "__main__":
    main()
