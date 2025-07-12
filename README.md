# AI-Powered Resume/CV Analyzer with ATS Optimization

This Python application provides comprehensive resume/CV analysis with ATS (Applicant Tracking System) optimization capabilities. It helps users improve their resumes to better align with job descriptions and increase their chances of passing through ATS systems.

## Features

- **Resume Parsing**: Extract structured data from PDF, DOCX, or TXT resumes (including OCR for scanned documents)
- **ATS Compatibility Analysis**: Check for ATS-unfriendly elements and provide feedback
- **Keyword Matching**: Compare resume keywords to job descriptions using NLP techniques
- **Feedback Generation**: Receive detailed suggestions to improve your resume
- **ATS Compatibility Score**: Get scored on keyword match, formatting, structure, and file type
- **Data Visualization**: View score breakdowns with interactive charts
- **Custom ATS Profiles**: Get specific recommendations based on different ATS platforms

## Installation

### Prerequisites

- Python 3.7+
- Required libraries (listed in requirements.txt)
- Tesseract OCR (required for processing scanned/image-based documents)

### Setup Instructions

#### Easy Installation (Recommended)

Use the provided installation script which handles virtual environment creation and dependency installation:

```
python install.py
```

For a minimal installation with only essential dependencies (if you experience issues with the full installation):
```
python install.py --minimal
```

#### Manual Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/cv-analyzer.git
cd cv-analyzer
```

2. Create and activate a virtual environment (recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Install spaCy language model:
```
python -m spacy download en_core_web_sm
```

#### Troubleshooting

If you encounter errors during installation of dependencies:

1. Try the minimal installation:
```
python install.py --minimal
```

2. Install dependencies manually one by one:
```
pip install customtkinter PyPDF2 pdfplumber matplotlib pandas
```

3. For specific dependency issues:
   - Python 3.11+ users may face compatibility issues with some packages
   - Some packages require a C compiler for installation (spaCy, blis, etc.)
   - To enable OCR functionality, install Tesseract OCR:
     - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
     - macOS: `brew install tesseract`
     - Linux: `sudo apt-get install tesseract-ocr` or equivalent

## Usage

### Running the Application

Launch the application with:
```
python main.py
```

Or using the module path:
```
python -m CV_Analayzer.main
```

The application supports different modes:
- **Full Mode**: All features available when all dependencies are installed
- **Compatibility Mode**: Limited functionality when some dependencies are missing

### How to Use

1. **Upload Resume**: Click "Select Resume File" to upload your PDF, DOCX, or TXT resume
2. **Add Job Description**: Either paste a job description or upload a job description file
3. **Select ATS Platform**: Choose a specific ATS platform for tailored recommendations
4. **Analyze**: Click "Analyze Resume" to start the analysis process
5. **Review Results**: Check the different tabs to view:
   - Summary with overall scores
   - ATS compatibility issues and recommendations
   - Keyword matching and gaps
   - Parsed resume content
6. **Comprehensive Feedback**: Click "View Comprehensive Feedback" for a detailed report

#### Tips for Best Results

- Use PDF format for most accurate parsing
- Ensure your resume has clear section headers (Experience, Education, Skills)
- For best results with keyword matching, paste the complete job description
- Try multiple ATS platforms to see how different systems might process your resume
- For scanned resumes, ensure the scan quality is good for optimal OCR results

## Technical Details

This application is built with:

- **customtkinter**: For a modern, responsive GUI
- **PyPDF2/pdfplumber/PyMuPDF**: For PDF parsing
- **spaCy/NLTK**: For NLP tasks and entity recognition
- **scikit-learn**: For keyword matching algorithms
- **matplotlib**: For data visualization
- **MVC Architecture**: For modular, maintainable code organization

### System Requirements

- Python 3.7 or newer
- 4GB RAM recommended for NLP processing
- Tesseract OCR (for processing scanned documents)
- Operating Systems:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+, Fedora 34+)

## Project Structure

- `core/`: Modular components for ATS rules, keyword extraction, feedback, resume file/text/entity extraction, and dependency validation
- `controllers/`: Business logic and coordination between modular components and views
- `views/`: UI implementation with customtkinter, progress indicators, and error dialogs
- `config/`: Configuration files including ATS platform rules
- `logs/`: Application logs
- `venv/`: Virtual environment (not tracked in version control)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This tool uses NLP techniques based on spaCy and scikit-learn
- UI built with customtkinter for a modern appearance
- Designed for modularity, performance, and robust error handling
- Icons and resources from
