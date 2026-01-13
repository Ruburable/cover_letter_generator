# Cover Letter Generator

An automated cover letter generation system that leverages local LLM models via Ollama to create personalized cover letters based on job postings and your CV. This project demonstrates the practical application of AI in streamlining the job application process.

**Note:** This project is created for educational and personal use only. It is not intended for commercial purposes.

## Overview

The Cover Letter Generator consists of two main components:

1. **Job Scraper** - Extracts job posting content from URLs
2. **Cover Letter Generator** - Creates tailored cover letters using local AI models

The system processes job postings automatically, generates customized cover letters that highlight relevant experience, and maintains an organized archive of processed applications.

## Features

- **Local AI Processing** - Uses Ollama for completely free, private, and offline cover letter generation
- **Web Scraping** - Automatically extracts job posting content from URLs
- **Intelligent Parsing** - Extracts company names and job titles from postings
- **Batch Processing** - Generates multiple cover letters in one operation
- **Smart Archiving** - Automatically renames and organizes processed job postings
- **Interactive Model Selection** - Choose from available Ollama models
- **Customizable** - Configure models, directories, and processing options

## Requirements

- Python 3.7+
- Ollama (for local LLM inference)
- Internet connection (for web scraping only)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cover_letter_generator.git
cd cover_letter_generator
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and Configure Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

Pull a recommended model:

```bash
# Recommended for quality
ollama pull llama3.2

# Or for best quality (larger model)
ollama pull mistral

# Or for faster processing
ollama pull llama3.2:1b
```

Start the Ollama service:

```bash
ollama serve
```

### 4. Setup Your Environment

Create a `.env` file in the project root:

```bash
# Optional: Set default model
OLLAMA_MODEL=llama3.2:latest

# Optional: Set Ollama host (if not using default)
OLLAMA_HOST=http://localhost:11434
```

### 5. Add Your CV

Place your CV file (LaTeX format) in the `input/` directory:

```bash
cp /path/to/your/resume.tex input/
```

## Directory Structure

```
cover_letter_generator/
├── input/              # Place your CV here; scraped jobs saved here
├── output/             # Generated cover letters
├── bin/                # Archived processed job postings
├── offers/             # Text file with job posting URLs
├── job_scraper.py      # Web scraping component
├── cover_letter_generator.py  # Main generator
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration (not tracked)
├── .gitignore
└── README.md
```

## Usage

### Quick Start

1. **Add job URLs** to `offers/job_urls.txt` (one URL per line)
2. **Scrape job postings:**
   ```bash
   python job_scraper.py
   ```
3. **Generate cover letters:**
   ```bash
   python cover_letter_generator.py --move-to-bin --model llama3.2:latest
   ```

### Detailed Usage

#### Job Scraper

```bash
# Basic usage (reads from offers/job_urls.txt)
python job_scraper.py

# Custom URLs file
python job_scraper.py --urls-file custom_urls.txt

# Save to custom directory
python job_scraper.py --output-dir custom_output

# Adjust delay between requests (be polite to servers)
python job_scraper.py --delay 2.0

# Combine all jobs into single file
python job_scraper.py --combine
```

#### Cover Letter Generator

```bash
# Automatic batch processing with archiving
python cover_letter_generator.py --move-to-bin

# Interactive model selection
python cover_letter_generator.py --move-to-bin --interactive

# Specify model directly
python cover_letter_generator.py --move-to-bin --model gpt-oss:latest

# Process single job file
python cover_letter_generator.py --job-file input/job_posting.txt

# Custom CV path
python cover_letter_generator.py --cv path/to/resume.tex --move-to-bin
```

### Command Line Options

#### job_scraper.py

| Option | Description | Default |
|--------|-------------|---------|
| `--urls-file` | Path to file containing URLs | `offers/job_urls.txt` |
| `--output-dir` | Directory to save scraped jobs | `input` |
| `--delay` | Delay between requests (seconds) | `1.0` |
| `--combine` | Combine all jobs into single file | `False` |
| `--combined-output` | Path for combined output file | Auto-generated |

#### cover_letter_generator.py

| Option | Description | Default |
|--------|-------------|---------|
| `--job-file` | Path to single job posting file | None |
| `--batch` | Explicitly enable batch processing | Auto-detected |
| `--move-to-bin` | Archive processed files to bin/ | `False` |
| `--model` | Ollama model to use | Interactive or from .env |
| `--interactive` | Force interactive model selection | Auto if no default |
| `--cv` | Path to CV file | `input/resume.tex` |
| `--input-dir` | Input directory for batch processing | `input` |
| `--output` | Custom output file path | Auto-generated |
| `--ollama-host` | Ollama server URL | `http://localhost:11434` |

## Workflow Example

### Complete End-to-End Process

```bash
# 1. Create offers/job_urls.txt and add URLs
echo "https://example.com/job1" >> offers/job_urls.txt
echo "https://example.com/job2" >> offers/job_urls.txt

# 2. Scrape all job postings
python job_scraper.py

# 3. Generate all cover letters and archive
python cover_letter_generator.py --move-to-bin --model llama3.2:latest

# Result: Cover letters in output/, archived jobs in bin/
```

### After Processing

- **Cover letters:** `output/cover_letter_[job_name].txt`
- **Archived jobs:** `bin/company-position-date.txt`
- **Input directory:** Empty (ready for next batch)

## Configuration

### Recommended Models

Based on testing for professional cover letter generation:

1. **llama3.2:latest** - Best balance of quality and speed
2. **mistral** - Excellent for professional writing
3. **gpt-oss:latest** - Highest quality (if available locally)
4. **llama3.2:1b** - Faster processing, acceptable quality

### Environment Variables

Create a `.env` file for persistent configuration:

```bash
# Default Ollama model
OLLAMA_MODEL=llama3.2:latest

# Ollama server (if running remotely)
OLLAMA_HOST=http://localhost:11434
```

## How It Works

### Job Scraper

1. Reads URLs from the specified file
2. Fetches webpage content using HTTP requests
3. Extracts main content using BeautifulSoup
4. Removes navigation, scripts, and non-content elements
5. Saves clean text with source URL reference
6. Generates human-readable filenames based on job titles

### Cover Letter Generator

1. Loads your CV and extracts meaningful content
2. Reads job posting files from input directory
3. Uses Ollama LLM to:
   - Extract company name and position
   - Generate tailored cover letter matching job requirements
4. Saves cover letters to output directory
5. Archives processed job postings with intelligent naming

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Test API connection
curl http://localhost:11434/api/tags
```

### Model Not Found

```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.2:latest
```

### Web Scraping Failures

- Some websites may block automated requests
- Try increasing delay: `--delay 2.0`
- Check if website requires authentication
- Verify URL is accessible in browser

### Generation Timeout

- Large models may take longer
- Increase timeout in code or use smaller model
- Check system resources (RAM, CPU)

## Privacy and Security

- All processing happens locally on your machine
- No data is sent to external APIs
- Your CV and job applications remain private
- Source code is open for inspection
- Recommended to review generated content before use

## Limitations

- Requires LaTeX CV format (`.tex` files)
- Web scraping success depends on website structure
- LLM quality varies by model size and configuration
- Generated content should be reviewed and edited
- Some job boards may block automated access

## Contributing

This is a personal project created for educational purposes. While contributions are welcome, please note:

- This project is not intended for commercial use
- Focus on improvements that benefit personal job search workflows
- Respect website terms of service when scraping
- Maintain privacy-first approach (local processing)

## License

This project is provided as-is for educational and personal use only. Not licensed for commercial use.

## Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- Uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping
- Inspired by the need to streamline job application processes

## Disclaimer

This tool is designed to assist in creating personalized cover letters. Users are responsible for:

- Reviewing and editing all generated content
- Ensuring accuracy of information
- Complying with job application requirements
- Respecting intellectual property and privacy
- Following website terms of service when scraping

Generated cover letters should be considered drafts requiring human review and customization.