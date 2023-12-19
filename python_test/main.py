from PIL import Image, ImageWin, ImageOps
import win32print
import win32ui

# Path to your image
image_path = 'print_img.jpg'

# Open the image with Pillow
image = Image.open(image_path)
# new_width = 6
# new_height = 4
# aspect_ratio = new_width / new_height
#
# original_width, original_height = image.size
# original_aspect = original_width / original_height
#
# if original_aspect > aspect_ratio:
#     # Original image is wider than 6:4
#     new_height = int(new_width / original_aspect)
# else:
#     # Original image is taller than 6:4
#     new_width = int(new_height * original_aspect)
# image = image.resize((new_width, new_height), Image.LANCZOS)

DPI = 300

target_size = (4 * DPI, 6 * DPI)
# Resize the image

image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)


# Get default printer
printer_name = win32print.GetDefaultPrinter()

# Start a print job
hprinter = win32print.OpenPrinter(printer_name)
printer_info = win32print.GetPrinter(hprinter, 2)
pdc = win32ui.CreateDC()
pdc.CreatePrinterDC(printer_name)
pdc.StartDoc(image_path)
pdc.StartPage()

# Print the image
dib = ImageWin.Dib(image)
width, height = image.size
dib.draw(pdc.GetHandleOutput(), (0, 0, width, height))

pdc.EndPage()
pdc.EndDoc()
pdc.DeleteDC()