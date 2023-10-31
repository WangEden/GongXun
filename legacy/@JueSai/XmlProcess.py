from xml.etree import ElementTree
import numpy as np


def xmlReadCommand(tag: str, mode: int):
    paraDomTree = ElementTree.parse("./parameter.xml")
    messageNode = paraDomTree.find("message")
    _ = messageNode.find(tag).text
    if mode == 0:
        return _  # -> str
    elif mode == 1:
        return list(_)  # -> ['a', 'b', 'c', 'd']


def xmlReadThreshold(tag: str, color: str, rank: list):  # rank: [min:[], max:[]]
    _min, _max = [], []
    paraDomTree = ElementTree.parse("./parameter.xml")
    threshold_node = paraDomTree.find(f'threshold[@tag="{tag}"]')
    colorNode = threshold_node.find(f'color[@category="{color}"]')
    floors = colorNode.findall('./*/floor')
    ceilings = colorNode.findall('./*/ceiling')
    for i in range(3):
        _min.append(int(floors[i].text))
        _max.append(int(ceilings[i].text))
    _min = np.array(_min)
    _max = np.array(_max)
    rank.append(_min)
    rank.append(_max)


def xmlReadSize(tag: str) -> int:
    paraDomTree = ElementTree.parse("./parameter.xml")
    size_node = paraDomTree.find('size')
    item_node = size_node.find(f'item[@tag="{tag}"]')
    return int(item_node.text)


def xmlReadCenter() -> tuple:
    with open("/home/pi/color.txt", "r", encoding="utf-8-sig") as file:
        color = file.read()
        tag = int(color)
        paraDomTree = ElementTree.parse("./parameter.xml")
        center_node = paraDomTree.find('center')
        if tag == 0:
            item_node = center_node.find(f'color[@tag="black"]')
        elif tag == 1:
            item_node = center_node.find(f'color[@tag="white"]')
        xy = item_node.text.split('+')
        x = int(xy[0])
        y = int(xy[1])
    return tuple([x, y])


if __name__ == "__main__":
    print(xmlReadCenter())
    # threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    # for i, c in enumerate(["red", "green", "blue"]):
    #     xmlReadThreshold("item", c, threshold[i])
    # for i in range(3):
    #     print(threshold[i])
