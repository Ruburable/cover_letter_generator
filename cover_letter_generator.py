import os
import requests
from datetime import datetime
import argparse
from dotenv import load_dotenv
import glob
import json


class CoverLetterGenerator:
    """Generate tailored cover letters using Ollama local LLM based on CV and job postings."""

    def __init__(self, cv_path="input/resume.tex", ollama_host="http://localhost:11434", model="llama3.2"):
        """
        Initialize the generator.

        Args:
            cv_path: Path to your CV file (default: input/resume.tex)
            ollama_host: Ollama server URL (default: http://localhost:11434)
            model: Ollama model to use (default: llama3.2)
        """
        # Load environment variables from .env file
        load_dotenv()

        self.ollama_host = os.getenv("OLLAMA_HOST", ollama_host)
        self.default_model = os.getenv("OLLAMA_MODEL", model)
        self.cv_content = self._load_cv(cv_path)

        # Test Ollama connection
        self._test_ollama_connection()

    def _test_ollama_connection(self):
        """Test if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            self.available_models = [m['name'] for m in models]
            print(f"✓ Connected to Ollama at {self.ollama_host}")
            print(f"  Available models: {', '.join(self.available_models) if self.available_models else 'None'}")

            if self.default_model not in self.available_models:
                print(f"\n⚠ Warning: Model '{self.default_model}' not found.")
                print(f"  Run: ollama pull {self.default_model}")
                if self.available_models:
                    print(f"  Or use one of: {', '.join(self.available_models)}")
        except requests.exceptions.ConnectionError:
            print(f"✗ Error: Cannot connect to Ollama at {self.ollama_host}")
            print("  Make sure Ollama is running: ollama serve")
            raise
        except Exception as e:
            print(f"✗ Error testing Ollama connection: {str(e)}")
            raise

    def select_model_interactive(self):
        """Interactive model selection from available models."""
        if not hasattr(self, 'available_models') or not self.available_models:
            print("No models available")
            return self.default_model

        print("\n" + "=" * 60)
        print("SELECT MODEL")
        print("=" * 60)

        for i, model in enumerate(self.available_models, 1):
            print(f"  [{i}] {model}")

        print(f"\nDefault: {self.default_model}")

        while True:
            choice = input("\nEnter number (or press Enter for default): ").strip()

            if not choice:
                selected = self.default_model
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.available_models):
                    selected = self.available_models[idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(self.available_models)}")
            except ValueError:
                print("Please enter a valid number")

        print(f"\n✓ Selected model: {selected}")
        print("=" * 60 + "\n")
        return selected

    def _load_cv(self, cv_path):
        """Load CV content from file."""
        try:
            with open(cv_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: CV file not found at {cv_path}")
            return ""

    def _extract_cv_text(self):
        """Extract meaningful text from LaTeX CV."""
        # Simple extraction - you could make this more sophisticated
        cv_text = self.cv_content

        # Remove LaTeX commands and focus on content
        lines = cv_text.split('\n')
        clean_lines = []

        for line in lines:
            # Skip package imports and setup
            if line.strip().startswith('\\usepackage') or \
                    line.strip().startswith('\\define') or \
                    line.strip().startswith('\\setmainfont') or \
                    line.strip().startswith('\\geometry') or \
                    line.strip().startswith('\\titleformat') or \
                    line.strip().startswith('\\newcommand'):
                continue
            # Keep lines with actual content
            if line.strip() and not line.strip().startswith('%'):
                clean_lines.append(line)

        return '\n'.join(clean_lines)

    def generate_cover_letter(self, job_posting, model=None, temperature=0.7):
        """
        Generate a cover letter for a specific job posting using Ollama.

        Args:
            job_posting: The job posting text
            model: Ollama model to use (default: from init or env)
            temperature: Temperature for generation (0-1, default: 0.7)

        Returns:
            Generated cover letter text
        """
        model = model or self.default_model
        cv_text = self._extract_cv_text()

        system_prompt = """You are an expert career counselor and cover letter writer. Create compelling, personalized cover letters that:
- Highlight relevant experience and skills from the candidate's background
- Match specific requirements from the job posting
- Use a professional yet engaging tone
- Are concise (300-400 words)
- Include specific examples and achievements
- Show genuine interest in the role and company
- Format as a proper business letter with greeting and closing
- Use the candidate's actual name and contact information from their CV"""

        user_prompt = f"""Based on this CV and job posting, write a tailored cover letter.

CV:
{cv_text}

JOB POSTING:
{job_posting}

Create a cover letter that highlights the most relevant experience and skills for this specific role."""

        try:
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=120  # Longer timeout for local generation
            )

            response.raise_for_status()
            result = response.json()

            return result.get('response', '')

        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The model might be taking too long to generate.")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {self.ollama_host}. Make sure it's running.")
        except Exception as e:
            raise Exception(f"Error generating cover letter: {str(e)}")

    def save_cover_letter(self, cover_letter, output_path=None):
        """
        Save cover letter to file.

        Args:
            cover_letter: The generated cover letter text
            output_path: Path to save (if None, auto-generates filename in output/)
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/cover_letter_{timestamp}.txt"

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'output', exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)

        print(f"  Saved to: {output_path}")
        return output_path

    def process_job_file(self, job_file_path, model=None):
        """
        Process a single job posting file and generate cover letter.

        Args:
            job_file_path: Path to job posting file
            model: Ollama model to use

        Returns:
            Path to generated cover letter
        """
        # Read job posting
        with open(job_file_path, 'r', encoding='utf-8') as f:
            job_posting = f.read()

        # Generate cover letter
        print(f"\nGenerating cover letter for: {os.path.basename(job_file_path)}")
        cover_letter = self.generate_cover_letter(job_posting, model=model)

        # Generate output filename based on input filename
        job_filename = os.path.basename(job_file_path)
        # Remove extension and add cover_letter prefix
        base_name = os.path.splitext(job_filename)[0]
        output_filename = f"cover_letter_{base_name}.txt"
        output_path = os.path.join("output", output_filename)

        # Save cover letter
        self.save_cover_letter(cover_letter, output_path)

        return output_path

    def batch_process(self, input_dir="input", model=None, pattern="*.txt"):
        """
        Process all job posting files in a directory.

        Args:
            input_dir: Directory containing job posting files
            model: Ollama model to use
            pattern: File pattern to match (default: *.txt)

        Returns:
            List of generated cover letter paths
        """
        # Find all matching files
        search_pattern = os.path.join(input_dir, pattern)
        job_files = glob.glob(search_pattern)

        if not job_files:
            print(f"No files found matching pattern: {search_pattern}")
            return []

        print(f"Found {len(job_files)} job posting(s) to process")
        print("=" * 80)

        generated_files = []

        for i, job_file in enumerate(job_files, 1):
            print(f"\n[{i}/{len(job_files)}]", end=" ")
            try:
                output_path = self.process_job_file(job_file, model=model)
                generated_files.append(output_path)
                print(f"✓ Success")
            except Exception as e:
                print(f"✗ Failed: {str(e)}")

        print("\n" + "=" * 80)
        print(f"Batch processing complete: {len(generated_files)}/{len(job_files)} successful")
        print("=" * 80)

        return generated_files


def main():
    """Command-line interface for the cover letter generator."""
    parser = argparse.ArgumentParser(
        description="Generate tailored cover letters using Ollama local LLM"
    )
    parser.add_argument(
        "--job-file",
        help="Path to file containing job posting",
        required=False
    )
    parser.add_argument(
        "--job-text",
        help="Job posting text directly",
        required=False
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all .txt files in input directory"
    )
    parser.add_argument(
        "--input-dir",
        default="input",
        help="Input directory for batch processing (default: input)"
    )
    parser.add_argument(
        "--cv",
        default="input/resume.tex",
        help="Path to CV file (default: input/resume.tex)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: auto-generated in output/)",
        required=False
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Ollama model to use (default: interactive selection or from OLLAMA_MODEL env var)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactively select model before processing"
    )
    parser.add_argument(
        "--ollama-host",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )

    args = parser.parse_args()

    # Initialize generator
    try:
        generator = CoverLetterGenerator(
            cv_path=args.cv,
            ollama_host=args.ollama_host,
            model=args.model or "llama3.2"
        )
    except Exception as e:
        print(f"\nFailed to initialize generator: {str(e)}")
        return

    # Interactive model selection
    if args.interactive or (not args.model and not os.getenv("OLLAMA_MODEL")):
        selected_model = generator.select_model_interactive()
    else:
        selected_model = args.model

    # Batch processing mode
    if args.batch:
        generator.batch_process(input_dir=args.input_dir, model=selected_model)
        return

    # Single file processing mode
    if args.job_file:
        output_path = generator.process_job_file(args.job_file, model=selected_model)
        print(f"\nDone! Cover letter saved to: {output_path}")
        return

    # Interactive mode or direct text
    if args.job_text:
        job_posting = args.job_text
    else:
        print("Please provide job posting via --job-file, --job-text, or --batch")
        print(
            "\nInteractive mode: Paste job posting (press Ctrl+D on Mac/Linux or Ctrl+Z then Enter on Windows when done):")
        job_posting = []
        try:
            while True:
                line = input()
                job_posting.append(line)
        except EOFError:
            pass
        job_posting = '\n'.join(job_posting)

    if not job_posting.strip():
        print("Error: No job posting provided")
        return

    # Generate cover letter
    print("\nGenerating cover letter...")
    cover_letter = generator.generate_cover_letter(job_posting, model=selected_model)

    # Display result
    print("\n" + "=" * 80)
    print("GENERATED COVER LETTER")
    print("=" * 80 + "\n")
    print(cover_letter)
    print("\n" + "=" * 80)

    # Save to file
    output_path = generator.save_cover_letter(cover_letter, args.output)

    print(f"\nDone! Cover letter saved to: {output_path}")


if __name__ == "__main__":
    main()