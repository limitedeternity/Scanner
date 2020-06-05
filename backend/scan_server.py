# Scanner requirements
import imutils
import transform
import cv2
import math
import itertools
import numpy as np
from scipy.spatial import distance as dist


def predicate(representatives, corner):
    return all(dist.euclidean(representative, corner) >= 20 for representative in representatives)

def angle_between_vectors_degrees(u, v):
    return np.degrees(math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))

def get_angle(p1, p2, p3):
    a = np.radians(np.array(p1))
    b = np.radians(np.array(p2))
    c = np.radians(np.array(p3))

    avec = a - b
    cvec = c - b
    return angle_between_vectors_degrees(avec, cvec)

def angle_range(quad):
    tl, tr, br, bl = quad
    ura = get_angle(tl[0], tr[0], br[0])
    ula = get_angle(bl[0], tl[0], tr[0])
    lra = get_angle(tr[0], br[0], bl[0])
    lla = get_angle(br[0], bl[0], tl[0])

    angles = [ura, ula, lra, lla]
    return np.ptp(angles)

def is_valid_contour(cnt, IM_WIDTH, IM_HEIGHT):
    return (len(cnt) == 4 and cv2.contourArea(cnt) > IM_WIDTH * IM_HEIGHT * 0.25 and angle_range(cnt) < 40)


# UDP broadcast requirements
from socket import *
from time import sleep
from threading import Thread


def ip_disclose():
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(0.2)
    while True:
        sock.sendto(b"e9ad115d-388e-4e8e-a630-999832d92217", ("255.255.255.255", 37020))
        sleep(3)

t = Thread(target = ip_disclose)
t.daemon = True
t.start()


# Server requirements
from flask import Flask, request, send_file
import io
from magicpatch import magic
import mimetypes

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/scan", methods=["POST"])
def scan():
    if not request.stream:
        return "", 400

    head = request.stream.read(1024)
    mime_detector = magic.Magic(mime = True)
    mime = mime_detector.from_buffer(head)
    if not mime.startswith("image/"):
        return "", 400

    buf = head + request.stream.read()
    nparr = np.frombuffer(buf, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    ratio = image.shape[0] / 500.0
    orig = image.copy()

    image = imutils.resize(image, height = 500)
    IM_HEIGHT, IM_WIDTH, _ = image.shape

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    dilated = cv2.dilate(gray, kernel)

    edged = cv2.Canny(dilated, 0, 84)
    lsd = cv2.createLineSegmentDetector()
    lines = lsd.detect(edged)[0]

    corners = []
    if lines is not None:
        lines = lines.squeeze().astype(np.int32).tolist()
        horizontal_lines_canvas = np.zeros(edged.shape, dtype=np.uint8)
        vertical_lines_canvas = np.zeros(edged.shape, dtype=np.uint8)
        for line in lines:
            x1, y1, x2, y2 = line
            if abs(x2 - x1) > abs(y2 - y1):
                (x1, y1), (x2, y2) = sorted(((x1, y1), (x2, y2)), key=lambda pt: pt[0])
                cv2.line(horizontal_lines_canvas, (max(x1 - 5, 0), y1), (min(x2 + 5, edged.shape[1] - 1), y2), 255, 2)

            else:
                (x1, y1), (x2, y2) = sorted(((x1, y1), (x2, y2)), key=lambda pt: pt[1])
                cv2.line(vertical_lines_canvas, (x1, max(y1 - 5, 0)), (x2, min(y2 + 5, edged.shape[0] - 1)), 255, 2)

        lines = []
        contours = cv2.findContours(horizontal_lines_canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[1]
        contours = sorted(contours, key=lambda c: cv2.arcLength(c, True), reverse=True)[:2]
        horizontal_lines_canvas = np.zeros(edged.shape, dtype=np.uint8)
        for contour in contours:
            contour = contour.reshape((contour.shape[0], contour.shape[2]))
            min_x = np.amin(contour[:, 0], axis=0) + 2
            max_x = np.amax(contour[:, 0], axis=0) - 2
            left_y = int(np.average(contour[contour[:, 0] == min_x][:, 1]))
            right_y = int(np.average(contour[contour[:, 0] == max_x][:, 1]))
            lines.append((min_x, left_y, max_x, right_y))
            cv2.line(horizontal_lines_canvas, (min_x, left_y), (max_x, right_y), 1, 1)
            corners.append((min_x, left_y))
            corners.append((max_x, right_y))

        contours = cv2.findContours(vertical_lines_canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[1]
        contours = sorted(contours, key=lambda c: cv2.arcLength(c, True), reverse=True)[:2]
        vertical_lines_canvas = np.zeros(edged.shape, dtype=np.uint8)
        for contour in contours:
            contour = contour.reshape((contour.shape[0], contour.shape[2]))
            min_y = np.amin(contour[:, 1], axis=0) + 2
            max_y = np.amax(contour[:, 1], axis=0) - 2
            top_x = int(np.average(contour[contour[:, 1] == min_y][:, 0]))
            bottom_x = int(np.average(contour[contour[:, 1] == max_y][:, 0]))
            lines.append((top_x, min_y, bottom_x, max_y))
            cv2.line(vertical_lines_canvas, (top_x, min_y), (bottom_x, max_y), 1, 1)
            corners.append((top_x, min_y))
            corners.append((bottom_x, max_y))

        corners_y, corners_x = np.where(horizontal_lines_canvas + vertical_lines_canvas == 2)
        corners += zip(corners_x, corners_y)

    test_corners = []
    for c in corners:
        if predicate(test_corners, c):
            test_corners.append(c)

    approx_contours = []
    if len(test_corners) >= 4:
        quads = []
        for quad in itertools.combinations(test_corners, 4):
            points = np.array(quad)
            points = transform.order_points(points)
            points = np.array([[p] for p in points], dtype = "int32")
            quads.append(points)

        quads = sorted(quads, key=cv2.contourArea, reverse=True)[:5]
        quads = sorted(quads, key=angle_range)

        approx = quads[0]
        if is_valid_contour(approx, IM_WIDTH, IM_HEIGHT):
            approx_contours.append(approx)

    (_, cnts, hierarchy) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    for c in cnts:
        approx = cv2.approxPolyDP(c, 80, True)
        if is_valid_contour(approx, IM_WIDTH, IM_HEIGHT):
            approx_contours.append(approx)
            break

    screenCnt = None
    if not approx_contours:
        TOP_RIGHT = (IM_WIDTH, 0)
        BOTTOM_RIGHT = (IM_WIDTH, IM_HEIGHT)
        BOTTOM_LEFT = (0, IM_HEIGHT)
        TOP_LEFT = (0, 0)
        screenCnt = np.array([[TOP_RIGHT], [BOTTOM_RIGHT], [BOTTOM_LEFT], [TOP_LEFT]])

    else:
        screenCnt = max(approx_contours, key=cv2.contourArea)

    screenCnt = screenCnt.reshape(4, 2)
    warped = transform.four_point_transform(orig, screenCnt * ratio)

    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    sharpen = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpen = cv2.addWeighted(gray, 1.5, sharpen, -0.5, 0)
    thresh = cv2.adaptiveThreshold(sharpen, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 15)

    scan = cv2.imencode(mimetypes.guess_extension(mime), thresh)[1]

    return send_file(
        io.BytesIO(scan),
        mimetype = mime,
        as_attachment=True,
        attachment_filename="Scan"
    )
