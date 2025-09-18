from PIL import Image
from io import BytesIO
import base64


def frame(frame_path: str, image: str) -> str:
    """
    Superimpose a picture inside a border frame.
    
    :param border_path: Path to the border image (your uploaded frame)
    :param picture_path: Path to the picture to insert
    :param output_path: Path to save the result
    """
    # Open border and picture
    border = Image.open(frame_path).convert("RGBA")

    # Decode base64 string to bytes
    image_data = base64.b64decode(image)
    # Convert to a BytesIO stream
    image_bytes = BytesIO(image_data)

    # Open image with Pillow
    img = Image.open(image_bytes).convert("RGBA")

    # Resize picture to fit inside border (with some margin)
    border_w, border_h = border.size
    margin_h = int(border_h * 0.071)  # 10% margin inside
    margin_w = int(border_w * 0.051)  # 10% margin inside
    new_w = border_w - 2 * margin_w
    new_h = border_h - int(3.3 * margin_h)

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Paste picture onto border (centered)
    border_copy = border.copy()
    border_copy.paste(img, (margin_w, margin_h), img)

    framed_bytes = BytesIO()
    border_copy.save(framed_bytes, format="PNG")
    framed_bytes.seek(0)

    # Save result
    return base64.b64encode(framed_bytes.read()).decode()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("frame_path")
    parser.add_argument("image_path")

    args = parser.parse_args()

    with open(args.image_path) as img:
        image = frame(args.frame_path, img.read())

    print(image)

