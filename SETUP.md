# 🚀 Quick Setup Guide

## Step-by-Step Setup

### 1️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `torch` - PyTorch for model inference
- `transformers` - Hugging Face transformers
- `python-dotenv` - Environment variable management
- `prompt-toolkit` - Enhanced CLI features (autocomplete, history)

### 2️⃣ Download the T5 Model

**Option A: Using git-lfs (Recommended)**

```bash
# Install git-lfs first
git lfs install

# Clone the model
git clone https://huggingface.co/mrm8488/t5-small-finetuned-wikiSQL
```

**Option B: Manual Download**

1. Go to [HuggingFace Model Page](https://huggingface.co/mrm8488/t5-small-finetuned-wikiSQL)
2. Click "Files and versions"
3. Download all files to a folder on your computer

### 3️⃣ Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, notepad, etc.
```

Set the model path:

```env
WIKISQL_MODEL=/absolute/path/to/t5-small-finetuned-wikiSQL
```

**Example paths:**
- Windows: `WIKISQL_MODEL=C:/Users/YourName/models/t5-small-finetuned-wikiSQL`
- Linux/Mac: `WIKISQL_MODEL=/home/yourname/models/t5-small-finetuned-wikiSQL`

### 4️⃣ Prepare Your Database

Place your SQLite database (`.db` file) in the project directory, or remember its full path.

**Example database structure:**

```sql
-- customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    state TEXT
);

-- orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product TEXT,
    amount DECIMAL,
    order_date DATE
);
```

### 5️⃣ Run the Program

```bash
python txt2sql.py
```

The program will:
1. Load the model (takes ~5-10 seconds)
2. Ask you to select a database
3. Start the interactive session

## ✅ Verification

To verify everything is working:

1. Start the program
2. Select your database
3. Try this simple query: `show all tables`
4. You should see your database tables listed

## 🐛 Troubleshooting

### Issue: "Model not found"

**Solution:** Check that:
- The path in `.env` is correct and absolute
- All model files are present in the directory
- You're using forward slashes `/` even on Windows

### Issue: "Database not found"

**Solution:** 
- Use the full path to your database
- Or place the database in the project directory

### Issue: "No module named 'torch'"

**Solution:**
```bash
pip install torch
```

### Issue: "Autocomplete not working"

**Solution:** Install prompt-toolkit:
```bash
pip install prompt-toolkit
```

### Issue: Model loading is slow

**Solution:** This is normal on first load. The model is ~240MB and needs to be loaded into memory.

## 💡 Tips

1. **First Run**: The first time you run the program, model loading takes longer
2. **Database Selection**: Place commonly used databases in the project folder for quick access
3. **Command History**: Use ↑↓ arrows to navigate previous commands
4. **Autocomplete**: Press Tab to see available commands

## 📚 Next Steps

Once setup is complete:

1. Read the [README.md](README.md) for usage examples
2. Try the example queries
3. Explore the `schema` and `tables` commands
4. Start asking your own questions!

---

**Need help?** Open an issue on GitHub!