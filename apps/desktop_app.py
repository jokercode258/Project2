from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO

from config import BEST_MODEL_PATH
from sign_knowledge import get_sign_info
from qa_module import answer_question


class TrafficSignQAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Sign Recognition & QA")
        self.root.geometry("1200x750")

        self.image_path = None
        self.display_image = None

        self.model = YOLO(str(BEST_MODEL_PATH))

        self.build_ui()

    def build_ui(self):
        title = tk.Label(self.root, text=" Nhận diện biển báo giao thông và hỏi đáp theo ảnh", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(left_frame, text="Chưa chọn ảnh", bg="#eeeeee", width=80, height=30)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        choose_btn = tk.Button(left_frame, text="Chọn ảnh", font=("Arial", 12), command=self.choose_image)
        choose_btn.pack(pady=5)

        right_frame = tk.Frame(main_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Label(right_frame, text="Câu hỏi:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.question_entry = tk.Entry(right_frame, font=("Arial", 12), width=45)
        self.question_entry.pack(pady=5)
        self.question_entry.insert(0, "Đây là biển gì?")

        tk.Label(right_frame, text="Câu hỏi mẫu:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))

        sample_questions = [
            "Đây là biển gì?",
            "Biển này có ý nghĩa gì?",
            "Biển này thuộc nhóm nào?",
            "Tốc độ tối đa là bao nhiêu?",
            "Có được chạy quá 80 km/h không?",
            "Cần chú ý gì khi đi qua đoạn đường này?",
            "Tóm tắt tình huống trong ảnh."
        ]

        self.sample_var = tk.StringVar(value=sample_questions[0])

        sample_menu = tk.OptionMenu(right_frame, self.sample_var, *sample_questions, command=self.set_sample_question)
        sample_menu.config(width=40)
        sample_menu.pack(pady=5)

        tk.Label(right_frame, text="YOLO confidence:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))

        self.conf_scale = tk.Scale(right_frame, from_=0.05, to=0.90, resolution=0.05, orient=tk.HORIZONTAL)
        self.conf_scale.set(0.25)
        self.conf_scale.pack(fill=tk.X)

        tk.Label(right_frame, text="QA confidence:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))

        self.qa_conf_scale = tk.Scale(right_frame, from_=0.05, to=0.90, resolution=0.05, orient=tk.HORIZONTAL)
        self.qa_conf_scale.set(0.25)
        self.qa_conf_scale.pack(fill=tk.X)

        run_btn = tk.Button(right_frame, text=" Nhận diện và trả lời", font=("Arial", 13, "bold"), bg="#2e7d32", fg="white", command=self.run_qa)
        run_btn.pack(pady=15, fill=tk.X)

        tk.Label(right_frame, text="Kết quả:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.result_box = scrolledtext.ScrolledText(right_frame, width=50, height=18, font=("Arial", 11))
        self.result_box.pack(fill=tk.BOTH, expand=True, pady=5)

    def set_sample_question(self, value):
        self.question_entry.delete(0, tk.END)
        self.question_entry.insert(0, value)

    def choose_image(self):
        file_path = filedialog.askopenfilename(title="Chọn ảnh biển báo", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")])
        if not file_path:
            return
        self.image_path = Path(file_path)
        self.show_image(self.image_path)

    def show_image(self, image_path):
        image = Image.open(image_path).convert("RGB")
        image = self.resize_image(image, max_width=750, max_height=550)
        self.display_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.display_image, text="")

    def show_cv2_image(self, cv2_image):
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_image)
        image = self.resize_image(image, max_width=750, max_height=550)
        self.display_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.display_image, text="")

    def resize_image(self, image, max_width=750, max_height=550):
        width, height = image.size
        scale = min(max_width / width, max_height / height)
        if scale < 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height))
        return image

    def run_detection(self):
        conf = float(self.conf_scale.get())

        results = self.model.predict(source=str(self.image_path), conf=conf, iou=0.45, imgsz=960, verbose=False)
        result = results[0]
        detections = []

        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf_score = float(box.conf[0])
                class_code = self.model.names[cls_id]

                info = get_sign_info(class_code)
                if info is None:
                    continue

                detections.append({
                    "class_code": class_code,
                    "name_vi": info["name_vi"],
                    "group": info["group"],
                    "meaning": info["meaning"],
                    "speed_limit": info.get("speed_limit"),
                    "confidence": conf_score,
                    "bbox_xyxy": box.xyxy.tolist()[0],
                })

        annotated_image = result.plot()

        return annotated_image, detections

    def run_qa(self):
        if self.image_path is None:
            messagebox.showwarning("Thiếu ảnh", "Bạn cần chọn ảnh trước.")
            return

        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Thiếu câu hỏi", "Bạn cần nhập câu hỏi.")
            return

        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, "Đang xử lý...\n")
        self.root.update()

        try:
            annotated_image, detections = self.run_detection()

            answer = answer_question(question=question, detections=detections, qa_conf_threshold=float(self.qa_conf_scale.get()))

            self.show_cv2_image(annotated_image)

            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END, "CÂU HỎI:\n")
            self.result_box.insert(tk.END, question + "\n\n")
            self.result_box.insert(tk.END, "CÂU TRẢ LỜI:\n")
            self.result_box.insert(tk.END, answer + "\n\n")
            self.result_box.insert(tk.END, "BIỂN BÁO PHÁT HIỆN:\n")

            if not detections:
                self.result_box.insert(tk.END, "- Không phát hiện biển báo.\n")
            else:
                for det in detections:
                    self.result_box.insert(tk.END, f"- {det['class_code']}: {det['name_vi']} | confidence={det['confidence']:.2f}\n")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


def main():
    root = tk.Tk()
    app = TrafficSignQAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
