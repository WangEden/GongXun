import socket, time


def main():
    # 1.创建一个udp套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2.绑定本地的相关信息，如果一个网络程序不绑定，则系统会随机分配
    # 30000  表示本地的端口 ip一般不用写
    local_addr = ("", 9050)
    udp_socket.bind(local_addr)

    # 3. 等待接收对方发送的数据
    recv_data = udp_socket.recvfrom(1024)
    # 1024表示本次接收的最大字节数

    # 6. 显示对方发送的数据
    # 接收到的数据recv_data是一个元组
    # 第1个元素是对方发送的数据
    # 第2个元素是对方的ip和端口
    print(recv_data[0].decode('gbk'))
    print(recv_data[1])

    # 3.关闭套接字
    udp_socket.close()


if __name__ == "__main__":
    main()
