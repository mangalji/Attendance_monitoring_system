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
    pdf = AttendancePDF(orientation='L', unit='mm', format='A4') 
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
   
    pdf.set_font('Helvetica', '', 12)
    period_str = f"Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
    pdf.cell(0, 10, period_str, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)


    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "Attendance Heatmap", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    
    cell_w = 8
    cell_h = 8
    margin_left = 40
    
   
    pdf.set_font('Helvetica', '', 8)
    
  
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    
  
    pdf.set_xy(start_x + margin_left, start_y)
    for d in date_list:
        pdf.cell(cell_w, 5, d.strftime('%d'), align='C', border=0)
    
    pdf.ln(5) 
    
    row_height = 10
    
    pdf.set_font('Helvetica', '', 9)
    
    for row in attendance_data:

        if pdf.get_y() > 180:
            pdf.add_page()
            pdf.set_y(20) 
        
        current_y = pdf.get_y()
        

        name = f"{row['student'].user.first_name} ({row['student'].roll_no})"
        pdf.set_xy(start_x, current_y)
        pdf.cell(margin_left, cell_h, name, border=0)
        

        current_x = start_x + margin_left
        for cell in row['daily_data']:
            pdf.set_xy(current_x, current_y)
            

            if cell['status_color'] == '#4caf50': 
                pdf.set_fill_color(76, 175, 80)
            elif cell['status_color'] == '#f44336': 
                pdf.set_fill_color(244, 67, 54)
            else: 
                pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(cell_w, cell_h, "", border=1, fill=True)
            current_x += cell_w
            
        pdf.ln(cell_h + 1) 


    pdf.ln(5)
    pdf.set_font('Helvetica', '', 10)
    
    pdf.set_fill_color(76, 175, 80)
    pdf.cell(5, 5, "", border=1, fill=True)
    pdf.cell(20, 5, " >= 6 Hrs", new_x="RIGHT")
    

    pdf.set_x(pdf.get_x() + 5)
    pdf.set_fill_color(244, 67, 54)
    pdf.cell(5, 5, "", border=1, fill=True)
    pdf.cell(20, 5, " < 6 Hrs", new_x="RIGHT")
    
   
    pdf.set_x(pdf.get_x() + 5)
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(5, 5, "", border=1, fill=True)
    pdf.cell(30, 5, " Absent/No Data", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)


    pdf.add_page() 
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "Detailed Data Table", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font('Helvetica', 'B', 8)
    col_w_name = 30
    col_w_roll = 15
    col_w_date = 8 
    col_w_total = 15
    col_w_present = 15
    

    total_dates = len(date_list)
    if total_dates > 20: 
        col_w_date = 6
        pdf.set_font('Helvetica', 'B', 6)
    pdf.cell(col_w_name, 8, "Name", border=1, align='C')
    pdf.cell(col_w_roll, 8, "Roll No", border=1, align='C')
    
    for d in date_list:
        pdf.cell(col_w_date, 8, d.strftime('%d'), border=1, align='C')
        
    pdf.cell(col_w_total, 8, "Total", border=1, align='C')
    pdf.cell(col_w_present, 8, "Days", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    
   
    pdf.set_font('Helvetica', '', 7 if total_dates > 20 else 8)
    
    for row in attendance_data:
    
        pdf.cell(col_w_name, 6, row['student'].user.first_name[:18], border=1) 
        pdf.cell(col_w_roll, 6, str(row['student'].roll_no), border=1, align='C')
        
        for cell in row['daily_data']:
            val = f"{cell['hours']:.1f}" if cell['hours'] > 0 else "-"
            pdf.cell(col_w_date, 6, val, border=1, align='C')
            
        pdf.cell(col_w_total, 6, f"{row['total_hours']:.1f}", border=1, align='C')
        pdf.cell(col_w_present, 6, str(row['days_present']), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

  
    buffer = io.BytesIO()
    pdf.output(buffer, dest='S')
    buffer.seek(0)
    return buffer
