"""
Shared components and utilities for card-based UI elements.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout

# Avatar constants
DEFAULT_AVATAR_SIZE = 64
AVATAR_CIRCLE_MARGIN = 4
AVATAR_FONT_SIZE_RATIO = 3  # Avatar size divided by this for font size
DEFAULT_AVATAR_SATURATION = 180
DEFAULT_AVATAR_VALUE = 220
FALLBACK_INITIAL = "?"

# Layout constants
DEFAULT_CARD_MARGINS = (16, 12, 16, 12)
DEFAULT_CARD_SPACING = 12
INFO_LAYOUT_SPACING = 4

# Shadow constants
DEFAULT_SHADOW_BLUR = 8
DEFAULT_SHADOW_OFFSET = (0, 2)
DEFAULT_SHADOW_ALPHA = 40

# Animation constants
DEFAULT_ANIMATION_DURATION = 150

# Card constants
DEFAULT_CARD_HEIGHT = 120

# Color constants
AVATAR_TEXT_COLOR = Qt.GlobalColor.white
TRANSPARENT_COLOR = Qt.GlobalColor.transparent
SHADOW_BASE_COLOR = (0, 0, 0)

# CSS property names
HOVERED_PROPERTY = "hovered"

# Animation property name
GEOMETRY_PROPERTY = b"geometry"


def create_avatar_pixmap(name: str, color: QColor, size: int = DEFAULT_AVATAR_SIZE) -> QPixmap:
    """Create a circular avatar with initial letter and background color."""
    pixmap = QPixmap(size, size)
    pixmap.fill(TRANSPARENT_COLOR)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw circle background
    painter.setBrush(QBrush(color))
    painter.setPen(QPen(TRANSPARENT_COLOR))
    circle_size = size - (AVATAR_CIRCLE_MARGIN * 2)
    painter.drawEllipse(AVATAR_CIRCLE_MARGIN, AVATAR_CIRCLE_MARGIN, circle_size, circle_size)

    # Draw initial letter
    painter.setPen(QPen(AVATAR_TEXT_COLOR))
    font = painter.font()
    font.setPixelSize(size // AVATAR_FONT_SIZE_RATIO)
    font.setBold(True)
    painter.setFont(font)

    initial = name[0].upper() if name else FALLBACK_INITIAL
    painter.drawText(
        AVATAR_CIRCLE_MARGIN, AVATAR_CIRCLE_MARGIN, circle_size, circle_size, Qt.AlignmentFlag.AlignCenter, initial
    )
    painter.end()

    return pixmap


def generate_color_from_name(
    name: str, saturation: int = DEFAULT_AVATAR_SATURATION, value: int = DEFAULT_AVATAR_VALUE
) -> QColor:
    """Generate a consistent color based on name hash."""
    hash_value = hash(name) % 360
    return QColor.fromHsv(hash_value, saturation, value)


def create_avatar_label(name: str, color: QColor, size: int = DEFAULT_AVATAR_SIZE) -> QLabel:
    """Create a QLabel with avatar pixmap."""
    label = QLabel()
    label.setFixedSize(size, size)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    pixmap = create_avatar_pixmap(name, color, size)
    label.setPixmap(pixmap)

    return label


def create_card_layout(margins=DEFAULT_CARD_MARGINS, spacing=DEFAULT_CARD_SPACING):
    """Create standard card layout structure.

    Returns:
        tuple: (main_layout, info_layout) where main_layout is QHBoxLayout
               and info_layout is QVBoxLayout for content
    """
    main_layout = QHBoxLayout()
    main_layout.setContentsMargins(*margins)
    main_layout.setSpacing(spacing)

    info_layout = QVBoxLayout()
    info_layout.setSpacing(INFO_LAYOUT_SPACING)

    return main_layout, info_layout


def apply_card_shadow(
    widget, blur_radius=DEFAULT_SHADOW_BLUR, offset=DEFAULT_SHADOW_OFFSET, color_alpha=DEFAULT_SHADOW_ALPHA
):
    """Apply drop shadow effect to a widget."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(QColor(*SHADOW_BASE_COLOR, color_alpha))
    shadow.setOffset(*offset)
    widget.setGraphicsEffect(shadow)


def setup_hover_animation(widget, duration=DEFAULT_ANIMATION_DURATION):
    """Setup hover animation for a widget.

    Returns:
        QPropertyAnimation: The animation object (caller should store reference)
    """
    animation = QPropertyAnimation(widget, GEOMETRY_PROPERTY)
    animation.setDuration(duration)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    return animation


def create_info_label(text: str, object_name: str) -> QLabel:
    """Create a label for card information with consistent styling."""
    label = QLabel(text)
    label.setObjectName(object_name)
    return label


class CardEventMixin:
    """Mixin for standard card hover behavior."""

    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
        self.setProperty(HOVERED_PROPERTY, True)
        self.style().unpolish(self)
        self.style().polish(self)

    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
        self.setProperty(HOVERED_PROPERTY, False)
        self.style().unpolish(self)
        self.style().polish(self)


def setup_card_widget(
    widget,
    height=DEFAULT_CARD_HEIGHT,
    cursor=Qt.CursorShape.PointingHandCursor,
    object_name=None,
    shadow=True,
    animation=True,
):
    """Apply standard card widget setup."""
    widget.setFixedHeight(height)
    widget.setCursor(cursor)

    if object_name:
        widget.setObjectName(object_name)

    if shadow:
        apply_card_shadow(widget)

    if animation:
        # Return animation for caller to store
        return setup_hover_animation(widget)

    return None
