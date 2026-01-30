# Clinical Patient Health Monitoring & Image Analysis Dashboard

A unified Python-based clinical dashboard developed as a Master's semester project at the **University of Paris-Est Créteil (UPEC)**. This tool integrates real-time vital sign monitoring, risk stratification, and medical image processing into a single, modular interface.

🔗 **Repository Link:** [https://github.com/malikishaq881/Patient-Health-Monitoring-Analysis-Dashboard](https://github.com/malikishaq881/Patient-Health-Monitoring-Analysis-Dashboard)

## 🌟 Key Features

* **Real-time Vital Monitoring:** Visualize time-series data (Heart Rate, Blood Pressure, SpO2, Temperature) with dynamic windowing and zoom controls.
* **MySQL Data Management:** Scalable backend for managing patient demographics and clinical records.
* **Cohort Analytics:** Population-level statistics including BMI and MAP (Mean Arterial Pressure) histograms.
* **Advanced Image Processing:** A dedicated module for medical image enhancement using Gaussian, Median, Sobel, and Canny filters.
* **Risk Stratification:** Automated classification of patient health status (Low, Medium, High) based on clinical thresholds.

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.x |
| **GUI Framework** | Tkinter |
| **Database** | MySQL (via `mysql-connector-python`) |
| **Data Analysis** | Pandas, NumPy |
| **Visualization** | Matplotlib |
| **Image Processing** | Scikit-image, OpenCV |

## 🚀 Quick Setup (Single Click Install)

To get all the necessary files and dependencies ready in one go, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone Patient-Health-Monitoring-Analysis-Dashboard
   cd Patient-Health-Monitoring-Analysis-Dashboard

   pip install mysql-connector-python pandas numpy matplotlib scikit-image opencv-python
   # Example:
host="localhost",
user="your_username",
password="your_password"
python main.py
