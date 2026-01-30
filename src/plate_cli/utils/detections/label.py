from ultralytics.engine.results import Results


def get_label(text: str, result: Results) -> str:
    if not result.boxes:
        return ""

    conf = float(result.boxes.conf[0])
    class_id = int(result.boxes[0].cls.item())
    class_name = result.names[class_id]
    label = f"{class_name}: {text} ({conf:.2f})"
    return label
