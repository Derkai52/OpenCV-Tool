"""
直方图的反向投影
主要还是利用hsv空间追踪颜色
和人手动去设定颜色其实差不多
1.把样本和目标图片转换到hsv色彩空间
2.做样本在hsv空间的直方图
3.把直方图归一化
4.直方图反向投影获得原图中的目标
"""
import cv2 as cv
from matplotlib import pyplot as plt


def back_projection_demo():
    """ 直方图的反向投影 """
    sample = cv.imread("test.png")
    target = cv.imread("rotate_image.png")
    roi_hsv = cv.cvtColor(sample, cv.COLOR_BGR2HSV)
    target_hsv = cv.cvtColor(target, cv.COLOR_BGR2HSV)
    #show images
    cv.imshow("sample", sample)
    cv.imshow("target", target)

    roiHist = cv.calcHist([roi_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])  #可以调的就是bins的个数
    cv.normalize(roiHist, roiHist, 0, 255, cv.NORM_MINMAX)  #归一化
    dst = cv.calcBackProject([target_hsv], [0, 1], roiHist, [0, 180, 0, 256], 1)
    cv.imshow("back_projection", dst)


def hist2d_demo(image):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    hist = cv.calcHist([hsv], [0, 1], None, [36, 64], [0, 180, 0, 256])
    #cv.imshow("hist_2d", hist)
    plt.imshow(hist, interpolation="nearest")
    plt.title("2D histogram")
    plt.show()

if __name__ == "__main__":
    src = cv.imread("test.png")
    #cv.namedWindow("input_image", cv.WINDOW_AUTOSIZE)
    cv.imshow("input_image", src)
    back_projection_demo()
    hist2d_demo(src)
    cv.waitKey(0)
    cv.destroyAllWindows()