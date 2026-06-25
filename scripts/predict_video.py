from pathlib import Path
import sys
import cv2
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO

from src.config import (
    BEST_MODEL_PATH,
    DEMO_VIDEO_PATH,
    OUTPUT_VIDEO_PATH,
    ensure_dirs,
)

from src.sign_knowledge import get_display_name


def draw_detection(frame, box, label, conf):
    x1, y1, x2, y2 = map(int, box)
    box_color = (0, 255, 0)
    text_color = (0, 0, 0)

    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
    text = f"{label} {conf:.2f}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 2
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = x1
    text_y = y1 - 8
    if text_y - text_h - baseline < 0:
        text_y = y1 + text_h + baseline + 8
    cv2.rectangle(frame, (text_x, text_y - text_h - baseline), (text_x + text_w + 8, text_y + baseline), box_color, -1)
    cv2.putText(frame, text, (text_x + 4, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)


def predict_on_video(video_path, model_path, output_path, conf_threshold=0.4, iou_threshold=0.45):
    video_path = Path(video_path)
    model_path = Path(model_path)
    output_path = Path(output_path)

    if not model_path.exists():
        print("❌ Không tìm thấy model:")
        print(model_path)
        return

    if not video_path.exists():
        print("❌ Không tìm thấy video:")
        print(video_path)
        return

    print("🚀 Loading model...")
    print("Model path:", model_path)
    model = YOLO(str(model_path))

    print("\n📌 Model classes:")
    for class_id, class_code in model.names.items():
        display_name = get_display_name(class_code, use_vietnamese=False)
        print(f"{class_id:2d}: {class_code:6s} -> {display_name}")

    print("\n📂 Opening video...")
    print("Video path:", video_path)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print("❌ OpenCV không mở được video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"🎬 Video info: {width}x{height} | {fps:.1f} FPS | {total_frames} frames")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    if not out.isOpened():
        print("❌ Không tạo được output video.")
        cap.release()
        return

    frame_count = 0
    start_time = time.time()

    print("\n⚡ Running inference...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        results = model.predict(frame, conf=conf_threshold, iou=iou_threshold, verbose=False)
        result = results[0]
        detected_names = []

        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_code = model.names[cls_id]
                display_name = get_display_name(class_code, use_vietnamese=False)
                box_xyxy = box.xyxy[0].tolist()

                draw_detection(frame=frame, box=box_xyxy, label=display_name, conf=conf)
                detected_names.append(display_name)

        elapsed_time = time.time() - start_time
        current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        cv2.putText(frame, f"FPS: {current_fps:.1f} | Frame: {frame_count}/{total_frames}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        unique_detected = list(dict.fromkeys(detected_names))
        y = 65
        for name in unique_detected[:5]:
            cv2.putText(frame, f"- {name}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            y += 25

        out.write(frame)

        if frame_count % 30 == 0:
            print(f"[{frame_count}/{total_frames}] FPS: {current_fps:.1f}")

    cap.release()
    out.release()

    total_time = time.time() - start_time

    print("\n✅ DONE")
    print(f"📁 Output video: {output_path}")
    print(f"🎞️ Total frames: {frame_count}")
    print(f"⏱️ Total time: {total_time:.2f}s")
    if total_time > 0:
        print(f"⚡ Average FPS: {frame_count / total_time:.2f}")


def main():
    ensure_dirs()

    predict_on_video(video_path=DEMO_VIDEO_PATH, model_path=BEST_MODEL_PATH, output_path=OUTPUT_VIDEO_PATH, conf_threshold=0.4, iou_threshold=0.45)


if __name__ == "__main__":
    main()
