from ultralytics import YOLO
import cv2
import numpy as np
import csv
import os

# จุด Homography: ปรับตามภาพ
src_pts = np.array([
    [140, 65],
    [990, 65],
    [1140, 650],
    [20, 650]
], dtype=np.float32)

# ขนาดสนามจริง (เมตร)
pitch_length = 105
pitch_width = 68
dst_pts = np.array([
    [0, 0],
    [pitch_length, 0],
    [pitch_length, pitch_width],
    [0, pitch_width]
], dtype=np.float32)

# คำนวณ Homography Matrix 
h_matrix, _ = cv2.findHomography(src_pts, dst_pts)

def run_tracking(video_path):
    # โหลดโมเดล YOLO
    model = YOLO('training/runs/detect/train4/weights/best.pt')

    # รัน YOLO
    results = model.predict(video_path, save=True, save_txt=False, conf=0.3)


    # เขียนผลลัพธ์
    with open('tracking_positions.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['frame', 'player_id', 'x', 'y', 'team'])

        frame_id = 0
        for result in results:
            frame_id += 1
            for i, box in enumerate(result.boxes):
                x_pixel = float((box.xyxy[0][0] + box.xyxy[0][2]) / 2)
                y_pixel = float((box.xyxy[0][1] + box.xyxy[0][3]) / 2)

                pt = np.array([[[x_pixel, y_pixel]]], dtype=np.float32)
                bird_eye = cv2.perspectiveTransform(pt, h_matrix)
                x_m, y_m = bird_eye[0][0]

                # Clamp ไม่ให้เกินขอบสนาม
                x_m = max(0, min(x_m, pitch_length))
                y_m = max(0, min(y_m, pitch_width))

                label = result.names[int(box.cls)].strip().lower()
                writer.writerow([frame_id, i, x_m, y_m, label])