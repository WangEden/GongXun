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


def xmlReadCenter(tag: str) -> tuple:
    paraDomTree = ElementTree.parse("./parameter.xml")
    center_node = paraDomTree.find('size')


if __name__ == "__main__":
    threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("item", c, threshold[i])
    for i in range(3):
        print(threshold[i])
