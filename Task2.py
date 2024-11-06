import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import ParagraphStyle

# Defined a function 
def generate_pdf_from_csv(csv_file, output_pdf):
    
    # Used pandas to read the file
    df = pd.read_csv(csv_file)
    
    # Created a document
    doc = SimpleDocTemplate(output_pdf, pagesize=landscape((1920,1080)))
    
    # Created a list
    story = []
    
    # Used 'for' loop for rows and columns and then if and else statement for putting the questions and options at their particular places
    for i in range(0,df.shape[0]):
        for j in range(0, len(df.columns)):
            text = df[df.columns[j]][i]
            if df.columns[j]=='Questions':
                story.append(Paragraph(text, ParagraphStyle(name='Q', fontSize=48, leading=56)))
                story.append(Paragraph("<br/><br/>", ParagraphStyle(name='S', fontSize=36)))
            else:
                story.append(Paragraph(df.columns[j]+": "+text, ParagraphStyle(name='O', fontSize=48, spaceBefore=80)))
                story.append(Paragraph("<br/>"))
            
        # Used pagebreak to change the page                    
        story.append(PageBreak())
    
    doc.build(story)
    
# Used for input from users
ip = input('Enter File Path with Name and Extension: ')
op = input('Enter Output File Path with Name without Extension: ')

# To generate the pdf file
generate_pdf_from_csv(ip, op+".pdf")