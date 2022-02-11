# OpenCV Tool

opencv_tool 通过封装常用功能块。将项目业务抽象为步骤块。

旨在加速开发者对产品原型的开发、调试、验证的过程。



## Base Package 包含以下示例：

|      示例      |          文件名           |                     说明                     |
| :------------: | :-----------------------: | :------------------------------------------: |
|    基础库      |        base.py           |              通用操作(可视化显示、进度条)                  |
| 超大图像二值化 | bbbbbig_threshold_test.py |                                              |
|    图像滤波    |       blur_test.py        |            包含了常见图像滤波操作            |
|   直方图匹配   |      compare_hist.py      |            多种直方图匹配算法比较            |
|    轮廓检测    |     countours_test.py     |            边缘检测、边缘掩膜提取            |
|  直方图均衡化  |       equal_hist.py       |             包含自适应直方图算法             |
|                |                           |                                              |
|  梯度操作算子  |     gradient_test.py      |           拉普拉斯算子、Sobel算子            |
| 直方图反向投影 | histo_reverse_project.py  |               从直方图生成图像               |
|   直方图统计   |       histogram.py        |                                              |
|    霍夫检测    |       hough_test.py       |           霍夫直线检测、霍夫圆检测           |
|                |                           |                                              |
|   图像金字塔   |   image_pyramid_test.py   |                                              |
|                |                           |                                              |
|   形态学操作   |    morphology_test.py     | 开闭运算、腐蚀、膨胀、形态学梯度、顶帽、黑帽 |
|    模板匹配    |     template_test.py      |         差值平方和匹配、标准相关匹配         |
|     二值化     |     threshold_test.py     |         全局二值化、自适应局部阈值化         |
|                |                           |                                              |
|                |                           |                                              |
|                |                           |                                              |



## Image Create Package 包含如下示例

|   示例   |     文件名      |                      说明                      |
| :------: | :-------------: | :--------------------------------------------: |
| 图像增强 | create_image.py | 随机添加背景图、仿射变换（2D）、透视变换（3D） |
|          |                 |                                                |
|          |                 |                                                |

