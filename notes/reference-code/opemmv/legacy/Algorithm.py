# 2023/5/10-20:06 repaired
from Data import _graph, _points, SpecialPoints

def dijkstra(start, end):
    if start == end:
        return []

    path = [end]  # 记录路径
    node_num = len(_graph)  # 获取节点数量
    dis = [0x3f3f3f for n in range(node_num)]  # 初始化距离数组
    dis[start] = 0  # 将起点到起点的距离初始化为零
    pre = [n for n in range(node_num)]  # 记录每个点距离最近的上一个节点编号
    visited = [False for n in range(node_num)]  # 记录没有被访问过的节点
    visited_num = 0
    current_node = start  # 将当前需要判别的节点初始化为起点

    # 忽略被删除的节点
    for i in range(node_num):
        if _graph[i][i] == -1:
            visited[i] = True
            visited_num += 1

    while visited_num < node_num:
        min_dis = 0x3f3f3f
        # 在没被访问过的节点中重新选择最近的那个作为新起点
        for i in range(node_num):
            if visited[i] == True or min_dis <= dis[i]:
                continue
            min_dis = dis[i]
            current_node = i

        # 贪心策略
        for i in range(node_num):
            if visited[i] == True or _graph[current_node][i] == -1:
                continue
            if _graph[current_node][i] + dis[current_node] < dis[i]:
                dis[i] = _graph[current_node][i] + dis[current_node]
                pre[i] = current_node

        visited[current_node] = True
        visited_num += 1
    
    # 写入最短路径
    n = end    
    while pre[n] != start:
        path.append(pre[n])
        n = pre[n]
    path.append(start)
    path.reverse()
    return path

def ban_point(pointIndex: int):
    for i in range(22):
        _graph[pointIndex][i] = -1
        _graph[i][pointIndex] = -1


def detectCirclePath(node1, node2): # --> True: a circle path
    if node1 == 0 or node2 == 0:
        return False
    else:
        if _graph[node1][node2] // 2 == 1:
            return True
        else:
            return False
        

def detectSpecialPoint(pointIndex):
    if pointIndex in SpecialPoints.loop1StorePos[0]: # 返回值是元组，要取出来先
        return 'l1sp'
