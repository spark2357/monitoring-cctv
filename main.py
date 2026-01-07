import cv2
import numpy as np
import mss
from test_blue_mean import test_blue_mean

def select_monitor(sct):
    # 모니터 목록 출력
    monitors = sct.monitors
    print("사용 가능한 모니터 목록:")
    for i, m in enumerate(monitors):
        print(f"{i}: {m}")

    # 사용자 입력으로 모니터 선택
    monitor_index = int(input("사용할 모니터 번호를 입력하세요: "))
    return monitors[monitor_index]


def select_area(sct, monitor):

    # 첫 화면 캡처
    img = np.array(sct.grab(monitor))
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # ROI 선택 (마우스로 드래그)
    roi = cv2.selectROI("ROI 선택", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("ROI 선택")

    return roi

def check_no_video(img):

    mean_color = cv2.mean(img)
    if mean_color[2] <= 55:
        return True
    
    return False


def monitor_screen_with_input(threshold=2000, interval=500):
    """
    CCTV 뷰어 화면을 캡처해서 ROI 내 움직임 감지 (실행 시 모니터 번호 입력 + ROI 선택)
    :param threshold: 움직임 감지 민감도
    :param interval: 캡처 간격 (초)
    """
    sct = mss.mss()
    monitor = select_monitor(sct)
    x, y, w, h = select_area(sct, monitor)

    prev_gray = None

    while True:
        # 화면 캡처
        try:
            img = np.array(sct.grab(monitor))
        except:
            sct = mss.mss()
            continue

        # ROI 잘라내기
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        roi_frame = frame[y:y+h, x:x+w]

        if check_no_video(roi_frame):
            if cv2.waitKey(interval) & 0xFF == 27:  # ESC 종료
                break
            continue

        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(prev_gray, gray)
            _, diff_thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            motion_pixels = cv2.countNonZero(diff_thresh)

            if motion_pixels > threshold:
                print(f"⚡ 이벤트 발생! ROI 내 변화 픽셀 수: {motion_pixels}")

        prev_gray = gray

        # ROI 화면 표시 (디버깅용)
        cv2.imshow("ROI Monitoring", roi_frame)
        if cv2.waitKey(interval) & 0xFF == 27:  # ESC 종료
            break

    cv2.destroyAllWindows()


# 사용 예시
monitor_screen_with_input(2000, 500)

# 사용 예시
# test_blue_mean("blue_screens")