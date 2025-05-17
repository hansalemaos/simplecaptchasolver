import cv2
import numpy as np
import easyocr
import base64
import re
import shutil
import tempfile
from functools import partial
from typing import Any, Union
import requests
import cv2
import numpy as np
import os
from touchtouch import touch
from PIL import Image
from tolerant_isinstance import isinstance_tolerant

reader = easyocr.Reader(["en"])


def _dummy_import():
    import torch


def get_tmpfile(suffix=".txt"):
    tfp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    filename = tfp.name
    filename = os.path.normpath(filename)
    tfp.close()
    return filename, partial(os.remove, tfp.name)


def save_cv_image(filepath: str, image: np.ndarray) -> str:
    format_ = filepath.split(".")[-1]
    filenametmp, deletefilename = get_tmpfile(suffix=f".{format_}")
    touch(path=filepath)
    touch(path=filenametmp)
    os.remove(filepath)
    cv2.imwrite(filenametmp, image)
    shutil.move(filenametmp, filepath)
    return filepath


def open_image_in_cv(
    image: Any, channels_in_output: Union[int, None] = None, bgr_to_rgb: bool = False
) -> np.ndarray:
    if isinstance(image, str):
        if os.path.exists(image):
            if os.path.isfile(image) or os.path.islink(image):
                try:
                    image2 = cv2.imread(image, cv2.IMREAD_UNCHANGED)
                    if isinstance_tolerant(image2, None):
                        image = np.array(Image.open(image))
                        bgr_to_rgb = not bgr_to_rgb
                    else:
                        image = image2
                except Exception:
                    try:
                        format_ = image.split(".")[-1]
                        filenametmp, deletefilename = get_tmpfile(suffix=f".{format_}")
                        try:
                            deletefilename()
                        except Exception:
                            pass
                        shutil.copy(image, filenametmp)
                        image = cv2.imread(filenametmp, cv2.IMREAD_UNCHANGED)
                        try:
                            deletefilename()
                        except Exception:
                            pass
                    except Exception:
                        image = np.array(Image.open(image))
                        bgr_to_rgb = not bgr_to_rgb

        elif re.search(r"^.{1,10}://", str(image)[:12]) is not None:
            x = requests.get(image).content
            if x.startswith(bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])):
                filenametmp, deletefilename = get_tmpfile(suffix=f".png")
                with open(filenametmp, mode="wb") as f:
                    f.write(x)
                image = cv2.imread(filenametmp, cv2.IMREAD_UNCHANGED)
                try:
                    deletefilename()
                except Exception:
                    pass
            else:
                image = cv2.imdecode(np.frombuffer(x, np.uint8), cv2.IMREAD_COLOR)
        else:
            try:
                image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
            except Exception:
                image = cv2.imdecode(
                    np.frombuffer(
                        base64.b64decode(image.split(",", maxsplit=1)[-1]), np.uint8
                    ),
                    cv2.IMREAD_COLOR,
                )
    elif isinstance(image, (bytes, bytearray)):
        image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
    elif "PIL" in str(type(image)):
        image = np.array(image)
        bgr_to_rgb = not bgr_to_rgb

    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    if bgr_to_rgb:
        if len(image.shape) > 2:
            if image.shape[-1] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            elif image.shape[-1] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if channels_in_output is not None:
        if len(image.shape) > 2:
            if image.shape[-1] == 4 and channels_in_output == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
            elif image.shape[-1] == 3 and channels_in_output == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            if image.shape[-1] == 4 and channels_in_output == 2:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
            elif image.shape[-1] == 3 and channels_in_output == 2:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                pass
        else:
            if channels_in_output == 3 and len(image.shape) < 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            if channels_in_output == 4 and len(image.shape) < 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)

    return image


def adjust_and_ocr(
    img: Any,
    thresh: int = 150,
    maxval: int = 255,
    cv2_type: int = cv2.THRESH_BINARY_INV,
    noise_width: int = 5,
    noise_height: int = 5,
) -> str:
    image = open_image_in_cv(img, channels_in_output=3)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, thresh, maxval, cv2_type)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
    image_copy = np.zeros_like(image)
    image_copy[:] = 255
    start_x = 1
    for ctr in sorted_contours:
        x, y, w, h = cv2.boundingRect(ctr)
        if w > noise_width and h > noise_height:
            image_copy[:h, start_x : start_x + w] = image[y : y + h, x : x + w]
            start_x += w
            start_x += 1

    result = reader.readtext(image_copy, detail=0)
    return result[0] if result else ""
