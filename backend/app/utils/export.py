"""Export utilities for PDF and CSV generation."""

import csv
import io
from datetime import datetime
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class ExportService:
    """Service for exporting data to PDF and CSV."""

    def generate_csv(self, data: List[Dict[str, Any]], filename: str) -> io.StringIO:
        """Generate CSV from data."""
        output = io.StringIO()

        if not data:
            return output

        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        output.seek(0)
        return output

    def generate_pdf(self, data: List[Dict[str, Any]], title: str, filename: str) -> io.BytesIO:
        """Generate PDF from data."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = styles["Title"]
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated on: {timestamp}", styles["Normal"]))
        story.append(Spacer(1, 12))

        if not data:
            story.append(Paragraph("No data available", styles["Normal"]))
        else:
            # Create table
            headers = list(data[0].keys())
            table_data = [headers]

            for row in data:
                table_data.append([str(row.get(key, "")) for key in headers])

            table = Table(table_data)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 14),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            story.append(table)

        doc.build(story)
        buffer.seek(0)
        return buffer

    def prepare_products_data(self, products: List[Any]) -> List[Dict[str, Any]]:
        """Prepare products data for export."""
        return [
            {
                "ID": product.id,
                "Name": product.name,
                "Category": getattr(product, "category", "N/A"),
                "Price": f"₦{product.price:,.2f}" if hasattr(product, "price") else "N/A",
                "Site": product.site,
                "Tracked": "Yes" if product.is_tracked else "No",
                "Created": product.created_at.strftime("%Y-%m-%d"),
            }
            for product in products
        ]

    def prepare_services_data(self, services: List[Any]) -> List[Dict[str, Any]]:
        """Prepare utility services data for export."""
        return [
            {
                "ID": service.id,
                "Name": service.name,
                "Type": service.service_type,
                "Provider": service.provider,
                "Price": f"₦{service.base_price:,.2f}",
                "Billing": service.billing_type,
                "Cycle": service.billing_cycle or "N/A",
                "Tracked": "Yes" if service.is_tracked else "No",
                "Created": service.created_at.strftime("%Y-%m-%d"),
            }
            for service in services
        ]

    def prepare_properties_data(self, properties: List[Any]) -> List[Dict[str, Any]]:
        """Prepare properties data for export."""
        return [
            {
                "ID": property.id,
                "Name": property.name,
                "Type": property.property_type,
                "Location": property.location,
                "Price": f"₦{property.price:,.2f}",
                "Bedrooms": property.bedrooms or "N/A",
                "Listing Type": property.listing_type,
                "Tracked": "Yes" if property.is_tracked else "No",
                "Created": property.created_at.strftime("%Y-%m-%d"),
            }
            for property in properties
        ]

    def prepare_travel_data(self, items: List[Any], item_type: str) -> List[Dict[str, Any]]:
        """Prepare travel data for export."""
        if item_type == "flights":
            return [
                {
                    "ID": item.id,
                    "Route": f"{item.origin} → {item.destination}",
                    "Departure": item.departure_date.strftime("%Y-%m-%d"),
                    "Return": (
                        item.return_date.strftime("%Y-%m-%d") if item.return_date else "One-way"
                    ),
                    "Class": item.flight_class,
                    "Price": f"₦{item.price:,.2f}",
                    "Airline": item.airline or "N/A",
                    "Passengers": item.passengers,
                    "Tracked": "Yes" if item.is_tracked else "No",
                }
                for item in items
            ]
        else:  # hotels
            return [
                {
                    "ID": item.id,
                    "Name": item.name,
                    "Location": item.location,
                    "Check-in": item.check_in.strftime("%Y-%m-%d"),
                    "Check-out": item.check_out.strftime("%Y-%m-%d"),
                    "Room Type": item.room_type,
                    "Total Price": f"₦{item.total_price:,.2f}",
                    "Per Night": f"₦{item.price_per_night:,.2f}",
                    "Guests": item.guests,
                    "Rating": item.rating or "N/A",
                    "Tracked": "Yes" if item.is_tracked else "No",
                }
                for item in items
            ]


# Global export service instance
export_service = ExportService()
