lis = [
    [320, 410, 2, 1, 2],
    [340, 468, 3, 2, 6],
    [347, 467, 4, 4, 14],
    [314, 412, 5, 9, 21],
    [305, 403, 10, 21, 101],
    [412, 399, 19, 16, 151],
    [305, 218, 99, 98, 7581]
]

lis = sorted(lis, key=lambda l: l[4], reverse=True)
print(lis)