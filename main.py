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


def select_area(frame):
    # 영역 선택 (마우스로 드래그)
    roi = cv2.selectROI("ROI 선택", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("ROI 선택")
    return roi

def check_no_video(img):
    # 영상 없는 파란 화면 검사
    mean_color = cv2.mean(img)
    if mean_color[2] <= 55:
        return True
    return False

def capture_screen(sct, monitor):
    # 화면 캡처
    max_iter = 10
    while(max_iter):
        max_iter -= 1
        try:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return frame
        except:
            sct = mss.mss()
            continue

def monitoring(threshold, interval, sct, monitor, fx, fy, fw, fh, tx, ty, tw, th):
    prev_gray = None
    event_frame = []
    event_time = []

    while True:
        # 이벤트 감지 영역 잘라내기
        frame = capture_screen(sct, monitor)

        watch_frame = frame[fy:fy+fh, fx:fx+fw]
        if check_no_video(watch_frame):
            if cv2.waitKey(interval) & 0xFF == 27:  # ESC 종료
                break
            continue

        gray = cv2.cvtColor(watch_frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            diff = cv2.absdiff(prev_gray, gray)
            _, diff_thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            motion_pixels = cv2.countNonZero(diff_thresh)
            # 이벤트 발생
            if motion_pixels > threshold:
                print(f"⚡ 이벤트 발생! ROI 내 변화 픽셀 수: {motion_pixels}")
                # 사진 저장
                event_frame.append(watch_frame)
                event_time.append(frame[ty:ty+th, tx:tx+tw])
                cv2.imshow("ROI Time", frame[ty:ty+th, tx:tx+tw])
                
        prev_gray = gray

        # ROI 화면 표시 (디버깅용)
        cv2.imshow("ROI Monitoring", watch_frame)
        if cv2.waitKey(interval) & 0xFF == 27:  # ESC 종료
            break

    cv2.destroyAllWindows()


def monitor_screen_with_input(threshold=2000, interval=500):
    # 필요 정보 획득 및 모니터링 함수 실행
    sct = mss.mss()
    monitor = select_monitor(sct)
    frame = capture_screen(sct, monitor)
    # 이벤트 감지 영역 선택
    fx, fy, fw, fh = select_area(frame)
    # 시간 표시 영역 선택
    tx, ty, tw, th = select_area(frame)

    monitoring(threshold, interval, sct, monitor, fx, fy, fw, fh, tx, ty, tw, th)

    
# 사용 예시
monitor_screen_with_input(2000, 500)

# 사용 예시
# test_blue_mean("blue_screens")