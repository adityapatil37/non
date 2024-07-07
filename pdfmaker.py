from fpdf import FPDF
import PyPDF2
from datetime import datetime
from pytz import timezone
import os
from pymongo import MongoClient
import gridfs



def add_watermark(input_pdf, output_pdf, watermark_pdf):
    with open(input_pdf, "rb") as input_file, open(watermark_pdf, "rb") as watermark_file:
        input_pdf_reader = PyPDF2.PdfReader(input_file)
        watermark_pdf_reader = PyPDF2.PdfReader(watermark_file)
        pdf_writer = PyPDF2.PdfWriter()

        watermark_page = watermark_pdf_reader.pages[0]

        for page_num in range(len(input_pdf_reader.pages)):
            page = input_pdf_reader.pages[page_num]
            page.merge_page(watermark_page)
            pdf_writer.add_page(page)

        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)




def upload_to_mongodb(file_path, db_name, collection_name):
    client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
    db = client[db_name]
    fs = gridfs.GridFS(db, collection=collection_name)
    
    with open(file_path, 'rb') as f:
        file_id = fs.put(f, filename=os.path.basename(file_path))
    
    return file_id

def create_pdf(text):
    time = datetime.now(timezone("Asia/Kolkata")).strftime('%H-%M-%S-%f')
    pdf_path = f'/fir_{time}adityacheckk.pdf'
    
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()

    logo_path = 'logo.png'
    pdf.image(logo_path, 10, 8, 33)
    pdf.image(logo_path, 160, 8, 33)

    pdf.set_font("helvetica", size=12)
    pdf.ln(40) #move below logo
    pdf.multi_cell(0, 5, text)
    pdf.output(pdf_path)
    
    add_watermark(pdf_path, pdf_path, watermark_pdf="watermark.pdf")
    
    # Upload the PDF to MongoDB
    file_id = upload_to_mongodb(pdf_path, db_name='PDF_db', collection_name='myfiles')
    
    return file_id