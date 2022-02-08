"""
霍夫变换这里对预处理的要求高
在滤波方面可以选择两种方法
霍夫圆检测对噪声敏感
需要提前边缘保留滤波
opencv中找圆心得方法是梯度方向方法
param1 canny检测的双阈值中的高阈值，低阈值是它的一半
param2 最小投票数（基于圆心的投票数）
minRadius 需要检测院的最小半径
maxRadius 需要检测院的最大半径
返回值是：圆心横纵坐标和半径
"""
import cv2 as cv
import numpy as np


def hough_circle_demo(image):
    #dst = cv.pyrMeanShiftFiltering(image, 10, 90)
    dst = cv.bilateralFilter(image, 0, 100000, 6)
    cv.imshow("afterFliter", dst)
    cimg = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
    circles = cv.HoughCircles(cimg, cv.HOUGH_GRADIENT, 1, 20, param1=50, param2=20, minRadius=0, maxRadius=0)
    print(circles)
    for i in circles[0]:
        cv.circle(dst, (i[0], i[1]), i[2], (0, 0, 255), 2)
        cv.circle(dst, (i[0], i[1]), 2, (2555, 0, 0), 2)
    cv.imshow("houghCircleDetection", dst)


"""
第一个函数可以返回线段，还可以限制minlinelengh和maxlinegap
第二个函数只能返回直线
"""

def hough_possible_line(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    edge = cv.Canny(gray, 50, 150)
    lines = cv.HoughLinesP(edge, 1, np.pi / 180, 100, minLineLength=10, maxLineGap=10)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv.imshow("hough_possible_line", image)


def hough_line(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    edge = cv.Canny(gray, 50, 150)
    lines = cv.HoughLines(edge, 1, np.pi/180, 200)
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0+1000*(-b))
        y1 = int(y0+1000*a)
        x2 = int(x0-1000*(-b))
        y2 = int(y0-1000*a)
        print("lines(%s,%s),(%s,%s)" % (x1, y1, x2, y2))
        cv.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv.imshow("houghLines", image)



if __name__ == "__main__":
    src = cv.imread("test.png")
    cv.imshow("input", src)
    hough_circle_demo(src)
    hough_line(src)
    hough_possible_line(src)
    cv.waitKey(0)
    cv.destroyAllWindows()
