import PyPDF2
import sys
import os
from reportlab.pdfgen import canvas

lines_filename = "lines.pdf"
lines_img = "lines_v2.png"
pdf_xscale = 1.75
add_lines = True

def resize_from_gui(in_filepath, in_scale = 1.75, in_use_lines = True):
    global pdf_xscale, add_lines
    pdf_xscale = in_scale
    add_lines = in_use_lines
    return resize_pdf(in_filepath)


def get_lines_enabled_input():
    use_lines = input("Add Writing Lines? (Y/N) (Default = Yes)")
    if use_lines.lower() == "y" or use_lines == "yes":
        return True
    elif use_lines.lower() == "n" or use_lines == "no":
        return False
    else:
        return True


def get_scale_input(default_scale=1.75):
    try:
        scale_input = input(f"Enter scale of the lines(default {(default_scale - 1) * 100}): ")
        scale = float(scale_input) / 100.0 + 1.0
        return float(scale) if scale else default_scale
    except ValueError:
        print("Skipped input. Using default scale.")
        return default_scale

def extend_pdf_with_image(original_pdf_path, output_pdf_path, scale_factor=1.75):
    if add_lines:
        reader = PyPDF2.PdfReader(original_pdf_path)
        first_page = reader.pages[0]
        page_width = first_page.mediabox.upper_right[0]
        page_height = first_page.mediabox.upper_right[1]
        page_width_extended = page_width * scale_factor

        # Create a watermark PDF
        # output_pdf_filename = os.path.join(output_pdf_path, "lines_generated.pdf")
        output_pdf_path = "watermark.pdf"
        c = canvas.Canvas(output_pdf_path, pagesize=(page_width_extended, page_height))

        app_path = get_script_dir()
        image_path = os.path.join(app_path, lines_img)
        image_desired_width = page_width_extended - page_width
        image_desired_width = image_desired_width - 10

        # Add the watermark image to the bottom-right corner of the page
        c.drawImage(image_path, x=page_width, y=0, width=image_desired_width, anchor='se')
        c.showPage()
        c.save()

        return output_pdf_path
    else:
        return ""

def get_script_dir():
    """Get the directory where the script or executable resides."""
    if getattr(sys, 'frozen', False):
        # The application is frozen (compiled as exe)
        return os.path.dirname(sys.executable)
    else:
        # The application is not frozen (running as .py script)
        return os.path.dirname(__file__)

def resize_pdf(file_path):

    directory, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(directory, f"{name}_wide{ext}")

    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        watermark_path = extend_pdf_with_image(file_path, output_path, pdf_xscale)
        # print(f"watermark generated: {watermark_path}")

        # Apply the new size to all pages
        for page in reader.pages:

            pixels_right = float(page.mediabox.right) * pdf_xscale
            page.mediabox.upper_right = (pixels_right, page.mediabox.top)

            # Add the modified page to the writer. Handle error if lines.pdf is missing.
            if add_lines:
                try:
                    watermark_reader =  PyPDF2.PdfReader(watermark_path)
                    watermark_page = watermark_reader.pages[0]
                    page.merge_page(watermark_page, False)
                except FileNotFoundError:
                    # Handle the case where the watermark file is not found
                    print(f"Error: Watermark file '{watermark_path}' not found in {get_script_dir()}.")
                    input("Press Enter to exit...")
                    sys.exit(1)
                except Exception as e:
                    # Handle other potential errors
                    print(f"An unknown error occurred: {e}")
                    input("Press Enter to exit...")
                    sys.exit(1)

            writer.add_page(page)

        # Save the new PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            print(f"Created File: {output_path}")
            return output_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Loop through each file dropped onto the EXE
        pdf_xscale = get_scale_input()
        add_lines = get_lines_enabled_input()
        if (add_lines):
            print("Adding Lines to PDF")
        else:
            print("Skipping Lines")

        for file_path in sys.argv[1:]:
            resize_pdf(file_path)
        print("All Files processed successfully")
    else:
        print("Please drag and drop a PDF file onto the executable.")
        input("Press Enter to exit...")