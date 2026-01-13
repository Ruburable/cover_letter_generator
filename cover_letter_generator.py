import os
from openai import OpenAI
from datetime import datetime
import argparse
from dotenv import load_dotenv


class CoverLetterGenerator:
    """Generate tailored cover letters using OpenAI API based on CV and job postings."""

    def __init__(self, api_key=None, cv_path="input/resume.tex"):
        """
        Initialize the generator.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            cv_path: Path to your CV file (default: input/resume.tex)
        """
        # Load environment variables from .env file
        load_dotenv()

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=self.api_key)
        self.cv_content = self._load_cv(cv_path)

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

    def generate_cover_letter(self, job_posting, model="gpt-4o", temperature=0.7):
        """
        Generate a cover letter for a specific job posting.

        Args:
            job_posting: The job posting text
            model: OpenAI model to use (default: gpt-4o)
            temperature: Temperature for generation (0-1, default: 0.7)

        Returns:
            Generated cover letter text
        """
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
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )

            return response.choices[0].message.content

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

        print(f"Cover letter saved to: {output_path}")
        return output_path


def main():
    """Command-line interface for the cover letter generator."""
    parser = argparse.ArgumentParser(
        description="Generate tailored cover letters using AI"
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
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var in .env file)",
        required=False
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )

    args = parser.parse_args()

    # Get job posting
    if args.job_file:
        with open(args.job_file, 'r', encoding='utf-8') as f:
            job_posting = f.read()
    elif args.job_text:
        job_posting = args.job_text
    else:
        print("Please provide job posting via --job-file or --job-text")
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
    generator = CoverLetterGenerator(api_key=args.api_key, cv_path=args.cv)
    cover_letter = generator.generate_cover_letter(job_posting, model=args.model)

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