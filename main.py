"""
main.py – Cronos: a GUI crontab manager built with PyQt6.
"""

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QComboBox,
    QPushButton, QTextEdit, QSplitter, QCheckBox, QFrame,
    QHeaderView, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtSvgWidgets import QSvgWidget

from styles import DARK_STYLE, LIGHT_STYLE
from i18n import tr, set_language, get_language, detect_system_language, Language
from cron_manager import (
    CronJob, read_crontab, write_crontab, backup_crontab,
    validate_cron_expression, HAS_CRONITER,
    _build_minute_presets, _build_hour_presets, _build_weekday_presets,
)

# How long (ms) the status bar message stays visible
_STATUS_TIMEOUT_MS = 3000


class CronGUI(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.jobs: list[CronJob] = []
        self.selected_index: int = -1
        self.dark_mode: bool = True
        self.editing_existing: bool = False

        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(900, 650)
        self.resize(1050, 720)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "cronos_icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()
        self._apply_theme()
        self._load_jobs()

        # Debounce timer for the live preview
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)

        # Auto-hide timer for the status label
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._clear_status)

        # Auto-refresh timer: update "Next Run" column every 60 seconds
        self._auto_refresh_timer = QTimer()
        self._auto_refresh_timer.timeout.connect(self._refresh_table)
        self._auto_refresh_timer.start(60_000)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        root.addLayout(self._build_header())
        root.addWidget(self._make_separator())

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(6)
        splitter.addWidget(self._build_table_panel())
        splitter.addWidget(self._build_form_panel())
        splitter.setSizes([360, 300])
        root.addWidget(splitter)

        # Status bar
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("status_label")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(self.lbl_status)

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(10)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "cronos_icon.svg")
        if os.path.exists(icon_path):
            svg_icon = QSvgWidget(icon_path)
            svg_icon.setFixedSize(36, 36)
            header.addWidget(svg_icon)

        title = QLabel(tr("app_title"))
        title.setObjectName("title_label")
        header.addWidget(title)
        header.addStretch()

        if not HAS_CRONITER:
            warn = QLabel(tr("warn_no_croniter"))
            warn.setStyleSheet("color: #f9e2af; font-size: 11px;")
            header.addWidget(warn)

        self.btn_refresh = QPushButton(tr("btn_refresh"))
        self.btn_refresh.setObjectName("btn_refresh")
        self.btn_refresh.setToolTip(tr("tooltip_refresh"))
        self.btn_refresh.setFixedHeight(30)
        self.btn_refresh.clicked.connect(self._refresh_from_disk)
        header.addWidget(self.btn_refresh)

        # Language toggle button
        self.btn_lang = QPushButton(self._lang_button_label())
        self.btn_lang.setObjectName("btn_toggle_theme")  # reuse pill style
        self.btn_lang.setToolTip("Switch language / Sprache wechseln")
        self.btn_lang.setFixedHeight(30)
        self.btn_lang.clicked.connect(self._toggle_language)
        header.addWidget(self.btn_lang)

        self.btn_theme = QPushButton("🌙")
        self.btn_theme.setObjectName("btn_toggle_theme")
        self.btn_theme.setToolTip(tr("tooltip_theme_to_light"))
        self.btn_theme.setFixedSize(80, 30)
        self.btn_theme.clicked.connect(self._toggle_theme)
        header.addWidget(self.btn_theme)

        return header

    def _lang_button_label(self) -> str:
        return "🇩🇪 DE" if get_language() == "de" else "🇬🇧 EN"

    def _build_table_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        hdr = QHBoxLayout()
        self.lbl_section_jobs = QLabel(tr("section_jobs"))
        self.lbl_section_jobs.setObjectName("section_label")
        hdr.addWidget(self.lbl_section_jobs)
        hdr.addStretch()
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("font-size: 11px; color: #6c7086;")
        hdr.addWidget(self.lbl_count)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self._update_table_headers()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 32)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(6, 160)
        self.table.setMinimumHeight(200)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.table.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

        return panel

    def _update_table_headers(self) -> None:
        self.table.setHorizontalHeaderLabels([
            tr("col_enabled"),
            tr("col_description"),
            tr("col_minute"),
            tr("col_hour"),
            tr("col_day_month_dow"),
            tr("col_command"),
            tr("col_next_run"),
        ])

    def _build_form_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(8)

        hdr = QHBoxLayout()
        self.lbl_form_title = QLabel(tr("section_new_job"))
        self.lbl_form_title.setObjectName("section_label")
        hdr.addWidget(self.lbl_form_title)
        hdr.addStretch()
        layout.addLayout(hdr)

        layout.addWidget(self._make_separator())

        # Row 1 – description + enabled
        row1 = QHBoxLayout()
        self.lbl_desc = QLabel(tr("label_description"))
        row1.addWidget(self.lbl_desc)
        self.inp_desc = QLineEdit()
        self.inp_desc.setPlaceholderText(tr("placeholder_description"))
        row1.addWidget(self.inp_desc, 3)
        self.chk_enabled = QCheckBox(tr("label_enabled"))
        self.chk_enabled.setChecked(True)
        row1.addWidget(self.chk_enabled)
        layout.addLayout(row1)

        # Row 2 – time fields
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        self.lbl_minute = QLabel(tr("label_minute"))
        self.combo_minute = self._make_preset_combo(_build_minute_presets())
        row2.addWidget(self.lbl_minute)
        row2.addWidget(self.combo_minute, 2)

        self.lbl_hour = QLabel(tr("label_hour"))
        self.combo_hour = self._make_preset_combo(_build_hour_presets())
        row2.addWidget(self.lbl_hour)
        row2.addWidget(self.combo_hour, 2)

        self.inp_day = QLineEdit("*")
        self.inp_day.setFixedWidth(55)
        self.inp_day.textChanged.connect(self._schedule_preview)
        self.lbl_day = QLabel(tr("label_day"))
        row2.addWidget(self.lbl_day)
        row2.addWidget(self.inp_day)

        self.inp_month = QLineEdit("*")
        self.inp_month.setFixedWidth(55)
        self.inp_month.textChanged.connect(self._schedule_preview)
        self.lbl_month = QLabel(tr("label_month"))
        row2.addWidget(self.lbl_month)
        row2.addWidget(self.inp_month)

        self.lbl_weekday = QLabel(tr("label_weekday"))
        self.combo_weekday = self._make_preset_combo(_build_weekday_presets())
        row2.addWidget(self.lbl_weekday)
        row2.addWidget(self.combo_weekday, 2)

        layout.addLayout(row2)

        # Row 3 – command
        row3 = QHBoxLayout()
        self.lbl_command = QLabel(tr("label_command"))
        row3.addWidget(self.lbl_command)
        self.inp_command = QLineEdit()
        self.inp_command.setPlaceholderText(tr("placeholder_command"))
        row3.addWidget(self.inp_command, 1)
        layout.addLayout(row3)

        # Row 4 – action buttons
        row4 = QHBoxLayout()
        row4.setSpacing(8)

        self.btn_add = QPushButton(tr("btn_add"))
        self.btn_add.setObjectName("btn_add")
        self.btn_add.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_add.clicked.connect(self._add_job)
        row4.addWidget(self.btn_add)

        self.btn_update = QPushButton(tr("btn_save"))
        self.btn_update.setObjectName("btn_save")
        self.btn_update.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_update.setEnabled(False)
        self.btn_update.clicked.connect(self._save_job)
        row4.addWidget(self.btn_update)

        self.btn_delete = QPushButton(tr("btn_delete"))
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._delete_job)
        row4.addWidget(self.btn_delete)

        self.btn_clear = QPushButton(tr("btn_clear"))
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_clear.clicked.connect(self._clear_form)
        row4.addWidget(self.btn_clear)

        layout.addLayout(row4)

        # Preview
        if HAS_CRONITER:
            self.lbl_preview_section = QLabel(tr("section_preview"))
            self.lbl_preview_section.setObjectName("section_label")
            layout.addWidget(self.lbl_preview_section)
            self.txt_preview = QTextEdit()
            self.txt_preview.setReadOnly(True)
            self.txt_preview.setMaximumHeight(90)
            self.txt_preview.setPlaceholderText(tr("placeholder_preview"))
            layout.addWidget(self.txt_preview)
        else:
            self.txt_preview = None
            self.lbl_preview_section = None

        return panel

    def _make_preset_combo(self, presets: list) -> QComboBox:
        combo = QComboBox()
        combo.setEditable(True)
        for label, _ in presets:
            combo.addItem(label)
        combo.setCurrentIndex(0)
        combo.currentIndexChanged.connect(
            lambda idx, c=combo, p=presets: self._on_preset_changed(c, p, idx)
        )
        combo.currentTextChanged.connect(self._schedule_preview)
        return combo

    @staticmethod
    def _make_separator() -> QFrame:
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        return sep

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def _toggle_language(self) -> None:
        new_lang: Language = "en" if get_language() == "de" else "de"
        set_language(new_lang)
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update all visible strings after a language switch."""
        self.setWindowTitle(tr("app_title"))

        # Header
        self.btn_refresh.setText(tr("btn_refresh"))
        self.btn_refresh.setToolTip(tr("tooltip_refresh"))
        self.btn_lang.setText(self._lang_button_label())
        if self.dark_mode:
            self.btn_theme.setToolTip(tr("tooltip_theme_to_light"))
        else:
            self.btn_theme.setToolTip(tr("tooltip_theme_to_dark"))

        # Table
        self.lbl_section_jobs.setText(tr("section_jobs"))
        self._update_table_headers()

        # Form labels
        self.lbl_form_title.setText(
            tr("section_edit_job") if self.editing_existing else tr("section_new_job")
        )
        self.lbl_desc.setText(tr("label_description"))
        self.inp_desc.setPlaceholderText(tr("placeholder_description"))
        self.chk_enabled.setText(tr("label_enabled"))
        self.lbl_minute.setText(tr("label_minute"))
        self.lbl_hour.setText(tr("label_hour"))
        self.lbl_day.setText(tr("label_day"))
        self.lbl_month.setText(tr("label_month"))
        self.lbl_weekday.setText(tr("label_weekday"))
        self.lbl_command.setText(tr("label_command"))
        self.inp_command.setPlaceholderText(tr("placeholder_command"))

        # Buttons
        self.btn_add.setText(tr("btn_add"))
        self.btn_update.setText(tr("btn_save"))
        self.btn_delete.setText(tr("btn_delete"))
        self.btn_clear.setText(tr("btn_clear"))

        # Rebuild combo presets with new language labels
        self._rebuild_combo(self.combo_minute, _build_minute_presets())
        self._rebuild_combo(self.combo_hour, _build_hour_presets())
        self._rebuild_combo(self.combo_weekday, _build_weekday_presets())

        # Preview section
        if self.lbl_preview_section:
            self.lbl_preview_section.setText(tr("section_preview"))
        if self.txt_preview:
            self.txt_preview.setPlaceholderText(tr("placeholder_preview"))
            self._update_preview()

        # Refresh table to re-translate job count label
        self._refresh_table()

    def _rebuild_combo(self, combo: QComboBox, new_presets: list) -> None:
        """Replace combo items with freshly translated labels, preserving the cron value.

        Strategy: save the current index (position in the preset list).  For a
        custom/raw value that doesn't match any preset, save the raw text and
        restore it after rebuilding.
        """
        current_index = combo.currentIndex()
        current_text  = combo.currentText()

        combo.blockSignals(True)
        combo.clear()
        for label, _ in new_presets:
            combo.addItem(label)

        # Reconnect signal with the new presets list
        combo.currentIndexChanged.disconnect()
        combo.currentIndexChanged.connect(
            lambda idx, c=combo, p=new_presets: self._on_preset_changed(c, p, idx)
        )

        # If the saved index is valid and not the "Custom" sentinel, restore it.
        # Index 0 is always a real preset ("Every minute" / "Jede Minute" etc.)
        last_preset_idx = len(new_presets) - 1  # "Custom / Benutzerdefiniert"
        if 0 <= current_index < last_preset_idx:
            # It was a named preset – restore by position (same cron value)
            combo.setCurrentIndex(current_index)
        else:
            # It was a custom raw value – keep the raw text
            combo.setCurrentIndex(last_preset_idx)
            combo.setEditText(current_text)

        combo.blockSignals(False)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def _apply_theme(self) -> None:
        if self.dark_mode:
            self.setStyleSheet(DARK_STYLE)
            self.btn_theme.setText("🌙")
            self.btn_theme.setToolTip(tr("tooltip_theme_to_light"))
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self.btn_theme.setText("☀️")
            self.btn_theme.setToolTip(tr("tooltip_theme_to_dark"))
        self._refresh_table()

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _show_status(self, message: str, is_error: bool = False) -> None:
        color = "#f38ba8" if is_error else "#a6e3a1"
        self.lbl_status.setStyleSheet(f"font-size: 11px; color: {color};")
        self.lbl_status.setText(message)
        self._status_timer.start(_STATUS_TIMEOUT_MS)

    def _clear_status(self) -> None:
        self.lbl_status.setText("")

    # ------------------------------------------------------------------
    # Load / Refresh
    # ------------------------------------------------------------------

    def _load_jobs(self) -> None:
        self.jobs = read_crontab()
        self._refresh_table()

    def _refresh_from_disk(self) -> None:
        self._load_jobs()
        self._show_status(tr("status_reloaded"))

    def _refresh_table(self) -> None:
        now = datetime.now()
        selected_row = self.table.currentRow()

        self.table.setRowCount(0)
        for job in self.jobs:
            row = self.table.rowCount()
            self.table.insertRow(row)

            enabled_item = QTableWidgetItem("✓" if job.enabled else "✗")
            enabled_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            enabled_item.setForeground(
                (Qt.GlobalColor.green if self.dark_mode else Qt.GlobalColor.darkGreen)
                if job.enabled else Qt.GlobalColor.gray
            )
            self.table.setItem(row, 0, enabled_item)

            desc_item = QTableWidgetItem(job.description or "—")
            if not job.enabled:
                desc_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 1, desc_item)

            self.table.setItem(row, 2, QTableWidgetItem(job.minute))
            self.table.setItem(row, 3, QTableWidgetItem(job.hour))
            self.table.setItem(row, 4, QTableWidgetItem(
                f"{job.day} {job.month} {job.weekday}"
            ))
            self.table.setItem(row, 5, QTableWidgetItem(job.command))

            next_runs = job.get_next_runs(1)
            if next_runs:
                next_dt = next_runs[0]
                if next_dt < now:
                    next_runs = job.get_next_runs(2)
                    future_runs = [r for r in next_runs if r > now]
                    next_str = future_runs[0].strftime("%d.%m.%Y %H:%M") if future_runs else "—"
                else:
                    next_str = next_dt.strftime("%d.%m.%Y %H:%M")
            else:
                next_str = "—"

            self.table.setItem(row, 6, QTableWidgetItem(next_str))
            self.table.setRowHeight(row, 34)

        count = len(self.jobs)
        suffix = "" if count == 1 else "s"
        unit = "Job" if get_language() == "de" else "job"
        self.lbl_count.setText(f"{count} {unit}{suffix}")

        if 0 <= selected_row < self.table.rowCount():
            self.table.selectRow(selected_row)

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def _on_select(self) -> None:
        if not self.table.selectedItems():
            self._reset_selection_state()
            return

        row = self.table.currentRow()
        if row < 0 or row >= len(self.jobs):
            return

        self.selected_index = row
        self.editing_existing = True
        self.btn_delete.setEnabled(True)
        self.btn_update.setEnabled(True)
        self.lbl_form_title.setText(tr("section_edit_job"))

        job = self.jobs[row]
        self.inp_desc.setText(job.description)
        self.chk_enabled.setChecked(job.enabled)
        self._set_combo_value(self.combo_minute, job.minute, _build_minute_presets())
        self._set_combo_value(self.combo_hour, job.hour, _build_hour_presets())
        self.inp_day.setText(job.day)
        self.inp_month.setText(job.month)
        self._set_combo_value(self.combo_weekday, job.weekday, _build_weekday_presets())
        self.inp_command.setText(job.command)
        self._update_preview()

    def _on_double_click(self, item: QTableWidgetItem) -> None:
        self.inp_command.setFocus()
        self.inp_command.selectAll()

    def _reset_selection_state(self) -> None:
        self.selected_index = -1
        self.editing_existing = False
        self.btn_delete.setEnabled(False)
        self.btn_update.setEnabled(False)
        self.lbl_form_title.setText(tr("section_new_job"))

    @staticmethod
    def _set_combo_value(combo: QComboBox, value: str, presets: list) -> None:
        for i, (_, preset_val) in enumerate(presets):
            if preset_val == value:
                combo.setCurrentIndex(i)
                return
        combo.setCurrentIndex(combo.count() - 1)
        combo.setEditText(value)

    # ------------------------------------------------------------------
    # Preset handling
    # ------------------------------------------------------------------

    @staticmethod
    def _on_preset_changed(combo: QComboBox, presets: list, index: int) -> None:
        if index < len(presets):
            val = presets[index][1]
            if val is not None:
                combo.setEditText(val)

    # ------------------------------------------------------------------
    # Preview
    # ------------------------------------------------------------------

    def _schedule_preview(self) -> None:
        self._preview_timer.start(400)

    def _update_preview(self) -> None:
        if self.txt_preview is None:
            return

        minute  = self._resolve_preset(self.combo_minute.currentText(), _build_minute_presets())
        hour    = self._resolve_preset(self.combo_hour.currentText(), _build_hour_presets())
        day     = self.inp_day.text().strip() or "*"
        month   = self.inp_month.text().strip() or "*"
        weekday = self._resolve_preset(self.combo_weekday.currentText(), _build_weekday_presets())

        # Don't show an error while the user hasn't typed anything yet
        if not all([minute, hour, day, month, weekday]):
            self.txt_preview.clear()
            return

        valid, err = validate_cron_expression(minute, hour, day, month, weekday)
        if not valid:
            self.txt_preview.setText(tr("preview_invalid", err=err))
            return

        tmp = CronJob(minute=minute, hour=hour, day=day, month=month, weekday=weekday)
        runs = tmp.get_next_runs(6)
        if not runs:
            self.txt_preview.setText(tr("preview_unavailable"))
            return

        now = datetime.now()
        runs = [r for r in runs if r > now][:5]
        if not runs:
            self.txt_preview.setText(tr("preview_no_future"))
            return

        lines = []
        for r in runs:
            diff = r - now
            total_mins = int(diff.total_seconds() // 60)
            hours, mins = divmod(total_mins, 60)
            if hours > 0:
                when = tr("preview_in_hours_mins", h=str(hours), m=str(mins))
            else:
                when = tr("preview_in_mins", m=str(mins))
            lines.append(f"  • {r.strftime('%d.%m.%Y %H:%M')}  ({when})")
        self.txt_preview.setText("\n".join(lines))

    @staticmethod
    def _resolve_preset(text: str, presets: list) -> str:
        for label, val in presets:
            if text == label and val is not None:
                return val
        return text

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def _add_job(self) -> None:
        job = self._build_job_from_form()
        if job is None:
            return

        ok, backup_path = backup_crontab()
        if not ok:
            if not self._confirm_without_backup(backup_path):
                return

        self.jobs.append(job)
        success, err = write_crontab(self.jobs)
        if not success:
            self.jobs.pop()
            QMessageBox.critical(self, tr("dlg_error_write_title"),
                                 tr("dlg_error_write_text", err=err))
            return

        self._refresh_table()
        self._clear_form()
        self._show_status(tr("status_added"))

    def _save_job(self) -> None:
        if self.selected_index < 0:
            return
        job = self._build_job_from_form()
        if job is None:
            return

        ok, backup_path = backup_crontab()
        if not ok:
            if not self._confirm_without_backup(backup_path):
                return

        previous = self.jobs[self.selected_index]
        self.jobs[self.selected_index] = job
        success, err = write_crontab(self.jobs)
        if not success:
            self.jobs[self.selected_index] = previous
            QMessageBox.critical(self, tr("dlg_error_write_title"),
                                 tr("dlg_error_write_text", err=err))
            return

        self._refresh_table()
        self._clear_form()
        self._show_status(tr("status_saved"))

    def _delete_job(self) -> None:
        if self.selected_index < 0:
            return

        job = self.jobs[self.selected_index]
        name = job.description or job.command[:40]
        reply = QMessageBox.question(
            self, tr("dlg_delete_title"),
            tr("dlg_delete_text", name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        ok, backup_path = backup_crontab()
        if not ok:
            if not self._confirm_without_backup(backup_path):
                return

        removed = self.jobs.pop(self.selected_index)
        success, err = write_crontab(self.jobs)
        if not success:
            self.jobs.insert(self.selected_index, removed)
            QMessageBox.critical(self, tr("dlg_error_write_title"),
                                 tr("dlg_error_write_text", err=err))
            return

        self._refresh_table()
        self._clear_form()
        self._show_status(tr("status_deleted"))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_job_from_form(self) -> CronJob | None:
        minute  = self._resolve_preset(self.combo_minute.currentText(), _build_minute_presets())
        hour    = self._resolve_preset(self.combo_hour.currentText(), _build_hour_presets())
        day     = self.inp_day.text().strip() or "*"
        month   = self.inp_month.text().strip() or "*"
        weekday = self._resolve_preset(self.combo_weekday.currentText(), _build_weekday_presets())
        command = self.inp_command.text().strip()
        description = self.inp_desc.text().strip()
        enabled = self.chk_enabled.isChecked()

        if not command:
            QMessageBox.warning(self, tr("dlg_error_write_title"), tr("dlg_error_command"))
            return None

        valid, err = validate_cron_expression(minute, hour, day, month, weekday)
        if not valid:
            QMessageBox.warning(self, tr("dlg_invalid_syntax_title"),
                                tr("dlg_invalid_syntax_text", err=err))
            return None

        return CronJob(
            minute=minute, hour=hour, day=day, month=month, weekday=weekday,
            command=command, description=description, enabled=enabled,
        )

    def _clear_form(self) -> None:
        self.inp_desc.clear()
        self.inp_command.clear()
        self.combo_minute.setCurrentIndex(0)
        self.combo_hour.setCurrentIndex(0)
        self.inp_day.setText("*")
        self.inp_month.setText("*")
        self.combo_weekday.setCurrentIndex(0)
        self.chk_enabled.setChecked(True)
        self.table.clearSelection()
        self._reset_selection_state()
        if self.txt_preview:
            self.txt_preview.clear()

    def _confirm_without_backup(self, error: str) -> bool:
        reply = QMessageBox.warning(
            self, tr("dlg_backup_fail_title"),
            tr("dlg_backup_fail_text", err=error),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Auto-detect system language before building the UI
    detected = detect_system_language()
    set_language(detected)

    app = QApplication(sys.argv)
    app.setApplicationName("Cronos")
    window = CronGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
