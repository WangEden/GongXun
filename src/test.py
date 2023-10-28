import socket, time


def main1():
    # 1、创建一个UDP套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2. 准备接收方的地址和端口，'192.168.0.107'表示目的ip地址，8080表示目的端口号
    dest_addr = ('192.168.31.255', 9050)  # 注意这是一个元组，其中ip地址是字符串，端口号是数字

    # 3. 发送数据到指定的ip和端口
    for i in range(1):
        udp_socket.sendto("Hello,I am a UDP socket.".encode('utf-8'), dest_addr)
        time.sleep(1)

    while True:
        # 4. 等待接收对方发送的数据
        recv_data = udp_socket.recvfrom(7)  # 1024表示本次接收的最大字节数

        # 5、打印接收到的数据
        print("接收到: ", recv_data)
        # 4. 关闭套接字
    udp_socket.close()


main1()
