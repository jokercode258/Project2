# src/config.py

from pathlib import Path


# =========================
# PROJECT ROOT
# =========================
ROOT = Path(__file__).resolve().parents[1]


# =========================
# DATA PATHS
# =========================
DATA_DIR = ROOT / "data_v1_filtered"
DATA_YAML = DATA_DIR / "data.yaml"

TRAIN_IMAGES_DIR = DATA_DIR / "images" / "train"
VAL_IMAGES_DIR = DATA_DIR / "images" / "val"

TRAIN_LABELS_DIR = DATA_DIR / "labels" / "train"
VAL_LABELS_DIR = DATA_DIR / "labels" / "val"


# =========================
# METADATA PATHS
# =========================
METADATA_DIR = ROOT / "metadata"
SELECTED_CLASSES_PATH = METADATA_DIR / "selected_classes.txt"
LABEL_MAP_PATH = METADATA_DIR / "label_map.csv"
CLASS_DISTRIBUTION_PATH = METADATA_DIR / "class_distribution.csv"


# =========================
# MODEL PATHS
# =========================
MODELS_DIR = ROOT / "models"
PRETRAINED_MODELS_DIR = MODELS_DIR / "pretrained"

# Model hiện tại dùng để predict/demo
BEST_MODEL_PATH = MODELS_DIR / "baseline_v1_best.pt"

# Sau này train final xong sẽ copy best.pt sang đây
FINAL_MODEL_PATH = MODELS_DIR / "final_best.pt"


# =========================
# OUTPUT PATHS
# =========================
RUNS_DIR = ROOT / "runs"
REPORTS_DIR = ROOT / "reports"

EVALUATION_DIR = REPORTS_DIR / "evaluation"
INFERENCE_DIR = REPORTS_DIR / "inference"

VALIDATION_INFERENCE_DIR = INFERENCE_DIR / "validation_v1"
IMAGE_QA_OUTPUT_DIR = INFERENCE_DIR / "image_qa"


# =========================
# QA PATHS
# =========================
QA_DIR = REPORTS_DIR / "qa"
QA_TEST_CASES_PATH = QA_DIR / "qa_test_cases.csv"
QA_RESULTS_PATH = QA_DIR / "qa_results.csv"


# =========================
# FINAL TRAINING PATHS
# =========================
FINAL_TRAIN_NAME = "final_train_v1"
FINAL_TRAIN_DIR = RUNS_DIR / "detect" / FINAL_TRAIN_NAME


# =========================
# DEMO PATHS
# =========================
DEMO_VIDEO_PATH = DATA_DIR / "demo.mp4"
OUTPUT_VIDEO_PATH = INFERENCE_DIR / "output_video_named.mp4"


# =========================
# COMMON SETTINGS
# =========================
CLASS_ID_TO_CODE = {
    0: "pn",
    1: "pne",
    2: "p11",
    3: "p26",
    4: "i2",
    5: "i4",
    6: "i5",
    7: "p3",
    8: "ph",
    9: "pl20",
    10: "pl30",
    11: "pl40",
    12: "pl50",
    13: "pl80",
    14: "pl90",
}


def ensure_dirs():
    """
    Tạo các thư mục cần thiết cho project.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PRETRAINED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    INFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_INFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    QA_DIR.mkdir(parents=True, exist_ok=True)

    RUNS_DIR.mkdir(parents=True, exist_ok=True)