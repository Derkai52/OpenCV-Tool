import cv2

import numpy as np

import os

import shutil

import time

import math

VIDEO_PATH = '../resource/test.mp4'  # 视频地址
EXTRACT_FOLDER = 'video'  # 存放帧图片的位置
EXTRACT_FREQUENCY = 1  # 帧提取频率

# 基础库示例:
#
# from base.base import modePutText # 导入基础工具库
# # 若导入基础工具库
# if "base" in sys.modules:
#     modePutText(image, "Origin Image")

class BaseTool():
    def __init__(self):
        pass


    def modePutText(self, image, text, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, scaleMode=1, sizeMode=1):
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


    def progress_bar(self, current, total, bar_len=35):
        """
        显示程序段执行进度条
        :param current: 当前执行数
        :param total: 总执行数
        :param bar_len: 进度条显示长度(默认为35字符格长)
        """
        completed_rate = int((current / total)*bar_len) # 已完成百分比量

        a = completed_rate * "▋" # 已完成进度条
        b = "." * int(bar_len - completed_rate) # 剩余进度条
        c = (current / total) * 100 # 当前进度点
        # print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c, a, b, dur), end="")
        print("\r{:^3.0f}%[{}->{}][{}/{}]".format(c, a, b, current, total), end="")


    def extract_frames(self, video_path, dst_folder, rate=[], index=1):
        """
        通过视频流生成数据集
        :param video_path: 视频流路径
        :param dst_folder: 数据集存放路径
        :param rate: 采集范围 eq:[13, 34] 即将采集范围限定到13%~34%进度区间的数据
        :param index: 命名计数起始下标

        参数rate 默认认为数据采集范围为所有帧;
        你可以使用 rate=[13] 来表示将范围限定在0%~13%之间;
        或者使用 rate=[13,27] 来表示将范围限定在13%~27%之间;
        """

        # 初始化视频流
        video = cv2.VideoCapture()
        if not video.open(video_path):
            print("can not open the video")
            exit(1)
        video_total_frame = video.get(cv2.CAP_PROP_FRAME_COUNT) # 获取视频总帧数

        # 获得采集范围
        if len(rate) == 0: # 默认数据采集范围为所有帧
            min_rate = 0
            max_rate = video_total_frame
        elif len(rate) == 1:
            min_rate = 0
            max_rate = rate[0]

        elif len(rate) == 2:
            if rate[0] < 0:
                raise ValueError("起始采集点需要大于0！")
            elif rate[0] >= rate[1]:
                raise ValueError("结束采集点需要比起始采集点大！")
            min_rate = rate[0]
            max_rate = rate[1]


        min_frame = math.ceil(min_rate/100*video_total_frame)
        max_frame = math.ceil(max_rate/100*video_total_frame)
        task_frame = max_frame-min_frame # 实际任务量
        count = 1 # 初始化计数器

        # 采集
        while True:
            ret, frame = video.read()
            if ret:
                if min_frame <= count and count <= max_frame: # 当处于帧采集范围内
                    if count % EXTRACT_FREQUENCY == 0:
                        save_path = "{}/{:>03d}.jpg".format(dst_folder, index) # 格式化生成数据文件名
                        cv2.imwrite(save_path, frame)
                        self.progress_bar(index, task_frame) # 终端显示进度条
                        index += 1
                count += 1

            else:break # 读完或读空则退出
        video.release()
        # 打印出所提取帧的总数
        print("\nTotally save {:d} pics".format(index - 1))


    def video2video(self, frame_ori=0, save_path="test.avi", save_format='XVID', save_fps=20, save_size=(1920,1080)):
        """ 视频的转换 """
        cap = cv2.VideoCapture(frame_ori)

        fourcc = cv2.VideoWriter_fourcc(*save_format)

        out = cv2.VideoWriter(save_path, fourcc, save_fps, save_size, True)

        while (cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:

                cv2.imshow('frame', frame)
                out.write(frame)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()


    def main(self):
        # 递归删除之前存放帧图片的文件夹，并新建一个
        try:
            shutil.rmtree(EXTRACT_FOLDER)
        except OSError:
            pass
        if not os.path.exists(EXTRACT_FOLDER):
            os.mkdir(EXTRACT_FOLDER)
        # 抽取帧图片，并保存到指定路径
        self.extract_frames(VIDEO_PATH, EXTRACT_FOLDER, [5])


if __name__ == '__main__':
    a = BaseTool()
    a.main()
