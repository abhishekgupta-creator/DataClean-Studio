"""DataClean Studio application sidebar navigation."""

from urllib.parse import urlencode

from PySide6.QtCore import Qt, Signal, QRectF, QUrl, QPointF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QPolygonF,
    QDesktopServices,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSizePolicy,
    QDialog,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QMessageBox,
    QFormLayout,
)


SUPPORT_EMAIL = "abhigupta995522@gmail.com"


class DataCleanLogo(QWidget):
    """Custom spreadsheet cleaning logo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 42)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#DCE8FF"))
        painter.drawRoundedRect(
            QRectF(0, 0, 42, 42), 12, 12
        )

        painter.setBrush(QColor("#1264D8"))
        painter.drawRoundedRect(
            QRectF(8, 6, 23, 29), 4, 4
        )

        painter.setBrush(QColor("#FFFFFF"))

        for y in (12, 19, 26):
            for x in (12, 19, 26):
                painter.drawRoundedRect(
                    QRectF(x, y, 4, 4), 1, 1
                )

        painter.setPen(
            QPen(
                QColor("#1264D8"),
                3.5,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(25, 29, 34, 17)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1264D8"))

        polygon = QPolygonF([
            QPointF(23, 29),
            QPointF(30, 33),
            QPointF(35, 27),
            QPointF(28, 24),
        ])

        painter.drawPolygon(polygon)
        painter.end()


class FeedbackDialog(QDialog):
    """Help and feedback form."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Help & Feedback")
        self.setMinimumWidth(440)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 24, 25, 24)
        layout.setSpacing(15)

        title = QLabel("How can we help you?")
        title.setObjectName("pageTitle")

        description = QLabel(
            "Report a problem, suggest a feature, "
            "or share your feedback."
        )
        description.setWordWrap(True)
        description.setObjectName("placeholderDescription")

        layout.addWidget(title)
        layout.addWidget(description)

        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText(
            "Your email address (optional)"
        )

        self.type_input = QComboBox()
        self.type_input.addItems([
            "Report a Problem",
            "Suggest a Feature",
            "General Feedback",
            "Other",
        ])

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText(
            "Describe your problem or suggestion..."
        )
        self.message_input.setMinimumHeight(125)

        form.addRow("Name:", self.name_input)
        form.addRow("Your Email:", self.email_input)
        form.addRow("Message Type:", self.type_input)
        form.addRow("Message:", self.message_input)

        layout.addLayout(form)

        self.send_button = QPushButton("Send Feedback")
        self.send_button.setObjectName("heroImportButton")
        self.send_button.setMinimumHeight(44)
        self.send_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.send_button.clicked.connect(self.send_feedback)

        layout.addWidget(self.send_button)

        note = QLabel(
            "Gmail will open in your browser with "
            "your feedback ready to send."
        )
        note.setWordWrap(True)
        note.setObjectName("placeholderDescription")

        layout.addWidget(note)

    def send_feedback(self):
        """Open Gmail Compose with the feedback prefilled."""

        name = self.name_input.text().strip()
        user_email = self.email_input.text().strip()
        message = self.message_input.toPlainText().strip()
        message_type = self.type_input.currentText()

        # Validate name
        if not name:
            QMessageBox.warning(
                self,
                "Name Required",
                "Please enter your name."
            )
            return

        # Validate message
        if not message:
            QMessageBox.warning(
                self,
                "Message Required",
                "Please enter your message."
            )
            return

        # Validate optional email
        if user_email and (
            "@" not in user_email
            or "." not in user_email.split("@")[-1]
        ):
            QMessageBox.warning(
                self,
                "Invalid Email",
                "Please enter a valid email address."
            )
            return

        subject = f"DataClean Studio - {message_type}"

        body = (
            f"Name: {name}\n"
            f"User Email: {user_email or 'Not provided'}\n"
            f"Message Type: {message_type}\n\n"
            f"Message:\n{message}"
        )

        # Prepare Gmail Compose URL
        params = {
            "view": "cm",
            "fs": "1",
            "to": SUPPORT_EMAIL,
            "su": subject,
            "body": body,
        }

        gmail_url = (
            "https://mail.google.com/mail/?"
            + urlencode(params)
        )

        # Open Gmail in the default web browser
        opened = QDesktopServices.openUrl(
            QUrl(gmail_url)
        )

        if opened:
            QMessageBox.information(
                self,
                "Feedback Ready",
                "Gmail has been opened with your feedback.\n\n"
                "Please review your message and press Send."
            )
            self.accept()

        else:
            QMessageBox.warning(
                self,
                "Unable to Open Gmail",
                "Could not open your browser.\n\n"
                "Please check your default browser settings."
            )


class NavigationSidebar(QWidget):
    """Modern sidebar for the data cleaning workflow."""

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.buttons = {}
        self.active_page = "Home"

        self.setObjectName("sidebar")
        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True
        )
        self.setFixedWidth(255)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 25, 18, 22)
        layout.setSpacing(9)

        # Branding
        branding_layout = QHBoxLayout()
        branding_layout.setSpacing(10)

        logo_icon = DataCleanLogo()

        branding_text = QVBoxLayout()
        branding_text.setSpacing(2)

        logo = QLabel("DataClean Studio")
        logo.setObjectName("logo")

        tagline = QLabel("Excel & CSV Data Cleaner")
        tagline.setObjectName("tagline")

        branding_text.addWidget(logo)
        branding_text.addWidget(tagline)

        branding_layout.addWidget(logo_icon)
        branding_layout.addLayout(branding_text)
        branding_layout.addStretch()

        layout.addLayout(branding_layout)
        layout.addSpacing(38)

        # Workspace
        section_label = QLabel("WORKSPACE")
        section_label.setObjectName("sidebarSection")
        layout.addWidget(section_label)
        layout.addSpacing(8)

        navigation_items = [
            ("⌂", "Home"),
            ("＋", "Import Data"),
            ("▤", "Data Preview"),
            ("✧", "Data Cleaning"),
            ("⇄", "Data Transformation"),
            ("↓", "Export Data"),
        ]

        for icon, page_name in navigation_items:
            button = QPushButton(
                f"  {icon}      {page_name}"
            )

            button.setObjectName("navButton")
            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            button.setMinimumHeight(48)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, name=page_name:
                self.select_page(name)
            )

            self.buttons[page_name] = button
            layout.addWidget(button)

        # Keep footer area at the bottom
        layout.addStretch()

        # Help and Feedback
        feedback_button = QPushButton(
            "  ✉      Help & Feedback"
        )
        feedback_button.setObjectName("navButton")
        feedback_button.setMinimumHeight(48)
        feedback_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        feedback_button.clicked.connect(
            self.open_feedback
        )

        layout.addWidget(feedback_button)

        # Footer
        footer = QLabel("Created by Abhishek")
        footer.setObjectName("sidebarFooter")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)

        layout.addWidget(footer)

        self.select_page("Home")

    def open_feedback(self):
        dialog = FeedbackDialog(self)
        dialog.exec()

    def select_page(self, page_name):
        """Update selected navigation item."""

        if page_name not in self.buttons:
            return

        self.active_page = page_name

        for name, button in self.buttons.items():
            is_active = name == page_name

            button.setChecked(is_active)
            button.setProperty("active", is_active)

            button.style().unpolish(button)
            button.style().polish(button)

        self.page_changed.emit(page_name)