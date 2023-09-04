import numpy as np
from math import sqrt


class Functions:
    @staticmethod
    def GetClockAngle(v1, v2):
         # 2个向量模的乘积 ,返回夹角
        TheNorm = np.linalg.norm(v1)*np.linalg.norm(v2)
        # 叉乘
        rho = np.rad2deg(np.arcsin(np.cross(v1, v2)/TheNorm))
        # 点乘
        theta = np.rad2deg(np.arccos(np.dot(v1,v2)/TheNorm))
        if rho > 0:
            return  360-theta
        else:
            return theta

    @staticmethod
    def Disttances(a, b):
        #返回两点间距离
        x1, y1 = a
        x2, y2 = b
        Disttances = int(sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
        return Disttances

    @staticmethod
    def couputeMean(deg):
        #对数据进行处理，提取均值
        """
        :funtion :
        :param b:
        :param c:
        :return:
        """
        if True:
            # new_nums = list(set(deg)) #剔除重复元素
            mean = np.mean(deg)
            var = np.var(deg)
            # print("原始数据共", len(deg), "个\n", deg)
            '''
            for i in range(len(deg)):
                print(deg[i],'→',(deg[i] - mean)/var)
                #另一个思路，先归一化，即标准正态化，再利用3σ原则剔除异常数据，反归一化即可还原数据
            '''
            # print("中位数:",np.median(deg))
            percentile = np.percentile(deg, (25, 50, 75), interpolation='midpoint')
            # print("分位数：", percentile)
            # 以下为箱线图的五个特征值
            Q1 = percentile[0]  # 上四分位数
            Q3 = percentile[2]  # 下四分位数
            IQR = Q3 - Q1  # 四分位距
            ulim = Q3 + 2.5 * IQR  # 上限 非异常范围内的最大值
            llim = Q1 - 1.5 * IQR  # 下限 非异常范围内的最小值

            new_deg = []
            uplim = []
            for i in range(len(deg)):
                if (llim < deg[i] and deg[i] < ulim):
                    new_deg.append(deg[i])
            # print("清洗后数据共", len(new_deg), "个\n", new_deg)
        new_deg = np.mean(new_deg)

        return new_deg