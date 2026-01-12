from fpdf import FPDF
from datetime import timedelta
import io

class AttendancePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Attendance Report', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def generate_attendance_pdf(attendance_data, date_list, start_date, end_date):
    pdf = AttendancePDF(orientation='L', unit='mm', format='A4') # Landscape for better width
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title Info
    pdf.set_font('Helvetica', '', 12)
    period_str = f"Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
    pdf.cell(0, 10, period_str, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # --- HEATMAP SECTION ---
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "Attendance Heatmap", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Config for Heatmap
    cell_w = 8
    cell_h = 8
    margin_left = 40 # Space for names
    
    # Header Dates
    pdf.set_font('Helvetica', '', 8)
    
    # Save starting position
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    
    # Draw Date Headers
    pdf.set_xy(start_x + margin_left, start_y)
    for d in date_list:
        pdf.cell(cell_w, 5, d.strftime('%d'), align='C', border=0)
    
    pdf.ln(5) # Move down for rows
    
    row_height = 10
    
    pdf.set_font('Helvetica', '', 9)
    
    for row in attendance_data:
        # Check page break
        if pdf.get_y() > 180:
            pdf.add_page()
            pdf.set_y(20) # Reset Y
        
        current_y = pdf.get_y()
        
        # Student Name
        name = f"{row['student'].user.first_name} ({row['student'].roll_no})"
        pdf.set_xy(start_x, current_y)
        pdf.cell(margin_left, cell_h, name, border=0)
        
        # Cells
        current_x = start_x + margin_left
        for cell in row['daily_data']:
            pdf.set_xy(current_x, current_y)
            
            # Color Logic
            if cell['status_color'] == '#4caf50': # Green
                pdf.set_fill_color(76, 175, 80)
            elif cell['status_color'] == '#f44336': # Red
                pdf.set_fill_color(244, 67, 54)
            else: # White/Absent
                pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(cell_w, cell_h, "", border=1, fill=True)
            current_x += cell_w
            
        pdf.ln(cell_h + 1) # Space between rows

    # Legend
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 10)
    
    # Green Box
    pdf.set_fill_color(76, 175, 80)
    pdf.cell(5, 5, "", border=1, fill=True)
    pdf.cell(20, 5, " >= 6 Hrs", new_x="RIGHT")
    
    # Red Box
    pdf.set_x(pdf.get_x() + 5)
    pdf.set_fill_color(244, 67, 54)
    pdf.cell(5, 5, "", border=1, fill=True)
    pdf.cell(20, 5, " < 6 Hrs", new_x="RIGHT")
    
    # White Box
    pdf.set_x(pdf.get_x() + 5)
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(5, 5, "", border=1, fill=True)
    pdf.cell(30, 5, " Absent/No Data", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)

    # --- DETAILED TABLE SECTION ---
    pdf.add_page() # Start table on new page if needed, or just flow
    # Actually let's force new page for clean table
    # pdf.add_page() 
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "Detailed Data Table", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    # Table Header
    pdf.set_font('Helvetica', 'B', 8)
    col_w_name = 30
    col_w_roll = 15
    col_w_date = 8 # Narrow cols for dates
    col_w_total = 15
    col_w_present = 15
    
    # Check width compatibility
    # Landscape A4 ~ 297mm width. Margins ~20mm. Usable ~ 277mm.
    # Name(30) + Roll(15) + Total(15) + Present(15) = 75mm
    # Remaining for dates: 277 - 75 = 202mm.
    # If 31 days: 202 / 31 = 6.5mm per col. 
    # If using 8mm per col, 31*8 = 248mm. Total = 75+248 = 323mm (Too wide).
    
    # Adjust widths for table layout
    total_dates = len(date_list)
    if total_dates > 20: 
        col_w_date = 6 # Decrease width for full month
        pdf.set_font('Helvetica', 'B', 6) # Smaller font
    
    pdf.cell(col_w_name, 8, "Name", border=1, align='C')
    pdf.cell(col_w_roll, 8, "Roll No", border=1, align='C')
    
    for d in date_list:
        pdf.cell(col_w_date, 8, d.strftime('%d'), border=1, align='C')
        
    pdf.cell(col_w_total, 8, "Total", border=1, align='C')
    pdf.cell(col_w_present, 8, "Days", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Table Body
    pdf.set_font('Helvetica', '', 7 if total_dates > 20 else 8)
    
    for row in attendance_data:
         # Name
        pdf.cell(col_w_name, 6, row['student'].user.first_name[:18], border=1) # Truncate long names
        pdf.cell(col_w_roll, 6, str(row['student'].roll_no), border=1, align='C')
        
        for cell in row['daily_data']:
            val = f"{cell['hours']:.1f}" if cell['hours'] > 0 else "-"
            pdf.cell(col_w_date, 6, val, border=1, align='C')
            
        pdf.cell(col_w_total, 6, f"{row['total_hours']:.1f}", border=1, align='C')
        pdf.cell(col_w_present, 6, str(row['days_present']), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

    # Output
    buffer = io.BytesIO()
    pdf.output(buffer, dest='S') # Write to buffer
    buffer.seek(0)
    return buffer
