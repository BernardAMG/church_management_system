import os
import csv
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter

class PDFExporter:
    @staticmethod
    def export_html_to_pdf(html_content, output_path="report.pdf", parent=None):
        """
        Exports HTML string content to a PDF file with file dialog prompt.
        """
        try:
            if not output_path or output_path.endswith(".pdf"):
                file_path, _ = QFileDialog.getSaveFileName(
                    parent, "Save PDF", output_path or "report.pdf", "PDF Files (*.pdf)"
                )
                if not file_path:
                    return False, "Cancelled"
                output_path = file_path

            doc = QTextDocument()
            doc.setHtml(html_content)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(output_path)

            doc.print_(printer)
            if parent:
                QMessageBox.information(parent, "Success", f"PDF exported successfully to:\n{output_path}")
            return True, "PDF exported successfully!"
        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "Export Error", f"Failed to generate PDF:\n{e}")
            return False, f"Failed to generate PDF: {e}"


class DataExporter:
    @staticmethod
    def export_to_pdf(*args, **kwargs):
        parent = None
        title = "Report"
        headers = []
        rows = []
        filename = "report.pdf"

        # Handle positional args flexibility
        if len(args) == 2 and isinstance(args[0], str):
            return PDFExporter.export_html_to_pdf(args[0], args[1])

        if len(args) >= 1:
            parent = args[0] if hasattr(args[0], 'layout') or hasattr(args[0], 'parent') else None
        if len(args) >= 2 and isinstance(args[1], str):
            title = args[1]
        if len(args) >= 3 and isinstance(args[2], list):
            headers = args[2]
        if len(args) >= 4 and isinstance(args[3], list):
            rows = args[3]
        if len(args) >= 5 and isinstance(args[4], str):
            filename = args[4]

        header_cells = "".join([f"<th style='border: 1px solid #ddd; padding: 8px; background-color: #2c3e50; color: white;'>{h}</th>" for h in headers])
        row_html = ""
        for row in rows:
            cells = "".join([f"<td style='border: 1px solid #ddd; padding: 6px;'>{cell}</td>" for cell in row])
            row_html += f"<tr>{cells}</tr>"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h2 {{ text-align: center; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h2>{title}</h2>
            <table>
                <thead>
                    <tr>{header_cells}</tr>
                </thead>
                <tbody>
                    {row_html}
                </tbody>
            </table>
        </body>
        </html>
        """

        return PDFExporter.export_html_to_pdf(html_content, filename, parent=parent)

    @staticmethod
    def export_to_csv(*args, **kwargs):
        parent = None
        headers = []
        data = []
        filename = "export.csv"

        if len(args) >= 4:
            parent, headers, data, filename = args[0], args[1], args[2], args[3]
        elif len(args) == 3:
            headers, data, filename = args[0], args[1], args[2]

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                parent, "Save CSV", filename, "CSV Files (*.csv)"
            )
            if not file_path:
                return False, "Cancelled"

            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)

            if parent:
                QMessageBox.information(parent, "Success", f"CSV exported successfully to:\n{file_path}")
            return True, "CSV exported successfully!"
        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "Export Error", f"Failed to export CSV:\n{e}")
            return False, f"Failed to export CSV: {e}"

    @staticmethod
    def export_table_to_csv(headers, data, output_path):
        return DataExporter.export_to_csv(None, headers, data, output_path)
