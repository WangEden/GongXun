# 2023/5/10-20:06 repaired
# 图
_graph = [
    # 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21
    [ 0, -1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], # 0
    [-1,  0,  4, -1, -1, -1, -1, -1, -1,  4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], # 1
    [ 1,  4,  0,  4,  3,  3, -1,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], # 2
    [-1, -1,  4,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,  4, -1, -1, -1, -1, -1, -1, -1, -1], # 3
    [-1, -1,  3, -1,  0, -1,  2, -1, -1,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], # 4
    [-1, -1,  3, -1, -1,  0, -1, -1,  2, -1, -1, -1, -1,  3, -1, -1, -1, -1, -1, -1, -1, -1], # 5
    [-1, -1, -1, -1,  2, -1,  0,  1, -1, -1,  1,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], # 6
    [-1, -1,  2, -1, -1, -1,  1,  0,  1, -1, -1,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], # 7
    [-1, -1, -1, -1, -1,  2, -1,  1,  0, -1, -1,  2,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1], # 8
    [-1,  4, -1, -1,  3, -1, -1, -1, -1,  0,  2, -1, -1, -1, -1, -1, -1,  3, -1,  4, -1, -1], # 9
    [-1, -1, -1, -1, -1, -1,  1, -1, -1,  2,  0,  2, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1], # 10
    [-1, -1, -1, -1, -1, -1,  2,  2,  2, -1,  2,  0,  2, -1,  2,  2,  2, -1, -1, -1, -1, -1], # 11
    [-1, -1, -1, -1, -1, -1, -1, -1,  1, -1, -1,  2,  0,  2, -1,  1, -1, -1, -1, -1, -1, -1], # 12
    [-1, -1, -1,  4, -1,  3, -1, -1, -1, -1, -1, -1,  2,  0, -1, -1, -1, -1,  3, -1, -1,  4], # 13
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1,  2, -1, -1,  0, -1,  1,  2, -1, -1, -1, -1], # 14
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  2,  1, -1, -1,  0,  1, -1,  2, -1, -1, -1], # 15
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  2, -1, -1,  1,  1,  0, -1, -1, -1,  2, -1], # 16
    [-1, -1, -1, -1, -1, -1, -1, -1, -1,  3, -1, -1, -1, -1,  2, -1, -1,  0, -1, -1,  3, -1], # 17
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3, -1,  2, -1, -1,  0, -1,  3, -1], # 18
    [-1, -1, -1, -1, -1, -1, -1, -1, -1,  4, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  4, -1], # 19
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  2,  3,  3,  4,  0,  4], # 20
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  4, -1, -1, -1, -1, -1, -1,  4,  0], # 21
]

# 点的坐标集
_points = [
  {'x': 4, 'y': -1},  # 0
  {'x': 0, 'y': 0},{'x': 4, 'y': 0},{'x': 8, 'y': 0}, # 1 2 3
  {'x': 1, 'y': 1},{'x': 7, 'y': 1}, # 4 5
  {'x': 3, 'y': 3},{'x': 4, 'y': 2},{'x': 5, 'y': 3}, # 6 7 8
  {'x': 0, 'y': 4},{'x': 2, 'y': 4},{'x': 4, 'y': 4},{'x': 6, 'y': 4},{'x': 8, 'y': 4}, # 9 10 11 12 13
  {'x': 3, 'y': 5},{'x': 5, 'y': 5},{'x': 4, 'y': 6}, # 14 15 16
  {'x': 1, 'y': 7},{'x': 7, 'y': 7}, # 17 18
  {'x': 0, 'y': 8},{'x': 4, 'y': 8},{'x': 8, 'y': 8}, # 19 20 21
]

# special points
class SpecialPoints():
  circleColorDes={7, 10, 12, 16},	# 在圈上的第一轮物料目标区
  circleColorDesDict={'ba':11, 'w':16, 'r':15, 'g':6, 'bu':10},          # 第一轮物料目标区的驻留点
  circleColorDesReside={},          # 第一轮物料目标区的驻留点
  loop1StorePos={4, 17, 18, 5},	# 第一轮的物料存储区