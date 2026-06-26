from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO
import shutil
import pandas as pd
import matplotlib.pyplot as plt

from src.config import DATA_YAML, RUNS_DIR, BEST_MODEL_PATH, ensure_dirs


def get_col(df, keyword):
    for col in df.columns:
        if keyword in col:
            return col
    return None


def main():
    ensure_dirs()

    if BEST_MODEL_PATH.exists():
        print(f"Found existing model: {BEST_MODEL_PATH}")
        print("Continue training from existing best model.")
        model = YOLO(str(BEST_MODEL_PATH))
    else:
        print("No existing best model found.")
        print("Training from YOLO26n pretrained model.")
        model = YOLO("yolo26n.pt")

    results = model.train(
        data=str(DATA_YAML),
        epochs=30,
        imgsz=640,
        batch=4,
        cache=False,
        device=0,
        workers=0,
        patience=20,
        project=str(RUNS_DIR / "detect"),
        name="baseline_v1_final",
        plots=True,
        exist_ok=True
    )

    print("\n" + "=" * 50)
    print("TRAINING COMPLETED")
    print("=" * 50)

    save_dir = Path(results.save_dir)
    csv_path = save_dir / "results.csv"

    if not csv_path.exists():
        print(" Không tìm thấy results.csv")
        return

    df = pd.read_csv(csv_path)

    p_col = get_col(df, "precision")
    r_col = get_col(df, "recall")
    map50_col = get_col(df, "mAP50(")
    map95_col = get_col(df, "mAP50-95")

    train_loss_col = get_col(df, "train/box_loss")
    val_loss_col = get_col(df, "val/box_loss")

    if None in [p_col, r_col, map50_col, map95_col]:
        print(" Không tìm đủ cột metrics")
        print(df.columns)
        return

    last = df.iloc[-1]
    best = df.loc[df[map95_col].idxmax()]

    print("\n FINAL METRICS:")
    print(f"Epoch: {last['epoch']}")
    print(f"Precision: {last[p_col]:.4f}")
    print(f"Recall: {last[r_col]:.4f}")
    print(f"mAP@0.5: {last[map50_col]:.4f}")
    print(f"mAP@0.5-0.95: {last[map95_col]:.4f}")

    print("\n BEST EPOCH:")
    print(f"Epoch: {best['epoch']}")
    print(f"Precision: {best[p_col]:.4f}")
    print(f"Recall: {best[r_col]:.4f}")
    print(f"mAP@0.5: {best[map50_col]:.4f}")
    print(f"mAP@0.5-0.95: {best[map95_col]:.4f}")

    print("\n LAST 5 EPOCHS:")
    print(df[['epoch', p_col, r_col, map50_col, map95_col]].tail())

    plt.figure()
    plt.plot(df[map50_col], label="mAP@0.5")
    plt.plot(df[map95_col], label="mAP@0.5-0.95")
    plt.xlabel("Epoch")
    plt.ylabel("mAP")
    plt.title("mAP theo epoch")
    plt.legend()
    plt.grid()
    plt.savefig(save_dir / "map_plot.png")
    plt.close()

    plt.figure()
    plt.plot(df[p_col], label="Precision")
    plt.plot(df[r_col], label="Recall")
    plt.xlabel("Epoch")
    plt.ylabel("Value")
    plt.title("Precision & Recall theo epoch")
    plt.legend()
    plt.grid()
    plt.savefig(save_dir / "pr_plot.png")
    plt.close()

    if train_loss_col and val_loss_col:
        plt.figure()
        plt.plot(df[train_loss_col], label="Train Box Loss")
        plt.plot(df[val_loss_col], label="Val Box Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Train vs Val Box Loss")
        plt.legend()
        plt.grid()
        plt.savefig(save_dir / "loss_plot.png")
        plt.close()

    new_best = save_dir / "weights" / "best.pt"

    if new_best.exists():
        shutil.copy2(new_best, BEST_MODEL_PATH)
        print(f"\n Copied best model to: {BEST_MODEL_PATH}")

    print(f"\n Training reports saved to: {save_dir}")


if __name__ == "__main__":
    main()
