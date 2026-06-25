from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# src/create_qa_test_cases.py

import argparse
import csv
from pathlib import Path

from ultralytics import YOLO

from src.config import (
    VAL_IMAGES_DIR,
    VAL_LABELS_DIR,
    QA_DIR,
    QA_TEST_CASES_PATH,
    BEST_MODEL_PATH,
    CLASS_ID_TO_CODE,
    ensure_dirs,
)

from src.sign_knowledge import (
    get_sign_info,
    get_sign_name,
    get_speed_limit,
)


# DEFAULT SETTINGS
YOLO_CONF = 0.05
QA_CONF = 0.25
IMG_SIZE = 960


def find_image_for_label(label_path):
    stem = label_path.stem
    possible_exts = [".jpg", ".jpeg", ".png", ".bmp"]

    for ext in possible_exts:
        image_path = VAL_IMAGES_DIR / f"{stem}{ext}"
        if image_path.exists():
            return image_path

    return None


def read_gt_classes(label_path):
    gt_classes = set()

    with open(label_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        class_id = int(float(parts[0]))
        class_code = CLASS_ID_TO_CODE.get(class_id)
        if class_code:
            gt_classes.add(class_code)

    return gt_classes


def write_csv(rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "image",
        "question",
        "expected_keyword",
        "type",
        "class_code",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def collect_first_image_per_class():
    class_to_image = {}

    label_paths = sorted(VAL_LABELS_DIR.glob("*.txt"))

    for label_path in label_paths:
        image_path = find_image_for_label(label_path)
        if image_path is None:
            continue
        gt_classes = read_gt_classes(label_path)
        for class_code in gt_classes:
            if class_code not in class_to_image:
                class_to_image[class_code] = image_path

    return class_to_image


def run_detection(model, image_path, yolo_conf=YOLO_CONF, imgsz=IMG_SIZE):
    results = model.predict(str(image_path), conf=yolo_conf, iou=0.45, imgsz=imgsz, verbose=False)
    result = results[0]
    detections = []
    if result.boxes is None or len(result.boxes) == 0:
        return detections

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_code = model.names[cls_id]
        detections.append({"class_code": class_code, "confidence": conf})

    return detections


def collect_best_image_per_class(yolo_conf=YOLO_CONF, qa_conf=QA_CONF, imgsz=IMG_SIZE):
    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy model tại: {BEST_MODEL_PATH}")

    print("🚀 Loading model for best-case selection...")
    print("Model:", BEST_MODEL_PATH)

    model = YOLO(str(BEST_MODEL_PATH))

    selected = {}

    label_paths = sorted(VAL_LABELS_DIR.glob("*.txt"))
    total = len(label_paths)

    print(f"\n🔎 Scanning validation labels: {total} files")
    print(f"YOLO conf: {yolo_conf}")
    print(f"QA conf:   {qa_conf}")
    print(f"imgsz:     {imgsz}")

    for idx, label_path in enumerate(label_paths):
        if idx % 100 == 0:
            print(f"Processing {idx}/{total}...")

        image_path = find_image_for_label(label_path)
        if image_path is None:
            continue

        gt_classes = read_gt_classes(label_path)
        if not gt_classes:
            continue

        detections = run_detection(model=model, image_path=image_path, yolo_conf=yolo_conf, imgsz=imgsz)

        for target_class in gt_classes:
            best_conf_for_target = 0.0
            for det in detections:
                if det["class_code"] == target_class:
                    best_conf_for_target = max(best_conf_for_target, det["confidence"])

            if best_conf_for_target < qa_conf:
                continue

            current_best = selected.get(target_class)
            if current_best is None or best_conf_for_target > current_best["confidence"]:
                selected[target_class] = {"image": image_path, "confidence": best_conf_for_target}

    return selected


def add_general_questions(rows, class_code, image_path):
    info = get_sign_info(class_code)
    name_vi = get_sign_name(class_code)
    if info is None:
        return

    rows.append({"image": str(image_path), "question": "Đây là biển gì?", "expected_keyword": name_vi, "type": "what_sign", "class_code": class_code})
    rows.append({"image": str(image_path), "question": "Biển này có ý nghĩa gì?", "expected_keyword": name_vi, "type": "meaning", "class_code": class_code})
    rows.append({"image": str(image_path), "question": "Biển này thuộc nhóm nào?", "expected_keyword": info["group"], "type": "group", "class_code": class_code})
    rows.append({"image": str(image_path), "question": "Tóm tắt tình huống trong ảnh.", "expected_keyword": name_vi, "type": "summary", "class_code": class_code})


def add_speed_questions(rows, class_code, image_path):
    speed = get_speed_limit(class_code)
    if speed is None:
        return

    rows.append({"image": str(image_path), "question": "Tốc độ tối đa là bao nhiêu?", "expected_keyword": str(speed), "type": "speed_limit", "class_code": class_code})
    rows.append({"image": str(image_path), "question": f"Có được chạy quá {speed} km/h không?", "expected_keyword": str(speed), "type": "speed_limit", "class_code": class_code})
    rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": str(speed), "type": "situation_advice", "class_code": class_code})


def add_specific_questions(rows, class_code, image_path):
    if class_code == "pn":
        rows.append({"image": str(image_path), "question": "Có được đỗ xe không?", "expected_keyword": "Không được đỗ xe", "type": "parking", "class_code": class_code})
        rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": "Không đỗ xe", "type": "situation_advice", "class_code": class_code})

    elif class_code == "pne":
        rows.append({"image": str(image_path), "question": "Có được đi vào đường này không?", "expected_keyword": "Không được đi vào", "type": "entry", "class_code": class_code})
        rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": "Không đi vào", "type": "situation_advice", "class_code": class_code})

    elif class_code == "p11":
        rows.append({"image": str(image_path), "question": "Có được bấm còi không?", "expected_keyword": "Không được bấm còi", "type": "honking", "class_code": class_code})
        rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": "Không sử dụng còi", "type": "situation_advice", "class_code": class_code})

    elif class_code == "p26":
        rows.append({"image": str(image_path), "question": "Xe tải có được đi vào không?", "expected_keyword": "Xe tải không được đi vào", "type": "truck", "class_code": class_code})
        rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": "Xe tải không được đi vào", "type": "situation_advice", "class_code": class_code})

    elif class_code == "p3":
        rows.append({"image": str(image_path), "question": "Xe khách lớn có được đi vào không?", "expected_keyword": "Xe khách lớn không được đi vào", "type": "large_bus", "class_code": class_code})
        rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": "Xe khách lớn không được đi vào", "type": "situation_advice", "class_code": class_code})

    elif class_code == "i5":
        rows.append({"image": str(image_path), "question": "Phải đi bên nào?", "expected_keyword": "bên phải", "type": "direction", "class_code": class_code})
        rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": "bên phải", "type": "situation_advice", "class_code": class_code})

    elif class_code == "ph":
        rows.append({"image": str(image_path), "question": "Cần chú ý gì về chiều cao?", "expected_keyword": "chiều cao", "type": "height", "class_code": class_code})
        rows.append({"image": str(image_path), "question": "Cần chú ý gì khi đi qua đoạn đường này?", "expected_keyword": "chiều cao", "type": "situation_advice", "class_code": class_code})


def build_rows_from_class_to_image(class_to_image):
    rows = []
    for class_id, class_code in CLASS_ID_TO_CODE.items():
        image_path = class_to_image.get(class_code)
        if image_path is None:
            print(f"⚠️ Không tìm thấy ảnh cho class {class_code}")
            continue
        print(f"✅ {class_code}: {image_path}")
        add_general_questions(rows, class_code, image_path)
        add_speed_questions(rows, class_code, image_path)
        add_specific_questions(rows, class_code, image_path)

    return rows


def parse_args():
    parser = argparse.ArgumentParser(description="Create QA test cases for traffic sign QA module.")

    parser.add_argument("--mode", choices=["label", "best"], default="label")
    parser.add_argument("--set-default", action="store_true")
    parser.add_argument("--yolo-conf", type=float, default=YOLO_CONF)
    parser.add_argument("--qa-conf", type=float, default=QA_CONF)
    parser.add_argument("--imgsz", type=int, default=IMG_SIZE)

    return parser.parse_args()


def main():
    args = parse_args()
    ensure_dirs()
    QA_DIR.mkdir(parents=True, exist_ok=True)

    if args.mode == "label":
        print("🔎 Mode: label")
        class_to_image = collect_first_image_per_class()
        output_path = QA_DIR / "qa_test_cases_label.csv"
    else:
        print("🔎 Mode: best")
        selected = collect_best_image_per_class(yolo_conf=args.yolo_conf, qa_conf=args.qa_conf, imgsz=args.imgsz)
        class_to_image = {class_code: item["image"] for class_code, item in selected.items()}
        output_path = QA_DIR / "qa_test_cases_best.csv"

    print("\n" + "=" * 70)
    print("GENERATING QA TEST CASES")
    print("=" * 70)

    rows = build_rows_from_class_to_image(class_to_image)
    write_csv(rows, output_path)

    print("\n✅ QA test cases created:")
    print(output_path)
    print(f"Total cases: {len(rows)}")

    if args.set_default:
        write_csv(rows, QA_TEST_CASES_PATH)
        print("\n✅ Also saved as default test cases:")
        print(QA_TEST_CASES_PATH)


if __name__ == "__main__":
    main()
