import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

df = pd.DataFrame()

def create_figure(parent):
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return fig, ax, canvas

def load_data():
    global df
    path = filedialog.askopenfilename(
        title="Select data file",
        filetypes=[("CSV files","*.csv"),("Excel files","*.xlsx;*.xls"),("All files","*.*")]
    )
    if not path:
        return
    if path.lower().endswith(".csv"):
        df_new = pd.read_csv(path)
    else:
        df_new = pd.read_excel(path)
    df_new.columns = [c.strip() for c in df_new.columns]
    print("Columns:", df_new.columns)

    # force numeric where appropriate
    df_new["PatientID"] = pd.to_numeric(df_new["PatientID"], errors="coerce")
    df_new["SampleIndex"] = pd.to_numeric(df_new["SampleIndex"], errors="coerce")
    df = df_new

    info_label.config(text=f"Loaded {len(df)} rows, {df['PatientID'].nunique()} patients")
    populate_widgets()

def populate_widgets():
    if df.empty:
        return

    # patients
    patient_list["values"] = sorted(df["PatientID"].dropna().unique())
    patient_list.current(0)

    # numeric vars except ids
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for c in ["PatientID","SampleIndex"]:
        if c in numeric_cols:
            numeric_cols.remove(c)
    var_list["values"] = numeric_cols
    if numeric_cols:
        var_list.current(0)

    update_plot()

def update_plot(*args):
    if df.empty:
        return
    pid = patient_list.get()
    var = var_list.get()
    if pid == "" or var == "":
        return
    pid = float(pid)
    sub = df[df["PatientID"] == pid].copy()
    if sub.empty:
        messagebox.showerror("Error", f"No rows for patient {pid}")
        return

    sub["SampleIndex"] = pd.to_numeric(sub["SampleIndex"], errors="coerce")
    sub[var] = pd.to_numeric(sub[var], errors="coerce")
    sub = sub.dropna(subset=["SampleIndex", var]).sort_values("SampleIndex")

    if sub.empty:
        messagebox.showerror("Error", f"{var} has no numeric values for patient {pid}")
        return

    x = sub["SampleIndex"].values
    y = sub[var].values
    print("Plotting", len(x), "points for patient", pid, "variable", var)

    ax.clear()
    ax.plot(x, y, marker="o")
    ax.set_xlabel("SampleIndex")
    ax.set_ylabel(var)
    ax.set_title(f"{var} over time – patient {int(pid)}")
    ax.grid(True)
    canvas.draw()

root = tk.Tk()
root.title("Quick Patient Time-Series Viewer")
root.geometry("900x500")

top = tk.Frame(root)
top.pack(fill="x")

tk.Button(top, text="Load CSV/XLSX", command=load_data).pack(side="left", padx=5, pady=5)
info_label = tk.Label(top, text="No data loaded")
info_label.pack(side="left", padx=10)

ctrl = tk.Frame(root)
ctrl.pack(fill="x", pady=5)

tk.Label(ctrl, text="PatientID:").pack(side="left", padx=5)
patient_list = ttk.Combobox(ctrl, state="readonly", width=10)
patient_list.pack(side="left", padx=5)
patient_list.bind("<<ComboboxSelected>>", update_plot)

tk.Label(ctrl, text="Variable:").pack(side="left", padx=5)
var_list = ttk.Combobox(ctrl, state="readonly", width=20)
var_list.pack(side="left", padx=5)
var_list.bind("<<ComboboxSelected>>", update_plot)

plot_frame = tk.Frame(root)
plot_frame.pack(fill="both", expand=True, padx=5, pady=5)
fig, ax, canvas = create_figure(plot_frame)

root.mainloop()
