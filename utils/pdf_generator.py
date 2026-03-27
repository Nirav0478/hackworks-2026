from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import date


def generate_receipt_pdf(driving, food, water, energy, savings, total_cost, total_water, inputs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.2 * inch,
        leftMargin=1.2 * inch,
        topMargin=1.2 * inch,
        bottomMargin=1 * inch,
    )

    # ── styles ──────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "title",
        fontSize=24,
        fontName="Courier-Bold",
        alignment=TA_CENTER,
        spaceAfter=16,
        spaceBefore=0,
        letterSpacing=5,
        textColor=colors.HexColor("#1a1a1a"),
    )
    subtitle_style = ParagraphStyle(
        "subtitle",
        fontSize=9,
        fontName="Courier",
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceBefore=4,
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "section",
        fontSize=11,
        fontName="Courier-Bold",
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a1a"),
    )
    caption_style = ParagraphStyle(
        "caption",
        fontSize=8,
        fontName="Courier-Oblique",
        textColor=colors.grey,
        spaceAfter=4,
        spaceBefore=2,
        leftIndent=8,
    )
    total_style = ParagraphStyle(
        "total",
        fontSize=12,
        fontName="Courier-Bold",
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=4,
        textColor=colors.HexColor("#1a1a1a"),
    )
    savings_style = ParagraphStyle(
        "savings",
        fontSize=9,
        fontName="Courier",
        spaceBefore=3,
        spaceAfter=3,
        leftIndent=12,
        textColor=colors.HexColor("#1e4d2b"),
    )
    tagline_style = ParagraphStyle(
        "tagline",
        fontSize=7.5,
        fontName="Courier-Oblique",
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceBefore=16,
    )

    def row(label, value):
        return Table(
            [[
                Paragraph(label, ParagraphStyle("l", fontSize=9, fontName="Courier", leading=13)),
                Paragraph(value, ParagraphStyle("r", fontSize=9, fontName="Courier-Bold", alignment=TA_RIGHT, leading=13))
            ]],
            colWidths=[4 * inch, 1.8 * inch],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ])
        )

    def divider():
        return HRFlowable(
            width="100%", thickness=0.5,
            color=colors.HexColor("#cccccc"),
            spaceAfter=8, spaceBefore=8
        )

    def thick_divider():
        return HRFlowable(
            width="100%", thickness=1.5,
            color=colors.HexColor("#333333"),
            spaceAfter=12, spaceBefore=4
        )

    # ── build story ──────────────────────────────────────────────────────────────
    story = []

    # Header
    story.append(Paragraph("THE GUILT RECEIPT", title_style))
    story.append(Spacer(1, 10))
    story.append(thick_divider())
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Week of {date.today().strftime('%B %d, %Y')}  |  Issued with love",
        subtitle_style
    ))
    story.append(divider())

    # Getting Around
    story.append(KeepTogether([
        Paragraph("GETTING AROUND", section_style),
        row(f"Driving ({inputs['miles_driven']} mi)", f"${driving['drive_cost']:.2f}"),
        row("Gas burned", f"{driving['gas_gallons']:.1f} gal"),
        row(f"Rideshare ({inputs['rideshare_trips']} trips)", f"${driving['rideshare_cost']:.2f}"),
        row("Time stuck in traffic", f"{driving['hours_in_traffic']} hrs"),
        Paragraph(f"  That's {driving['hours_in_traffic']} hours you'll never get back.", caption_style),
        divider(),
    ]))

    # What You Ate
    story.append(KeepTogether([
        Paragraph("WHAT YOU ATE", section_style),
        row(f"Beef meals ({inputs['burgers']}x)", f"{food['water_beef']:,} gal water"),
        row(f"Chicken meals ({inputs['chicken_meals']}x)", f"{food['water_chicken']:,} gal water"),
        Paragraph(f"  Your meals alone used {food['total_water_food']:,} gallons of water this week.", caption_style),
        divider(),
    ]))

    # Showers
    story.append(KeepTogether([
        Paragraph("SHOWERS", section_style),
        row(f"{inputs['showers_per_week']} showers x {inputs['shower_minutes']} min", f"{water['shower_gallons']:.0f} gal"),
        Paragraph(f"  That's enough to fill {water['bathtubs']} bathtubs.", caption_style),
        divider(),
    ]))

    # Home Energy
    story.append(KeepTogether([
        Paragraph("HOME ENERGY", section_style),
        row(f"AC ({inputs['ac_hours']} hrs)", f"${energy['ac_cost']:.2f}"),
        row(f"Phantom devices ({inputs['devices_left_on']} plugged in)", f"${energy['phantom_cost']:.2f}"),
        Paragraph(f"  = {energy['charger_equiv']} phone chargers left plugged in all month.", caption_style),
        divider(),
    ]))

    # Totals box
    story.append(Spacer(1, 8))
    story.append(thick_divider())
    story.append(Paragraph(f"Weekly Cost to You: ${total_cost:.2f}  |  That's ${total_cost * 52:,.0f}/year", total_style))
    story.append(Paragraph(f"Total Water Used: {total_water:,.0f} gallons", total_style))
    story.append(Paragraph(f"Time Lost to Traffic: {driving['hours_in_traffic']} hrs this week", total_style))
    story.append(thick_divider())
    story.append(Spacer(1, 8))

    # Small Swaps
    story.append(Paragraph("SMALL SWAPS, REAL SAVINGS", section_style))
    story.append(Paragraph(
        f"  [+] Replace 30% of driving with transit  ->  save ${savings['saved_drive']:.2f}/week (${savings['saved_drive_yearly']:.0f}/year)",
        savings_style
    ))
    story.append(Paragraph(
        f"  [+] Swap half your beef for chicken  ->  save {savings['saved_water_food']:,.0f} gal water/week",
        savings_style
    ))
    story.append(Paragraph(
        f"  [+] Cut shower by {savings['shower_minutes_cut']} min  ->  save {savings['saved_shower']:.0f} gallons this week",
        savings_style
    ))
    story.append(Paragraph(
        f"  [+] Turn AC down 25%  ->  save ${savings['saved_ac']:.2f}/week (${savings['saved_ac_yearly']:.0f}/year)",
        savings_style
    ))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=8))
    story.append(Paragraph(
        "Data sourced from EPA, USDA & EIA  |  Not here to judge. Just here to show you the math.",
        tagline_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer