import PyPDF2

def clean(text):
    return text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ' , ' ')

def pdf_to_text(pdf_path='./data/bitcoin.pdf'):
    """
    Convert a PDF file to text.

    :param pdf_path: Path to the PDF file.
    :return: Text content of the PDF.
    """
    text = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page in range(num_pages):
            t=pdf_reader.pages[page].extract_text()
            text.append( clean(t) ) 
    return text

# Replace 'your_pdf_file.pdf' with the path to your PDF file
if __name__ == '__main__':
    text = pdf_to_text('./data/bitcoin.pdf')

    print(text)