import cv2
import numpy as np


# 基础库示例:
#
# from base.base import modePutText # 导入基础工具库
# # 若导入基础工具库
# if "base" in sys.modules:
#     modePutText(image, "Origin Image")



def modePutText(image, text, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, scaleMode=1, sizeMode=1):
    """
    模式化绘制字体，支持窗口自适应绘制、自定义绘制位置
    :param image: 图像
    :param text: 绘制内容
    :param fontFace: 字体格式
    :param fontScale: 字体尺寸
    :param scaleMode: 显示方式(1: (默认)自适应显示  2: 最大化显示)
    :param sizeMode: 位置(1: (默认)左上角  2:右上角 3:左下角 4:右下角)
    :return: newImage, (x, y), new_scale, baseline
    """
    best_scale = 1.0
    bgd_w = image.shape[1]
    bgd_h = image.shape[0]
    txt_rect_w = 0
    txt_rect_h = 0
    baseline = 0
    if scaleMode == 1:  # 选用自适应字体
        scale_w, scale_h = 0.15, 0.2
    elif scaleMode == 2:  # 选用最大字体
        scale_w, scale_h = 1, 1

    # 生成字体尺寸信息
    for scale in np.arange(1.0, 6.0, 0.2):
        (ret_w, ret_h), tmp_bsl = cv2.getTextSize(
            text, fontFace, scale, fontScale)
        tmp_w = ret_w + 2 * fontScale
        tmp_h = ret_h + 2 * fontScale + tmp_bsl
        if tmp_w >= bgd_w * scale_w or tmp_h >= bgd_h * scale_h:
            break

    baseline = tmp_bsl
    txt_rect_w = tmp_w
    txt_rect_h = tmp_h
    best_scale = scale

    if sizeMode == 1:  # 左上角显示
        lt_x, lt_y = 5, txt_rect_h
    elif sizeMode == 2:  # 右上角显示
        lt_x, lt_y = bgd_w - txt_rect_w - 5, txt_rect_h
    elif sizeMode == 3:  # 左下角显示
        lt_x, lt_y = 5, bgd_h - txt_rect_h + 25
    elif sizeMode == 4:  # 右下角显示
        lt_x, lt_y = bgd_w - txt_rect_w - 5, bgd_h - txt_rect_h + 25

    # lt_x, lt_y = round(bgd_w / 2 - txt_rect_w / 2), round(bgd_h / 2 - txt_rect_h / 2)
    # rb_x, rb_y = round(bgd_w / 2 + txt_rect_w / 2), round(bgd_h / 2 + txt_rect_h / 2) - baseline
    cv2.putText(image, text, (lt_x, lt_y),
                fontFace=fontFace,
                fontScale=best_scale,
                color=(0, 255, 0),
                thickness=3)
    return image, (lt_x, lt_y), best_scale, baseline