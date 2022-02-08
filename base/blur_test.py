"""
这里包含了常见的图像滤波操作(高斯模糊、均值滤波、边缘锐化、双边滤波)
"""
import cv2 as cv
import numpy as np


def gaussian_noise(image):
    """ 高斯噪声 """
    def clamp(pv):
        if pv > 255:
            return 255
        if pv < 0:
            return 0
        else:
            return pv

    h, w, c = image.shape
    dst = image.copy()
    for row in range(h):
        for col in range(w):
            s = np.random.normal(0, 20, 3)  #高斯随机序列 均值：0 方差：20 输出个数：3个
            b = dst[row, col, 0]  #blue
            g = dst[row, col, 1]  #green
            r = dst[row, col, 2]  #red
            dst[row, col, 0] = clamp(b + s[0])
            dst[row, col, 1] = clamp(g + s[1])
            dst[row, col, 2] = clamp(r + s[2])
    cv.imshow("noise_image", dst)
    return dst


def blur_image(image):
    """ 模糊滤波 """
    kernel_self = np.ones([5, 5], np.float32)/25
    print(kernel_self)
    dst = cv.filter2D(image, -1, kernel=kernel_self)
    cv.imshow("blur_photo", dst)
    return dst


def sharpen(image):
    """ 锐化 """
    kernel_self = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)
    print(kernel_self)
    dst = cv.filter2D(image, -1, kernel=kernel_self)
    cv.imshow("sharpen_photo", dst)
    return dst


def filter_list(image):
    """ 滤波测试列表 """

    k1 = [[-1, 0, 1],
          [-1, 0, 1],
          [-1, 0, 1]]

    k2 = [[1, 1, 1],
          [0, 0, 0],
          [-1,-1,-1]]

    sobel_x = [[-1, 0, 1],
               [-2, 0, 2],
               [-1, 0, 1]]

    sobel_y = [[1, 2, 1],
               [0, 0, 0],
               [-1, 2,-1]]

    k5 = [[-1,-1,-1],
          [-1, 8,-1],
          [-1,-1,-1]]

    # 拉普拉斯算子
    lap = [[0, 1, 0],
          [1,-4, 1],
          [0, 1, 0]]

    k7 = [[-1,-3,-4,-3,-1],
          [-3, 0, 6, 0,-3],
          [-4, 6,20, 6,-4],
          [-3, 0, 6, 0,-3],
          [-1,-3,-4,-3,-1]]

    robert_x = [[1,0],
          [0,-1]]

    robert_y = [[0,1],
          [-1,0]]

    kernel_list = [k1, k2, sobel_x, sobel_y, k5, lap, k7, robert_x, robert_y]
    for k in kernel_list:
        kernel_self = np.array(k, np.float32)
        dst = cv.filter2D(image, -1, kernel=kernel_self)
        cv.imshow("filter_k"+str(kernel_list.index(k)+1), dst)
    return dst


def bilateral(image):
    """ 双边滤波 """
    dst = cv.bilateralFilter(image, 0, 100, 10)
    cv.imshow("bilateral_photo", dst)
    return dst


if __name__ == "__main__":
    src = cv.imread("../resource/test.png")
    # cv.namedWindow("input_image", cv.WINDOW_AUTOSIZE)
    cv.imshow("input_image", src)
    # blur_image(src) # 均值滤波
    # sharpen(src) # 边缘锐化
    # bilateral(src) # 双边滤波
    t1 = cv.getTickCount()
    # gaussian_noise(src) # 高斯噪声
    sharpen(src) # 边缘锐化
    filter_list(src)
    t2 = cv.getTickCount()
    time = (t2-t1)/cv.getTickFrequency()*1000
    print("time consume:%s" % time)
    # dst = cv.GaussianBlur(src, (5, 5), 0) # 高斯模糊
    # cv.imshow("gaussian_blur", dst)
    cv.waitKey(0)
    cv.destroyAllWindows()