from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from ultralytics import YOLO
from pathlib import Path
import cv2
import json

from src.config import (
    DATA_YAML,
    VAL_IMAGES_DIR,
    BEST_MODEL_PATH,
    EVALUATION_DIR,
    VALIDATION_INFERENCE_DIR,
    ensure_dirs,
)


def main():
    ensure_dirs()

    model = YOLO(str(BEST_MODEL_PATH))

    val_results = model.val(
        data=str(DATA_YAML),
        imgsz=640,
        device=0,
        workers=0,
        plots=True,
        project=str(EVALUATION_DIR),
        name="baseline_v1",
        exist_ok=True
    )

    print("\n📊 OVERALL METRICS:")
    print("=" * 60)
    print(f"Precision: {val_results.box.mp:.4f}")
    print(f"Recall:    {val_results.box.mr:.4f}")
    print(f"mAP50:     {val_results.box.map50:.4f}")
    print(f"mAP50-95:  {val_results.box.map:.4f}")

    print("\n📊 CLASS-WISE mAP50:")
    print("=" * 60)

    ap50_by_class = {
        int(cls_id): float(ap50)
        for cls_id, ap50 in zip(val_results.box.ap_class_index, val_results.box.ap50)
    }

    for i, name in model.names.items():
        ap50 = ap50_by_class.get(i, 0.0)
        print(f"{i:2d} {name:10s} | mAP50={ap50:.4f}")

    predictions_log = []

    results = model.predict(
        source=str(VAL_IMAGES_DIR),
        conf=0.25,
        iou=0.45,
        save=False,
        stream=True,
        verbose=False
    )

    VALIDATION_INFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    for r in results:
        img_path = Path(r.path)

        for box in r.boxes:
            predictions_log.append({
                "image": img_path.name,
                "class": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "box": box.xywhn.tolist()[0]
            })

        annotated = r.plot()
        cv2.imwrite(str(VALIDATION_INFERENCE_DIR / img_path.name), annotated)

    with open(VALIDATION_INFERENCE_DIR / "predictions.json", "w", encoding="utf-8") as f:
        json.dump(predictions_log, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Inference saved to: {VALIDATION_INFERENCE_DIR}")


if __name__ == "__main__":
    main()
