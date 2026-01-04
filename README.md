# LeetCode Exporter

A command-line tool to export your accepted LeetCode submissions with a clean, organized structure. Perfect for backing up your solutions or building a personal code library.

## ✨ Features

- Fetch all your accepted LeetCode submissions
- Organize solutions by programming language
- Automatically include problem IDs and slugs in filenames
- Beautiful terminal interface with [Rich](https://rich.readthedocs.io/)
- Smart deduplication (keeps only the latest submission per problem)
- Secure credential handling
- Progress tracking with visual feedback

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/luleoa12/LeetCode-Exporter.git
   cd LeetCode-Exporter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 Authentication

To use this tool, you'll need to provide your LeetCode session information:

1. Open [LeetCode](https://leetcode.com) in your browser
2. Open Developer Tools (F12 or Right-click → Inspect)
3. Go to Application/Storage → Cookies → `https://leetcode.com`
4. Find and copy the values for:
   - `LEETCODE_SESSION`
   - `csrftoken`

## 🛠️ Usage

Run the script:
```bash
python main.py
```

The tool will:
1. Prompt you for your LeetCode credentials
2. Fetch all your accepted submissions
3. Organize them by language in the `solutions` directory
4. Show progress and statistics

## 📁 File Structure

Solutions are saved with the following structure:
```
leetcode/
├── python/
│   ├── 0001-two-sum.py
│   └── 0002-add-two-numbers.py
├── cpp/
│   └── 0001-two-sum.cpp
└── ...
```

## 🗺️ Roadmap

### Upcoming Features
- [ ] Include problem descriptions and examples in exported files
- [ ] Add option to sort by difficulty
- [ ] Add more detailed submission statistics

### Future Possibilities
- [ ] Browser extension for one-click exports
- [ ] GUI version of the exporter
- [ ] Integration with GitHub (auto-commit solutions)
- [ ] Support for other coding platforms (HackerRank, CodeForces)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
