"""
PDF Generator for Wells Fargo Bank Statements.
Creates PDF documents matching the Wells Fargo statement format.
"""

import os
from datetime import date, datetime
from typing import List, Optional
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, SimpleDocTemplate, Frame, PageTemplate, NextPageTemplate,
    Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, Flowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas

from .models import BankStatement, Transaction, StatementSummary


# Wells Fargo brand colors
WF_RED = colors.Color(0.8, 0.0, 0.0)
WF_YELLOW = colors.Color(1.0, 0.8, 0.0)
WF_DARK_RED = colors.Color(0.6, 0.0, 0.0)
LINK_BLUE = colors.Color(0.0, 0.0, 0.8)


class DrawnCheckbox(Flowable):
    """Simple drawn checkbox that works reliably in generated PDFs."""

    def __init__(self, checked: bool, size: float = 8):
        super().__init__()
        self.checked = checked
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        self.canv.setStrokeColor(colors.black)
        self.canv.setLineWidth(0.7)
        self.canv.rect(0, 0, self.size, self.size, stroke=1, fill=0)

        if self.checked:
            self.canv.setLineWidth(1.2)
            self.canv.line(self.size * 0.18, self.size * 0.45, self.size * 0.40, self.size * 0.18)
            self.canv.line(self.size * 0.40, self.size * 0.18, self.size * 0.82, self.size * 0.78)


class StatementPDFGenerator:
    """Generates Wells Fargo style bank statement PDFs."""
    
    def __init__(self, output_dir: str = "output", logo_path: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Logo path - default to templates folder
        if logo_path is None:
            self.logo_path = Path(__file__).parent.parent / "templates" / "wells-fargo-logo.png"
        else:
            self.logo_path = Path(logo_path)
        
        # Page dimensions
        self.page_width, self.page_height = letter
        self.margin = 0.5 * inch
        
        # Initialize styles
        self._init_styles()
    
    def _init_styles(self):
        """Initialize paragraph styles."""
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            'StatementTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=11,
            textColor=colors.black,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            'StatementBody',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            'SmallText',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=9,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            'LinkText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=LINK_BLUE,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            'RedText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
    
    def generate(self, statement: BankStatement) -> str:
        """
        Generate a PDF statement and return the file path.
        """
        # Store statement so header/footer callback can access it
        self._current_statement = statement

        # Build filename: Name_Wells_Fargo_Statement_Month_Year_YYYYMMDD_HHMMSS.pdf
        holder_name = statement.account_holder.name.replace(' ', '_')
        stmt_month = statement.period.end_date.strftime('%B')   # e.g. August
        stmt_year  = statement.period.end_date.strftime('%Y')   # e.g. 2021
        now        = datetime.now().strftime('%Y%m%d_%H%M%S')   # e.g. 20260325_204103
        filename   = f"{holder_name}_Wells_Fargo_Statement_{stmt_month}_{stmt_year}_{now}.pdf"
        filepath = self.output_dir / filename

        # Height reserved for the drawn header on pages 2+ (logo + rule + padding)
        HEADER_RESERVE = 0.85 * inch

        content_w = self.page_width - 2 * self.margin
        content_h = self.page_height - 2 * self.margin

        # Full-height frame for page 1
        frame_p1 = Frame(
            self.margin, self.margin,
            content_w, content_h,
            id='page1',
        )
        # Shorter frame for pages 2+ — leaves room for the canvas-drawn header
        frame_later = Frame(
            self.margin, self.margin,
            content_w, content_h - HEADER_RESERVE,
            id='later',
        )

        template_p1 = PageTemplate(
            id='FirstPage',
            frames=[frame_p1],
            onPage=self._add_header_footer,
        )
        template_later = PageTemplate(
            id='LaterPages',
            frames=[frame_later],
            onPage=self._add_later_page_header,
        )

        doc = BaseDocTemplate(
            str(filepath),
            pagesize=letter,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
        )
        doc.addPageTemplates([template_p1, template_later])

        # Build content
        story = []

        # Page 1: Account Summary
        story.extend(self._build_page1(statement))

        # Switch to the later-pages template, then page-break
        story.append(NextPageTemplate('LaterPages'))
        story.append(PageBreak())
        story.extend(self._build_transaction_pages(statement))

        doc.build(story)

        return str(filepath)
    
    def _build_page1(self, statement: BankStatement) -> List:
        """Build the first page with account summary."""
        elements = []
        
        # Header section
        elements.append(self._create_header(statement, 1))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Two-column layout: Customer info (left) and Questions (right)
        left_content = self._build_customer_info(statement)
        right_content = self._build_questions_section()
        
        header_table = Table(
            [[left_content, right_content]],
            colWidths=[3.5 * inch, 4 * inch]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LINEAFTER', (0, 0), (0, 0), 1.0, colors.black),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # You and Wells Fargo + Account Options
        elements.append(HRFlowable(width="100%", thickness=1.0, color=colors.black))
        elements.append(Spacer(1, 0.1 * inch))
        
        left_fargo = self._build_you_and_wells_fargo()
        right_options = self._build_account_options()
        
        middle_table = Table(
            [[left_fargo, right_options]],
            colWidths=[3.5 * inch, 4 * inch]
        )
        middle_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(middle_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Statement Period Activity Summary + Account Info
        elements.append(HRFlowable(width="100%", thickness=1.0, color=colors.black))
        elements.append(Spacer(1, 0.1 * inch))
        
        left_summary = self._build_activity_summary(statement)
        right_account = self._build_account_info(statement)
        
        summary_table = Table(
            [[left_summary, right_account]],
            colWidths=[3.5 * inch, 4 * inch]
        )
        summary_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Overdraft Protection
        elements.append(HRFlowable(width="100%", thickness=1.0, color=colors.black))
        elements.append(self._build_overdraft_section())
        
        return elements
    
    def _create_header(self, statement: BankStatement, page_num: int) -> Table:
        """Create the page header with title and logo."""
        # Title section
        title = Paragraph(statement.account_info.account_type, self.styles['StatementTitle'])
        date_text = Paragraph(
            f"{statement.period.end_date.strftime('%B %d, %Y')} ■ Page {page_num} of {statement.page_count}",
            self.styles['StatementBody']
        )
        
        left_col = [title, date_text]
        
        # Load Wells Fargo logo image
        if self.logo_path.exists():
            # Logo is 920x500 pixels (aspect ratio ~1.84:1), scaled up 50%
            logo = Image(str(self.logo_path), width=1.5*inch, height=0.81*inch)
        else:
            # Fallback to text if logo not found
            logo_table = Table(
                [['WELLS', 'FARGO']],
                colWidths=[0.5 * inch, 0.5 * inch],
                rowHeights=[0.4 * inch]
            )
            logo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), WF_RED),
                ('BACKGROUND', (1, 0), (1, 0), WF_YELLOW),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('TEXTCOLOR', (1, 0), (1, 0), WF_RED),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            logo = logo_table
        
        header_data = [[
            [left_col[0], left_col[1]], 
            logo
        ]]
        
        header = Table(header_data, colWidths=[6 * inch, 1.5 * inch])
        header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        return header
    
    def _build_customer_info(self, statement: BankStatement) -> List:
        """Build customer name and address section."""
        elements = []
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(statement.account_holder.name, self.styles['StatementBody']))
        elements.append(Paragraph(statement.account_holder.address.format_line1(), self.styles['StatementBody']))
        elements.append(Paragraph(statement.account_holder.address.format_line2(), self.styles['StatementBody']))
        return elements
    
    def _build_questions_section(self) -> List:
        """Build the Questions? contact information section."""
        elements = []
        
        elements.append(Paragraph("<b>Questions?</b>", self.styles['RedText']))
        elements.append(Spacer(1, 0.1 * inch))
        
        contact_text = """
        <b>Available by phone</b> 24 hours a day, 7 days a week:<br/>
        We accept all relay calls, including 711<br/>
        <b>1-800-TO-WELLS</b> (1-800-869-3557)<br/>
        <b>En español:</b> 1-877-727-2932<br/><br/>
        <b>Online:</b> wellsfargo.com<br/><br/>
        <b>Write:</b> Wells Fargo Bank, N.A. (347)<br/>
        P.O. Box 6995<br/>
        Portland, OR 97228-6995
        """
        elements.append(Paragraph(contact_text, self.styles['SmallText']))
        
        return elements
    
    def _build_you_and_wells_fargo(self) -> List:
        """Build You and Wells Fargo section."""
        elements = []
        elements.append(Paragraph("<b>You and Wells Fargo</b>", self.styles['SectionHeader']))
        text = "Thank you for being a loyal Wells Fargo customer. We value your trust in our company and look forward to continuing to serve you with your financial needs."
        elements.append(Paragraph(text, self.styles['SmallText']))
        return elements
    
    def _build_account_options(self) -> List:
        """Build Account Options section with checkboxes."""
        elements = []
        elements.append(Paragraph("<b>Account options</b>", self.styles['SectionHeader']))
        
        intro = "A check mark in the box indicates you have these convenient services with your account(s). Go to wellsfargo.com or call the number above if you have questions or if you would like to add new services."
        elements.append(Paragraph(intro, self.styles['SmallText']))
        elements.append(Spacer(1, 0.1 * inch))
        
        option_pairs = [
            ((True, 'Online Banking'), (True, 'Direct Deposit')),
            ((True, 'Online Bill Pay'), (True, 'Auto Transfer/Payment')),
            ((True, 'Online Statements'), (False, 'Overdraft Protection')),
            ((False, 'Mobile Banking'), (True, 'Debit Card')),
            ((False, 'My Spending Report'), (False, 'Overdraft Service')),
        ]

        options_data = []
        for left_option, right_option in option_pairs:
            options_data.append([
                DrawnCheckbox(left_option[0], size=8),
                Paragraph(left_option[1], self.styles['SmallText']),
                DrawnCheckbox(right_option[0], size=8),
                Paragraph(right_option[1], self.styles['SmallText']),
            ])

        options_table = Table(options_data, colWidths=[0.16 * inch, 1.64 * inch, 0.16 * inch, 1.64 * inch])
        options_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(options_table)
        
        return elements
    
    def _build_activity_summary(self, statement: BankStatement) -> List:
        """Build Statement period activity summary."""
        elements = []
        elements.append(Paragraph("<b>Statement period activity summary</b>", self.styles['SectionHeader']))
        
        summary = statement.summary
        period = statement.period
        
        # Summary table
        summary_data = [
            [f'Beginning balance on {period.start_date.strftime("%m/%d")}', 
             f'${summary.beginning_balance:,.2f}'],
            ['Deposits/Additions', f'{summary.total_deposits:,.2f}'],
            ['Withdrawals/Subtractions', f'- {summary.total_withdrawals:,.2f}'],
            [f'Ending balance on {period.end_date.strftime("%m/%d")}', 
             f'${summary.ending_balance:,.2f}'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.2 * inch, 1 * inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('LINEABOVE', (0, 3), (-1, 3), 0.5, colors.black),
        ]))
        elements.append(summary_table)
        
        return elements
    
    def _build_account_info(self, statement: BankStatement) -> List:
        """Build account info section."""
        elements = []
        
        info = statement.account_info
        holder = statement.account_holder
        state_name = self._get_state_name(holder.address.state)
        
        elements.append(Spacer(1, 0.2 * inch))
        
        info_data = [
            [Paragraph('<font color="red"><b>Account number:</b></font>', self.styles['SmallText']), 
             info.account_number],
            ['', holder.name],
            ['', ''],
            ['', Paragraph(f'<i>{state_name} account terms and conditions apply.</i>', self.styles['SmallText'])],
            ['', ''],
            [Paragraph('<b>For Direct Deposit use</b>', self.styles['SmallText']), ''],
            [Paragraph('<b>Routing Number (RTN):</b>', self.styles['SmallText']), info.routing_number],
        ]
        
        info_table = Table(info_data, colWidths=[1.5 * inch, 2.5 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(info_table)
        
        return elements

    def _get_state_name(self, state_code: str) -> str:
        state_names = {
            'AL': 'Alabama',
            'AK': 'Alaska',
            'AZ': 'Arizona',
            'AR': 'Arkansas',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'HI': 'Hawaii',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'IA': 'Iowa',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'ME': 'Maine',
            'MD': 'Maryland',
            'MA': 'Massachusetts',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MS': 'Mississippi',
            'MO': 'Missouri',
            'MT': 'Montana',
            'NE': 'Nebraska',
            'NV': 'Nevada',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NY': 'New York',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VT': 'Vermont',
            'VA': 'Virginia',
            'WA': 'Washington',
            'WV': 'West Virginia',
            'WI': 'Wisconsin',
            'WY': 'Wyoming',
            'DC': 'District of Columbia',
        }
        return state_names.get((state_code or '').upper(), state_code or 'State')
    
    def _build_overdraft_section(self) -> Paragraph:
        """Build overdraft protection disclaimer."""
        text = """
        <b>Overdraft Protection</b><br/>
        This account is not currently covered by Overdraft Protection. If you would like more information regarding Overdraft Protection and eligibility requirements, please call the number listed on your statement or visit your Wells Fargo branch.
        """
        return Paragraph(text, self.styles['SmallText'])
    
    def _build_transaction_pages(self, statement: BankStatement) -> List:
        """Build transaction history pages."""
        elements = []
        
        # Transaction history header
        elements.append(Paragraph("<b>Transaction history</b>", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Build transaction table
        transactions = statement.transactions
        
        # Table header
        header = ['Date', 'Check\nNumber', 'Description', 'Deposits/\nAdditions', 
                  'Withdrawals/\nSubtractions', 'Ending daily\nbalance']
        
        # Build rows
        table_data = [header]
        
        for txn in transactions:
            row = [
                txn.date.strftime('%m/%d'),
                txn.check_number or '',
                txn.description[:50] + ('...' if len(txn.description) > 50 else ''),
                f'{txn.deposit_amount:,.2f}' if txn.deposit_amount else '',
                f'{txn.withdrawal_amount:,.2f}' if txn.withdrawal_amount else '',
                f'{txn.running_balance:,.2f}' if txn.running_balance != 0.0 else ''
            ]
            table_data.append(row)
        
        # Create table
        col_widths = [0.5*inch, 0.5*inch, 3.2*inch, 0.9*inch, 0.9*inch, 0.9*inch]
        
        txn_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        txn_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Date and check number centered
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),     # Description left
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),   # Amounts right
            
            # Grid
            ('LINEBELOW', (0, 0), (-1, 0), 1.0, colors.black),
            ('LINEBELOW', (0, 1), (-1, -2), 1.0, colors.lightgrey),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(txn_table)
        
        return elements
    
    def _add_header_footer(self, canvas_obj: canvas.Canvas, doc):
        """Add header and footer to each page (page 1 only, via onFirstPage)."""
        canvas_obj.saveState()
        canvas_obj.restoreState()

    def _add_later_page_header(self, canvas_obj: canvas.Canvas, doc):
        """Draw the date / page-number header and logo on pages 2+."""
        canvas_obj.saveState()

        statement = getattr(self, '_current_statement', None)
        page_num = doc.page

        # --- Date and page indicator (top-left) ---
        if statement is not None:
            date_str = statement.period.end_date.strftime('%B %d, %Y')
            page_str = f"{date_str}  \u25a0  Page {page_num} of {statement.page_count}"
        else:
            page_str = f"Page {page_num}"

        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.black)
        canvas_obj.drawString(
            self.margin,
            self.page_height - self.margin - 10,
            page_str,
        )

        # --- Wells Fargo logo (top-right) ---
        logo_w = 1.1 * inch
        logo_h = 0.60 * inch
        logo_x = self.page_width - self.margin - logo_w
        logo_y = self.page_height - self.margin - logo_h

        if self.logo_path.exists():
            canvas_obj.drawImage(
                str(self.logo_path),
                logo_x, logo_y,
                width=logo_w, height=logo_h,
                preserveAspectRatio=True,
                anchor='ne',
            )
        else:
            # Fallback: red box with "WELLS FARGO" text
            canvas_obj.setFillColor(WF_RED)
            canvas_obj.rect(logo_x, logo_y, logo_w, logo_h, fill=1, stroke=0)
            canvas_obj.setFillColor(colors.white)
            canvas_obj.setFont('Helvetica-Bold', 8)
            canvas_obj.drawCentredString(
                logo_x + logo_w / 2,
                logo_y + logo_h / 2 - 4,
                'WELLS FARGO',
            )

        # --- Horizontal rule below header ---
        rule_y = self.page_height - self.margin - logo_h - 4
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(1.0)
        canvas_obj.line(self.margin, rule_y, self.page_width - self.margin, rule_y)

        canvas_obj.restoreState()
