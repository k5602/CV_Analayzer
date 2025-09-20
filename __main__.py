"""
AI-Powered Resume/CV Analyzer with ATS Optimization
Main entry point for the application
"""

import os
import sys
import tkinter as tk
from loguru import logger

# Add the parent directory to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(os.path.dirname(current_dir))

# Setup logging
log_dir = os.path.join(current_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
logger.add(os.path.join(log_dir, "app_{time}.log"),
           rotation="10 MB",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

# Import after sys.path is configured
from CV_Analayzer.views.main_view import MainView

def main():
    """Main entry point for the application"""
    try:
        logger.info("Starting CV Analyzer application")

        # Initialize the main application window
        app = MainView()

        # Set icon if available
        icon_path = os.path.join(current_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)

        # Start the main event loop
        app.mainloop()

        logger.info("Application closed normally")

    except Exception as e:
        logger.error(f"Error running application: {e}")

        # Show error in a dialog if GUI is available
        try:
            root = tk.Tk()
            root.withdraw()
            tk.messagebox.showerror(
                "Application Error",
                f"An error occurred while starting the application:\n\n{str(e)}"
            )
            root.destroy()
        except:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()
