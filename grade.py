import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from fpdf import FPDF

class GradeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Grade Architect")
        self.root.geometry("550x750")
        
        self.filename = 'academic_records_v2.csv'
        self.grade_points = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
        self.grade_colors = {'A': '#2ecc71', 'B': '#3498db', 'C': '#f1c40f', 'D': '#e67e22', 'E': '#e74c3c', 'F': '#c0392b'}
        
        self.all_data = self.load_data() # Format: [{'sem': '100L Harmattan', 'name': 'CSC201', 'units': 3, 'grade': 'A'}, ...]

        # --- UI Elements ---
        header = tk.Frame(root)
        header.pack(pady=10)

        tk.Label(header, text="Semester (e.g., 100L Rain):").grid(row=0, column=0)
        self.entry_sem = tk.Entry(header); self.entry_sem.grid(row=0, column=1)

        tk.Label(header, text="Course Code:").grid(row=1, column=0)
        self.entry_name = tk.Entry(header); self.entry_name.grid(row=1, column=1)

        tk.Label(header, text="Units:").grid(row=2, column=0)
        self.entry_units = tk.Entry(header); self.entry_units.grid(row=2, column=1)

        tk.Label(header, text="Grade:").grid(row=3, column=0)
        self.entry_grade = tk.Entry(header); self.entry_grade.grid(row=3, column=1)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Course", command=self.add_and_save, bg="#90ee90", width=15).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove Last", command=self.remove_last, bg="#ffcccb", width=15).grid(row=0, column=1, padx=5)
        tk.Button(root, text="EXPORT PDF REPORT", command=self.export_pdf, bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=33).pack(pady=5)

        # Stats Area
        self.label_cgpa = tk.Label(root, text="OVERALL CGPA: 0.00", font=("Arial", 16, "bold"), fg="#2c3e50")
        self.label_cgpa.pack(pady=10)

        # Scrollable Display
        self.display = tk.Text(root, height=20, width=65, font=("Courier", 10))
        self.display.pack(pady=10)
        
        # Color Tags for Text Widget
        for grade, color in self.grade_colors.items():
            self.display.tag_config(grade, foreground=color)

        self.refresh_ui()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, mode='r') as file:
                return list(csv.DictReader(file))
        return []

    def save_to_csv(self):
        with open(self.filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['sem', 'name', 'credits', 'grade'])
            writer.writeheader()
            writer.writerows(self.all_data)

    def add_and_save(self):
        sem, name, units, grade = self.entry_sem.get().strip(), self.entry_name.get().upper(), self.entry_units.get(), self.entry_grade.get().upper()
        if sem and name and units.isdigit() and grade in self.grade_points:
            self.all_data.append({'sem': sem, 'name': name, 'credits': units, 'grade': grade})
            self.save_to_csv()
            self.refresh_ui()
            self.entry_name.delete(0, tk.END); self.entry_units.delete(0, tk.END); self.entry_grade.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Check all fields!")

    def remove_last(self):
        if self.all_data:
            self.all_data.pop(); self.save_to_csv(); self.refresh_ui()

    def refresh_ui(self):
        self.display.delete('1.0', tk.END)
        grouped = {}
        for c in self.all_data:
            grouped.setdefault(c['sem'], []).append(c)

        overall_pts, overall_units = 0, 0

        for sem, courses in grouped.items():
            sem_pts, sem_units = 0, 0
            self.display.insert(tk.END, f"\n=== {sem} ===\n", "bold")
            for c in courses:
                p = self.grade_points[c['grade']] * int(c['credits'])
                sem_pts += p
                sem_units += int(c['credits'])
                self.display.insert(tk.END, f"{c['name']:<10} | {c['credits']} Units | Grade: ")
                self.display.insert(tk.END, f"{c['grade']}\n", c['grade']) # Apply color tag
            
            sem_gpa = round(sem_pts / sem_units, 2) if sem_units > 0 else 0
            self.display.insert(tk.END, f"Semester GPA: {sem_gpa}\n", "italic")
            overall_pts += sem_pts
            overall_units += sem_units

        cgpa = round(overall_pts / overall_units, 2) if overall_units > 0 else 0.00
        self.label_cgpa.config(text=f"OVERALL CGPA: {cgpa}")

    def export_pdf(self):
        if not self.all_data: return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18); pdf.cell(200, 15, "Full Academic Transcript", ln=True, align='C')
        
        grouped = {}
        for c in self.all_data: grouped.setdefault(c['sem'], []).append(c)

        for sem, courses in grouped.items():
            pdf.ln(5)
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f" Semester: {sem}", 1, ln=True, fill=True)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(80, 8, "Course", 1); pdf.cell(50, 8, "Units", 1); pdf.cell(50, 8, "Grade", 1); pdf.ln()
            
            pdf.set_font("Arial", '', 10)
            sem_pts, sem_units = 0, 0
            for c in courses:
                # Add color logic to PDF (RGB)
                color = self.grade_colors[c['grade']].lstrip('#')
                rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                
                pdf.cell(80, 8, c['name'], 1)
                pdf.cell(50, 8, c['credits'], 1)
                pdf.set_text_color(*rgb) # Set color for the grade
                pdf.cell(50, 8, c['grade'], 1)
                pdf.set_text_color(0, 0, 0) # Reset to black
                pdf.ln()
                sem_pts += self.grade_points[c['grade']] * int(c['credits'])
                sem_units += int(c['credits'])
            
            gpa = round(sem_pts/sem_units, 2) if sem_units > 0 else 0
            pdf.set_font("Arial", 'I', 10); pdf.cell(0, 10, f"Semester GPA: {gpa}", ln=True, align='R')

        pdf.ln(10); pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"FINAL CUMULATIVE GPA: {self.label_cgpa.cget('text').split(': ')[1]}", border=1, ln=True, align='C')
        
        pdf.output("Academic_Transcript.pdf")
        messagebox.showinfo("Success", "Professional Transcript Generated!")

if __name__ == "__main__":
    root = tk.Tk(); app = GradeApp(root); root.mainloop()
