from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# src/predict_image_with_qa.py

from ultralytics import YOLO
from pathlib import Path
import cv2
import argparse
import json

from src.config import (
    BEST_MODEL_PATH,
    IMAGE_QA_OUTPUT_DIR,
    ensure_dirs,
)

from src.sign_knowledge import (
    get_display_name,
    get_sign_name,
    get_sign_info,
)

from src.qa_module import answer_question


def draw_detection(frame, box, label, conf, is_reliable=True):
    x1, y1, x2, y2 = map(int, box)
    if is_reliable:
        box_color = (0, 255, 0)
    else:
        box_color = (0, 255, 255)
    text_color = (0, 0, 0)

    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
    text = f"{label} {conf:.2f}"
    if not is_reliable:
        text = f"{label} {conf:.2f} low"

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


def predict_image_with_qa(image_path, question, conf_threshold=0.05, iou_threshold=0.45, imgsz=960, qa_conf_threshold=0.25):
    ensure_dirs()

    image_path = Path(image_path)
    if not BEST_MODEL_PATH.exists():
        print(" Không tìm thấy model:")
        print(BEST_MODEL_PATH)
        print("\n Hãy kiểm tra file models/baseline_v1_best.pt")
        return

    if not image_path.exists():
        print(" Không tìm thấy ảnh:")
        print(image_path)
        return

    image = cv2.imread(str(image_path))
    if image is None:
        print(" Không đọc được ảnh:")
        print(image_path)
        return

    print(" Loading model...")
    print("Model:", BEST_MODEL_PATH)
    model = YOLO(str(BEST_MODEL_PATH))

    print("\n Image:", image_path)
    print(" Question:", question)
    print(f" YOLO conf threshold: {conf_threshold}")
    print(f" QA conf threshold: {qa_conf_threshold}")
    print(f" Predict imgsz: {imgsz}")

    results = model.predict(image, conf=conf_threshold, iou=iou_threshold, imgsz=imgsz, verbose=False)
    result = results[0]
    detections = []

    if result.boxes is not None and len(result.boxes) > 0:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_code = model.names[cls_id]
            info = get_sign_info(class_code)

            display_name = get_display_name(class_code, use_vietnamese=False)
            name_vi = get_sign_name(class_code)
            box_xyxy = box.xyxy[0].tolist()
            box_xywhn = box.xywhn[0].tolist()

            detection = {
                "class_id": cls_id,
                "class_code": class_code,
                "name_vi": name_vi,
                "display_name": display_name,
                "group": info["group"] if info else "Không xác định",
                "meaning": info["meaning"] if info else "",
                "speed_limit": info.get("speed_limit") if info else None,
                "confidence": conf,
                "box_xyxy": box_xyxy,
                "box_xywhn": box_xywhn,
            }

            detections.append(detection)

    qa_output = answer_question(question=question, detections=detections, qa_conf_threshold=qa_conf_threshold, return_debug=True)

    answer = qa_output["answer"]
    reliable_detections = qa_output["reliable_detections"]
    ignored_detections = qa_output["ignored_detections"]
    intent = qa_output["intent"]
    facts = qa_output["facts"]

    reliable_keys = {det["class_code"] for det in reliable_detections}

    for det in detections:
        is_reliable = det["confidence"] >= qa_conf_threshold and det["class_code"] in reliable_keys
        draw_detection(frame=image, box=det["box_xyxy"], label=det["display_name"], conf=det["confidence"], is_reliable=is_reliable)

    print("\n All YOLO detections:")
    if detections:
        for det in detections:
            status = "USED_BY_QA" if det["confidence"] >= qa_conf_threshold else "IGNORED_LOW_CONF"
            print(f"- {det['class_code']}: {det['name_vi']} | conf={det['confidence']:.2f} | {status}")
    else:
        print("- Không có detection nào từ YOLO")

    print("\n Reliable detections used by QA:")
    if reliable_detections:
        for det in reliable_detections:
            print(f"- {det['class_code']}: {det['name_vi']} | conf={det['confidence']:.2f}")
    else:
        print("- Không có detection đủ tin cậy để đưa vào QA")

    if ignored_detections:
        print("\n Ignored low-confidence detections:")
        for det in ignored_detections:
            print(f"- {det['class_code']}: {det['name_vi']} | conf={det['confidence']:.2f}")

    print("\n Question intent:")
    print(intent)

    print("\n Answer:")
    print(answer)

    output_image_path = IMAGE_QA_OUTPUT_DIR / f"{image_path.stem}_qa.jpg"
    cv2.imwrite(str(output_image_path), image)

    output_json_path = IMAGE_QA_OUTPUT_DIR / f"{image_path.stem}_qa.json"

    result_log = {
        "image": str(image_path),
        "question": question,
        "conf_threshold": conf_threshold,
        "qa_conf_threshold": qa_conf_threshold,
        "iou_threshold": iou_threshold,
        "imgsz": imgsz,
        "intent": intent,
        "detections": detections,
        "reliable_detections": reliable_detections,
        "ignored_detections": ignored_detections,
        "facts": facts,
        "answer": answer,
        "output_image": str(output_image_path),
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result_log, f, indent=2, ensure_ascii=False)

    print("\n Output image saved to:")
    print(output_image_path)

    print("\n QA result saved to:")
    print(output_json_path)


def main():
    parser = argparse.ArgumentParser(description="Predict traffic signs from image and answer a rule-based question.")

    parser.add_argument("--image", required=True, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--question", required=True, help="Câu hỏi muốn hỏi về ảnh")
    parser.add_argument("--conf", type=float, default=0.05)
    parser.add_argument("--qa-conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--imgsz", type=int, default=960)

    args = parser.parse_args()

    predict_image_with_qa(image_path=args.image, question=args.question, conf_threshold=args.conf, iou_threshold=args.iou, imgsz=args.imgsz, qa_conf_threshold=args.qa_conf)


if __name__ == "__main__":
    main()
