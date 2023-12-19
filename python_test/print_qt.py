from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt

def print_jpg(filename):
    # Load the image
    image = QImage(filename)
    if image.isNull():
        raise Exception("Unable to load image.")

    # Create Printer object
    printer = QPrinter()
    printer.setPrinterName("Your_Printer_Name")  # Set your printer's name
    printer.setOrientation(QPrinter.Portrait)
    printer.setResolution(300)  # Set resolution
    printer.setPaperSize(QPrinter.A4)  # Set paper size

    # Create QPainter object
    painter = QPainter()
    painter.begin(printer)

    # Scaling the image to fit on the printer page
    rect = painter.viewport()
    size = image.size()
    size.scale(rect.size(), Qt.KeepAspectRatio)
    painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
    painter.setWindow(image.rect())

    # Draw the image
    painter.drawImage(0, 0, image)

    # End the print job
    painter.end()

# Usage
print_jpg("path_to_your_image.jpg")