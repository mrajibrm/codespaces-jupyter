import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
import re

# Set up LaTeX rendering options for matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
pdfmetrics.registerFont(TTFont("Lato","fonts/Lato-Regular.ttf"))
latex_image_dir = "latex_eqn_images"
os.makedirs(latex_image_dir, exist_ok=True)

# Load data from CSV file and select the last 5 rows
data = pd.read_csv("QUE4.csv")

# Function to render LaTeX string as an image file
def render_latex_to_image(latex_string, filename, img_width=75):
    fig = plt.figure(figsize=(img_width/100, 0.5))
    fig.text(x=0.5, y=0.5, s=latex_string, fontsize=14, ha='center', va='center')
    fig.savefig(filename, dpi=500, pad_inches=0.03, bbox_inches='tight')
    plt.close(fig)

# Function to wrap text into lines that fit within a specified width
def wrap_text(text, max_width):
    words = re.split(r'(\$.*?\$)', text)
    lines = []
    current_line = ""

    for word in words:
        if re.match(r'\$.*?\$', word):
            if current_line:
                lines.append(current_line.strip())
                current_line = ""
            lines.append(word)
        else:
            for sub_word in word.split():
                if stringWidth(current_line + " " + sub_word, "Lato", 16) < max_width:
                    current_line += " " + sub_word
                else:
                    lines.append(current_line.strip())
                    current_line = sub_word
    if current_line:
        lines.append(current_line.strip())
    
    return lines

# Function to draw a justified string
def draw_justified_string(c, text, x_position, y_position, max_line_width, font_name="Lato", font_size=16):
    words = text.split()
    space_width = stringWidth(" ", font_name, font_size)
    line_width = sum(stringWidth(word, font_name, font_size) for word in words) + space_width * (len(words) - 1)
    
    if line_width >= max_line_width or len(words) == 1:
        c.drawString(x_position, y_position, text)
        return

    extra_space = (max_line_width - line_width) / (len(words) - 1)
    x = x_position

    for word in words:
        c.drawString(x, y_position, word)
        x += stringWidth(word, font_name, font_size) + space_width + extra_space

# Main function to create PDF with justified text for 'question name' column
def create_pdf_with_latex(df, filename="output_fixed_wrap_text_and_LaTeX_Eqn_increased_font.pdf"):
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = landscape(letter)
    c.setFont("Lato", 16)

    left_margin = 50
    top_margin = height - 50
    line_spacing = 30
    max_line_width = width - 2 * left_margin
    min_y_position = 50

    for index, row in df.iterrows():
        y_position = top_margin

        for col, value in row.items():
            text = f"{col}: {value}"
            lines = wrap_text(text, max_line_width)
            x_position = left_margin

            for line in lines:
                if y_position <= min_y_position:
                    c.showPage()
                    y_position = top_margin
                    x_position = left_margin

                if col == "question name":
                    draw_justified_string(c, line, x_position, y_position, max_line_width)
                elif re.match(r'\$.*?\$', line):
                    latex_image_path = os.path.join(latex_image_dir, f"latex_{index}.png")
                    if not os.path.exists(latex_image_path):
                        render_latex_to_image(line, latex_image_path, img_width=70)

                    image_width = 70
                    if x_position + image_width <= max_line_width:
                        c.drawImage(latex_image_path, x_position + 40, y_position - 10, width=image_width, height=30)
                        x_position += image_width + 45
                    else:
                        y_position -= line_spacing
                        x_position = left_margin
                        c.drawImage(latex_image_path, x_position, y_position - 10, width=image_width, height=30)
                        x_position += image_width + 5
                else:
                    line_width = stringWidth(line, "Lato", 16)
                    if x_position + line_width <= max_line_width:
                        c.drawString(x_position, y_position, line)
                        x_position += line_width + 5
                    else:
                        y_position -= line_spacing
                        x_position = left_margin
                        c.drawString(x_position, y_position, line)
                        x_position += line_width + 5

            y_position -= line_spacing
        c.showPage()
        c.setFont("Lato", 16) #Reset font for new Page 

    c.save()

# Run the function to create PDF
create_pdf_with_latex(data)
