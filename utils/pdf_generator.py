from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
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
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    # ── styles ──────────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        fontSize=22,
        fontName="Courier-Bold",
        alignment=TA_CENTER,
        spaceAfter=4,
        letterSpacing=4,
    )
    subtitle_style = ParagraphStyle(
        "subtitle",
        fontSize=9,
        fontName="Courier",
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "section",
        fontSize=11,
        fontName="Courier-Bold",
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#333333"),
    )
    caption_style = ParagraphStyle(
        "caption",
        fontSize=8,
        fontName="Courier",
        textColor=colors.grey,
        spaceAfter=6,
        leftIndent=8,
    )
    total_style = ParagraphStyle(
        "total",
        fontSize=12,
        fontName="Courier-Bold",
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=4,
        textColor=colors.HexColor("#1a1a1a"),
    )
    savings_style = ParagraphStyle(
        "savings",
        fontSize=9,
        fontName="Courier",
        spaceBefore=4,
        spaceAfter=4,
        leftIndent=8,
        textColor=colors.HexColor("#1e4d2b"),
    )
    tagline_style = ParagraphStyle(
        "tagline",
        fontSize=8,
        fontName="Courier",
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceBefore=12,
    )

    def row(label, value):
        return Table(
            [[Paragraph(label, ParagraphStyle("l", fontSize=9, fontName="Courier")),
              Paragraph(value, ParagraphStyle("r", fontSize=9, fontName="Courier-Bold", alignment=TA_RIGHT))]],
            colWidths=[4 * inch, 1.8 * inch],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
            ])
        )

    def divider():
        return HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=6, spaceBefore=6)

    # ── build content ────────────────────────────────────────────────────────────
    story = []

    story.append(Paragraph("THE GUILT RECEIPT", title_style))
    story.append(Paragraph(
        f"Week of {date.today().strftime('%B %d, %Y')}  |  Issued with love",
        subtitle_style
    ))
    story.append(divider())

    # Driving
    story.append(Paragraph("🚗 Getting Around", section_style))
    story.append(row(f"Driving ({inputs['miles_driven']} mi)", f"${driving['drive_cost']:.2f}"))
    story.append(row("Gas burned", f"{driving['gas_gallons']:.1f} gal"))
    story.append(row(f"Rideshare ({inputs['rideshare_trips']} trips)", f"${driving['rideshare_cost']:.2f}"))
    story.append(row("Time stuck in traffic", f"{driving['hours_in_traffic']} hrs"))
    story.append(Paragraph(f"  That's {driving['hours_in_traffic']} hours you'll never get back.", caption_style))
    story.append(divider())

    # Food
    story.append(Paragraph("🍔 What You Ate", section_style))
    story.append(row(f"Beef meals ({inputs['burgers']}x)", f"{food['water_beef']:,} gal water"))
    story.append(row(f"Chicken meals ({inputs['chicken_meals']}x)", f"{food['water_chicken']:,} gal water"))
    story.append(Paragraph(f"  Your meals alone used {food['total_water_food']:,} gallons of water this week.", caption_style))
    story.append(divider())

    # Showers
    story.append(Paragraph("🚿 Showers", section_style))
    story.append(row(f"{inputs['showers_per_week']} showers x {inputs['shower_minutes']} min", f"{water['shower_gallons']:.0f} gal"))
    story.append(Paragraph(f"  That's enough to fill {water['bathtubs']} bathtubs.", caption_style))
    story.append(divider())

    # Energy
    story.append(Paragraph("❄️  Home Energy", section_style))
    story.append(row(f"AC ({inputs['ac_hours']} hrs)", f"${energy['ac_cost']:.2f}"))
    story.append(row(f"Phantom devices ({inputs['devices_left_on']} plugged in)", f"${energy['phantom_cost']:.2f}"))
    story.append(Paragraph(f"  = {energy['charger_equiv']} phone chargers left plugged in all month.", caption_style))
    story.append(divider())

    # Totals
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Weekly Cost to You: ${total_cost:.2f}  |  That's ${total_cost * 52:,.0f}/year", total_style))
    story.append(Paragraph(f"Total Water Used: {total_water:,.0f} gallons", total_style))
    story.append(Paragraph(f"Time Lost to Traffic: {driving['hours_in_traffic']} hrs", total_style))
    story.append(divider())

    # Savings
    story.append(Paragraph("🌱 Small Swaps, Real Savings", section_style))
    story.append(Paragraph(
        f"  Replace 30% of driving with transit → save ${savings['saved_drive']:.2f}/week (${savings['saved_drive_yearly']:.0f}/year)",
        savings_style
    ))
    story.append(Paragraph(
        f"  Swap half your beef meals for chicken → save {savings['saved_water_food']:,.0f} gal water/week",
        savings_style
    ))
    story.append(Paragraph(
        f"  Cut shower by {savings['shower_minutes_cut']} min → save {savings['saved_shower']:.0f} gallons this week",
        savings_style
    ))
    story.append(Paragraph(
        f"  Turn AC down 25% → save ${savings['saved_ac']:.2f}/week (${savings['saved_ac_yearly']:.0f}/year)",
        savings_style
    ))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Data sourced from EPA, USDA & EIA  |  Not here to judge. Just here to show you the math.",
        tagline_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer