import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
import re

matplotlib.rcParams['mathtext.fontset'] = 'stix'
latex_image_dir = "latex_images"
os.makedirs(latex_image_dir, exist_ok=True)

data = pd.read_csv("QUE4.csv")
df = data.tail(5)  # Take the last 5 rows of the dataframe

def render_latex_to_image(latex_string, filename, img_width=50):
    fig = plt.figure(figsize=(img_width/100, 0.5))
    fig.text(x=0.5, y=0.5, s=latex_string, fontsize=11, ha='center', va='center')
    fig.savefig(filename, dpi=300, pad_inches=0.03, bbox_inches='tight')
    plt.close(fig)

def wrap_text(text, max_width):
    words = re.split(r'(\$.*?\$)', text)  # Split by LaTeX equations
    lines = []
    current_line = ""
    
    for word in words:
        if re.match(r'\$.*?\$', word):  # If it's a LaTeX equation
            if current_line:  # Add the current line if it has content
                lines.append(current_line.strip())
                current_line = ""
            lines.append(word)  # Treat the equation as a separate line
        else:  # Regular text
            if stringWidth(current_line + " " + word, "Helvetica", 10) < max_width:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word
    if current_line:
        lines.append(current_line.strip())
    
    return lines

def create_pdf_with_latex(df, filename="output3fff.pdf"):
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = landscape(letter)

    left_margin = 50
    top_margin = height - 50
    line_spacing = 30
    max_line_width = 575

    for index, row in df.iterrows():
        y_position = top_margin

        for col, value in row.items():
            text = f"{col}: {value}"
            lines = wrap_text(text, max_line_width)
            x_position = left_margin  # Track position within line width

            for line in lines:
                if re.match(r'\$.*?\$', line):  # If line is a LaTeX equation
                    # Render LaTeX to image and calculate width
                    latex_image_path = os.path.join(latex_image_dir, f"latex_{index}.png")
                    if not os.path.exists(latex_image_path):
                        render_latex_to_image(line, latex_image_path, img_width=70)

                    image_width = 70
                    if x_position + image_width <= max_line_width:
                        # Draw image on the same line if space allows
                        c.drawImage(latex_image_path, x_position+40, y_position - 10, width=image_width, height=30)
                        x_position += image_width + 45  # Adjust x-position
                    else:
                        # Start a new line if image doesn't fit
                        y_position -= line_spacing
                        x_position = left_margin
                        c.drawImage(latex_image_path, x_position, y_position - 10, width=image_width, height=30)
                        x_position += image_width + 5

                else:
                    line_width = stringWidth(line, "Helvetica", 10)
                    if x_position + line_width <= max_line_width:
                        # Draw text on the same line if space allows
                        c.drawString(x_position, y_position, line)
                        x_position += line_width + 5  # Adjust x-position
                    else:
                        # Start a new line if text doesn't fit
                        y_position -= line_spacing
                        x_position = left_margin
                        c.drawString(x_position, y_position, line)
                        x_position += line_width + 5

            y_position -= line_spacing  # Extra space after each row
        c.showPage()  # Start a new page for each row

    c.save()

create_pdf_with_latex(df)
