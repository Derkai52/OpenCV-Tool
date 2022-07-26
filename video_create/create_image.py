import os
import random
from PIL import Image, ImageOps
from tqdm import tqdm
# import torchvision.transforms as transforms

import cv2
import numpy as np
import math, sys




class ImageEnhance():

    def add_background_randomly(self, image, background, box_list=[]):
        """
        自动添加背景
        :param image: 前景图
        :param background: 背景图
        :param box_list: 点序列
        :return:
        """

        img_height, img_width = image.shape[:2]
        bg_height, bg_width = background.shape[:2]

        # resize 图像至背景大小
        # 图片至少占三分之二，但不超过五分之四
        min_size = min(bg_height, bg_width) // 3 * 2
        max_size = min(bg_height, bg_width) // 5 * 4
        new_size = random.randint(min_size, max_size)
        resize_multiple = round(new_size / max(img_height, img_width), 4)
        image = cv2.resize(image, (int(img_width * resize_multiple), int(img_height * resize_multiple)))
        img_height, img_width = image.shape[:2]

        # 将图像粘贴到背景上
        height_pos = random.randint(0, (bg_height - img_height))
        width_pos = random.randint(0, (bg_width - img_width))
        background[height_pos:(height_pos + img_height), width_pos:(width_pos + img_width)] = image
        img_height, img_width = background.shape[:2]

        # 添加背景后计算boxes
        import copy
        new_box_list = []
        box_ori_list = copy.deepcopy(box_list)  # 因为下面的操作会更新列表的值，这里用深拷贝留个备份
        for cls_type, rect in box_list:
            for coor_index in range(len(rect) // 2):
                # resize
                rect[coor_index * 2] = int(rect[coor_index * 2] * resize_multiple)  # x
                rect[coor_index * 2 + 1] = int(rect[coor_index * 2 + 1] * resize_multiple)  # y

                # paste
                rect[coor_index * 2] += width_pos  # x
                rect[coor_index * 2 + 1] += height_pos  # y

                # limite
                rect[coor_index * 2] = max(min(rect[coor_index * 2], img_width), 0)  # x
                rect[coor_index * 2 + 1] = max(min(rect[coor_index * 2 + 1], img_height), 0)  # y
            box = (cls_type, rect)
            new_box_list.append(box)
        image_with_boxes = [background, new_box_list]

        # 绘制变更情况
        self.display_diff(image, box_ori_list, new_box_list)

        return image_with_boxes


    def display_diff(self, image, box_ori_list, box_new_list):
        """ 绘制旋转变换后的差异 """
        # 显示原坐标点
        for (cls_type, box) in box_ori_list:
            for i in range(4):
                cv2.circle(image, center=(int(box[i*2]+0.5), int(box[i*2+1]+0.5)),
                           radius=5,
                           color=(0,0,200),
                           thickness=5)

        # 显示新坐标点
        for (cls_type, box) in box_new_list:
            for i in range(4):
                cv2.circle(image, center=(int(box[i * 2] + 0.5), int(box[i * 2 + 1] + 0.5)),
                           radius=5,
                           color=(0, 255, 0),
                           thickness=5)


    def rotate_image(self, image, label_box_list=[], angle=70, color=(0, 0, 0), img_scale=1.0):
        """
        按照角度进行旋转变换,背景默认用黑色填充(0,0,0)
        :param image: 输入图像
        :param label_box_list: 图像点序列
        :param angle: 旋转角度
        :param color: 背景填充颜色(默认为 black(0,0,0) )
        :param img_scale: 缩放比例(默认为1)
        :return:
        """

        # 如果角度小于0，则逆时针旋转；如果角度>0，则顺时针旋转
        height_ori, width_ori = image.shape[:2]
        x_center_ori, y_center_ori = (width_ori // 2, height_ori // 2)

        rotation_matrix = cv2.getRotationMatrix2D((x_center_ori, y_center_ori), angle, img_scale)
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])

        # 计算图像的新边界尺寸
        width_new = int((height_ori * sin) + (width_ori * cos))
        height_new = int((height_ori * cos) + (width_ori * sin))

        width_new = 640
        height_new = 480

        # 调整旋转矩阵以考虑平移
        rotation_matrix[0, 2] += (width_new / 2) - x_center_ori
        rotation_matrix[1, 2] += (height_new / 2) - y_center_ori

        # 执行实际旋转并返回图像
        # borderValue - 用于填充缺失背景的颜色，默认为黑色，可自定义
        image_new = cv2.warpAffine(image, rotation_matrix, (width_new, height_new), borderValue=color)

        # 获得每个点的新坐标
        angle = angle / 180 * math.pi
        box_rot_list = self.cal_rotate_box(label_box_list, angle, (x_center_ori, y_center_ori),
                                      (width_new // 2, height_new // 2))

        box_new_list = []
        for cls_type, box_rot in box_rot_list:
            for index in range(len(box_rot) // 2):
                box_rot[index * 2] = int(box_rot[index * 2])
                box_rot[index * 2] = max(min(box_rot[index * 2], width_new), 0)
                box_rot[index * 2 + 1] = int(box_rot[index * 2 + 1])
                box_rot[index * 2 + 1] = max(min(box_rot[index * 2 + 1], height_new), 0)
            box_new_list.append((cls_type, box_rot))

        # 显示变换差异
        self.display_diff(image_new, label_box_list, box_new_list)

        image_with_boxes = [image_new, box_new_list]
        return image_with_boxes


    def rotate_image_3d(self, img, angle_vari=30):
        """ 3维图像变换 """

        def rad(x):
            return x * np.pi / 180

        w, h = img.shape[0:2]
        fov = 42
        anglex = np.random.uniform(-angle_vari, angle_vari)
        angley = np.random.uniform(-angle_vari, angle_vari)
        anglez = np.random.uniform(-angle_vari + 10, angle_vari - 10)

        # 镜头与图像间的距离，21为半可视角，算z的距离是为了保证在此可视角度下恰好显示整幅图像
        z = np.sqrt(w ** 2 + h ** 2) / 2 / np.tan(rad(fov / 2))
        # 齐次变换矩阵
        rx = np.array([[1, 0, 0, 0],
                       [0, np.cos(rad(anglex)), -np.sin(rad(anglex)), 0],
                       [0, -np.sin(rad(anglex)), np.cos(rad(anglex)), 0, ],
                       [0, 0, 0, 1]], np.float32)

        ry = np.array([[np.cos(rad(angley)), 0, np.sin(rad(angley)), 0],
                       [0, 1, 0, 0],
                       [-np.sin(rad(angley)), 0, np.cos(rad(angley)), 0, ],
                       [0, 0, 0, 1]], np.float32)

        rz = np.array([[np.cos(rad(anglez)), np.sin(rad(anglez)), 0, 0],
                       [-np.sin(rad(anglez)), np.cos(rad(anglez)), 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]], np.float32)

        r = rx.dot(ry).dot(rz)

        # 四对点的生成
        pcenter = np.array([h / 2, w / 2, 0, 0], np.float32)

        p1 = np.array([0, 0, 0, 0], np.float32) - pcenter
        p2 = np.array([w, 0, 0, 0], np.float32) - pcenter
        p3 = np.array([0, h, 0, 0], np.float32) - pcenter
        p4 = np.array([w, h, 0, 0], np.float32) - pcenter

        dst1 = r.dot(p1)
        dst2 = r.dot(p2)
        dst3 = r.dot(p3)
        dst4 = r.dot(p4)

        list_dst = [dst1, dst2, dst3, dst4]

        org = np.array([[0, 0],
                        [w, 0],
                        [0, h],
                        [w, h]], np.float32)

        dst = np.zeros((4, 2), np.float32)

        # 投影至成像平面
        for i in range(4):
            dst[i, 0] = list_dst[i][0] * z / (z - list_dst[i][2]) + pcenter[0]
            dst[i, 1] = list_dst[i][1] * z / (z - list_dst[i][2]) + pcenter[1]

        warpR = cv2.getPerspectiveTransform(org, dst)

        result = cv2.warpPerspective(img, warpR, (h, w))
        print(h, w)
        return result


    def cal_rotate_box(self, box_list, angle, ori_center, new_center):
        """
        计算【点序列】旋转变换坐标
        :param box_list: 点序列
        :param angle: 变换角度
        :param ori_center: 源图像中心点
        :param new_center: 变换后图像中心点
        :return:
        """
        box_list_new = []
        for (cls_type, box) in box_list:
            box_new = []
            for index in range(len(box) // 2):
                box_new.extend(self.cal_rotate_coordinate(box[index * 2], box[index * 2 + 1], angle, ori_center, new_center))
            label_box = (cls_type, box_new)
            box_list_new.append(label_box)
        return box_list_new


    def cal_rotate_coordinate(self, x_ori, y_ori, angle, ori_center, new_center):
        """ 计算点旋转变换坐标 """
        x_0 = x_ori - ori_center[0]
        y_0 = ori_center[1] - y_ori
        x_new = x_0 * math.cos(angle) - y_0 * math.sin(angle) + new_center[0]
        y_new = new_center[1] - (y_0 * math.cos(angle) + x_0 * math.sin(angle))
        return (x_new, y_new)


    # def hue_change(image):
    #     if np.random.rand() < 0.8: image = transforms.ColorJitter(brightness=0.5)(image)
    #     if np.random.rand() < 0.2: image = transforms.ColorJitter(contrast=0.2)(image)
    #     if np.random.rand() < 0.2: image = transforms.ColorJitter(saturation=0.2)(image)
    #     if np.random.rand() < 0.2: image = transforms.ColorJitter(hue=0.2)(image)
    #     return image


    def perspective_tranform(self, image, perspective_rate=0.5, label_box_list=[]):
        """
        图像透视变换
        :param image:输入图像
        :param perspective_rate: 变换比率
        :param label_box_list:
        :return:
        """
        img_height, img_width = image.shape[:2]
        points_src = np.float32([[0, 0], [img_width - 1, 0], [img_width - 1, img_height - 1], [0, img_height - 1]])
        max_width = int(img_width * (1.0 + perspective_rate))
        max_height = int(img_height * (1.0 + perspective_rate))
        min_width = int(img_width * (1.0 - perspective_rate))
        min_height = int(img_height * (1.0 + perspective_rate))
        delta_width = (max_width - min_width) // 2
        delta_height = (max_height - min_height) // 2
        x0 = random.randint(0, delta_width)
        y0 = random.randint(0, delta_height)
        x1 = random.randint(delta_width + min_width, max_width)
        y1 = random.randint(0, delta_height)
        x2 = random.randint(delta_width + min_width, max_width)
        y2 = random.randint(delta_height + min_height, max_height)
        x3 = random.randint(0, delta_width)
        y3 = random.randint(delta_height + min_height, max_height)
        points_dst = np.float32([[x0, y0], [x1, y1], [x2, y2], [x3, y3]])

        # if True:
            # bbox = cv2.selectROI(image, False)
            # x0 = bbox[0]
            # y0 = bbox[1]
            #
            # x1 = bbox[0]+bbox[2]
            # y1 = bbox[1]
            #
            # x2 = bbox[0]+bbox[2]
            # y2 = bbox[1]+bbox[3]
            #
            # x3 = bbox[0]
            # y3 = bbox[1]+bbox[3]
            # cv2.circle(image, (int(x0), int(y0)), 4,(255,0,0),5)  # 在正方形内部点一点（为了给闭操作用）
            # cv2.circle(image, (int(x1), int(y1)), 4,(255,0,0),5)  # 在正方形内部点一点（为了给闭操作用）
            # cv2.circle(image, (int(x2), int(y2)), 4,(255,0,0),5)  # 在正方形内部点一点（为了给闭操作用）
            # cv2.circle(image, (int(x3), int(y3)), 4,(255,0,0),5)  # 在正方形内部点一点（为了给闭操作用）






        M = cv2.getPerspectiveTransform(points_src, points_dst)
        image_res = cv2.warpPerspective(image, M, (max_width, max_height))
        # cut
        image_new = image_res[min(y0, y1):max(y2, y3), min(x0, x3):max(x1, x2)]

        # labels
        import copy
        box_new_list = []
        box_ori_list = copy.deepcopy(label_box_list) # 因为下面的操作会更新列表的值，这里用深拷贝留个备份
        for cls_type, box in label_box_list:
            # after transformation
            for index in range(len(box) // 2):
                px = (M[0][0] * box[index * 2] + M[0][1] * box[index * 2 + 1] + M[0][2]) / (
                (M[2][0] * box[index * 2] + M[2][1] * box[index * 2 + 1] + M[2][2]))
                py = (M[1][0] * box[index * 2] + M[1][1] * box[index * 2 + 1] + M[1][2]) / (
                (M[2][0] * box[index * 2] + M[2][1] * box[index * 2 + 1] + M[2][2]))
                box[index * 2] = int(px)
                box[index * 2 + 1] = int(py)
                # cut
                box[index * 2] -= min(x0, x3)
                box[index * 2 + 1] -= min(y0, y1)
                box[index * 2] = max(min(box[index * 2], image_new.shape[1]), 0)
                box[index * 2 + 1] = max(min(box[index * 2 + 1], image_new.shape[0]), 0)
            box_new_list.append((cls_type, box))

        # 显示变换差异
        self.display_diff(image_new, box_ori_list, box_new_list)

        image_with_boxes = [image_new, box_new_list]
        return image_with_boxes





if __name__ == "__main__":
    image_test = ImageEnhance()
    img_test_path = './test.png' # 测试图像路径
    image = cv2.imread(img_test_path)

    import time

    start_time = time.time() # 初始化时间戳
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter("rotate_image_3d.avi", fourcc, 1, (372,372), True)
    while True:
        t = time.time()-start_time
        angles = (57.295*(0.785*math.sin(1.884*t)+1.305))
        # image_with_boxes = image_test.rotate_image(image, angle=angles) # 测试透视变换
        image_with_boxes = image_test.perspective_tranform(image)
        # out.write(image_with_boxes)
        cv2.imshow("test",image_with_boxes[0])
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            out.release()
            cv2.destroyAllWindows()
            break