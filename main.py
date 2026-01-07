import cv2
import mss
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from monitor_functions import capture_screen, select_area, check_no_video

class CCTVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CCTV 이벤트 감지 프로그램")
        self.root.geometry("800x600")

        self.sct = mss.mss()
        self.monitor = self.sct.monitors[-1]
        self.frame = None
        
        self.threshold = 2000
        self.interval = 500
        self.thresh = 25
        self.prev_gray = None

        self.fx = self.fy = self.fw = self.fh = 0
        self.tx = self.ty = self.tw = self.th = 0

        # 좌/우 구분 Frame
        left_frame = tk.Frame(root)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = tk.Frame(root)
        right_frame.pack(side="right", fill="both", expand=True)

        # GUI 버튼 / 왼쪽 위
        button_frame = tk.Frame(left_frame)
        button_frame.pack(side="top", pady=5, fill="both")
        tk.Button(root, text="감시 영역 선택", command=self.select_event_roi).pack(side="left", pady=5, padx=5)
        tk.Button(root, text="시간 영역 선택", command=self.select_time_roi).pack(side="left", pady=5, padx=5)
        tk.Button(root, text="모니터링 시작", command=self.monitoring).pack(side="left", pady=5, padx=5)

        # 모니터링 화면 표시 영역 / 왼쪽 아래
        self.monitor_label = tk.Label(left_frame)
        self.monitor_label.pack(side="bottom", pady=10, fill="both")

        # 스크롤 가능한 이벤트 이미지 영역 / 오른쪽
        self.canvas = tk.Canvas(right_frame)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def custom_warning(self, title, message):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("400x200")  # 원하는 크기 지정
        tk.Label(win, text=message, font=("맑은 고딕", 15)).pack(pady=20)
        tk.Button(win, text="확인", command=win.destroy).pack(pady=10)

    def select_event_roi(self):
        self.frame = capture_screen(self.sct, self.monitor)
        roi = select_area(self.frame, "감시 영역 선택")
        self.fx, self.fy, self.fw, self.fh = roi
        self.custom_warning("알림", "영역 선택 완료")


    def select_time_roi(self):
        self.frame = capture_screen(self.sct, self.monitor)
        roi = select_area(self.frame, "시간 영역 선택")
        self.tx, self.ty, self.tw, self.th = roi
        self.custom_warning("알림", "영역 선택 완료")

    def monitoring(self):
        if self.fw == 0 or self.tw == 0:
            self.custom_warning("경고", "영역을 먼저 선택하세요")
            return

        frame = capture_screen(self.sct, self.monitor)
        # 이벤트 감지 영역 잘라내기
        watch_frame = frame[self.fy:self.fy+self.fh, self.fx:self.fx+self.fw]
        # 영상 없는 파란 화면 검사
        if not check_no_video(watch_frame):
            # gray scale로 변환
            gray = cv2.cvtColor(watch_frame, cv2.COLOR_BGR2GRAY)
            if self.prev_gray is not None:
                diff = cv2.absdiff(self.prev_gray, gray)
                _, diff_thresh = cv2.threshold(diff, self.thresh, 255, cv2.THRESH_BINARY)
                motion_pixels = cv2.countNonZero(diff_thresh)
                # 이벤트 발생
                if motion_pixels > self.threshold:
                    # 사진 표시
                    self.add_event_image(watch_frame, frame[self.ty:self.ty+self.th, self.tx:self.tx+self.tw])

            self.prev_gray = gray

            self.update_monitor_label(watch_frame)
        
        self.root.after(self.interval, self.monitoring)
        
    def update_monitor_label(self, watch_frame):
        watch_rgb = cv2.cvtColor(watch_frame, cv2.COLOR_BGR2RGB)
        watch_pil = Image.fromarray(watch_rgb)
        watch_tk = ImageTk.PhotoImage(watch_pil)

        self.monitor_label.configure(image=watch_tk)
        self.monitor_label.image = watch_tk

        
    def add_event_image(self, watch_frame, time_frame):
        # OpenCV → PIL 변환
        # cv2와 PIL의 색 속성 순서가 달라서 변환
        watch_rgb = cv2.cvtColor(watch_frame, cv2.COLOR_BGR2RGB)
        watch_img = Image.fromarray(watch_rgb)
        watch_tk = ImageTk.PhotoImage(watch_img)

        time_rgb = cv2.cvtColor(time_frame, cv2.COLOR_BGR2RGB)
        time_img = Image.fromarray(time_rgb)
        time_tk = ImageTk.PhotoImage(time_img)

        # 두 이미지를 넣을 한 줄 Frame 생성
        row_frame = tk.Frame(self.scrollable_frame)

        # Frame에 넣을 Label 생성
        watch_label = tk.Label(row_frame, image=watch_tk)
        watch_label.image = watch_tk

        time_label = tk.Label(row_frame, image=time_tk)
        time_label.image = time_tk

        # Frame에 Label 넣기
        time_label.pack(side="left", padx=5)
        watch_label.pack(side="left", padx=5)

        # Row 프레임을 scrollable_frame에 추가
        row_frame.pack(pady=5, anchor="w")


if __name__ == "__main__":
    root = tk.Tk()
    app = CCTVApp(root)
    root.mainloop()
