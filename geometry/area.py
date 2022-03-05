import numpy as np

def polygon_area(poly):
    """
    计算多边形的面积
    原理：https://zhuanlan.zhihu.com/p/110025234
    :param poly:[[0,4],[4,4],[4,0],[0,0]] # 保证输入的poly点是按顺时针或逆时针连续传入的
    """
    edge = [(poly[1][0] - poly[0][0]) * (poly[1][1] + poly[0][1]),
            (poly[2][0] - poly[1][0]) * (poly[2][1] + poly[1][1]),
            (poly[3][0] - poly[2][0]) * (poly[3][1] + poly[2][1]),
            (poly[0][0] - poly[3][0]) * (poly[0][1] + poly[3][1])]
    return float(np.sum(edge) / 2.)

# print(polygon_area([[0,4],[4,4],[4,0],[0,0]]))