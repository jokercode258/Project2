# src/qa_module.py
import re

"""
Rule-based QA nâng cao cho hệ thống nhận diện biển báo giao thông.

Module này hỗ trợ:
1. Lọc detection theo confidence.
2. Chuyển detection thành facts.
3. Phân loại intent câu hỏi.
4. Trả lời theo facts và có giải thích căn cứ.
5. Hỗ trợ một số câu hỏi tình huống đơn giản.
"""

from sign_knowledge import (
    SIGN_INFO,
    get_sign_info,
    get_sign_name,
    get_sign_meaning,
    get_sign_group,
    get_speed_limit,
    explain_detected_signs,
)


# =========================
# NORMALIZATION
# =========================

def normalize_question(question):
    if question is None:
        return ""
    return str(question).strip().lower()


def normalize_detected_classes(detected_classes):
    if not detected_classes:
        return []

    unique_classes = []

    for cls in detected_classes:
        cls = str(cls).strip().lower()
        if cls in SIGN_INFO and cls not in unique_classes:
            unique_classes.append(cls)

    return unique_classes


# =========================
# DETECTION PROCESSING
# =========================

def build_detections_from_classes(detected_classes):
    """
    Dùng cho trường hợp chỉ có list class cũ, ví dụ ["pl80", "pn"].
    Khi không có confidence thì mặc định confidence = 1.0.
    """
    detected_classes = normalize_detected_classes(detected_classes)

    detections = []

    for cls in detected_classes:
        info = get_sign_info(cls)

        if info is None:
            continue

        detections.append({
            "class_code": cls,
            "name_vi": info["name_vi"],
            "group": info["group"],
            "meaning": info["meaning"],
            "speed_limit": info.get("speed_limit"),
            "confidence": 1.0,
        })

    return detections


def normalize_detections(
    detections=None,
    detected_classes=None,
    qa_conf_threshold=0.25
):
    """
    Chuẩn hóa detection đầu vào.

    Args:
        detections: list[dict] từ predict_image_with_qa.py
        detected_classes: list[str] fallback
        qa_conf_threshold: ngưỡng confidence để đưa vào QA

    Returns:
        reliable_detections: detection đủ tin cậy
        ignored_detections: detection bị loại vì confidence thấp
    """
    if detections is None:
        detections = build_detections_from_classes(detected_classes)

    reliable_detections = []
    ignored_detections = []

    seen_classes = set()

    for det in detections:
        class_code = str(det.get("class_code", "")).strip().lower()

        if class_code not in SIGN_INFO:
            continue

        confidence = float(det.get("confidence", 1.0))

        info = get_sign_info(class_code)

        clean_det = {
            "class_code": class_code,
            "name_vi": det.get("name_vi", info["name_vi"]),
            "group": det.get("group", info["group"]),
            "meaning": det.get("meaning", info["meaning"]),
            "speed_limit": det.get("speed_limit", info.get("speed_limit")),
            "confidence": confidence,
        }

        if confidence < qa_conf_threshold:
            ignored_detections.append(clean_det)
            continue

        # Nếu cùng một class xuất hiện nhiều lần, giữ detection confidence cao nhất
        if class_code in seen_classes:
            for i, old_det in enumerate(reliable_detections):
                if old_det["class_code"] == class_code and confidence > old_det["confidence"]:
                    reliable_detections[i] = clean_det
            continue

        reliable_detections.append(clean_det)
        seen_classes.add(class_code)

    reliable_detections = sorted(
        reliable_detections,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return reliable_detections, ignored_detections


# =========================
# FACT BUILDING
# =========================

def build_facts(reliable_detections):
    """
    Chuyển danh sách detection thành facts để suy luận.
    """
    facts = {
        "has_sign": len(reliable_detections) > 0,
        "signs": reliable_detections,
        "speed_limits": [],
        "max_speed": None,

        "parking_forbidden": False,
        "entry_forbidden": False,
        "honking_forbidden": False,
        "truck_forbidden": False,
        "large_bus_forbidden": False,

        "keep_right": False,
        "height_limited": False,
    }

    for det in reliable_detections:
        cls = det["class_code"]

        speed = det.get("speed_limit")
        if speed is not None:
            facts["speed_limits"].append({
                "speed": speed,
                "source": det
            })

        if cls == "pn":
            facts["parking_forbidden"] = True

        elif cls == "pne":
            facts["entry_forbidden"] = True

        elif cls == "p11":
            facts["honking_forbidden"] = True

        elif cls == "p26":
            facts["truck_forbidden"] = True

        elif cls == "p3":
            facts["large_bus_forbidden"] = True

        elif cls == "i5":
            facts["keep_right"] = True

        elif cls == "ph":
            facts["height_limited"] = True

    if facts["speed_limits"]:
        # Nếu có nhiều biển tốc độ, chọn biển có confidence cao nhất
        best_speed = sorted(
            facts["speed_limits"],
            key=lambda x: x["source"]["confidence"],
            reverse=True
        )[0]
        facts["max_speed"] = best_speed["speed"]

    return facts


# =========================
# INTENT CLASSIFICATION
# =========================

def classify_intent(question):
    """
    Phân loại câu hỏi thành intent đơn giản.

    Lưu ý thứ tự kiểm tra rất quan trọng:
    - summary phải đứng trước situation_advice vì câu
      "Tóm tắt tình huống trong ảnh" có chứa từ "tình huống".
    - truck và large_bus phải đứng trước entry vì câu
      "Xe tải có được đi vào không?" cũng chứa cụm "đi vào".
    """
    q = normalize_question(question)

    # =========================
    # 1. SUMMARY
    # Đặt đầu tiên để tránh bị bắt nhầm thành situation_advice.
    # =========================
    if any(k in q for k in [
        "tóm tắt",
        "tom tat",
        "tổng hợp",
        "tong hop",
        "tổng kết",
        "tong ket",
        "liệt kê các biển",
        "liet ke cac bien",
        "các biển báo trong ảnh",
        "cac bien bao trong anh",
        "trong ảnh có những biển nào",
        "trong anh co nhung bien nao"
    ]):
        return "summary"

    # =========================
    # 2. WHAT SIGN
    # =========================
    if any(k in q for k in [
        "biển gì",
        "bien gi",
        "đây là biển gì",
        "day la bien gi",
        "đây là gì",
        "day la gi",
        "biển nào",
        "bien nao",
        "phát hiện được gì",
        "phat hien duoc gi",
        "nhận diện được gì",
        "nhan dien duoc gi",
        "trong ảnh có gì",
        "trong anh co gi"
    ]):
        return "what_sign"

    # =========================
    # 3. MEANING
    # =========================
    if any(k in q for k in [
        "ý nghĩa",
        "y nghia",
        "nghĩa là gì",
        "nghia la gi",
        "giải thích",
        "giai thich",
        "biển này có nghĩa",
        "bien nay co nghia",
        "biển báo này nghĩa",
        "bien bao nay nghia"
    ]):
        return "meaning"

    # =========================
    # 4. GROUP
    # =========================
    if any(k in q for k in [
        "thuộc nhóm",
        "thuoc nhom",
        "loại biển",
        "loai bien",
        "nhóm nào",
        "nhom nao",
        "nhóm biển",
        "nhom bien"
    ]):
        return "group"

    # =========================
    # 5. SPEED LIMIT
    # =========================
    if any(k in q for k in [
        "tốc độ",
        "toc do",
        "bao nhiêu km",
        "bao nhieu km",
        "chạy bao nhiêu",
        "chay bao nhieu",
        "tốc độ tối đa",
        "toc do toi da",
        "được chạy bao nhiêu",
        "duoc chay bao nhieu",
        "quá tốc độ",
        "qua toc do",
        "chạy quá",
        "chay qua",
        "vượt quá",
        "vuot qua",
        "quá bao nhiêu",
        "qua bao nhieu",
        "được chạy quá",
        "duoc chay qua",
        "km/h"
    ]):
        return "speed_limit"

    # =========================
    # 6. TRUCK
    # Đặt trước entry vì câu "Xe tải có được đi vào không?"
    # có chứa cụm "đi vào".
    # =========================
    if any(k in q for k in [
        "xe tải",
        "xe tai",
        "ô tô tải",
        "o to tai",
        "oto tải",
        "oto tai",
        "truck"
    ]):
        return "truck"

    # =========================
    # 7. LARGE BUS
    # Đặt trước entry vì câu "Xe khách lớn có được đi vào không?"
    # có chứa cụm "đi vào".
    # =========================
    if any(k in q for k in [
        "xe khách lớn",
        "xe khach lon",
        "xe khách",
        "xe khach",
        "ô tô khách",
        "o to khach",
        "bus",
        "large bus"
    ]):
        return "large_bus"

    # =========================
    # 8. PARKING
    # =========================
    if any(k in q for k in [
        "đỗ xe",
        "do xe",
        "đậu xe",
        "dau xe",
        "dừng đỗ",
        "dung do",
        "có được đỗ",
        "co duoc do",
        "có được đậu",
        "co duoc dau"
    ]):
        return "parking"

    # =========================
    # 9. ENTRY
    # Đặt sau truck và large_bus.
    # =========================
    if any(k in q for k in [
        "đi vào",
        "di vao",
        "vào đường này",
        "vao duong nay",
        "được vào",
        "duoc vao",
        "cấm đi vào",
        "cam di vao",
        "có được vào",
        "co duoc vao"
    ]):
        return "entry"

    # =========================
    # 10. HONKING
    # =========================
    if any(k in q for k in [
        "bấm còi",
        "bam coi",
        "dùng còi",
        "dung coi",
        "sử dụng còi",
        "su dung coi",
        "còi",
        "coi"
    ]):
        return "honking"

    # =========================
    # 11. DIRECTION
    # =========================
    if any(k in q for k in [
        "đi bên phải",
        "di ben phai",
        "bên phải",
        "ben phai",
        "hướng nào",
        "huong nao",
        "đi hướng nào",
        "di huong nao",
        "phải đi bên nào",
        "phai di ben nao"
    ]):
        return "direction"

    # =========================
    # 12. HEIGHT
    # =========================
    if any(k in q for k in [
        "chiều cao",
        "chieu cao",
        "cao bao nhiêu",
        "cao bao nhieu",
        "hạn chế chiều cao",
        "han che chieu cao"
    ]):
        return "height"

    # =========================
    # 13. SITUATION ADVICE
    # Đặt gần cuối để tránh bắt nhầm summary.
    # =========================
    if any(k in q for k in [
        "cần chú ý",
        "can chu y",
        "lưu ý gì",
        "luu y gi",
        "gặp biển này",
        "gap bien nay",
        "phải làm gì",
        "phai lam gi",
        "xử lý thế nào",
        "xu ly the nao",
        "tình huống",
        "tinh huong",
        "khi đi qua",
        "khi di qua",
        "nên làm gì",
        "nen lam gi"
    ]):
        return "situation_advice"

    return "unknown"


# =========================
# ANSWER HELPERS
# =========================

def format_confidence(conf):
    return f"{conf:.2f}"


def no_reliable_detection_answer(ignored_detections):
    if ignored_detections:
        return (
            "Hệ thống có một số dự đoán nhưng độ tin cậy thấp, "
            "nên chưa sử dụng để trả lời nhằm tránh kết luận sai."
        )

    return "Không phát hiện được biển báo đủ tin cậy trong ảnh."


def answer_what_sign(facts):
    signs = facts["signs"]

    if not signs:
        return "Không phát hiện được biển báo đủ tin cậy trong ảnh."

    if len(signs) == 1:
        det = signs[0]
        return (
            f"Đây là {det['name_vi']}. "
            f"Căn cứ: mô hình phát hiện biển này với độ tin cậy {format_confidence(det['confidence'])}."
        )

    lines = ["Trong ảnh phát hiện các biển báo sau:"]

    for det in signs:
        lines.append(
            f"- {det['name_vi']} "
            f"(độ tin cậy {format_confidence(det['confidence'])})"
        )

    return "\n".join(lines)


def answer_meaning(facts):
    signs = facts["signs"]

    if not signs:
        return "Không có biển báo đủ tin cậy để giải thích ý nghĩa."

    lines = []

    for det in signs:
        lines.append(
            f"{det['name_vi']}: {det['meaning']} "
            f"(độ tin cậy {format_confidence(det['confidence'])})."
        )

    return "\n".join(lines)


def answer_group(facts):
    signs = facts["signs"]

    if not signs:
        return "Không có biển báo đủ tin cậy để xác định nhóm."

    lines = []

    for det in signs:
        lines.append(
            f"{det['name_vi']} thuộc nhóm {det['group']}."
        )

    return "\n".join(lines)

def extract_speed_from_question(question):
    """
    Trích số tốc độ trong câu hỏi.
    Ví dụ: 'Có được chạy quá 80 km/h không?' -> 80
    """
    q = normalize_question(question)
    numbers = re.findall(r"\d+", q)

    if not numbers:
        return None

    return int(numbers[0])

def answer_speed_limit(facts, question=None):
    if facts["max_speed"] is None:
        return (
            "Không phát hiện biển giới hạn tốc độ đủ tin cậy trong ảnh. "
            "Vì vậy hệ thống chưa thể kết luận tốc độ tối đa."
        )

    best = sorted(
        facts["speed_limits"],
        key=lambda x: x["source"]["confidence"],
        reverse=True
    )[0]

    det = best["source"]
    max_speed = facts["max_speed"]

    asked_speed = extract_speed_from_question(question)

    if asked_speed is not None and (
        "chạy quá" in normalize_question(question)
        or "vượt quá" in normalize_question(question)
        or "được chạy quá" in normalize_question(question)
    ):
        if asked_speed >= max_speed:
            return (
                f"Không được chạy quá {max_speed} km/h. "
                f"Căn cứ: hệ thống phát hiện {det['name_vi']} "
                f"với độ tin cậy {format_confidence(det['confidence'])}."
            )

    return (
        f"Tốc độ tối đa cho phép là {max_speed} km/h. "
        f"Căn cứ: hệ thống phát hiện {det['name_vi']} "
        f"với độ tin cậy {format_confidence(det['confidence'])}."
    )


def answer_parking(facts):
    if facts["parking_forbidden"]:
        return (
            "Không được đỗ xe. "
            "Căn cứ: hệ thống phát hiện biển Cấm đỗ xe trong ảnh."
        )

    return (
        "Hệ thống không phát hiện biển Cấm đỗ xe đủ tin cậy trong ảnh. "
        "Tuy nhiên kết luận này chỉ dựa trên các biển báo mà mô hình nhận diện được."
    )


def answer_entry(facts):
    if facts["entry_forbidden"]:
        return (
            "Không được đi vào. "
            "Căn cứ: hệ thống phát hiện biển Cấm đi vào trong ảnh."
        )

    return (
        "Hệ thống không phát hiện biển Cấm đi vào đủ tin cậy trong ảnh."
    )


def answer_honking(facts):
    if facts["honking_forbidden"]:
        return (
            "Không được bấm còi. "
            "Căn cứ: hệ thống phát hiện biển Cấm bấm còi."
        )

    return "Hệ thống không phát hiện biển Cấm bấm còi đủ tin cậy trong ảnh."


def answer_truck(facts):
    if facts["truck_forbidden"]:
        return (
            "Xe tải không được đi vào. "
            "Căn cứ: hệ thống phát hiện biển Cấm xe tải đi vào."
        )

    return "Hệ thống không phát hiện biển Cấm xe tải đi vào đủ tin cậy trong ảnh."


def answer_large_bus(facts):
    if facts["large_bus_forbidden"]:
        return (
            "Xe khách lớn không được đi vào. "
            "Căn cứ: hệ thống phát hiện biển Cấm xe khách lớn đi vào."
        )

    return "Hệ thống không phát hiện biển Cấm xe khách lớn đi vào đủ tin cậy trong ảnh."


def answer_direction(facts):
    if facts["keep_right"]:
        return (
            "Phương tiện cần đi về bên phải theo chỉ dẫn của biển báo. "
            "Căn cứ: hệ thống phát hiện biển Đi bên phải."
        )

    return "Hệ thống không phát hiện biển chỉ dẫn đi bên phải đủ tin cậy trong ảnh."


def answer_height(facts):
    if facts["height_limited"]:
        return (
            "Trong ảnh có biển hạn chế chiều cao. "
            "Người điều khiển cần chú ý chiều cao phương tiện trước khi đi qua."
        )

    return "Hệ thống không phát hiện biển hạn chế chiều cao đủ tin cậy trong ảnh."


def answer_situation_advice(facts):
    signs = facts["signs"]

    if not signs:
        return "Chưa phát hiện biển báo đủ tin cậy nên chưa thể đưa ra khuyến nghị."

    advice = []

    if facts["max_speed"] is not None:
        advice.append(
            f"Không vượt quá tốc độ {facts['max_speed']} km/h."
        )

    if facts["parking_forbidden"]:
        advice.append("Không đỗ xe tại khu vực có biển Cấm đỗ xe.")

    if facts["entry_forbidden"]:
        advice.append("Không đi vào đường/khu vực có biển Cấm đi vào.")

    if facts["honking_forbidden"]:
        advice.append("Không sử dụng còi tại khu vực có biển Cấm bấm còi.")

    if facts["truck_forbidden"]:
        advice.append("Xe tải không được đi vào đoạn đường có biển cấm.")

    if facts["large_bus_forbidden"]:
        advice.append("Xe khách lớn không được đi vào đoạn đường có biển cấm.")

    if facts["keep_right"]:
        advice.append("Cần đi về bên phải theo chỉ dẫn của biển báo.")

    if facts["height_limited"]:
        advice.append("Cần chú ý giới hạn chiều cao của phương tiện.")

    if not advice:
        return (
            "Hệ thống đã phát hiện biển báo nhưng chưa có rule khuyến nghị cụ thể. "
            "Thông tin phát hiện:\n" + answer_what_sign(facts)
        )

    lines = ["Khi đi qua khu vực này, người lái cần chú ý:"]

    for item in advice:
        lines.append(f"- {item}")

    return "\n".join(lines)


def answer_summary(facts):
    signs = facts["signs"]

    if not signs:
        return "Không phát hiện được biển báo đủ tin cậy trong ảnh."

    lines = ["Tóm tắt kết quả nhận diện:"]

    for det in signs:
        lines.append(
            f"- {det['name_vi']} ({det['group']}), "
            f"độ tin cậy {format_confidence(det['confidence'])}."
        )

    if facts["max_speed"] is not None:
        lines.append(f"Tốc độ tối đa suy ra từ biển báo là {facts['max_speed']} km/h.")

    return "\n".join(lines)


# =========================
# MAIN QA FUNCTION
# =========================

def answer_question(
    question,
    detections=None,
    detected_classes=None,
    qa_conf_threshold=0.25,
    return_debug=False
):
    """
    Hàm QA chính.

    Có thể gọi theo 2 kiểu:

    Kiểu mới:
        answer_question(question="...", detections=detections)

    Kiểu cũ:
        answer_question(question="...", detected_classes=["pl80"])

    Args:
        question: câu hỏi người dùng
        detections: list dict detection từ YOLO
        detected_classes: list class fallback
        qa_conf_threshold: ngưỡng confidence dùng cho QA
        return_debug: nếu True trả thêm facts/debug

    Returns:
        str hoặc dict
    """
    reliable_detections, ignored_detections = normalize_detections(
        detections=detections,
        detected_classes=detected_classes,
        qa_conf_threshold=qa_conf_threshold
    )

    facts = build_facts(reliable_detections)
    intent = classify_intent(question)

    if not facts["has_sign"]:
        answer = no_reliable_detection_answer(ignored_detections)
    elif intent == "what_sign":
        answer = answer_what_sign(facts)
    elif intent == "meaning":
        answer = answer_meaning(facts)
    elif intent == "group":
        answer = answer_group(facts)
    elif intent == "speed_limit":
        answer = answer_speed_limit(facts, question)
    elif intent == "parking":
        answer = answer_parking(facts)
    elif intent == "entry":
        answer = answer_entry(facts)
    elif intent == "honking":
        answer = answer_honking(facts)
    elif intent == "truck":
        answer = answer_truck(facts)
    elif intent == "large_bus":
        answer = answer_large_bus(facts)
    elif intent == "direction":
        answer = answer_direction(facts)
    elif intent == "height":
        answer = answer_height(facts)
    elif intent == "situation_advice":
        answer = answer_situation_advice(facts)
    elif intent == "summary":
        answer = answer_summary(facts)
    else:
        answer = (
            "Hệ thống chưa hiểu rõ câu hỏi. "
            "Dưới đây là thông tin biển báo phát hiện được:\n"
            + answer_summary(facts)
        )

    if return_debug:
        return {
            "answer": answer,
            "intent": intent,
            "facts": facts,
            "reliable_detections": reliable_detections,
            "ignored_detections": ignored_detections,
        }

    return answer


# =========================
# DEMO
# =========================

def demo():
    detections = [
        {
            "class_code": "pl80",
            "name_vi": "Giới hạn tốc độ 80 km/h",
            "group": "Biển giới hạn tốc độ",
            "meaning": "Biển báo quy định tốc độ tối đa cho phép là 80 km/h.",
            "speed_limit": 80,
            "confidence": 0.75,
        },
        {
            "class_code": "pl20",
            "name_vi": "Giới hạn tốc độ 20 km/h",
            "group": "Biển giới hạn tốc độ",
            "meaning": "Biển báo quy định tốc độ tối đa cho phép là 20 km/h.",
            "speed_limit": 20,
            "confidence": 0.08,
        }
    ]

    questions = [
        "Đây là biển gì?",
        "Tốc độ tối đa là bao nhiêu?",
        "Cần chú ý gì khi đi qua đoạn đường này?",
        "Tóm tắt tình huống trong ảnh.",
    ]

    print("DEMO ADVANCED QA")
    print("=" * 60)

    for question in questions:
        print("\nQ:", question)
        print("A:", answer_question(
            question=question,
            detections=detections,
            qa_conf_threshold=0.25
        ))


if __name__ == "__main__":
    demo()