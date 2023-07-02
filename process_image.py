import cv2 as cv
import os, shutil
import sys
import numpy as np
import dlib
import insightface
from insightface.app import FaceAnalysis

# 加强img的亮部
def dodge(img, mask):
    return cv.divide(img, 255 - mask, scale = 256)

# 素描化img
def pencil_sketch(img_path):
    img = cv.imread(img_path)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    neg = 255 - gray
    blur = cv.GaussianBlur(neg, ksize = (21, 21), sigmaX = 0, sigmaY = 0)
    sketch = dodge(gray, blur)
    return sketch

def mass_pencil_sketch(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok = True)
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            cartoon_image = pencil_sketch(filepath)
            output_filepath = os.path.join(output_dir, filename)
            cv.imwrite(output_filepath, cartoon_image)

# 卡通化img
def cartoonify(img_path):
    img = cv.imread(img_path)
    col_img = cv.bilateralFilter(img, 5, 255, 255)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 3)
    edges = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 5, 5)
    cartoon = cv.bitwise_and(col_img, col_img, mask = edges)
    return cartoon

def mass_cartoonify(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok = True)
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            cartoon_image = cartoonify(filepath)
            output_filepath = os.path.join(output_dir, filename)
            cv.imwrite(output_filepath, cartoon_image)



# 从txt中读取点对
def read_from_txt(txt_path):
    points = []
    with open(txt_path) as file:
        for line in file:
            x, y = line.split()
            points.append((int(x), int(y)))
    return points

# 检查一个点是否在rect内部
def in_rect(rect, point):
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] > rect[0] + rect[2]:
        return False
    elif point[1] > rect[1] + rect[3]:
        return False
    return True

# 三角剖分，返回的res是一个二维数组，每个一维数组记录一个三角形的三个顶点在原来的点集中的下标
def Delaunay(rect, points):
    subdiv = cv.Subdiv2D(rect)
    for point in points:
        subdiv.insert(point)
    triangleList = subdiv.getTriangleList()
    # rect是img1的宽高，点集是img2的，所以要检查三角形是否在rect内部
    res = []
    for t in triangleList:
        tmp = []
        tmp.append((t[0], t[1]))
        tmp.append((t[2], t[3]))
        tmp.append((t[4], t[5]))
        if in_rect(rect, tmp[0]) and in_rect(rect, tmp[1]) and in_rect(rect, tmp[2]):
            ind = []
            for j in range(3):
                for k in range(0, len(points)):
                    if abs(tmp[j][0] - points[k][0]) < 1.0 and abs(tmp[j][1] - points[k][1]) < 1.0:
                        ind.append(k)
            if (len(ind) == 3):
                res.append((ind[0], ind[1], ind[2]))
    return res

def affine_transform(src,srcTri,dstTri,size):
    # 计算变换矩阵
    warpMat = cv.getAffineTransform(np.float32(srcTri), np.float32(dstTri))
    # 返回变换后的图像
    dst = cv.warpAffine(src, warpMat, (size[0], size[1]), None, flags = cv.INTER_LINEAR, borderMode = cv.BORDER_REFLECT_101)
    return dst

# 对三角形仿射变换
def warp_triangle(img1, img2, t1, t2):
    # cv.boundingRect计算包围每个三角形的最小矩形
    r1 = cv.boundingRect(np.float32([t1]))
    r2 = cv.boundingRect(np.float32([t2]))
    t1Rect =[]
    t2Rect = []
    t2RectInt = []
    # 将顶点坐标转换为相对于它们各自边界矩形的左边
    for i in range(0,3):
        t1Rect.append(((t1[i][0] - r1[0]), (t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))
        t2RectInt.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))
    # 创建一个和边界矩形大小相同的mask
    mask = np.zeros((r2[3], r2[2], 3),dtype = np.float32)
    cv.fillConvexPoly(mask, np.int32(t2RectInt), (1.0, 1.0, 1.0), 16,0)
    # 从源图像中裁剪出源三角形的边界矩形区域
    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0] : r1[0] + r1[2]]
    # 对裁剪出的源三角形区域进行仿射变换，然后再用得到的变换后的图像与遮罩图像相乘，这样就得到了只包含目标三角形区域的图像
    size = (r2[2], r2[3])
    img2Rect = affine_transform(img1Rect, t1Rect, t2Rect, size)
    img2Rect = img2Rect * mask
    # 将变换后的图像添加到目标图像的相应位置，实现了源三角形到目标三角形的映射。第一行先将目标图像中目标三角形位置的像素清零，然后第二行将变换后的图像添加到目标图像的相应位置
    img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] = img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] * ((1.0, 1.0, 1.0) - mask)
    img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] = img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] + img2Rect

# 将img1的五官放在img2的脸上
def swap_face_ML(img2_path):
    img1_path = "xz.jpg"
    img1 = cv.imread(img1_path)
    img2 = cv.imread(img2_path)

    # 清空两个记录特征点的文件夹
    with open("points1.txt", 'a+', encoding = 'utf-8') as txt:
        txt.truncate(0)
    with open("points2.txt", 'a+', encoding = 'utf-8') as txt:
        txt.truncate(0)

    # 提取两张脸的68个特征点，写到两个txt里，方便调试
    img1_gray = cv.cvtColor(img1, cv.COLOR_BGR2GRAY);
    img2_gray = cv.cvtColor(img2, cv.COLOR_BGR2GRAY);
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    detector = dlib.get_frontal_face_detector()
    face1 = detector(img1_gray)
    face2 = detector(img2_gray)
    fin = open("points1.txt", 'a')
    for face in face1:
        landmarks = predictor(img1_gray, face)
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            fin.write(str(x))
            fin.write(" ")
            fin.write(str(y))
            fin.write("\n")
    fin.close()
    fin = open("points2.txt", 'a')
    for face in face2:
        landmarks = predictor(img2_gray, face)
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            fin.write(str(x))
            fin.write(" ")
            fin.write(str(y))
            fin.write("\n")
    fin.close()
    points1 = read_from_txt("points1.txt")
    points2 = read_from_txt("points2.txt")

    # 求特征点的凸包, 先求img2的，然后让img1适应img2的脸部特征
    hull2_idx = cv.convexHull(np.array(points2), returnPoints = False)
    hull1 = []
    hull2 = []
    for i in range(0, len(hull2_idx)):
        hull1.append(points1[int(hull2_idx[i])])
        hull2.append(points2[int(hull2_idx[i])])

    # 调试用，看凸包求得对不对
    # img1_hull = img1.copy()
    # img2_hull = img2.copy()
    # for i in hull1:
    #     cv.circle(img1_hull,tuple(i), 2, (0, 255, 0), 5)
    # for i in hull2:
    #     cv.circle(img2_hull,tuple(i), 2, (0, 255, 0), 5)
    # cv.imwrite("img1_hull.jpg", img1_hull)
    # cv.imwrite("img2_hull.jpg", img2_hull)

    # 对凸包构成的多边形进行Delaunay三角剖分
    # 该三角剖分满足两性质：
    # 1.任何一个三角形的外接圆不包含其他点
    # 2.在点集所可能形成的所有三角剖分中，Delaunay三角剖分所形成的三角形的最小角最大
    rect = (0, 0, img1.shape[1], img1.shape[0])
    dt = Delaunay(rect, hull2)

    # 对每个三角形应用仿射变换
    img_warped = np.copy(img2)
    for i in range(0, len(dt)):
        t1 = []
        t2 = []
        for j in range(0, 3):
            t1.append(hull1[dt[i][j]])
            t2.append(hull2[dt[i][j]])
        warp_triangle(img1, img_warped, t1, t2)

    # 将hull2列表中的坐标转换为整数类型，并存储在hull8U中
    hull8U = []
    for i in range(0, len(hull2)):
        hull8U.append((hull2[i][0], hull2[i][1]))
    # 创建了一个全零的掩码，其大小和img2相同，然后在这个全黑的掩码图像上填充了目标图像的凸包，填充的颜色是白色。这样就得到了一个只有目标凸包内部为白色，其余部分为黑色的掩码图像
    mask = np.zeros(img2.shape, dtype = img2.dtype)
    cv.fillConvexPoly(mask, np.int32(hull8U), (255, 255, 255))
    # 计算了目标图像凸包的边界矩形的中心点坐标
    r = cv.boundingRect(np.float32([hull2]))
    center = ((r[0] + int(r[2] / 2), r[1] + int(r[3] / 2)))
    # 将img_warped和img2根据掩码图像和中心点坐标进行无缝融合。无缝融合的结果是，img_warped中的白色部分（即目标凸包部分）将替换img2中的相应部分，而img2的其余部分则保持不变。然后函数返回了融合后的图像
    output = cv.seamlessClone(np.uint8(img_warped), img2, mask, center, cv.NORMAL_CLONE)
    return output

def mass_swap_face_ML(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok = True)
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            cartoon_image = swap_face_ML(filepath)
            output_filepath = os.path.join(output_dir, filename)
            #cv.imwrite(output_filepath, cv.cvtColor(cartoon_image, cv.COLOR_RGB2BGR))
            cv.imwrite(output_filepath, cartoon_image)


# 将img1的五官放在img2的脸上
def swap_face_DL(img2_path):
    img1_path = "xz.jpg"
    # 创建了一个名为'buffalo_l'的面部分析对象，用于检测和分析面部特征
    face_analyer = FaceAnalysis(name = 'buffalo_l')
    # 准备了面部分析器，设定了检测设备ID为0（通常0表示使用第一个可用的GPU），以及图像的大小（640 x 640）
    face_analyer.prepare(ctx_id = 0, det_size = (640, 640))
    face_swapper = insightface.model_zoo.get_model('inswapper_128.onnx')
    source_img = cv.imread(img1_path, cv.IMREAD_COLOR)
    target_img = cv.imread(img2_path, cv.IMREAD_COLOR)
    # 在源图像中进行面部检测
    source_faces = face_analyer.get(source_img)
    # 将源图像中的面部按照检测框的x坐标排序
    source_faces = sorted(source_faces, key = lambda x : x.bbox[0])
    assert len(source_faces) == 1
    source_face = source_faces[0]
    # 同理
    target_faces = face_analyer.get(target_img)
    target_faces = sorted(target_faces, key=lambda x: x.bbox[0])
    # 使用预训练的面部替换模型，将源面部替换到目标面部，然后将替换后的面部粘贴回原位置
    for target_face in target_faces:
        target_img = face_swapper.get(target_img, target_face, source_face, paste_back=True)
    return target_img

def mass_swap_face_DL(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok = True)
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            cartoon_image = swap_face_DL(filepath)
            output_filepath = os.path.join(output_dir, filename)
            cv.imwrite(output_filepath, cartoon_image)
