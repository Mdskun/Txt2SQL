from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

save_path = "E:/Store/Zip/AIs/wikiSQL"

tokenizer = AutoTokenizer.from_pretrained(save_path)
model = AutoModelForSeq2SeqLM.from_pretrained(save_path)

def text_to_sql(text):
    input_text = "translate English to SQL: " + text
    inputs = tokenizer.encode(input_text, return_tensors="pt")
    with torch.no_grad():  # CPU-friendly
        outputs = model.generate(inputs, max_length=128, num_beams=2)
    sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sql

# Example
query = text_to_sql("List all employees who joined after 2020")
print(query)
