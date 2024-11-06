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
# df = pd.DataFrame(data)
# df.tail()
# data.tail()
df = data.tail(5)

def render_latex_to_image(latex_string, filename):
    fig = plt.figure(figsize=(4,0.5))
    text = fig.text(x=0.5, y=0.5, s=latex_string, fontsize=11, ha='center', va='center')
    fig.savefig(filename, dpi=300, pad_inches=0.03, bbox_inches='tight')
    plt.close(fig)

def wrap_text(text, max_width):
    words = text.split()
    lines = []
    current_line = words[0]
    for word in words[1:]:
        if stringWidth(current_line + " " + word, "Helvetica", 10) < max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines
def create_pdf_with_latex(df, filename= "outputfff.pdf"):
    
    #Set the canvas
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Layout Setting
    left_margin = 50
    top_margin = height - 50
    line_spacing = 20
    max_line_width = 575

    for index, row in df.iterrows():
        y_position = top_margin

        for col,value in row.items():
            text = f"{col}:{value}"
            lines = wrap_text(text, max_line_width)

            # Iterate for LateX Eqn.
            for line in lines:
                latex_match = re.findall(r'\$(.*?)\$', line)
                if latex_match:
                    x_position = left_margin
                    for eqn in latex_match:
                        eqn_pos = line.find(f"${eqn}$")
                        prefix_text = line[:eqn_pos]

                        # Draw text Upto the equation
                        c.drawString(x_position, y_position, prefix_text)
                        x_position += stringWidth(prefix_text, 'Helvetica', 10)

                        # Render Latex Equation and save as image file
                        latex_image_path = os.path.join(latex_image_dir, f"latex_{index}.png")
                        if not os.path.exists(latex_image_path): # Avoid generating exixting image
                            wrapped_equation = f"""${eqn}$"""
                            render_latex_to_image(wrapped_equation, latex_image_path)

                        # Insert the saved Latex Image into the PDF
                        c.drawImage(latex_image_path, x_position + 40 , y_position - 10, width=70, height=30)

                        # Continue after equation
                        remaining_text = line[eqn_pos + len(eqn) + 2:]
                        next_pos = left_margin + stringWidth(prefix_text, 'Helvetica', 10) + 55 
                        c.drawString(next_pos, y_position, remaining_text)

                else:
                    # Draw Text Without Latex
                    c.drawString(left_margin, y_position, line)

                y_position -= line_spacing # Move for next line

            y_position -= line_spacing # Extra space after each row
        c.showPage()# For each row new page

    c.save()
    

create_pdf_with_latex(df)
