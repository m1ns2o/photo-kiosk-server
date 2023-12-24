import subprocess
import os

import win32print
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(image_path, output_pdf_path, page_size=letter):
    # 이미지를 PDF로 변환
    img_width, img_height = letter
    c = canvas.Canvas(output_pdf_path, pagesize=page_size)
    c.drawImage(image_path, 0, 0, width=img_width, height=img_height)
    c.save()

def print_pdf(pdf_path, printer_name=None):
    # PDF를 인쇄
    printer_name = printer_name or win32print.GetDefaultPrinter()

    if os.name == 'nt':  # Windows 환경에서만 사용
        print_command = f'AcroRd32.exe /t "{pdf_path}" "{printer_name}"'
        subprocess.run(print_command, shell=True)
    else:
        pass

if __name__ == "__main__":
    image_path = "print_img.jpg"
    output_pdf_path = "output.pdf"

    create_pdf(image_path, output_pdf_path)

    # 인쇄할 때 프린터 이름을 지정하려면 print_pdf 함수의 두 번째 매개변수에 프린터 이름을 전달합니다.
    # 예: print_pdf(output_pdf_path, "Your_Printer_Name")
    print_pdf(output_pdf_path)