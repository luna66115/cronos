"""
styles.py – Qt stylesheet definitions for Cronos (Dark and Light themes).

Both themes follow the Catppuccin colour palette:
  Dark  → Catppuccin Mocha   (https://github.com/catppuccin/catppuccin)
  Light → Catppuccin Latte
"""

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #1e1e2e;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Ubuntu', 'Noto Sans', sans-serif;
    font-size: 13px;
}

QLabel {
    color: #cdd6f4;
    background: transparent;
}

QLabel#title_label {
    font-size: 20px;
    font-weight: bold;
    color: #89b4fa;
    letter-spacing: 1px;
}

QLabel#section_label {
    font-size: 11px;
    font-weight: bold;
    color: #6c7086;
    letter-spacing: 2px;
}

QLabel#status_label {
    font-size: 11px;
    color: #a6e3a1;
    padding: 2px 0;
}

QTableWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    gridline-color: #313244;
    selection-background-color: #45475a;
    outline: none;
}

QTableWidget::item {
    padding: 6px 10px;
    border: none;
    color: #cdd6f4;
}

QTableWidget::item:selected {
    background-color: #45475a;
    color: #cdd6f4;
}

QTableWidget::item:hover {
    background-color: #313244;
}

QHeaderView::section {
    background-color: #181825;
    color: #89b4fa;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #313244;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 1px;
}

QLineEdit, QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}

QLineEdit:hover, QComboBox:hover {
    border: 1px solid #585b70;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #89b4fa;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    selection-background-color: #45475a;
    color: #cdd6f4;
    outline: none;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
    color: #89b4fa;
}

QPushButton:pressed {
    background-color: #1e1e2e;
}

QPushButton:disabled {
    background-color: #252535;
    color: #45475a;
    border-color: #313244;
}

QPushButton#btn_add {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
}

QPushButton#btn_add:hover {
    background-color: #b4befe;
}

QPushButton#btn_delete {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
}

QPushButton#btn_delete:hover {
    background-color: #eba0ac;
}

QPushButton#btn_delete:disabled {
    background-color: #3d2535;
    color: #6c7086;
}

QPushButton#btn_save {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: none;
}

QPushButton#btn_save:hover {
    background-color: #94e2d5;
}

QPushButton#btn_save:disabled {
    background-color: #1e3028;
    color: #6c7086;
}

QPushButton#btn_clear {
    background-color: #fab387;
    color: #1e1e2e;
    border: none;
}

QPushButton#btn_clear:hover {
    background-color: #f9e2af;
}

QPushButton#btn_toggle_theme {
    background-color: transparent;
    border: 1px solid #45475a;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 16px;
    color: #f9e2af;
}

QPushButton#btn_toggle_theme:hover {
    background-color: #313244;
    border-color: #f9e2af;
}

QPushButton#btn_icon {
    background-color: transparent;
    border: 1px solid #45475a;
    border-radius: 6px;
    font-size: 14px;
    padding: 0;
    color: #cdd6f4;
}

QPushButton#btn_icon:hover {
    background-color: #313244;
    border-color: #89b4fa;
}

QPushButton#btn_refresh {
    background-color: #45475a;
    border: 2px solid #89b4fa;
    border-radius: 6px;
    font-size: 13px;
    padding: 4px 12px;
    color: #89b4fa;
    font-weight: bold;
}

QPushButton#btn_refresh:hover {
    background-color: #585b70;
    border-color: #b4befe;
    color: #b4befe;
}

QPushButton#btn_refresh:pressed {
    background-color: #1e1e2e;
}

QTextEdit {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    color: #a6e3a1;
    font-family: 'Ubuntu Mono', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
}

QCheckBox {
    color: #cdd6f4;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QSplitter::handle {
    background-color: #313244;
    height: 2px;
}

QScrollBar:vertical {
    background: #181825;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #89b4fa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QFrame#separator {
    background-color: #313244;
    max-height: 1px;
}

QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}
"""

LIGHT_STYLE = """
QMainWindow, QDialog {
    background-color: #eff1f5;
}

QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: 'Ubuntu', 'Noto Sans', sans-serif;
    font-size: 13px;
}

QLabel {
    color: #4c4f69;
    background: transparent;
}

QLabel#title_label {
    font-size: 20px;
    font-weight: bold;
    color: #1e66f5;
    letter-spacing: 1px;
}

QLabel#section_label {
    font-size: 11px;
    font-weight: bold;
    color: #9ca0b0;
    letter-spacing: 2px;
}

QLabel#status_label {
    font-size: 11px;
    color: #40a02b;
    padding: 2px 0;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    gridline-color: #e6e9ef;
    selection-background-color: #bcc0cc;
    outline: none;
}

QTableWidget::item {
    padding: 6px 10px;
    border: none;
    color: #4c4f69;
}

QTableWidget::item:selected {
    background-color: #bcc0cc;
    color: #4c4f69;
}

QTableWidget::item:hover {
    background-color: #e6e9ef;
}

QHeaderView::section {
    background-color: #ffffff;
    color: #1e66f5;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #ccd0da;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 1px;
}

QLineEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 6px 10px;
    color: #4c4f69;
    selection-background-color: #1e66f5;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #1e66f5;
}

QLineEdit:hover, QComboBox:hover {
    border: 1px solid #9ca0b0;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #1e66f5;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    selection-background-color: #bcc0cc;
    color: #4c4f69;
    outline: none;
}

QPushButton {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #ccd0da;
    border-color: #1e66f5;
    color: #1e66f5;
}

QPushButton:pressed {
    background-color: #bcc0cc;
}

QPushButton:disabled {
    background-color: #f0f2f5;
    color: #bcc0cc;
    border-color: #dce0e8;
}

QPushButton#btn_add {
    background-color: #1e66f5;
    color: #ffffff;
    border: none;
}

QPushButton#btn_add:hover {
    background-color: #04a5e5;
}

QPushButton#btn_delete {
    background-color: #d20f39;
    color: #ffffff;
    border: none;
}

QPushButton#btn_delete:hover {
    background-color: #e64553;
}

QPushButton#btn_delete:disabled {
    background-color: #f5dce2;
    color: #bcc0cc;
}

QPushButton#btn_save {
    background-color: #40a02b;
    color: #ffffff;
    border: none;
}

QPushButton#btn_save:hover {
    background-color: #179299;
}

QPushButton#btn_save:disabled {
    background-color: #ddf3d8;
    color: #bcc0cc;
}

QPushButton#btn_clear {
    background-color: #fe640b;
    color: #ffffff;
    border: none;
}

QPushButton#btn_clear:hover {
    background-color: #df8e1d;
}

QPushButton#btn_toggle_theme {
    background-color: transparent;
    border: 1px solid #ccd0da;
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 16px;
    color: #df8e1d;
}

QPushButton#btn_toggle_theme:hover {
    background-color: #e6e9ef;
    border-color: #df8e1d;
}

QPushButton#btn_icon {
    background-color: transparent;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    font-size: 14px;
    padding: 0;
    color: #4c4f69;
}

QPushButton#btn_icon:hover {
    background-color: #e6e9ef;
    border-color: #1e66f5;
}

QPushButton#btn_refresh {
    background-color: #dce8fd;
    border: 2px solid #1e66f5;
    border-radius: 6px;
    font-size: 13px;
    padding: 4px 12px;
    color: #1e66f5;
    font-weight: bold;
}

QPushButton#btn_refresh:hover {
    background-color: #c5d8fb;
    border-color: #04a5e5;
    color: #04a5e5;
}

QPushButton#btn_refresh:pressed {
    background-color: #bcc0cc;
}

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    color: #40a02b;
    font-family: 'Ubuntu Mono', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
}

QCheckBox {
    color: #4c4f69;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid #ccd0da;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #1e66f5;
    border-color: #1e66f5;
}

QSplitter::handle {
    background-color: #ccd0da;
    height: 2px;
}

QScrollBar:vertical {
    background: #e6e9ef;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #bcc0cc;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #1e66f5;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QFrame#separator {
    background-color: #ccd0da;
    max-height: 1px;
}

QToolTip {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 4px;
    padding: 4px 8px;
}
"""
