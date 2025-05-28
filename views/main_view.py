import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from loguru import logger
from PIL import Image, ImageTk
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.analyzer_controller import AnalyzerController

class MainView(ctk.CTk):
    """
    Main application window for the ATS Resume Analyzer
    built with customtkinter for a modern UI experience.
    """

    def __init__(self):
        super().__init__()

        # Initialize controller
        self.controller = AnalyzerController()

        # Setup window properties
        self.title("AI-Powered Resume/CV Analyzer with ATS Optimization")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Set appearance mode and theme
        ctk.set_appearance_mode("System")  # Use system setting
        ctk.set_default_color_theme("blue")

        # Initialize state variables
        self.resume_path = None
        self.job_description = ""
        self.selected_ats = None
        self.analysis_results = None
        self.is_analyzing = False

        # Create main layout
        self.create_layout()

    def create_layout(self):
        """Create the main application layout."""
        # Create main container with 2x2 grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=6)

        # Create panels
        self.create_input_panel()
        self.create_visualization_panel()
        self.create_result_panel()
        self.create_feedback_panel()

    def create_input_panel(self):
        """Create the left panel for inputs"""
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Configure grid for input frame
        input_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            input_frame,
            text="Resume Analysis Tool",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="w")

        # Resume upload section
        upload_label = ctk.CTkLabel(
            input_frame,
            text="1. Upload Resume (PDF/DOCX/TXT)",
            font=ctk.CTkFont(size=14)
        )
        upload_label.grid(row=1, column=0, padx=10, pady=(20, 5), sticky="w")

        self.resume_button = ctk.CTkButton(
            input_frame,
            text="Select Resume File",
            command=self.browse_resume
        )
        self.resume_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.resume_label = ctk.CTkLabel(
            input_frame,
            text="No file selected",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.resume_label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")

        # Job description section
        job_description_label = ctk.CTkLabel(
            input_frame,
            text="2. Enter Job Description (Optional)",
            font=ctk.CTkFont(size=14)
        )
        job_description_label.grid(row=4, column=0, padx=10, pady=(20, 5), sticky="w")

        self.job_description_text = ctk.CTkTextbox(
            input_frame,
            height=150
        )
        self.job_description_text.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # Job description file upload option
        self.job_file_button = ctk.CTkButton(
            input_frame,
            text="Or Upload Job Description File",
            command=self.browse_job_description
        )
        self.job_file_button.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        # ATS platform selection
        ats_label = ctk.CTkLabel(
            input_frame,
            text="3. Select ATS Platform (Optional)",
            font=ctk.CTkFont(size=14)
        )
        ats_label.grid(row=7, column=0, padx=10, pady=(20, 5), sticky="w")

        # Get available platforms from controller
        platforms = self.controller.get_available_ats_platforms()
        platform_options = [platform["name"] for platform in platforms]
        self.platform_ids = {platform["name"]: platform["id"] for platform in platforms}

        self.ats_dropdown = ctk.CTkOptionMenu(
            input_frame,
            values=platform_options,
            command=self.on_ats_selected
        )
        self.ats_dropdown.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

        # ATS platform info
        self.ats_info_label = ctk.CTkLabel(
            input_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=250
        )
        self.ats_info_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")

        # Analyze button
        self.analyze_button = ctk.CTkButton(
            input_frame,
            text="Analyze Resume",
            command=self.analyze_resume,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#2A8C55",
            hover_color="#206040"
        )
        self.analyze_button.grid(row=10, column=0, padx=20, pady=(30, 10), sticky="ew")

        # Progress indicator (initially hidden)
        self.progress_label = ctk.CTkLabel(
            input_frame,
            text="Analysis in progress...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.progress_label.grid(row=11, column=0, padx=10, pady=5, sticky="w")
        self.progress_label.grid_remove()  # Hide initially

        self.progress_bar = ctk.CTkProgressBar(input_frame)
        self.progress_bar.grid(row=12, column=0, padx=20, pady=5, sticky="ew")
        self.progress_bar.grid_remove()  # Hide initially

    def create_visualization_panel(self):
        """Create the top-right panel for visualizations"""
        viz_frame = ctk.CTkFrame(self)
        viz_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid
        viz_frame.grid_columnconfigure(0, weight=1)
        viz_frame.grid_rowconfigure(0, weight=0)
        viz_frame.grid_rowconfigure(1, weight=1)

        # Title
        viz_title = ctk.CTkLabel(
            viz_frame,
            text="Resume Analysis Scores",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        viz_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        # Create empty chart frame to be filled later
        self.chart_frame = ctk.CTkFrame(viz_frame, fg_color="transparent")
        self.chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Initial empty plot
        self.create_empty_chart()

    def create_empty_chart(self):
        """Create an empty chart with placeholder text."""
        # Clear any existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "Upload a resume to see analysis results",
                horizontalalignment='center', verticalalignment='center',
                fontsize=12, color='gray')
        ax.set_axis_off()

        # Create canvas for figure
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

    def create_result_panel(self):
        """Create the bottom-right panel for detailed results"""
        result_frame = ctk.CTkFrame(self)
        result_frame.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew")

        # Configure grid
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=0)
        result_frame.grid_rowconfigure(1, weight=1)

        # Title
        result_title = ctk.CTkLabel(
            result_frame,
            text="Detailed Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        result_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        # Create tabview for organized results
        self.tabs = ctk.CTkTabview(result_frame)
        self.tabs.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Add tabs
        self.summary_tab = self.tabs.add("Summary")
        self.ats_tab = self.tabs.add("ATS Compatibility")
        self.keywords_tab = self.tabs.add("Keywords")
        self.resume_tab = self.tabs.add("Resume Content")

        # Configure tab layouts
        self._setup_summary_tab()
        self._setup_ats_tab()
        self._setup_keywords_tab()
        self._setup_resume_tab()

    def create_feedback_panel(self):
        """Create float panel for comprehensive feedback"""
        self.feedback_frame = ctk.CTkToplevel(self)
        self.feedback_frame.title("Comprehensive Resume Feedback")
        self.feedback_frame.geometry("800x600")
        self.feedback_frame.withdraw()  # Hide initially

        # Configure grid
        self.feedback_frame.grid_columnconfigure(0, weight=1)
        self.feedback_frame.grid_rowconfigure(0, weight=0)
        self.feedback_frame.grid_rowconfigure(1, weight=1)
        self.feedback_frame.grid_rowconfigure(2, weight=0)

        # Title
        feedback_title = ctk.CTkLabel(
            self.feedback_frame,
            text="Comprehensive Resume Feedback",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        feedback_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Feedback content
        self.feedback_text = ctk.CTkTextbox(self.feedback_frame)
        self.feedback_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Close button
        close_button = ctk.CTkButton(
            self.feedback_frame,
            text="Close",
            command=self.feedback_frame.withdraw
        )
        close_button.grid(row=2, column=0, padx=20, pady=(5, 20))

    def _setup_summary_tab(self):
        """Set up the summary tab with overview information"""
        self.summary_tab.grid_columnconfigure(0, weight=1)

        # ATS Score Frame
        score_frame = ctk.CTkFrame(self.summary_tab)
        score_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ats_label = ctk.CTkLabel(
            score_frame,
            text="ATS Compatibility Score:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ats_label.grid(row=0, column=0, padx=10, pady=10)

        self.ats_score_value = ctk.CTkLabel(
            score_frame,
            text="N/A",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.ats_score_value.grid(row=0, column=1, padx=10, pady=10)

        # Match score frame (if job description provided)
        match_frame = ctk.CTkFrame(self.summary_tab)
        match_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        match_label = ctk.CTkLabel(
            match_frame,
            text="Overall Match Score:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        match_label.grid(row=0, column=0, padx=10, pady=10)

        self.match_score_value = ctk.CTkLabel(
            match_frame,
            text="N/A",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.match_score_value.grid(row=0, column=1, padx=10, pady=10)

        # Summary feedback
        summary_frame = ctk.CTkFrame(self.summary_tab)
        summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        summary_label = ctk.CTkLabel(
            summary_frame,
            text="Summary Feedback:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        summary_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.summary_text = ctk.CTkTextbox(summary_frame, height=100)
        self.summary_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.summary_text.insert("1.0", "No analysis has been performed yet.")

        # View detailed feedback button
        self.feedback_button = ctk.CTkButton(
            self.summary_tab,
            text="View Comprehensive Feedback",
            command=self.show_feedback_panel
        )
        self.feedback_button.grid(row=3, column=0, padx=10, pady=(20, 10))

    def _setup_ats_tab(self):
        """Set up the ATS compatibility tab"""
        self.ats_tab.grid_columnconfigure(0, weight=1)

        # ATS Platform
        platform_frame = ctk.CTkFrame(self.ats_tab)
        platform_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        platform_label = ctk.CTkLabel(
            platform_frame,
            text="ATS Platform:",
            font=ctk.CTkFont(weight="bold")
        )
        platform_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.platform_value = ctk.CTkLabel(platform_frame, text="N/A")
        self.platform_value.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Formatting Issues
        issues_label = ctk.CTkLabel(
            self.ats_tab,
            text="Formatting Issues:",
            font=ctk.CTkFont(weight="bold")
        )
        issues_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")

        self.issues_text = ctk.CTkTextbox(self.ats_tab, height=100)
        self.issues_text.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.issues_text.insert("1.0", "No analysis has been performed yet.")

        # Recommendations
        recommendations_label = ctk.CTkLabel(
            self.ats_tab,
            text="ATS Recommendations:",
            font=ctk.CTkFont(weight="bold")
        )
        recommendations_label.grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")

        self.recommendations_text = ctk.CTkTextbox(self.ats_tab)
        self.recommendations_text.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.recommendations_text.insert("1.0", "No analysis has been performed yet.")

    def _setup_keywords_tab(self):
        """Set up the keywords tab"""
        self.keywords_tab.grid_columnconfigure(0, weight=1)

        # Matching Keywords
        matching_label = ctk.CTkLabel(
            self.keywords_tab,
            text="Matching Keywords:",
            font=ctk.CTkFont(weight="bold")
        )
        matching_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.matching_text = ctk.CTkTextbox(self.keywords_tab, height=100)
        self.matching_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.matching_text.insert("1.0", "No job description provided for comparison.")

        # Missing Keywords
        missing_label = ctk.CTkLabel(
            self.keywords_tab,
            text="Missing Keywords:",
            font=ctk.CTkFont(weight="bold")
        )
        missing_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")

        self.missing_text = ctk.CTkTextbox(self.keywords_tab, height=100)
        self.missing_text.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.missing_text.insert("1.0", "No job description provided for comparison.")

        # Section Match Scores
        section_label = ctk.CTkLabel(
            self.keywords_tab,
            text="Section Match Scores:",
            font=ctk.CTkFont(weight="bold")
        )
        section_label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="w")

        self.section_text = ctk.CTkTextbox(self.keywords_tab, height=100)
        self.section_text.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.section_text.insert("1.0", "No analysis has been performed yet.")

    def _setup_resume_tab(self):
        """Set up the resume content tab"""
        self.resume_tab.grid_columnconfigure(0, weight=1)

        # Create a scrollable frame for content
        self.resume_scroll = ctk.CTkScrollableFrame(self.resume_tab)
        self.resume_scroll.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.resume_scroll.grid_columnconfigure(0, weight=1)

        # Contact Info
        contact_label = ctk.CTkLabel(
            self.resume_scroll,
            text="Contact Information:",
            font=ctk.CTkFont(weight="bold")
        )
        contact_label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w")

        self.contact_text = ctk.CTkTextbox(self.resume_scroll, height=80)
        self.contact_text.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.contact_text.insert("1.0", "No data available")

        # Skills
        skills_label = ctk.CTkLabel(
            self.resume_scroll,
            text="Skills:",
            font=ctk.CTkFont(weight="bold")
        )
        skills_label.grid(row=2, column=0, padx=5, pady=(10, 0), sticky="w")

        self.skills_text = ctk.CTkTextbox(self.resume_scroll, height=80)
        self.skills_text.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.skills_text.insert("1.0", "No data available")

        # Experience
        experience_label = ctk.CTkLabel(
            self.resume_scroll,
            text="Experience:",
            font=ctk.CTkFont(weight="bold")
        )
        experience_label.grid(row=4, column=0, padx=5, pady=(10, 0), sticky="w")

        self.experience_text = ctk.CTkTextbox(self.resume_scroll, height=150)
        self.experience_text.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        self.experience_text.insert("1.0", "No data available")

        # Education
        education_label = ctk.CTkLabel(
            self.resume_scroll,
            text="Education:",
            font=ctk.CTkFont(weight="bold")
        )
        education_label.grid(row=6, column=0, padx=5, pady=(10, 0), sticky="w")

        self.education_text = ctk.CTkTextbox(self.resume_scroll, height=80)
        self.education_text.grid(row=7, column=0, padx=5, pady=5, sticky="ew")
        self.education_text.insert("1.0", "No data available")

    def browse_resume(self):
        """Open file dialog to select a resume file"""
        filetypes = [
            ("All Supported Files", "*.pdf *.docx *.txt"),
            ("PDF Files", "*.pdf"),
            ("Word Documents", "*.docx"),
            ("Text Files", "*.txt")
        ]

        file_path = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=filetypes
        )

        if file_path:
            self.resume_path = file_path
            self.resume_label.configure(text=os.path.basename(file_path))

    def browse_job_description(self):
        """Open file dialog to select a job description file"""
        filetypes = [
            ("Text Files", "*.txt"),
            ("PDF Files", "*.pdf"),
            ("Word Documents", "*.docx")
        ]

        file_path = filedialog.askopenfilename(
            title="Select Job Description",
            filetypes=filetypes
        )

        if file_path:
            try:
                # Try to read the file as a text file first
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.job_description_text.delete("1.0", "end")
                    self.job_description_text.insert("1.0", content)
            except:
                messagebox.showinfo(
                    "File Loading",
                    "Could not read file as text. File path will be used directly."
                )
                self.job_description = file_path

    def on_ats_selected(self, choice):
        """Handle ATS platform selection"""
        self.selected_ats = self.platform_ids.get(choice)

        # Show platform description if available
        for platform in self.controller.ats_checker.ats_rules.values():
            if platform.get("name") == choice:
                self.ats_info_label.configure(
                    text=platform.get("description", "")
                )
                break

    def analyze_resume(self):
        """Start the resume analysis process"""
        if self.is_analyzing:
            messagebox.showinfo("Analysis in Progress", "Please wait for the current analysis to complete.")
            return

        if not self.resume_path:
            messagebox.showerror("Error", "Please select a resume file first.")
            return

        # Get job description from text box
        job_description = self.job_description_text.get("1.0", "end").strip()
        if not job_description:
            job_description = None

        # Start analysis process
        self.is_analyzing = True
        self.progress_label.grid()
        self.progress_bar.grid()
        self.progress_bar.set(0)

        # Disable analysis button
        self.analyze_button.configure(state="disabled", text="Analyzing...")

        # Run analysis in a separate thread to keep UI responsive
        threading.Thread(target=self._run_analysis, args=(job_description,), daemon=True).start()

    def _run_analysis(self, job_description):
        """Run the analysis process in a background thread"""
        try:
            # Update progress
            self.update_progress(0.2, "Parsing resume...")
            time.sleep(0.5)  # Small delay for UI feedback

            # Run analysis
            results = self.controller.analyze_resume(
                self.resume_path,
                job_description,
                self.selected_ats
            )

            self.update_progress(0.8, "Processing results...")

            # Store results and update UI
            self.analysis_results = results
            self.after(100, lambda: self.display_results(results))

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.after(100, lambda: messagebox.showerror("Analysis Error", str(e)))
            self.after(100, self.reset_analysis_ui)

    def update_progress(self, value, message=None):
        """Update progress bar and message"""
        def _update():
            self.progress_bar.set(value)
            if message:
                self.progress_label.configure(text=message)
        self.after(10, _update)

    def reset_analysis_ui(self):
        """Reset UI after analysis completes or fails"""
        self.is_analyzing = False
        self.analyze_button.configure(state="normal", text="Analyze Resume")
        self.progress_label.grid_remove()
        self.progress_bar.grid_remove()

    def display_results(self, results):
        """Display analysis results in the interface"""
        try:
            if "error" in results:
                messagebox.showerror("Analysis Error", results["error"])
                self.reset_analysis_ui()
                return

            # Get main components
            resume_data = results.get("resume_data", {})
            ats_analysis = results.get("ats_analysis", {})
            keyword_analysis = results.get("keyword_analysis")
            feedback = results.get("feedback", {})

            # Update summary tab
            self.ats_score_value.configure(
                text=f"{ats_analysis.get('compatibility_score', 0)}%",
                text_color=self._get_score_color(ats_analysis.get('compatibility_score', 0))
            )

            if keyword_analysis:
                self.match_score_value.configure(
                    text=f"{keyword_analysis.get('overall_match_percentage', 0)}%",
                    text_color=self._get_score_color(keyword_analysis.get('overall_match_percentage', 0))
                )

            # Update summary text
            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("1.0", feedback.get("summary", "No summary feedback available."))

            # Update ATS tab
            self.platform_value.configure(text=ats_analysis.get("ats_platform", "Default"))

            self.issues_text.delete("1.0", "end")
            issues = ats_analysis.get("formatting_issues", [])
            if issues:
                self.issues_text.insert("1.0", "\n".join(f"• {issue}" for issue in issues))
            else:
                self.issues_text.insert("1.0", "No formatting issues detected.")

            self.recommendations_text.delete("1.0", "end")
            recommendations = ats_analysis.get("improvement_suggestions", [])
            if recommendations:
                self.recommendations_text.insert("1.0", "\n".join(f"• {rec}" for rec in recommendations))
            else:
                self.recommendations_text.insert("1.0", "No specific recommendations provided.")

            # Update keywords tab
            if keyword_analysis:
                self.matching_text.delete("1.0", "end")
                matching = keyword_analysis.get("matching_keywords", [])
                if matching:
                    self.matching_text.insert("1.0", ", ".join(matching[:20]))
                else:
                    self.matching_text.insert("1.0", "No matching keywords found.")

                self.missing_text.delete("1.0", "end")
                missing = keyword_analysis.get("missing_keywords", [])
                if missing:
                    self.missing_text.insert("1.0", ", ".join(missing[:20]))
                else:
                    self.missing_text.insert("1.0", "No missing keywords identified.")

                # Add section match scores
                self.section_text.delete("1.0", "end")
                section_text = f"Overall Match: {keyword_analysis.get('overall_match_percentage', 0)}%\n"
                section_text += f"Skills Match: {keyword_analysis.get('skills_match_percentage', 0)}%\n"
                section_text += f"Experience Match: {keyword_analysis.get('experience_match_percentage', 0)}%\n"
                section_text += f"Education Match: {keyword_analysis.get('education_match_percentage', 0)}%"
                self.section_text.insert("1.0", section_text)

            # Update resume content tab
            self._update_contact_info(resume_data.get("contact_info", {}))
            self._update_skills(resume_data.get("skills", []))
            self._update_experience(resume_data.get("experience", []))
            self._update_education(resume_data.get("education", []))

            # Update visualization
            self._create_visualization(results.get("scores", {}))

            # Prepare comprehensive feedback
            self._prepare_comprehensive_feedback(feedback, results)

        except Exception as e:
            logger.error(f"Error displaying results: {e}")
            messagebox.showerror("Display Error", f"Error displaying results: {str(e)}")

        finally:
            self.reset_analysis_ui()

    def _create_visualization(self, scores):
        """Create visualization of analysis scores"""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('none')  # Transparent background

        # Prepare data
        categories = []
        values = []

        # Always include ATS compatibility
        categories.append('ATS\nCompatibility')
        values.append(scores.get('ats_compatibility', 0))

        # Include match scores if available
        if 'overall_match' in scores and scores['overall_match'] is not None:
            categories.extend(['Overall\nMatch', 'Skills\nMatch', 'Experience\nMatch'])
            values.extend([
                scores.get('overall_match', 0),
                scores.get('skills_match', 0),
                scores.get('experience_match', 0)
            ])

        # Set colors based on scores
        colors = [self._get_bar_color(value) for value in values]

        # Create chart
        bars = ax.bar(categories, values, color=colors)

        # Add score labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + 2,
                f'{height}%',
                ha='center',
                fontsize=10,
                fontweight='bold'
            )

        # Customize chart appearance
        ax.set_ylim(0, 105)  # Leave room for labels
        ax.set_ylabel('Score (%)')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Add threshold line at 70%
        ax.axhline(y=70, color='gray', linestyle='
--', alpha=0.7)
        ax.text(len(categories)-1, 72, 'Target (70%)', ha='right', fontsize=8, style='italic')
        
        # Create canvas and embed in frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    def _get_score_color(self, score):
        """Return color based on score value"""
        if score >= 80:
            return "#4CAF50"  # Green
        elif score >= 60:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Red
    
    def _get_bar_color(self, value):
        """Return bar color based on score value"""
        if value >= 80:
            return "#4CAF50"  # Green
        elif value >= 60:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Red
    
    def _update_contact_info(self, contact_info):
        """Update contact information display"""
        self.contact_text.delete("1.0", "end")
        text = f"Name: {contact_info.get('name', 'Not found')}\n"
        text += f"Email: {contact_info.get('email', 'Not found')}\n"
        text += f"Phone: {contact_info.get('phone', 'Not found')}\n"
        
        if contact_info.get('linkedin'):
            text += f"LinkedIn: {contact_info.get('linkedin')}\n"
        if contact_info.get('github'):
            text += f"GitHub: {contact_info.get('github')}\n"
        if contact_info.get('location'):
            text += f"Location: {contact_info.get('location')}\n"
        
        self.contact_text.insert("1.0", text)
    
    def _update_skills(self, skills):
        """Update skills display"""
        self.skills_text.delete("1.0", "end")
        if skills:
            self.skills_text.insert("1.0", ", ".join(skills))
        else:
            self.skills_text.insert("1.0", "No skills identified in resume.")
    
    def _update_experience(self, experience_list):
        """Update experience display"""
        self.experience_text.delete("1.0", "end")
        if not experience_list:
            self.experience_text.insert("1.0", "No experience entries found.")
            return
        
        text = ""
        for i, exp in enumerate(experience_list):
            if i > 0:
                text += "\n\n"
                
            if exp.get('title'):
                text += f"Title: {exp.get('title')}\n"
            if exp.get('company'):
                text += f"Company: {exp.get('company')}\n"
            if exp.get('date_range'):
                text += f"Period: {exp.get('date_range')}\n"
                
            if exp.get('description'):
                text += f"\n{exp.get('description')}"
        
        self.experience_text.insert("1.0", text)
    
    def _update_education(self, education_list):
        """Update education display"""
        self.education_text.delete("1.0", "end")
        if not education_list:
            self.education_text.insert("1.0", "No education entries found.")
            return
        
        text = ""
        for i, edu in enumerate(education_list):
            if i > 0:
                text += "\n\n"
                
            if edu.get('degree'):
                text += f"Degree: {edu.get('degree')}\n"
            if edu.get('institution'):
                text += f"Institution: {edu.get('institution')}\n"
            if edu.get('date_range'):
                text += f"Period: {edu.get('date_range')}"
        
        self.education_text.insert("1.0", text)
    
    def _prepare_comprehensive_feedback(self, feedback, results):
        """Prepare comprehensive feedback for detailed view"""
        self.feedback_text.delete("1.0", "end")
        
        # Add summary
        self.feedback_text.insert("end", "SUMMARY FEEDBACK\n", "heading")
        self.feedback_text.insert("end", "================\n\n")
        self.feedback_text.insert("end", f"{feedback.get('summary', 'No summary available.')}\n\n\n")
        
        # Add ATS compatibility feedback
        self.feedback_text.insert("end", "ATS COMPATIBILITY\n", "heading")
        self.feedback_text.insert("end", "================\n\n")
        
        ats_feedback = feedback.get("ats_compatibility", {})
        self.feedback_text.insert("end", f"Score: {ats_feedback.get('score', 0)}%\n\n")
        
        if ats_feedback.get("issues"):
            self.feedback_text.insert("end", "Issues:\n")
            for issue in ats_feedback.get("issues", []):
                self.feedback_text.insert("end", f"• {issue}\n")
            self.feedback_text.insert("end", "\n")
        
        if ats_feedback.get("recommendations"):
            self.feedback_text.insert("end", "Recommendations:\n")
            for rec in ats_feedback.get("recommendations", []):
                self.feedback_text.insert("end", f"• {rec}\n")
            self.feedback_text.insert("end", "\n\n")
        
        # Add content quality feedback
        self.feedback_text.insert("end", "CONTENT QUALITY\n", "heading")
        self.feedback_text.insert("end", "==============\n\n")
        
        content_feedback = feedback.get("content_quality", {})
        
        if content_feedback.get("strengths"):
            self.feedback_text.insert("end", "Strengths:\n")
            for strength in content_feedback.get("strengths", []):
                self.feedback_text.insert("end", f"• {strength}\n")
            self.feedback_text.insert("end", "\n")
        
        if content_feedback.get("weaknesses"):
            self.feedback_text.insert("end", "Areas for Improvement:\n")
            for weakness in content_feedback.get("weaknesses", []):
                self.feedback_text.insert("end", f"• {weakness}\n")
            self.feedback_text.insert("end", "\n")
        
        if content_feedback.get("recommendations"):
            self.feedback_text.insert("end", "Recommendations:\n")
            for rec in content_feedback.get("recommendations", []):
                self.feedback_text.insert("end", f"• {rec}\n")
            self.feedback_text.insert("end", "\n\n")
        
        # Add keyword match feedback if available
        keyword_feedback = feedback.get("keyword_match", {})
        if keyword_feedback and "score" in keyword_feedback:
            self.feedback_text.insert("end", "KEYWORD MATCHING\n", "heading")
            self.feedback_text.insert("end", "===============\n\n")
            self.feedback_text.insert("end", f"Score: {keyword_feedback.get('score', 0)}%\n\n")
            
            if keyword_feedback.get("recommendations"):
                self.feedback_text.insert("end", "Recommendations:\n")
                for rec in keyword_feedback.get("recommendations", []):
                    self.feedback_text.insert("end", f"• {rec}\n")
                self.feedback_text.insert("end", "\n\n")
        
        # Add section-by-section feedback
        self.feedback_text.insert("end", "SECTION-BY-SECTION FEEDBACK\n", "heading")
        self.feedback_text.insert("end", "==========================\n\n")
        
        section_feedback = results.get("section_feedback", {})
        for section_name, feedback_items in section_feedback.items():
            display_name = section_name.replace("_", " ").title()
            self.feedback_text.insert("end", f"{display_name} Section:\n", "subheading")
            
            for item in feedback_items:
                self.feedback_text.insert("end", f"• {item}\n")
            
            self.feedback_text.insert("end", "\n")
        
        # Configure tags for formatting
        self.feedback_text.tag_configure("heading", font=ctk.CTkFont(size=16, weight="bold"))
        self.feedback_text.tag_configure("subheading", font=ctk.CTkFont(size=14, weight="bold"))
    
    def show_feedback_panel(self):
        """Display the comprehensive feedback panel"""
        if self.analysis_results:
            self.feedback_frame.deiconify()
            self.feedback_frame.focus_set()
        else:
            messagebox.showinfo("No Analysis", "Please analyze a resume first.")