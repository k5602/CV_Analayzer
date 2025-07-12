import os
import sys
import tkinter as tk
import importlib.util
from datetime import datetime

# Dependency validation and custom exceptions
from core.dependency_validator import validate_and_exit_if_missing
from core.exceptions import CVAnalyzerError

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure logging - try to use loguru, fallback to standard logging if not available
try:
    from loguru import logger
    log_dir = os.path.join(current_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logger.add(os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log"),
            rotation="10 MB",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
except ImportError:
    import logging
    log_dir = os.path.join(current_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log"),
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    logger = logging
    logger.info = logger.info
    logger.error = logger.error
    logger.warning = logger.warning
    logger.success = lambda msg: logger.info(f"SUCCESS: {msg}")

# Try to import customtkinter, fallback to tkinter if not available
try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
except ImportError:
    HAS_CUSTOMTKINTER = False
    logger.warning("customtkinter not found, falling back to standard tkinter")

def show_error_dialog(message):
    """Display an error dialog with the given message"""
    try:
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Application Error", message)
        root.destroy()
    except:
        print(f"ERROR: {message}")

def fallback_to_basic_ui():
    """Create a basic UI using standard tkinter when customtkinter is not available"""
    try:
        root = tk.Tk()
        root.title("CV Analyzer (Basic Mode)")
        root.geometry("600x400")

        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(
            frame,
            text="Running in compatibility mode with limited functionality.\n\n"
                 "Please install all required dependencies for full features:\n"
                 "pip install -r requirements.txt",
            justify=tk.CENTER,
            padx=20, pady=20
        )
        label.pack(pady=20)

        # Basic resume upload button
        upload_button = tk.Button(
            frame,
            text="Select Resume",
            command=lambda: tk.messagebox.showinfo(
                "Limited Functionality",
                "Full functionality requires all dependencies to be installed."
            )
        )
        upload_button.pack(pady=10)

        # Info display
        info_text = tk.Text(frame, height=10, width=60)
        info_text.insert(tk.END, "CV Analyzer - Basic Mode\n\n")
        info_text.insert(tk.END, "To use all features, please install required dependencies:\n")
        info_text.insert(tk.END, "1. Run 'pip install -r requirements.txt'\n")
        info_text.insert(tk.END, "2. Restart the application\n\n")
        info_text.config(state=tk.DISABLED)
        info_text.pack(pady=10, fill=tk.BOTH, expand=True)

        # Exit button
        exit_button = tk.Button(frame, text="Exit", command=root.destroy)
        exit_button.pack(pady=10)

        root.mainloop()

    except Exception as e:
        print(f"ERROR: Could not create basic UI: {e}")
        print("Please install all dependencies with: pip install -r requirements.txt")

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    optional_deps = []

    # Critical dependencies
    critical_deps = {
        "PyPDF2": "PyPDF2",
        "pdfplumber": "pdfplumber",
        "scikit-learn": "sklearn",
        "matplotlib": "matplotlib.pyplot"
    }

    # Optional dependencies
    optional_deps_dict = {
        "spacy": "spacy",
        "sentence-transformers": "sentence_transformers",
        "keybert": "keybert"
    }

    # Check critical dependencies
    for package_name, import_name in critical_deps.items():
        if not importlib.util.find_spec(import_name.split('.')[0]):
            missing_deps.append(package_name)

    # Check optional dependencies
    for package_name, import_name in optional_deps_dict.items():
        if not importlib.util.find_spec(import_name):
            optional_deps.append(package_name)

    # If spaCy is installed, check for model
    if "spacy" not in optional_deps:
        try:
            import spacy
            try:
                spacy.load("en_core_web_sm")
            except:
                logger.warning("spaCy model 'en_core_web_sm' not found. Attempting to download...")
                user_choice = tk.messagebox.askyesno("Download Required",
                    "The spaCy language model is missing. Would you like to download it now?")
                if user_choice:
                    try:
                        import subprocess
                        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
                    except Exception as e:
                        logger.error(f"Failed to download spaCy model: {e}")
                        optional_deps.append("spacy model")
        except Exception as e:
            logger.error(f"Error checking spaCy model: {e}")
            optional_deps.append("spacy model")

    # Report missing dependencies
    if missing_deps:
        error_message = (
            f"Missing critical dependencies: {', '.join(missing_deps)}\n"
            f"Please install all dependencies with:\n"
            f"pip install -r requirements.txt"
        )
        logger.error(error_message)
        show_error_dialog(error_message)
        return False

    # Report optional dependencies
    if optional_deps:
        warning_message = (
            f"Some optional dependencies are missing: {', '.join(optional_deps)}\n"
            f"The application will run with limited functionality.\n\n"
            f"To install all dependencies: pip install -r requirements.txt"
        )
        logger.warning(warning_message)
        tk.messagebox.showwarning("Limited Functionality", warning_message)

    return True

def main():
    """Main entry point for the application"""
    try:
        logger.info("Starting CV Analyzer application")

        # Validate dependencies before proceeding
        validate_and_exit_if_missing()

        # Handle customtkinter vs standard tkinter
        if HAS_CUSTOMTKINTER:
            # Set appearance mode and default color theme for customtkinter
            ctk.set_appearance_mode("System")  # Use system setting
            ctk.set_default_color_theme("blue")

            # Import the main view after dependency check
            try:
                from views.main_view import MainView

                # Initialize the main application window
                app = MainView()
            except Exception as e:
                logger.error(f"Error initializing MainView: {e}")
                fallback_to_basic_ui()
                return
        else:
            # Fallback to basic UI if customtkinter is not available
            fallback_to_basic_ui()
            return

        # Try to set icon if available
        try:
            icon_path = os.path.join(current_dir, "assets", "icon.ico")
            if os.path.exists(icon_path):
                app.iconbitmap(icon_path)
        except Exception as icon_error:
            logger.warning(f"Could not load application icon: {icon_error}")

        # Start the main event loop
        app.mainloop()

        logger.info("Application closed normally")

    except CVAnalyzerError as ce:
        error_message = f"CVAnalyzerError: {str(ce)}"
        logger.error(error_message)
        show_error_dialog(error_message)
    except Exception as e:
        error_message = f"Error running application: {str(e)}"
        logger.error(error_message)
        show_error_dialog(error_message)

if __name__ == "__main__":
    main()
