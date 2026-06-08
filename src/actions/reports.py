from fpdf import FPDF
from datetime import datetime
from ..intelligence.ai_prompts import generate_insight_summary

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Feedback Intelligence - Weekly Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_weekly_report(stats_data: dict, top_issues: list, filepath: str = "report.pdf"):
    pdf = PDFReport()
    pdf.add_page()
    
    # Overview
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, f'Report Generated: {datetime.now().strftime("%Y-%m-%d")}', 0, 1)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 10, f'Total Feedback Processed: {stats_data.get("total_feedback", 0)}', 0, 1)
    
    sentiment = stats_data.get("sentiment_distribution", {})
    pdf.cell(0, 10, f'Positive: {sentiment.get("positive", 0)} | Negative: {sentiment.get("negative", 0)}', 0, 1)
    pdf.cell(0, 10, f'Total Bugs Flagged: {stats_data.get("total_bugs", 0)}', 0, 1)
    pdf.ln(5)
    
    # AI Executive Summary
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'AI Executive Summary', 0, 1)
    pdf.set_font('Helvetica', 'I', 10)
    
    ai_summary = generate_insight_summary(stats_data, top_issues)
    pdf.multi_cell(0, 6, ai_summary)
    pdf.ln(5)
    
    # Top Issues
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Top Urgent Issues / Bugs', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    
    if not top_issues:
        pdf.cell(0, 10, 'No urgent issues reported this week.', 0, 1)
    else:
        for issue in top_issues:
            # handle multi-line text safely and encode to handle weird chars (FPDF limitation)
            raw_text = issue.get("original_text", "").replace("\n", " ").replace("\r", "")
            # Basic ascii encoding to avoid FPDF charset errors
            clean_text = raw_text.encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 8, f"- [{issue.get('source')}] {clean_text}")
    
    pdf.output(filepath)
    return filepath
