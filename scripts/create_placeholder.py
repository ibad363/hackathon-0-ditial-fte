from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "default_post_image.png")

def create_placeholder():
    img = Image.new("RGB", (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    text = "New Post"
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (1080 - text_w) // 2
    y = (1080 - text_h) // 2

    draw.text((x, y), text, fill=(0, 0, 0), font=font)

    output = os.path.abspath(OUTPUT_PATH)
    img.save(output)
    print(f"Saved: {output}")

if __name__ == "__main__":
    create_placeholder()
