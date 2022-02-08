"""
模板匹配
这里和hsv追踪颜色不同，是通过和样本的方差，相关度，卡方的比对来找到模板所对应的位置
三种匹配方法
其中type(cv.TM_SQDIFF_NORMED)是int
假枚举类型
"""
import cv2 as cv


def template_demo(img):
    """ 模板匹配 """
    target = cv.imread("rotate_image.png") # 模板图像路径
    cv.imshow("tpl", img)
    cv.imshow("target", target)
    method = [cv.TM_SQDIFF_NORMED, cv.TM_CCORR_NORMED, cv.TM_CCOEFF_NORMED]
    th, tw = img.shape[:2]
    for md in method:
        print(md)
        result = cv.matchTemplate(target, img, md)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if md == cv.TM_SQDIFF_NORMED:
            tl = min_loc
        else:
            tl = max_loc
        br = (tl[0] + tw, tl[1] + th)
        cv.rectangle(target, tl, br, (0, 0, 255), 2)
        cv.imshow("match-" + str(md), target)

if __name__ == "__main__":
    img = cv.imread("test.png")
    template_demo(img)
    cv.waitKey(0)
    cv.destroyAllWindows()
