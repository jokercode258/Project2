from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# src/evaluate_qa.py

from pathlib import Path
import unicodedata
import pandas as pd
from ultralytics import YOLO

from src.config import (
    BEST_MODEL_PATH,
    QA_TEST_CASES_PATH,
    QA_RESULTS_PATH,
    QA_DIR,
    ensure_dirs,
)

from src.sign_knowledge import (
    get_display_name,
    get_sign_name,
    get_sign_info,
)

from src.qa_module import answer_question


# =========================
# TEXT NORMALIZATION
# =========================

def normalize_text(text):
    if text is None:
        return ""

    text = str(text).strip().lower()

    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")

    return text


def contains_expected_keyword(answer, expected_keyword):
    answer_norm = normalize_text(answer)
    expected_norm = normalize_text(expected_keyword)

    if not expected_norm:
        return False

    return expected_norm in answer_norm


# =========================
# YOLO DETECTION
# =========================

def run_detection(model, image_path, conf_threshold=0.05, iou_threshold=0.45, imgsz=960):
    results = model.predict(str(image_path), conf=conf_threshold, iou=iou_threshold, imgsz=imgsz, verbose=False)

    result = results[0]
    detections = []

    if result.boxes is None or len(result.boxes) == 0:
        return detections

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        class_code = model.names[cls_id]
        info = get_sign_info(class_code)

        detection = {
            "class_id": cls_id,
            "class_code": class_code,
            "name_vi": get_sign_name(class_code),
            "display_name": get_display_name(class_code, use_vietnamese=False),
            "group": info["group"] if info else "Không xác định",
            "meaning": info["meaning"] if info else "",
            "speed_limit": info.get("speed_limit") if info else None,
            "confidence": conf,
            "box_xyxy": box.xyxy[0].tolist(),
            "box_xywhn": box.xywhn[0].tolist(),
        }

        detections.append(detection)

    return detections


def summarize_detections(detections):
    if not detections:
        return ""

    items = []
    for det in detections:
        items.append(f"{det['class_code']}({det['confidence']:.2f})")

    return "; ".join(items)


def summarize_reliable_detections(reliable_detections):
    if not reliable_detections:
        return ""

    items = []
    for det in reliable_detections:
        items.append(f"{det['class_code']}({det['confidence']:.2f})")

    return "; ".join(items)


# =========================
# QA EVALUATION
# =========================

def evaluate_one_case(model, image_path, question, expected_keyword, yolo_conf=0.05, qa_conf=0.25, iou=0.45, imgsz=960):
    image_path = Path(image_path)

    if not image_path.exists():
        return {
            "answer": "Không tìm thấy ảnh.",
            "correct": False,
            "detections": [],
            "reliable_detections": [],
            "ignored_detections": [],
            "intent": "image_not_found",
            "detected_summary": "",
            "reliable_summary": "",
        }

    detections = run_detection(model=model, image_path=image_path, conf_threshold=yolo_conf, iou_threshold=iou, imgsz=imgsz)

    qa_output = answer_question(question=question, detections=detections, qa_conf_threshold=qa_conf, return_debug=True)

    answer = qa_output["answer"]
    intent = qa_output["intent"]
    reliable_detections = qa_output["reliable_detections"]
    ignored_detections = qa_output["ignored_detections"]

    correct = contains_expected_keyword(answer=answer, expected_keyword=expected_keyword)

    return {
        "answer": answer,
        "correct": correct,
        "detections": detections,
        "reliable_detections": reliable_detections,
        "ignored_detections": ignored_detections,
        "intent": intent,
        "detected_summary": summarize_detections(detections),
        "reliable_summary": summarize_reliable_detections(reliable_detections),
    }


def main():
    ensure_dirs()
    QA_DIR.mkdir(parents=True, exist_ok=True)

    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy model: {BEST_MODEL_PATH}")

    if not QA_TEST_CASES_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file QA test cases: {QA_TEST_CASES_PATH}")

    print("🚀 Loading model...")
    print("Model:", BEST_MODEL_PATH)

    model = YOLO(str(BEST_MODEL_PATH))

    print("\n📄 Loading QA test cases...")
    print("Test cases:", QA_TEST_CASES_PATH)

    df = pd.read_csv(QA_TEST_CASES_PATH)

    results = []
    total = len(df)
    correct_count = 0

    for idx, row in df.iterrows():
        image_path = row["image"]
        question = row["question"]
        expected_keyword = row["expected_keyword"]
        q_type = row.get("type", "")
        class_code = row.get("class_code", "")

        print("\n" + "-" * 70)
        print(f"[{idx + 1}/{total}]")
        print("Image:", image_path)
        print("Class:", class_code)
        print("Type:", q_type)
        print("Question:", question)
        print("Expected keyword:", expected_keyword)

        eval_result = evaluate_one_case(model=model, image_path=image_path, question=question, expected_keyword=expected_keyword, yolo_conf=0.05, qa_conf=0.25, iou=0.45, imgsz=960)

        answer = eval_result["answer"]
        correct = eval_result["correct"]

        if correct:
            correct_count += 1

        print("Detected:", eval_result["detected_summary"])
        print("Used by QA:", eval_result["reliable_summary"])
        print("Intent:", eval_result["intent"])
        print("Answer:", answer)
        print("Correct:", correct)

        results.append({
            "image": image_path,
            "class_code": class_code,
            "type": q_type,
            "question": question,
            "expected_keyword": expected_keyword,
            "answer": answer,
            "intent": eval_result["intent"],
            "detected_summary": eval_result["detected_summary"],
            "reliable_summary": eval_result["reliable_summary"],
            "correct": correct,
        })

    result_df = pd.DataFrame(results)
    result_df.to_csv(QA_RESULTS_PATH, index=False, encoding="utf-8-sig")

    accuracy = correct_count / total if total > 0 else 0

    summary_by_type = result_df.groupby("type")["correct"].agg(["count", "sum", "mean"]).reset_index()

    summary_path = QA_DIR / "qa_summary_by_type.csv"
    summary_by_type.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 70)
    print("QA EVALUATION RESULT")
    print("=" * 70)
    print(f"Total cases:   {total}")
    print(f"Correct cases: {correct_count}")
    print(f"Accuracy:      {accuracy:.2%}")

    print("\nAccuracy by question type:")
    print(summary_by_type)

    print("\n✅ QA results saved to:")
    print(QA_RESULTS_PATH)

    print("\n✅ QA summary saved to:")
    print(summary_path)


if __name__ == "__main__":
    main()
