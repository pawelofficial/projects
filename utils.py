import PyPDF2
import logging 
import json 
# setup logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',filename='log.txt',filemode='w')
logger = logging.getLogger(__name__)



def clean(text):
    return text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('   ' , ' ').replace('  ',' ').strip()

# turns pdf into a list of strings based on pages 
def pdf_to_text(pdf_path='./data/bitcoin.pdf') -> list:
    text_list = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page in range(num_pages):
            t=pdf_reader.pages[page].extract_text()
            text_list.append( clean(t) ) 
    return text_list, '\n'.join(text_list)

# splits string but keeps the delimiter ! 
def split_with_delim(text,delim='. '):
    text_list=text.split(delim)
    text_list=[i+delim for i in text_list if i.strip()!='']
    return text_list

# puts pdf into a list of strings of approximately N characters, split by delim 
def text_loader(N=2500,pdf_path='./data/bitcoin.pdf',delim='. ') -> list:
    text_list,text=pdf_to_text(pdf_path)
    text_list=split_with_delim(text,delim=delim)
    text_list_nchar=[]
    tmp_text=''
    for t in text_list:
        tmp_text+=t
        if len(tmp_text)>N:
            text_list_nchar.append(tmp_text)
            tmp_text=''
    text_list_nchar.append(tmp_text)
    return text_list_nchar
    
# mixes chunks with an overlao of n items split by delim 
def text_mixer(nchunk=2,N=2500,pdf_path='./data/bitcoin.pdf',delim='. ',dump_res=True) -> list:
    text_list_nchar=text_loader(N,pdf_path)
    text_list_mixed=[]
    d={}
    prev_chunk=''
    prev_chunk_overlap=''
    # mix current chunk of text with next one 
    for i in range(0,len(text_list_nchar),1):
        if i>0:
            prev_chunk=text_list_nchar[i-1]
            prev_chunk_overlap_list=split_with_delim(prev_chunk,delim=delim)                  # split prev chunk
            prev_chunk_overlap=' '.join(prev_chunk_overlap_list[-nchunk:])                    # get last n items of prev chunk 
        
        cur_chunk=text_list_nchar[i]                                                          # current chunk of text 
        
        if i<len(text_list_nchar)-1:
            next_chunk=text_list_nchar[i+1]                                                   # next chunk of text 
            next_chunk_overlap_list=split_with_delim(next_chunk,delim=delim)                  # split next chunk
            next_chunk_overlap=' '.join(next_chunk_overlap_list[:nchunk])                     # get first n items of next chunk
        else:
            next_chunk=''
            next_chunk_overlap=''
        
        mixed_chunk=prev_chunk_overlap+' ' + cur_chunk+' '+next_chunk_overlap
        text_list_mixed.append(mixed_chunk.replace('   ',' ').replace('  ',' ') )
        logger.log(logging.INFO, f'cur_chunk: {cur_chunk}')
        logger.log(logging.INFO, f'next_chunk: {next_chunk}')
        logger.log(logging.INFO, f'next_chunk_overlap: {next_chunk_overlap}')        
        logger.log(logging.INFO, f'mixed_chunk: {mixed_chunk}')
        logger.log(logging.INFO, f'------------------------')
        d[f'chunks_{i}']={'cur_chunk':cur_chunk
                          ,'next_chunk':next_chunk
                          ,'next_chunk_overlap':next_chunk_overlap
                          ,'prev_chunk_overlap':prev_chunk_overlap
                          ,'mixed_chunk':mixed_chunk}
    # add rest of text 

    if dump_res:
        with open('./data/chunks_json.json', 'w') as f:
            json.dump(d, f,indent=4)    
    return d 



    


# Replace 'your_pdf_file.pdf' with the path to your PDF file
if __name__ == '__main__x':
    text = pdf_to_text('./data/bitcoin.pdf')
    text_list_nchar=text_loader(500,'./data/bitcoin.pdf')
    d=text_mixer()
    