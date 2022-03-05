# 相机的内外参，失真系数，校准等。
# 拿到一组3D点对象，2D图像点，可以使用相应的方法进行校准；
import numpy as np
import cv2
import glob
import json


# 将相机矩阵、失真系数写入文件
def write2Npz(ret, mtx, dist, rvecs, tvecs):
    print("ret", ret)
    print("mtx", mtx)
    print("dist", dist)
    print("rvecs", rvecs)
    print("tvecs", tvecs)
    np.savez('calibration.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)


# 校准的终止准则
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 准备3D的对象点，如(0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

# 存储3D对象点、2D图像点
objpoints = []  # 现实世界3D点
imgpoints = []  # 图像平面2D点

images = glob.glob('chessboard_image/*.jpg')

for fname in images:
    origin = cv2.imread(fname)
    img = origin.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 查找网格模式，寻找角点
    ret, corners = cv2.findChessboardCorners(gray, (7, 6), None)

    # 如果找到了，添加对象点，以及经过细化后的图像点
    if ret == True:
        objpoints.append(objp)

        # 提高角点的准确度
        cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)

        # 绘制模式角点和显示
        cv2.drawChessboardCorners(img, (7, 6), corners, ret)
        cv2.imshow('origin VS pattern', np.hstack([origin, img]))
        cv2.waitKey(0)

cv2.destroyAllWindows()

# 有了目标点和图像点可以开始校准了。为此使用函数 cv2.calibrateCamera()。它返回相机矩阵、失真系数、旋转和平移向量等。
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
write2Npz(ret, mtx, dist, rvecs, tvecs)

# cv2.getOptimalNewCameraMatrix() 获取基于自由缩放参数细化相机矩阵。如果缩放参数 alpha=0，则返回具有最少不需要像素的未失真图像。所以它甚至可能会去除图像角落的一些像素。
# 如果 alpha=1，所有像素都会保留一些额外的黑色图像。它还返回一个图像 ROI，可用于裁剪结果。
img = cv2.imread('qpimgs/left12.jpg')
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# 法一：
# 不失真
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

# 剪裁ROI图像
x, y, w, h = roi
dst = dst[y:y + h, x:x + w]
cv2.imwrite('qpimgs/calibresult1.jpg', dst)
cv2.imshow("origin", img)
cv2.imshow("caliresult", dst)

# 法二：
# 首先找到从失真图像到未失真图像的映射函数。然后使用重映射功能。
# 不失真
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

# 剪裁ROI
x, y, w, h = roi
dst = dst[y:y + h, x:x + w]
cv2.imwrite('qpimgs/calibresult2.jpg', dst)
cv2.imshow("caliresult2", dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 校准后可以看到棋盘的所有边缘都是直的。可以使用 Numpy 中的写入函数（np.savez、np.savetxt 等）存储相机矩阵和失真系数以备将来使用。

# 重投影误差
# 重新投影误差可以很好地估计找到的参数的精确程度，应该尽可能接近于零。
# 给定内在、扭曲、旋转和平移矩阵，首先使用 cv2.projectPoints() 将对象点转换为图像点。然后计算变换得到的和角点寻找算法之间的绝对范数。
# 为了找到平均误差，计算了为所有校准图像计算的误差的算术平均值。
mean_error = 0
tot_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    tot_error += error

print("total error: ", mean_error / len(objpoints))
