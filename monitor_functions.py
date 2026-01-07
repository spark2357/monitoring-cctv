import cv2
import numpy as np
import mss

def capture_screen(sct, monitor):
    # 화면 캡처
    max_iter = 5
    while max_iter:
        max_iter -= 1
        try:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return frame
        except:
            sct = mss.mss()
            continue

def select_area(frame, title):
    # 영역 선택
    roi = cv2.selectROI(title, frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow(title)
    return roi

def check_no_video(img):
     # 영상 없는 파란 화면 검사
    mean_color = cv2.mean(img)
    if mean_color[2] <= 55:
        return True
    return False