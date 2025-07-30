import os
import cv2
import pytesseract
from pytesseract import Output
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from textwrap3 import wrap
from typing import List

# Set Tesseract OCR path
# For Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class TextExtractor:
    def __init__(self, image_path: str):
        self.image_path = image_path

    def preprocess_image(self, img):
        # Denoise the image using GaussianBlur
        denoised_img = cv2.GaussianBlur(img, (3, 3), 0)

        # Enhance the contrast of the image
        gray = cv2.cvtColor(denoised_img, cv2.COLOR_BGR2GRAY)
        equalized_img = cv2.equalizeHist(gray)

        return equalized_img

    def find_horizontal_lines(self):
        img = cv2.imread(self.image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply threshold
        thresh = cv2.threshold(
            gray, 30, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        # Define the horizontal structure
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (200, 1))
        line_locations = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

        return line_locations

    def page_segmentation(self, img, w, df_SegmentLocations):
        img = cv2.imread(img)
        segments = []

        for i in range(len(df_SegmentLocations)):
            y = df_SegmentLocations['SegmentStart'][i]
            h = df_SegmentLocations['Height'][i]
            cropped = img[y:y + h, 0:w]

            if cropped.size != 0:
                segments.append(cropped)

        return segments

    def extract_text_from_img(self, segment):
        text = pytesseract.image_to_string(segment, lang='eng')
        text = text.encode("utf-8", 'ignore').decode("utf-8", "ignore")
        return text

    def extract_handwritten_segments(self):
        line_locations = self.find_horizontal_lines()
        if line_locations is None or line_locations.size == 0:
            print("No lines found in the image.")
            return []

        df_line_locations = pd.DataFrame(
            line_locations.sum(axis=1), dtype='object'
        ).reset_index()
        df_line_locations.columns = ['rowLoc', 'LineLength']
        df_line_locations['line'] = 0
        df_line_locations.loc[df_line_locations['LineLength'] > 100, 'line'] = 1
        df_line_locations['cumSum'] = df_line_locations['line'].cumsum()

        if df_line_locations['line'].sum() == 0:
            print("No segments found.")
            return []

        df_SegmentLocations = df_line_locations[df_line_locations['line'] == 0].groupby('cumSum').agg(
            SegmentOrder=('rowLoc', lambda x: x.index.min() + 1),
            SegmentStart=('rowLoc', 'min'),
            Height=('rowLoc', lambda x: x.max() - x.min())
        ).reset_index()

        img = cv2.imread(self.image_path)
        if img is None:
            print(f"Failed to read image at '{self.image_path}'.")
            return []

        w = line_locations.shape[1]
        segments = self.page_segmentation(self.image_path, w, df_SegmentLocations)
        handwritten_segments = []

        for segment in segments:
            text = self.extract_text_from_img(segment)
            if text.strip():
                handwritten_segments.append({
                    'segment': segment,
                    'text': text.strip()
                })

        return handwritten_segments

    def save_extracted_data(self, handwritten_segments, output_file):
        with open(output_file, 'w') as file:
            for i, segment_data in enumerate(handwritten_segments):
                segment_text = segment_data['text']
                wrapped_text = wrap(segment_text, 30)
                file.write(f"Segment {i+1} Handwritten Text:\n")
                file.write('\n'.join(wrapped_text))
                file.write('\n\n')

            print(f"Extracted data saved to '{output_file}'")

        return None

if __name__ == "__main__":
    # Usage example
    image_path = './test_images/sample_image.jpg'
    text_extractor = TextExtractor(image_path)
    handwritten_segments = text_extractor.extract_handwritten_segments()

    for i, segment_data in enumerate(handwritten_segments):
        segment = segment_data['segment']
        text = segment_data['text']

        # Plot the segment and text
        fig = plt.figure(figsize=(12, 6))
        gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
        ax0 = plt.subplot(gs[0])
        ax0.imshow(segment)
        ax0.set_title(f"Segment {i+1}")
        ax1 = plt.subplot(gs[1])
        ax1.text(0.1, 0.5, "\n".join(wrap(text, 30)), fontsize=12)
        ax1.axis('off')
        ax1.set_title("Extracted Text")
        plt.tight_layout()
        plt.show()

    output_file = './extracted_data/extracted_data.txt'
    text_extractor.save_extracted_data(handwritten_segments, output_file)
