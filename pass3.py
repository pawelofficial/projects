from openai import OpenAI
from utils import *
import json
import dotenv

def main(input_file='./data/pass2.txt', output_file_json='./data/pass3_json.json', output_file_txt='./data/pass3.txt', model="gpt-4"):
    dotenv.load_dotenv()
    client = OpenAI()

    chunks = read_chunks(input_file)
    sys_prompt = "Make the conversation provided by user less formal and a little bit less dense by adding additional dialogue between Joe, Adam, and Sarah. Don't add any meta commentary such as [Laughs] or [Sighs] or [Pause] etc"
    
    mode = 'w'
    dic = {}

    for no, chunk in enumerate(chunks):
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": chunk}
            ]
        )
        out = completion.choices[0].message
        d = json.loads(out.model_dump_json())
        text = d['content']
        text = clean_gpt_output(text)  # cleanup string

        dic[f'{no}'] = {'gpttext': text, 'sys_prompt': sys_prompt, 'original_text': chunk}
        chunks[no] = text
        with open(output_file_json, 'w') as f:
            json.dump(dic, f, indent=4)
        mywritelines(output_file_txt, text.split('\n'), mode=mode, add_end_line=False)
        mode = 'a'

if __name__ == "__main__":
    main()
