<div align="center">

# 🔮 Txt2SQL

### *Transform Natural Language into SQL Queries with AI*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-T5%20Transformer-orange.svg)](https://huggingface.co/mrm8488/t5-small-finetuned-wikiSQL)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples) • [Contributing](#-contributing)

---

</div>

## 📖 About

**Txt2SQL** is an intelligent command-line tool that converts your natural language questions into SQL queries and executes them on your SQLite database. No need to remember complex SQL syntax—just ask in plain English!

### 🎯 Perfect For

- 📊 Quick database queries without writing SQL
- 🎓 Learning SQL by seeing generated queries
- 🔍 Data exploration and analysis
- 🛠️ Rapid prototyping and testing

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 **AI-Powered**
Uses fine-tuned T5 transformer model for accurate SQL generation

### 🔒 **100% Local**
All processing happens on your machine—no API calls, no data sharing

### ⚡ **CPU Optimized**
Efficient inference designed for everyday computers

</td>
<td width="50%">

### 🎨 **Beautiful CLI**
Interactive interface with colors, autocomplete, and command history

### 🛡️ **Safe by Design**
Warns before executing dangerous operations like DELETE or DROP

### 📊 **Smart Schema Detection**
Automatically reads and understands your database structure

</td>
</tr>
</table>

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- 2GB+ RAM recommended
- SQLite database

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Txt2SQL.git
cd Txt2SQL
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Download T5 Model

Download the pre-trained model from HuggingFace:

```bash
# Using git-lfs
git lfs install
git clone https://huggingface.co/mrm8488/t5-small-finetuned-wikiSQL
```

Or download manually from: [HuggingFace Model Hub](https://huggingface.co/mrm8488/t5-small-finetuned-wikiSQL)

### Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your model path:

```env
WIKISQL_MODEL=/path/to/t5-small-finetuned-wikiSQL
```

---

## 💻 Usage

### Starting the Application

Simply run:

```bash
python txt2sql.py
```

The program will:
1. ✅ Load the AI model
2. 📂 Ask you to select a database
3. 🎯 Start the interactive session

### Interactive Session

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  ████████╗██╗  ██╗████████╗██████╗ ███████╗ ██████╗ ██╗         ║
║  ╚══██╔══╝╚██╗██╔╝╚══██╔══╝╚════██╗██╔════╝██╔═══██╗██║         ║
║     ██║    ╚███╔╝    ██║    █████╔╝███████╗██║   ██║██║         ║
║     ██║    ██╔██╗    ██║   ██╔═══╝ ╚════██║██║▄▄ ██║██║         ║
║     ██║   ██╔╝ ██╗   ██║   ███████╗███████║╚██████╔╝███████╗    ║
║     ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚══════╝ ╚══▀▀═╝ ╚══════╝    ║
║                                                                  ║
║              Natural Language to SQL Query Converter             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

✓ Model loaded
✓ Database: mydb.db
✓ Tables: customers, orders, products

❯ show me all customers from California
```

---

## 🎮 Commands

| Command | Description |
|---------|-------------|
| `?` or `help` | Show help message |
| `schema` | Display database schema |
| `tables` | List all tables |
| `clear` | Clear the screen |
| `exit` or `quit` | Exit the program |

### 💡 Features

- **↑↓ Arrow Keys**: Navigate command history
- **Tab**: Autocomplete commands
- **Ctrl+R**: Search command history (if prompt-toolkit installed)

---

## 📝 Examples

### Example 1: Simple Query

```
❯ show all customers

Generated SQL:
SELECT * FROM customers

│ id  │ name          │ email                │ state       │
─────────────────────────────────────────────────────────────
│ 1   │ John Doe      │ john@example.com     │ California  │
│ 2   │ Jane Smith    │ jane@example.com     │ New York    │
│ 3   │ Bob Johnson   │ bob@example.com      │ Texas       │

(3 rows)
```

### Example 2: Filtered Query

```
❯ how many customers are from California?

Generated SQL:
SELECT COUNT(*) FROM customers WHERE state = 'California'

│ COUNT(*) │
────────────
│ 15       │

(1 row)
```

### Example 3: Join Query

```
❯ show customer names and their order counts

Generated SQL:
SELECT customers.name, COUNT(orders.id) 
FROM customers 
LEFT JOIN orders ON customers.id = orders.customer_id 
GROUP BY customers.name

│ name          │ COUNT(orders.id) │
────────────────────────────────────
│ John Doe      │ 5                │
│ Jane Smith    │ 3                │
│ Bob Johnson   │ 7                │

(3 rows)
```

---

## 🏗️ Project Structure

```
Txt2SQL/
├── 📄 config.py              # Configuration management
├── 📄 database.py            # Database operations
├── 📄 generator.py           # SQL generation with T5
├── 📄 cli.py                 # Interactive CLI interface
├── 📄 utils.py               # Utility functions
├── 📄 txt2sql.py             # Main entry point
│
├── 📋 requirements.txt       # Python dependencies
├── 📋 requirements-dev.txt   # Development dependencies
├── 🧪 test_basic.py          # Unit tests
│
├── 📝 .env.example           # Environment template
├── 📝 .gitignore             # Git ignore rules
├── 📝 LICENSE                # License file
└── 📝 README.md              # This file
```

---

## 🛡️ Safety Features

| Feature | Description |
|---------|-------------|
| ⚠️ **Dangerous Operation Warnings** | Prompts confirmation before DELETE, DROP, TRUNCATE, ALTER |
| ✅ **Input Validation** | Validates all user inputs and SQL queries |
| 🔍 **Query Preview** | Shows generated SQL before execution |
| 📝 **Error Messages** | Clear, helpful error messages |

---

## 🎨 Customization

### Environment Variables

Only one required variable in `.env`:

```env
WIKISQL_MODEL=/path/to/model
```

### Model Parameters

You can adjust these in `config.py`:

```python
self.max_length = 128      # Maximum SQL length
self.num_beams = 2         # Beam search beams
self.torch_threads = 2     # CPU threads
```

---

## 🧪 Development

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest test_basic.py -v
```

### Code Formatting

```bash
black *.py
ruff check *.py
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🔧 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🎉 Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Google Research](https://github.com/google-research/text-to-text-transfer-transformer)** - T5 Transformer Model
- **[Salesforce](https://github.com/salesforce/WikiSQL)** - WikiSQL Dataset
- **[Hugging Face](https://huggingface.co)** - Transformers Library
- **[Manuel Romero](https://huggingface.co/mrm8488)** - Fine-tuned WikiSQL Model

---

## 📞 Support

<div align="center">

**Found a bug?** [Open an issue](https://github.com/yourusername/Txt2SQL/issues)

**Have a question?** [Start a discussion](https://github.com/yourusername/Txt2SQL/discussions)

**Love the project?** Give it a ⭐ on GitHub!

</div>

---

<div align="center">

### 🚀 **Ready to get started?**

```bash
git clone https://github.com/yourusername/Txt2SQL.git
cd Txt2SQL
pip install -r requirements.txt
python txt2sql.py
```

**Made with ❤️ and 🤖 by the Txt2SQL Team**

</div>