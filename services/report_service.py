import csv
from database.db_manager import DatabaseManager
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_financial_report_data(self, start_date="", end_date=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            query += " ORDER BY date ASC"
            cursor.execute(query, params)
            return cursor.fetchall()

    def export_financial_csv(self, filepath, start_date="", end_date=""):
        records = self.get_financial_report_data(start_date, end_date)
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Type", "Category", "Amount (GHS)", "Description"])
            for r in records:
                writer.writerow([r["id"], r["date"], r["type"], r["category"], r["amount"], r["description"]])

    def export_financial_pdf(self, filepath, start_date="", end_date=""):
        records = self.get_financial_report_data(start_date, end_date)
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, spaceAfter=10)
        elements.append(Paragraph("Church Financial Report", title_style))
        
        date_range_str = f"Period: {start_date or 'All Time'} to {end_date or 'Present'}"
        elements.append(Paragraph(date_range_str, styles['Normal']))
        elements.append(Spacer(1, 15))

        data = [["ID", "Date", "Type", "Category", "Amount (GH?)", "Description"]]
        total_income = 0.0
        total_expense = 0.0

        for r in records:
            amt = float(r["amount"])
            if r["type"] == "Income":
                total_income += amt
            else:
                total_expense += amt
            data.append([str(r["id"]), str(r["date"]), str(r["type"]), str(r["category"]), f"GH? {amt:,.2f}", str(r["description"] or "")])

        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A2B4C")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

        net = total_income - total_expense
        summary_text = f"<b>Total Income:</b> GH? {total_income:,.2f} | <b>Total Expenses:</b> GH? {total_expense:,.2f} | <b>Net Balance:</b> GH? {net:,.2f}"
        elements.append(Paragraph(summary_text, styles['Normal']))

        doc.build(elements)
