import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import mysql.connector 


# Graphics & Processing
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from skimage import io as skio
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.feature import canny
from skimage import img_as_ubyte
from PIL import Image, ImageTk

# --- Global Configurations ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "health_dashboard"
}
TABLE_NAME = "synthetic_patient_timeseries"

class HealthDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Health Analytics Dashboard v2.1")
        self.root.geometry("1500x900")
        
        self.df = pd.DataFrame()
        self.current_image = None
        self.processed_image = None
        
        self.setup_styles()
        self.create_layout()
        
        # Auto-sync on launch
        self.root.after(1000, self.fetch_data_from_sql)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook.Tab", padding=[12, 8], font=("Segoe UI", 10, "bold"))

    def create_layout(self):
        # Top Status Bar
        self.status_bar = tk.Frame(self.root, bg="#2c3e50", height=45)
        self.status_bar.pack(side="top", fill="x")
        self.info_label = tk.Label(self.status_bar, text="Initializing...", bg="#2c3e50", fg="#ecf0f1", font=("Segoe UI", 10))
        self.info_label.pack(side="left", padx=20)

        # Sidebar
        self.sidebar = tk.Frame(self.root, bg="#34495e", width=220)
        self.sidebar.pack(side="left", fill="y")
        
        tk.Label(self.sidebar, text="COMMAND CENTER", bg="#34495e", fg="#bdc3c7", font=("Segoe UI", 10, "bold")).pack(pady=20)
        btn_style = {"bg": "#2980b9", "fg": "white", "font": ("Segoe UI", 9, "bold"), "relief": "flat", "width": 20, "pady": 12}
        
        tk.Button(self.sidebar, text="🔄 REFRESH DATABASE", command=self.fetch_data_from_sql, **btn_style).pack(pady=8)
        tk.Button(self.sidebar, text="📂 OPEN MEDICAL IMAGE", command=self.load_image_from_db, **btn_style).pack(pady=8)

        # Main Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Tab 1: Patient Trends
        self.tab_patient = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_patient, text=" PATIENT TRENDS ")
        self.setup_patient_tab()

        # Tab 2: Cohort Analytics
        self.tab_cohort = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cohort, text=" STATISTICS VISUALIZATION")
        self.setup_cohort_tab()

        # Tab 3: Imaging
        self.tab_image = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_image, text=" IMAGE PROCESSING ")
        self.setup_image_tab()

    def setup_patient_tab(self):
        header = tk.Frame(self.tab_patient, pady=10)
        header.pack(fill="x")
        
        tk.Label(header, text="Patient ID:").pack(side="left", padx=5)
        self.p_combo = ttk.Combobox(header, state="readonly", width=12)
        self.p_combo.pack(side="left", padx=5)
        self.p_combo.bind("<<ComboboxSelected>>", self.update_patient_plots)

        tk.Label(header, text="Vital Sign:").pack(side="left", padx=20)
        self.v_combo = ttk.Combobox(header, state="readonly", width=20)
        self.v_combo.pack(side="left", padx=5)
        self.v_combo.bind("<<ComboboxSelected>>", self.update_patient_plots)

        self.p_fig = Figure(figsize=(10, 5), dpi=100)
        self.p_ax = self.p_fig.add_subplot(111)
        self.p_canvas = FigureCanvasTkAgg(self.p_fig, master=self.tab_patient)
        self.p_canvas.get_tk_widget().pack(fill="both", expand=True)

    def setup_cohort_tab(self):
        # Selector Header (Fixing the missing options)
        sel_frame = tk.LabelFrame(self.tab_cohort, text=" Global Variable Comparison ", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        sel_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(sel_frame, text="X Variable:").pack(side="left", padx=5)
        self.cohort_x = ttk.Combobox(sel_frame, state="readonly", width=20)
        self.cohort_x.pack(side="left", padx=5)
        
        tk.Label(sel_frame, text="Y Variable:").pack(side="left", padx=20)
        self.cohort_y = ttk.Combobox(sel_frame, state="readonly", width=20)
        self.cohort_y.pack(side="left", padx=5)
        
        tk.Button(sel_frame, text="Update Analytics", command=self.update_cohort_plots, bg="#27ae60", fg="white").pack(side="left", padx=20)

        # Graphs Area
        graph_container = tk.Frame(self.tab_cohort)
        graph_container.pack(fill="both", expand=True)

        self.c_fig1 = Figure(figsize=(5, 4), dpi=90)
        self.c_ax1 = self.c_fig1.add_subplot(111)
        self.c_can1 = FigureCanvasTkAgg(self.c_fig1, master=graph_container)
        self.c_can1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)

        self.c_fig2 = Figure(figsize=(5, 4), dpi=90)
        self.c_ax2 = self.c_fig2.add_subplot(111)
        self.c_can2 = FigureCanvasTkAgg(self.c_fig2, master=graph_container)
        self.c_can2.get_tk_widget().pack(side="right", fill="both", expand=True, padx=5)

    def setup_image_tab(self):
        img_ctrl = tk.Frame(self.tab_image, pady=10)
        img_ctrl.pack(fill="x")
        
        ops = [("Original", self.reset_image), ("Grayscale", self.to_gray), 
               ("Gaussian", self.apply_gaussian), ("Edge (Canny)", self.apply_canny)]
        
        for text, cmd in ops:
            tk.Button(img_ctrl, text=text, command=cmd, width=12).pack(side="left", padx=5)

        self.img_container = tk.Frame(self.tab_image)
        self.img_container.pack(fill="both", expand=True)
        
        self.orig_label = tk.Label(self.img_container, text="No Image Loaded", bg="#bdc3c7")
        self.orig_label.pack(side="left", fill="both", expand=True, padx=5)
        
        self.proc_label = tk.Label(self.img_container, text="Processed View", bg="#bdc3c7")
        self.proc_label.pack(side="right", fill="both", expand=True, padx=5)

    def fetch_data_from_sql(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            self.df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
            conn.close()
            
            self.df.columns = [c.strip() for c in self.df.columns]
            self.info_label.config(text=f"✅ DATABASE CONNECTED: {len(self.df)} Records", fg="#2ecc71")
            
            # Populate all combos
            vitals = sorted(self.df.select_dtypes(include=[np.number]).columns.tolist())
            vitals = [v for v in vitals if v not in ["PatientID", "SampleIndex", "Age"]]
            
            self.p_combo["values"] = sorted(self.df["PatientID"].unique().tolist())
            self.v_combo["values"] = vitals
            self.cohort_x["values"] = vitals
            self.cohort_y["values"] = vitals
            
            # Defaults
            if not self.p_combo.get():
                self.p_combo.current(0)
                self.v_combo.set("HeartRate")
                self.cohort_x.set("HeartRate")
                self.cohort_y.set("RespiratoryRate")
                self.update_patient_plots()
                self.update_cohort_plots()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def update_patient_plots(self, event=None):
        pid, vital = self.p_combo.get(), self.v_combo.get()
        if not pid or not vital: return
        sub = self.df[self.df["PatientID"] == int(pid)].sort_values("SampleIndex")
        
        self.p_ax.clear()
        self.p_ax.plot(sub["SampleIndex"], sub[vital], color='#2980b9', marker='o', label=vital)
        self.p_ax.set_title(f"Patient {pid} {vital} Trend")
        self.p_ax.grid(True, alpha=0.3)
        self.p_canvas.draw()

    def update_cohort_plots(self):
        x_var, y_var = self.cohort_x.get(), self.cohort_y.get()
        if not x_var or not y_var: return
        
        # Hist
        self.c_ax1.clear()
        self.c_ax1.hist(self.df[x_var].dropna(), bins=20, color='#3498db', alpha=0.7)
        self.c_ax1.set_title(f"Cohort Distribution: {x_var}")
        self.c_can1.draw()
        
        # Scatter
        self.c_ax2.clear()
        self.c_ax2.scatter(self.df[x_var], self.df[y_var], alpha=0.4, color='#e67e22')
        self.c_ax2.set_title(f"Relationship: {x_var} vs {y_var}")
        self.c_can2.draw()

    # --- Image Loading (Fully Integrated with Sidebar Button) ---
    def load_image_from_db(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.current_image = skio.imread(path)
            self.processed_image = self.current_image.copy()
            self.update_image_view(self.orig_label, self.current_image)
            self.update_image_view(self.proc_label, self.processed_image)
            self.notebook.select(2) # Switch to Image tab automatically

    def update_image_view(self, label, img_array):
        im_uint8 = img_as_ubyte(img_array)
        pil_img = Image.fromarray(im_uint8)
        if pil_img.mode != 'RGB' and pil_img.mode != 'L':
            pil_img = pil_img.convert('L')
        pil_img = pil_img.resize((450, 450), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil_img)
        label.image = tk_img
        label.configure(image=tk_img, text="")

    def reset_image(self):
        self.processed_image = self.current_image.copy()
        self.update_image_view(self.proc_label, self.processed_image)

    def to_gray(self):
        if self.current_image is not None:
            self.processed_image = rgb2gray(self.current_image)
            self.update_image_view(self.proc_label, self.processed_image)

    def apply_gaussian(self):
        if self.processed_image is not None:
            img = rgb2gray(self.processed_image) if self.processed_image.ndim == 3 else self.processed_image
            self.processed_image = gaussian(img, sigma=2.0)
            self.update_image_view(self.proc_label, self.processed_image)

    def apply_canny(self):
        if self.processed_image is not None:
            img = rgb2gray(self.processed_image) if self.processed_image.ndim == 3 else self.processed_image
            self.processed_image = canny(img, sigma=1.0)
            self.update_image_view(self.proc_label, self.processed_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthDashboard(root)
    root.mainloop()