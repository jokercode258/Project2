SIGN_INFO = {
    "pn": {
        "code": "pn",
        "name_vi": "Cấm đỗ xe",
        "name_en": "No parking",
        "group": "Biển cấm",
        "meaning": "Biển báo cấm các phương tiện đỗ xe tại khu vực có đặt biển.",
        "short_answer": "Đây là biển cấm đỗ xe.",
        "prohibited_actions": ["đỗ xe", "dừng đỗ lâu"],
        "allowed_actions": ["đi tiếp nếu không vi phạm biển báo khác"],
        "speed_limit": None,
    },

    "pne": {
        "code": "pne",
        "name_vi": "Cấm đi vào",
        "name_en": "No entry",
        "group": "Biển cấm",
        "meaning": "Biển báo cấm tất cả hoặc một số loại phương tiện đi vào theo chiều đặt biển.",
        "short_answer": "Đây là biển cấm đi vào.",
        "prohibited_actions": ["đi vào", "lưu thông vào đường này"],
        "allowed_actions": ["chọn hướng đi khác"],
        "speed_limit": None,
    },

    "p11": {
        "code": "p11",
        "name_vi": "Cấm bấm còi",
        "name_en": "No honking",
        "group": "Biển cấm",
        "meaning": "Biển báo cấm người điều khiển phương tiện sử dụng còi tại khu vực có đặt biển.",
        "short_answer": "Đây là biển cấm bấm còi.",
        "prohibited_actions": ["bấm còi", "sử dụng còi"],
        "allowed_actions": ["tiếp tục di chuyển nhưng không sử dụng còi"],
        "speed_limit": None,
    },

    "p26": {
        "code": "p26",
        "name_vi": "Cấm xe tải đi vào",
        "name_en": "No trucks",
        "group": "Biển cấm",
        "meaning": "Biển báo cấm xe tải đi vào đoạn đường hoặc khu vực có đặt biển.",
        "short_answer": "Đây là biển cấm xe tải đi vào.",
        "prohibited_actions": ["xe tải đi vào"],
        "allowed_actions": ["xe không thuộc nhóm bị cấm có thể đi nếu không có biển cấm khác"],
        "speed_limit": None,
    },

    "i2": {
        "code": "i2",
        "name_vi": "Đường dành cho xe không động cơ",
        "name_en": "Road for non-motor vehicles",
        "group": "Biển chỉ dẫn",
        "meaning": "Biển báo chỉ dẫn đoạn đường hoặc làn đường dành cho các phương tiện không động cơ.",
        "short_answer": "Đây là biển chỉ dẫn đường dành cho xe không động cơ.",
        "prohibited_actions": [],
        "allowed_actions": ["xe không động cơ lưu thông theo chỉ dẫn"],
        "speed_limit": None,
    },

    "i4": {
        "code": "i4",
        "name_vi": "Đường dành cho xe cơ giới",
        "name_en": "Road for motor vehicles",
        "group": "Biển chỉ dẫn",
        "meaning": "Biển báo chỉ dẫn đoạn đường hoặc làn đường dành cho xe cơ giới.",
        "short_answer": "Đây là biển chỉ dẫn đường dành cho xe cơ giới.",
        "prohibited_actions": [],
        "allowed_actions": ["xe cơ giới lưu thông theo chỉ dẫn"],
        "speed_limit": None,
    },

    "i5": {
        "code": "i5",
        "name_vi": "Đi bên phải",
        "name_en": "Keep right",
        "group": "Biển bắt buộc",
        "meaning": "Biển báo yêu cầu phương tiện đi về phía bên phải theo hướng chỉ dẫn.",
        "short_answer": "Đây là biển bắt buộc đi bên phải.",
        "prohibited_actions": ["đi sai hướng chỉ dẫn"],
        "allowed_actions": ["đi về bên phải"],
        "speed_limit": None,
    },

    "p3": {
        "code": "p3",
        "name_vi": "Cấm xe khách lớn đi vào",
        "name_en": "No large passenger vehicles",
        "group": "Biển cấm",
        "meaning": "Biển báo cấm xe khách lớn đi vào khu vực hoặc đoạn đường có đặt biển.",
        "short_answer": "Đây là biển cấm xe khách lớn đi vào.",
        "prohibited_actions": ["xe khách lớn đi vào"],
        "allowed_actions": ["phương tiện không thuộc nhóm bị cấm có thể đi nếu không có biển cấm khác"],
        "speed_limit": None,
    },

    "ph": {
        "code": "ph",
        "name_vi": "Hạn chế chiều cao",
        "name_en": "Height limit",
        "group": "Biển hạn chế",
        "meaning": "Biển báo giới hạn chiều cao tối đa của phương tiện được phép đi qua.",
        "short_answer": "Đây là biển hạn chế chiều cao.",
        "prohibited_actions": ["phương tiện vượt quá chiều cao cho phép đi qua"],
        "allowed_actions": ["phương tiện có chiều cao nằm trong giới hạn được phép đi qua"],
        "speed_limit": None,
    },

    "pl20": {
        "code": "pl20",
        "name_vi": "Giới hạn tốc độ 20 km/h",
        "name_en": "Speed limit 20 km/h",
        "group": "Biển giới hạn tốc độ",
        "meaning": "Biển báo quy định tốc độ tối đa cho phép là 20 km/h.",
        "short_answer": "Đây là biển giới hạn tốc độ 20 km/h.",
        "prohibited_actions": ["chạy quá 20 km/h"],
        "allowed_actions": ["chạy với tốc độ không vượt quá 20 km/h"],
        "speed_limit": 20,
    },

    "pl30": {
        "code": "pl30",
        "name_vi": "Giới hạn tốc độ 30 km/h",
        "name_en": "Speed limit 30 km/h",
        "group": "Biển giới hạn tốc độ",
        "meaning": "Biển báo quy định tốc độ tối đa cho phép là 30 km/h.",
        "short_answer": "Đây là biển giới hạn tốc độ 30 km/h.",
        "prohibited_actions": ["chạy quá 30 km/h"],
        "allowed_actions": ["chạy với tốc độ không vượt quá 30 km/h"],
        "speed_limit": 30,
    },

    "pl40": {
        "code": "pl40",
        "name_vi": "Giới hạn tốc độ 40 km/h",
        "name_en": "Speed limit 40 km/h",
        "group": "Biển giới hạn tốc độ",
        "meaning": "Biển báo quy định tốc độ tối đa cho phép là 40 km/h.",
        "short_answer": "Đây là biển giới hạn tốc độ 40 km/h.",
        "prohibited_actions": ["chạy quá 40 km/h"],
        "allowed_actions": ["chạy với tốc độ không vượt quá 40 km/h"],
        "speed_limit": 40,
    },

    "pl50": {
        "code": "pl50",
        "name_vi": "Giới hạn tốc độ 50 km/h",
        "name_en": "Speed limit 50 km/h",
        "group": "Biển giới hạn tốc độ",
        "meaning": "Biển báo quy định tốc độ tối đa cho phép là 50 km/h.",
        "short_answer": "Đây là biển giới hạn tốc độ 50 km/h.",
        "prohibited_actions": ["chạy quá 50 km/h"],
        "allowed_actions": ["chạy với tốc độ không vượt quá 50 km/h"],
        "speed_limit": 50,
    },

    "pl80": {
        "code": "pl80",
        "name_vi": "Giới hạn tốc độ 80 km/h",
        "name_en": "Speed limit 80 km/h",
        "group": "Biển giới hạn tốc độ",
        "meaning": "Biển báo quy định tốc độ tối đa cho phép là 80 km/h.",
        "short_answer": "Đây là biển giới hạn tốc độ 80 km/h.",
        "prohibited_actions": ["chạy quá 80 km/h"],
        "allowed_actions": ["chạy với tốc độ không vượt quá 80 km/h"],
        "speed_limit": 80,
    },

    "pl90": {
        "code": "pl90",
        "name_vi": "Giới hạn tốc độ 90 km/h",
        "name_en": "Speed limit 90 km/h",
        "group": "Biển giới hạn tốc độ",
        "meaning": "Biển báo quy định tốc độ tối đa cho phép là 90 km/h.",
        "short_answer": "Đây là biển giới hạn tốc độ 90 km/h.",
        "prohibited_actions": ["chạy quá 90 km/h"],
        "allowed_actions": ["chạy với tốc độ không vượt quá 90 km/h"],
        "speed_limit": 90,
    },
}


def normalize_class_name(class_name):
    """
    Chuẩn hóa tên class đầu vào.

    Ví dụ:
    - "PL40" -> "pl40"
    - " pl40 " -> "pl40"
    """
    if class_name is None:
        return None

    return str(class_name).strip().lower()


def get_sign_info(class_name):
    """
    Lấy toàn bộ thông tin của một biển báo theo class name.

    Args:
        class_name (str): mã class, ví dụ: "pl40", "pn", "pne"

    Returns:
        dict | None: thông tin biển báo nếu có, None nếu không tìm thấy
    """
    class_name = normalize_class_name(class_name)
    return SIGN_INFO.get(class_name)


def get_sign_name(class_name):
    """
    Trả về tên tiếng Việt của biển báo.
    """
    info = get_sign_info(class_name)

    if info is None:
        return "Không xác định"

    return info["name_vi"]


def get_sign_meaning(class_name):
    """
    Trả về ý nghĩa của biển báo.
    """
    info = get_sign_info(class_name)

    if info is None:
        return "Chưa có dữ liệu giải thích cho biển báo này."

    return info["meaning"]


def get_sign_group(class_name):
    """
    Trả về nhóm biển báo.
    """
    info = get_sign_info(class_name)

    if info is None:
        return "Không xác định"

    return info["group"]


def get_speed_limit(class_name):
    """
    Trả về tốc độ giới hạn nếu biển báo là biển tốc độ.

    Returns:
        int | None
    """
    info = get_sign_info(class_name)

    if info is None:
        return None

    return info.get("speed_limit")


def explain_sign(class_name):
    """
    Sinh câu giải thích đầy đủ cho một biển báo.
    """
    info = get_sign_info(class_name)

    if info is None:
        return f"Chưa có thông tin giải thích cho class '{class_name}'."

    return (
        f"{info['name_vi']} ({info['code']}): "
        f"thuộc nhóm {info['group']}. "
        f"{info['meaning']}"
    )


def explain_detected_signs(class_names):
    """
    Giải thích danh sách biển báo đã phát hiện.

    Args:
        class_names (list[str]): danh sách mã class detect được

    Returns:
        str: nội dung giải thích
    """
    if not class_names:
        return "Không phát hiện được biển báo trong ảnh hoặc video."

    unique_classes = []

    for cls in class_names:
        cls = normalize_class_name(cls)
        if cls not in unique_classes:
            unique_classes.append(cls)

    explanations = []

    for cls in unique_classes:
        explanations.append(explain_sign(cls))

    return "\n".join(explanations)


def is_speed_limit_sign(class_name):
    """
    Kiểm tra class có phải biển giới hạn tốc độ không.
    """
    info = get_sign_info(class_name)

    if info is None:
        return False

    return info.get("speed_limit") is not None


def is_prohibited_action(class_name, action):
    """
    Kiểm tra một hành động có bị cấm bởi biển báo hay không.

    Args:
        class_name (str): mã class biển báo
        action (str): hành động cần kiểm tra, ví dụ "đỗ xe", "bấm còi"

    Returns:
        bool
    """
    info = get_sign_info(class_name)

    if info is None:
        return False

    action = str(action).strip().lower()

    for prohibited_action in info.get("prohibited_actions", []):
        if action in prohibited_action.lower() or prohibited_action.lower() in action:
            return True

    return False


def get_all_supported_classes():
    """
    Trả về danh sách các class đang được hỗ trợ.
    """
    return list(SIGN_INFO.keys())


def print_supported_classes():
    """
    In ra danh sách class và tên biển báo.
    Dùng để kiểm tra nhanh.
    """
    print("Danh sách biển báo đang hỗ trợ:")
    print("=" * 50)

    for code, info in SIGN_INFO.items():
        print(f"{code:5s} | {info['name_vi']} | {info['group']}")

DISPLAY_NAMES = {
    "pn": "Cam do xe",
    "pne": "Cam di vao",
    "p11": "Cam bam coi",
    "p26": "Cam xe tai di vao",
    "i2": "Duong danh cho xe khong dong co",
    "i4": "Duong danh cho xe co gioi",
    "i5": "Di ben phai",
    "p3": "Cam xe khach lon di vao",
    "ph": "Han che chieu cao",
    "pl20": "Gioi han toc do 20 km/h",
    "pl30": "Gioi han toc do 30 km/h",
    "pl40": "Gioi han toc do 40 km/h",
    "pl50": "Gioi han toc do 50 km/h",
    "pl80": "Gioi han toc do 80 km/h",
    "pl90": "Gioi han toc do 90 km/h",
}


def get_display_name(class_name, use_vietnamese=False):
    """
    Trả về tên hiển thị của biển báo.

    use_vietnamese=False:
        Dùng tên không dấu để vẽ lên video bằng OpenCV.

    use_vietnamese=True:
        Dùng tên tiếng Việt có dấu, phù hợp cho phần text QA.
    """
    info = get_sign_info(class_name)

    if info is None:
        return str(class_name)

    class_name = normalize_class_name(class_name)

    if use_vietnamese:
        return info["name_vi"]

    return DISPLAY_NAMES.get(class_name, info["name_vi"])

if __name__ == "__main__":
    print_supported_classes()

    print("\nVí dụ giải thích:")
    print(explain_sign("pl40"))

    print("\nVí dụ danh sách biển detect được:")
    print(explain_detected_signs(["pl40", "pn", "pne"]))