# A captcha solver for number captchas

## `pip install simplecaptchasolver`

### Converts this kind of capture

![](https://github.com/hansalemaos/simplecaptchasolver/blob/main/captcha.jpg?raw=true)

### into

![](https://github.com/hansalemaos/simplecaptchasolver/blob/main/captcha2.jpg?raw=true)

### and performs a OCR

### How to use

```py
from simplecaptchasolver import adjust_and_ocr
import cv2

# adjust_and_ocr(
#     img: Any,
#     thresh: int = 150,
#     maxval: int = 255,
#     cv2_type: int = cv2.THRESH_BINARY_INV,
#     noise_width: int = 5,
#     noise_height: int = 5,
# ) -> str:
#     """
#     Perform the following steps:
#     1. Read the image (any format that can be read by PIL or OpenCV)
#     2. Convert the image to grayscale
#     3. Apply a binary threshold to the grayscale image using OpenCV's `cv2.threshold` with the given arguments
#     4. Find contours using OpenCV's `cv2.findContours` and sort them by x-coordinate
#     5. Create a new image with the same shape as the original, and iterate over the contours
#     6. For each contour, if its width and height are both greater than the given noise width and height, copy the corresponding region from the original image to the new image, and increment the x-coordinate by the contour's width
#     7. OCR the new image using EasyOCR and return the text

#     :param img: The image to process
#     :param thresh: The value to use for the binary threshold
#     :param maxval: The maximum value to use for the binary threshold
#     :param cv2_type: The type of thresholding to use (see OpenCV's `cv2.threshold` documentation)
#     :param noise_width: The minimum width of a contour to consider it not noise
#     :param noise_height: The minimum height of a contour to consider it not noise
#     :return: The text that was extracted from the image
#     """

text=adjust_and_ocr(
    img="https://github.com/hansalemaos/simplecaptchasolver/blob/main/captcha.jpg?raw=true",
    thresh=150,
    maxval=255,
    cv2_type=cv2.THRESH_BINARY_INV,
    noise_width=5,
    noise_height=5,
)
print(text)
# 03361885
```

