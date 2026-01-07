import cv2
import numpy as np
import glob

def test_blue_mean(image_folder="blue_screens"):
    """
    지정된 폴더 안의 모든 이미지 파일을 불러와서 mean 색상 값을 출력
    :param image_folder: 파란 화면 이미지가 저장된 폴더 경로
    """
    image_files = glob.glob(f"{image_folder}/*.png")

    if not image_files:
        print("이미지 파일이 없습니다.")
        return

    for file in image_files:
        img = cv2.imread(file)
        if img is None:
            print(f"이미지를 불러올 수 없음: {file}")
            continue

        mean_color = cv2.mean(img)  # (B, G, R, A)
        print(f"\n{file}")
        print(f"평균: {mean_color}")
        print(f"빨강 최댓값: {np.max(img[:, :, 2])}, 파랑 최댓값: {np.max(img[:, :, 0])}, 초록 최댓값: {np.max(img[:, :, 1])}")
        print(f"빨강 최소값: {np.min(img[:, :, 2])}, 파랑 최소값: {np.min(img[:, :, 0])}, 초록 최소값: {np.min(img[:, :, 1])}")