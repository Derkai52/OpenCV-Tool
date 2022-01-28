import cv2
import os
import time


class GetImage():
    def __init__(self):
        pass


    def video_info(self, capture, mode=0):
        try:
            print("================< 图像信息 >===================")
            print("视频编码格式: {}".format(self.get_video_format(capture)))
            print("视频帧率: {} FPS".format(capture.get(cv2.CAP_PROP_FPS)))
            print("视频总帧数: {}".format(int(capture.get(cv2.CAP_PROP_FRAME_COUNT))))
            print("帧画面尺寸: {}x{}".format(int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))))

            if mode == 1: # 相机模式
                print("图像亮度: {}".format(capture.get(cv2.cv2.CAP_PROP_BRIGHTNESS))) # 图像亮度
                print("图像对比度: {}".format(capture.get(cv2.cv2.CAP_PROP_CONTRAST))) # 图像对比度
                print("图像饱和度: {}".format(capture.get(cv2.CAP_PROP_SATURATION))) # 图像饱和度
                print("图像色相: {}".format(capture.get(cv2.CAP_PROP_HUE))) # 图像色相
                print("图像增益: {}".format(capture.get(cv2.CAP_PROP_GAIN))) # 图像增益
                print("图像曝光: {}".format(capture.get(cv2.CAP_PROP_EXPOSURE))) # 图像曝光

        except Exception as e:
            print("图像信息加载错误: ",e)



    def display_video(self, video_path, display_mode=0, video_fps=100):
        """
        显示视频流
        :param video_path: 视频文件路径
        :param display_mode: 显示模式(0:默认 1:灰度处理)
        :param video_fps: 视频帧率(最大值) 默认值:100
        :return:
        """

        capture = cv2.VideoCapture(video_path)
        if capture.isOpened() is False:
            raise FileNotFoundError('打开视频流错误')

        # 显示图像信息
        self.video_info(capture)
        fps = 0.0
        while capture.isOpened():
            ret, frame = capture.read()
            start_time = time.time()
            if ret:
                # 显示摄像头捕获的帧
                cv2.imshow('Original frame from the video file', frame)

                # 将图像进行处理后的展示
                if display_mode == 1:
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 把摄像头捕捉到的帧转换为灰度
                    cv2.imshow('Grayscale frame', gray_frame) # 显示处理后的帧

                if (cv2.waitKey(int(1000/video_fps+0.5)) & 0xFF) == ord('q'): # 准确到整数位的帧率上限控制
                    break
                # print("FPS:{}".format(1000/(time.time()-start_time)))
                fps = (fps + (1. / (time.time() - start_time))) / 2
                print("FPS:",fps)
            else:
                break
        capture.release()
        cv2.destroyAllWindows()


    def get_video_format(self, cap):
        """ 获取视频流编码格式 """
        raw_codec_format = int(cap.get(cv2.CAP_PROP_FOURCC))
        decoded_codec_format = (chr(raw_codec_format & 0xFF), chr((raw_codec_format & 0xFF00) >> 8),
                                chr((raw_codec_format & 0xFF0000) >> 16), chr((raw_codec_format & 0xFF000000) >> 24))
        return decoded_codec_format


    def from_picture(self, picture_path):
        """ 从本地图片中获取图像:retrun:图片图像 """
        if os.path.exists(picture_path):
            image = cv2.imread(picture_path)
            return image
        raise FileNotFoundError("未能找到图像文件")


    def from_video(self, capture):
        """ 从本地视频流中获取帧图像 :return:视频流帧图像 """
        if capture.isOpened() is False:
            raise FileNotFoundError('打开视频流错误')
        ret, frame = capture.read()
        return ret, frame


    def from_thirdparty(self):
        """
        从第三方设备获取图像（例如工业相机SDK）,待开发
        :return:
        """
        pass



if __name__ == "__main__":
    a = GetImage()
    a.display_video('../resource/test.mp4', display_mode=1, video_fps=25)
