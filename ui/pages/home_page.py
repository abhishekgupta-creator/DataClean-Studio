
"""DataClean Studio - Modern Home Page."""

from PySide6.QtCore import Signal, Qt, QRectF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QLinearGradient,
    QPainterPath,
    QFont,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)


class HeroIllustration(QWidget):
    """Draw a lightweight spreadsheet cleaning illustration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 210)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Soft background glow
        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0, QColor("#E5F3FF"))
        gradient.setColorAt(1, QColor("#EAE7FF"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            QRectF(w * 0.08, h * 0.10, w * 0.84, h * 0.78)
        )

        # Laptop screen
        screen = QRectF(
            w * 0.20, h * 0.12,
            w * 0.63, h * 0.58
        )

        painter.setBrush(QColor("#2458A8"))
        painter.setPen(QPen(QColor("#174B96"), 2))
        painter.drawRoundedRect(screen, 15, 15)

        # Screen display
        display = screen.adjusted(9, 12, -9, -12)
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(display, 8, 8)

        # Spreadsheet header
        header = QRectF(
            display.x() + 8,
            display.y() + 10,
            display.width() - 16,
            20
        )

        painter.setBrush(QColor("#43C6A5"))
        painter.drawRoundedRect(header, 4, 4)

        # Spreadsheet cells
        start_x = display.x() + 10
        start_y = display.y() + 42
        cell_width = (display.width() - 24) / 3
        cell_height = 19

        for row in range(4):
            for col in range(3):
                rect = QRectF(
                    start_x + col * cell_width,
                    start_y + row * cell_height,
                    cell_width - 3,
                    cell_height - 3
                )

                painter.setBrush(
                    QColor("#DDF5EF")
                    if row == 0
                    else QColor("#EFF7FC")
                )
                painter.setPen(
                    QPen(QColor("#D5E7F0"), 1)
                )
                painter.drawRoundedRect(rect, 3, 3)

        # Laptop base
        base = QPainterPath()
        base.moveTo(w * 0.13, h * 0.73)
        base.lineTo(w * 0.89, h * 0.73)
        base.lineTo(w * 0.96, h * 0.81)
        base.lineTo(w * 0.07, h * 0.81)
        base.closeSubpath()

        painter.setBrush(QColor("#3675CB"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(base)

        # Excel file badge
        painter.setBrush(QColor("#18A66A"))
        painter.drawRoundedRect(
            QRectF(w * 0.02, h * 0.39, 65, 43),
            9, 9
        )

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.drawText(
            QRectF(w * 0.02, h * 0.39, 65, 43),
            Qt.AlignmentFlag.AlignCenter,
            "XLSX"
        )

        # CSV badge
        painter.setBrush(QColor("#7453DC"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            QRectF(w * 0.83, h * 0.48, 65, 43),
            9, 9
        )

        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(
            QRectF(w * 0.83, h * 0.48, 65, 43),
            Qt.AlignmentFlag.AlignCenter,
            "CSV"
        )

        # Cleaning sparkle marks
        painter.setPen(QPen(QColor("#2563EB"), 3))
        painter.drawLine(
            int(w * 0.89), int(h * 0.15),
            int(w * 0.92), int(h * 0.08)
        )
        painter.drawLine(
            int(w * 0.94), int(h * 0.21),
            int(w * 0.98), int(h * 0.19)
        )

        painter.end()


class HomePage(QWidget):
    """Main landing page of DataClean Studio."""

    import_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Create the modern home page layout."""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(45, 30, 45, 28)
        main_layout.setSpacing(24)

        # Hero section
        hero_card = QFrame()
        hero_card.setObjectName("heroCard")

        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(35, 25, 25, 25)
        hero_layout.setSpacing(15)

        # Left content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(13)

        welcome_badge = QLabel("👋  Welcome to")
        welcome_badge.setObjectName("welcomeBadge")

        welcome_badge.setFixedWidth(180)
        welcome_badge.setFixedHeight(38)

        title = QLabel("DataClean Studio")
        title.setObjectName("heroTitle")

        subtitle = QLabel("Excel & CSV Data Cleaner")
        subtitle.setObjectName("heroSubtitle")

        description = QLabel(
            "Import, clean and transform your data "
            "in a simple and user-friendly way."
        )
        description.setObjectName("heroDescription")
        description.setWordWrap(True)
        description.setMaximumWidth(440)

        import_button = QPushButton("⇧   Import Data")
        import_button.setObjectName("heroImportButton")
        import_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        import_button.setFixedSize(275, 58)
        import_button.clicked.connect(
            self.import_requested.emit
        )

        content_layout.addWidget(welcome_badge)
        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(5)
        content_layout.addWidget(description)
        content_layout.addSpacing(12)
        content_layout.addWidget(
            import_button,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        content_layout.addStretch()

        hero_layout.addLayout(content_layout, 5)

        # Right illustration
        illustration = HeroIllustration()
        hero_layout.addWidget(illustration, 5)

        main_layout.addWidget(hero_card, 5)

        # Feature section
        section_title = QLabel("What You Can Do")
        section_title.setObjectName("featureSectionTitle")

        main_layout.addWidget(section_title)

        features_layout = QHBoxLayout()
        features_layout.setSpacing(22)

        features = [
            (
                "▤",
                "Prepare Data",
                "Import Excel or CSV files.",
                "prepareCard"
            ),
            (
                "✧",
                "Clean Data",
                "Remove errors and duplicates.",
                "cleanCard"
            ),
            (
                "⇄",
                "Transform Data",
                "Modify and organize your data.",
                "transformCard"
            ),
        ]

        for icon, heading, description, object_name in features:
            card = self.create_feature_card(
                icon,
                heading,
                description,
                object_name
            )
            features_layout.addWidget(card)

        main_layout.addLayout(features_layout, 2)
        main_layout.addStretch()

    def create_feature_card(
        self,
        icon,
        heading,
        description,
        object_name
    ):
        """Create an individual feature card."""

        card = QFrame()
        card.setObjectName("featureCard")
        card.setProperty("featureType", object_name)

        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        card.setMinimumHeight(155)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setObjectName("featureIcon")
        icon_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        icon_label.setFixedSize(55, 55)

        heading_label = QLabel(heading)
        heading_label.setObjectName("featureHeading")
        heading_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label = QLabel(description)
        description_label.setObjectName("featureDescription")
        description_label.setWordWrap(True)
        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            icon_label,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )
        layout.addWidget(heading_label)
        layout.addWidget(description_label)
        layout.addStretch()

        return card
