# Dependency Validator for CV_Analayzer
# Checks for required libraries, models, and binaries at startup

import importlib.util
import sys
import os
from typing import List, Dict

REQUIRED_LIBRARIES = [
    "PyPDF2",
    "pdfplumber",
    "docx",
    "matplotlib",
    "pandas",
    "loguru",
    "customtkinter",
    "PIL",
]

OPTIONAL_LIBRARIES = [
    "spacy",
    "pytesseract",
    "fitz",  
    "sentence_transformers",
    "keybert",
    "nltk",
    "scikit-learn",
]

REQUIRED_MODELS = [
    ("spacy", "en_core_web_sm"),
]

REQUIRED_BINARIES = [
    ("tesseract", "Tesseract OCR"),
]

def check_library_installed(lib_name: str) -> bool:
    return importlib.util.find_spec(lib_name) is not None

def check_model_installed(lib_name: str, model_name: str) -> bool:
    if lib_name == "spacy":
        try:
            import spacy
            spacy.load(model_name)
            return True
        except Exception:
            return False
    return True

def check_binary_installed(binary_name: str) -> bool:
    from shutil import which
    return which(binary_name) is not None

def validate_dependencies() -> Dict[str, List[str]]:
    missing_required = []
    missing_optional = []
    missing_models = []
    missing_binaries = []

    # Check required libraries
    for lib in REQUIRED_LIBRARIES:
        if not check_library_installed(lib):
            missing_required.append(lib)

    # Check optional libraries
    for lib in OPTIONAL_LIBRARIES:
        if not check_library_installed(lib):
            missing_optional.append(lib)

    # Check required models
    for lib, model in REQUIRED_MODELS:
        if check_library_installed(lib) and not check_model_installed(lib, model):
            missing_models.append(f"{lib}:{model}")

    # Check required binaries
    for binary, desc in REQUIRED_BINARIES:
        if not check_binary_installed(binary):
            missing_binaries.append(desc)

    return {
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "missing_models": missing_models,
        "missing_binaries": missing_binaries,
    }

def print_dependency_report(report: Dict[str, List[str]]):
    if report["missing_required"]:
        print("Missing required libraries:")
        for lib in report["missing_required"]:
            print(f"  - {lib}")
    if report["missing_optional"]:
        print("Missing optional libraries (limited functionality):")
        for lib in report["missing_optional"]:
            print(f"  - {lib}")
    if report["missing_models"]:
        print("Missing required models:")
        for model in report["missing_models"]:
            print(f"  - {model}")
    if report["missing_binaries"]:
        print("Missing required binaries:")
        for binary in report["missing_binaries"]:
            print(f"  - {binary}")

def validate_and_exit_if_missing():
    report = validate_dependencies()
    print_dependency_report(report)
    if report["missing_required"] or report["missing_models"] or report["missing_binaries"]:
        print("\nCritical dependencies are missing. Please install all required libraries, models, and binaries before running the application.")
        sys.exit(1)

if __name__ == "__main__":
    validate_and_exit_if_missing()
