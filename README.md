# Txt2SQL

> Convert natural language questions into SQL queries using AI

A simple, offline tool that uses T5 transformer model to convert English questions into SQL queries and execute them on your SQLite database.

## ✨ Features

- 🤖 **AI-Powered**: Uses T5 model fine-tuned on WikiSQL
- 💾 **Offline**: Works completely offline, no API calls
- 🔒 **Local**: All data stays on your machine
- ⚡ **CPU-Optimized**: Efficient CPU inference
- 🎯 **Schema-Aware**: Automatically reads database schema
- 🖥️ **Interactive CLI**: User-friendly command-line interface
- ⚠️ **Safe**: Warns before executing dangerous operations

## 📋 Requirements

- Python 3.8 or higher
- SQLite3
- 2GB+ RAM recommended

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Txt2SQL.git
cd Txt2SQL
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the Model

Download the T5-WikiSQL model from [HuggingFace](https://huggingface.co/mrm8488/t5-small-finetuned-wikiSQL) and save it locally.

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your model path:

```env
WIKISQL_MODEL=/path/to/your/t5-model
DB_PATH=mydb.db
```

### 5. Run

```bash
python txt2sql.py
```

## 📖 Usage

### Interactive Mode

Run without arguments for interactive mode:

```bash
python txt2sql.py
```

Example session:

```
Query> show all customers from California
Generated SQL: SELECT * FROM customers WHERE state = 'California'

│ id  │ name          │ state       │
──────────────────────────────────────
│ 1   │ John Doe      │ California  │
│ 2   │ Jane Smith    │ California  │

(2 rows)
```

### Single Query Mode

Execute a single query and exit:

```bash
python txt2sql.py --query "how many products do we have"
```

### View Database Schema

```bash
python txt2sql.py --show-schema
```

### Custom Database

```bash
python txt2sql.py --database /path/to/database.db
```

### Verbose Mode

```bash
python txt2sql.py --verbose
```

## 🎯 Commands

In interactive mode:

- Type your question in natural language
- `schema` - Show database schema
- `tables` - List all tables
- `exit` or `quit` - Exit the program

## 🏗️ Project Structure

```
Txt2SQL/
├── config.py          # Configuration management
├── database.py        # Database operations
├── generator.py       # SQL generation with T5
├── cli.py             # Command-line interface
├── utils.py           # Utility functions
├── txt2sql.py         # Main entry point
├── requirements.txt   # Dependencies
├── .env.example       # Environment template
└── README.md          # This file
```

## ⚙️ Configuration

Environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `WIKISQL_MODEL` | Path to T5 model | Required |
| `DB_PATH` | Path to SQLite database | `mydb.db` |
| `MAX_SQL_LENGTH` | Maximum SQL length | `128` |
| `NUM_BEAMS` | Beam search beams | `2` |
| `TORCH_THREADS` | CPU threads | `2` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🔒 Security Features

- **Dangerous Operation Warnings**: Prompts before executing DROP, DELETE, TRUNCATE, or ALTER
- **Read-only Queries**: Safe for SELECT queries
- **Input Validation**: Validates all inputs
- **Error Handling**: Comprehensive error handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [T5 Model](https://github.com/google-research/text-to-text-transfer-transformer) by Google Research
- [WikiSQL Dataset](https://github.com/salesforce/WikiSQL)
- [Hugging Face Transformers](https://github.com/huggingface/transformers)

## 📞 Support

For issues and questions, please use the [GitHub Issues](https://github.com/yourusername/Txt2SQL/issues) page.

---

**Note**: This tool is for educational and development purposes. Always validate generated SQL queries before executing them on production databases.