import cv2

def cal_proportion(img):
    """ 计算二值化图像黑白像素占比 """
    # 注意这里s已经是单通道，此时不返回通道值。
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    if ret:
        x, y = binary.shape
        bk = 0
        wt = 0
        # 遍历二值图，为0则bk+1，否则wt+1
        for i in range(x):
            for j in range(y):
                if binary[i, j] == 0:
                    bk += 1
                else:
                    wt += 1
        rate1 = wt / (x * y)
        rate2 = bk / (x * y)
        # round()第二个值为保留几位有效小数。
        print("白色占比:", round(rate1 * 100, 2), '%')
        print("黑色占比:", round(rate2 * 100, 2), '%')