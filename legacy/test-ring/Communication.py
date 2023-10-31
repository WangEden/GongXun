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
    rank.append(_min)
    rank.append(_max)


if __name__ == "__main__":
    color = ['red', 'green', 'blue']
    threshold = [[], [], []] # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(color): xmlReadThreshold("item", c, threshold[i])
