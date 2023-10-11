import serial, struct
from xml.etree import ElementTree as ET
import numpy as np


def xmlReadCommand(tag, mode):
    paraDomTree = ET.parse("./parameter.xml")
    messageNode = paraDomTree.find("message")
    _ = messageNode.find(tag).text
    if mode == 0:
        return _ # -> str
    elif mode == 1:
        return list(_) # -> ['a', 'b', 'c', 'd']
    

def xmlReadThreshold(tag, color, rank): # rank: [min:[], max:[]]
    _min, _max = [], []
    paraDomTree = ET.parse("./parameter.xml")
    threshold_node = paraDomTree.find(f'threshold[@tag="{tag}"]')
    colorNode = threshold_node.find(f'color[@category="{color}"]')
    floors = colorNode.findall('./*/floor')
    ceilings = colorNode.findall('./*/ceiling')
    for i in range(3):
        _min.append(int(floors[i].text))
        _max.append(int(ceilings[i].text))
    _min = np.array(_min)
    _max = np.array(_max)
    rank[0] = _min
    rank[1] = _max


#定义数据包，格式为2个帧头+4个字符数据+2个半整型数据+帧尾（11byte）
#4个字符传输命令名，2个int传输xy方向的偏差
def send_data(uart, cmd:list, i, f):
    a, b, c, d = cmd
    data = struct.pack("<bbbbbbhhb", # 四个字符作为命令, 两个浮点作为xy偏差
                        0x2C,      # 帧头1      ','
                        0x3C,      # 帧头2      '<'
                        ord(str(a)), # 字符1
                        ord(str(b)), # 字符2
                        ord(str(c)), # 字符3
                        ord(str(d)), # 字符4
                        int(i), # 半整型数据1
                        int(f), # 半整型数据2
                        0x3E)      # 帧尾       '>'
    uart.write(data)

