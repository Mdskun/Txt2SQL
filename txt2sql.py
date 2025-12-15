import os
import torch
import sqlite3
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import dotenv
dotenv.load_dotenv()

# CONFIG
# MODEL_PATH = "mrm8488/t5-small-finetuned-wikiSQL" # online model(if you do not have it saved locally)
MODEL_PATH = os.getenv("WIKISQL_MODEL")  # path where you saved the model
DB_PATH = "mydb.db"              # path to your SQLite database

# SILENCE TORCH LOGS

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # ignore TensorFlow info messages
torch.set_num_threads(2)                  # limit CPU threads for smoother CPU usage

# LOAD MODEL OFFLINE

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)

# FUNCTION: Scan DB schema
def get_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    schema_info = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        table = table_name[0]
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        schema_info.append(f"{table}({', '.join(col_names)})")
    conn.close()
    return "Database schema:\n" + "\n".join(schema_info)


# FUNCTION: English -> SQL
def text_to_sql(text, schema):
    input_text = schema + "\nQuestion: " + text
    inputs = tokenizer.encode(input_text, return_tensors="pt")
    with torch.no_grad():  # CPU-friendly
        outputs = model.generate(inputs, max_length=128, num_beams=2)
    sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sql

# FUNCTION: Execute SQL on SQLite
def execute_query(query, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        return f"Error executing SQL: {e}"
    finally:
        conn.close()

# MAIN LOOP
if __name__ == "__main__":
    print("Offline Text-to-SQL (CPU only)")

    # Get database schema once
    schema_text = get_db_schema(DB_PATH)
    print("\nDetected Database Schema:\n", schema_text)

    while True:
        user_input = input("\nEnter English query (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break

        sql_query = text_to_sql(user_input, schema_text)
        print("\nGenerated SQL:\n", sql_query)

        results = execute_query(sql_query)
        print("\nQuery Results:\n", results)
