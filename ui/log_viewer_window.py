from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QComboBox, QPushButton, QCheckBox, QListWidget, QTreeWidget,
    QTreeWidgetItem, QTextBrowser, QFileDialog, QProgressDialog,
    QMessageBox, QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextOption

from botocore.exceptions import ProfileNotFound

from core.s3_manager import S3Manager
from core.log_parser import LogParser
from core.aws_util import get_aws_profiles

class LogViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Low Cost Watch - Log Viewer")
        self.setGeometry(100, 100, 1400, 800)

        # Inicializa os managers
        self.s3_manager = S3Manager()
        self.log_data = {}
        self.file_keys = []

        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self._setup_top_section()
        self._setup_file_list()
        self._setup_splitter()
        self._setup_filter_export_section()

        self.setCentralWidget(container)

    def _setup_top_section(self):
        """
        Monta a parte superior: seleção de profile, campo S3, checkbox e botão de carregar.
        """
        top_layout = QHBoxLayout()

        top_layout.addWidget(QLabel("AWS Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(get_aws_profiles())
        top_layout.addWidget(self.profile_combo)

        top_layout.addWidget(QLabel("S3 Path:"))
        self.s3_path_input = QLineEdit()
        self.s3_path_input.setPlaceholderText("s3://bucket-name/path/to/logs/")
        top_layout.addWidget(self.s3_path_input)

        self.load_all_checkbox = QCheckBox("Load All Files")
        top_layout.addWidget(self.load_all_checkbox)

        self.load_button = QPushButton("Load Logs")
        self.load_button.clicked.connect(self.load_logs)
        top_layout.addWidget(self.load_button)

        self.main_layout.addLayout(top_layout)

    def _setup_file_list(self):
        """
        Lista de arquivos (QListWidget) para o caso de não carregar tudo de uma vez.
        """
        self.file_list = QListWidget()
        self.file_list.setVisible(False)
        self.file_list.itemSelectionChanged.connect(self.on_file_selection_changed)
        self.main_layout.addWidget(self.file_list)

    def _setup_splitter(self):
        """
        Splitter que divide a lista de logs (QTreeWidget) dos detalhes (QTextBrowser).
        """
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Log events
        self.log_events = QTreeWidget()
        self.log_events.setHeaderLabels(["Timestamp", "Level", "Worker", "Task", "Message"])
        self.log_events.setColumnWidth(0, 200)
        self.log_events.setColumnWidth(1, 60)
        self.log_events.setColumnWidth(2, 150)
        self.log_events.setColumnWidth(3, 200)
        self.log_events.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.log_events.setWordWrap(True)
        self.log_events.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.log_events.itemClicked.connect(self.on_event_clicked)
        splitter.addWidget(self.log_events)

        # Log details
        self.log_details = QTextBrowser()
        self.log_details.setVisible(False)
        self.log_details.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        splitter.addWidget(self.log_details)

        self.main_layout.addWidget(splitter)

    def _setup_filter_export_section(self):
        """
        Seção para o campo de filtro e botão de exportar logs.
        """
        filter_export_layout = QHBoxLayout()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter logs... (Press Enter to apply)")
        self.filter_input.returnPressed.connect(self.apply_filter)
        filter_export_layout.addWidget(self.filter_input)

        self.filter_button = QPushButton("Apply Filter")
        self.filter_button.clicked.connect(self.apply_filter)
        filter_export_layout.addWidget(self.filter_button)

        self.export_button = QPushButton("Export Logs")
        self.export_button.clicked.connect(self.export_logs)
        filter_export_layout.addWidget(self.export_button)

        self.main_layout.addLayout(filter_export_layout)


    def load_logs(self):
        """
        Carrega a lista de arquivos do S3 ou todos os logs de uma vez.
        """
        profile = self.profile_combo.currentText()
        s3_path = self.s3_path_input.text()

        if not s3_path.startswith('s3://'):
            QMessageBox.warning(self, "Invalid S3 Path", "S3 path must start with 's3://'")
            return

        try:
            # Conecta no S3
            self.s3_manager.profile_name = profile
            self.s3_manager.connect()

            parts = s3_path[5:].split('/', 1)
            bucket_name = parts[0]
            prefix = parts[1] if len(parts) > 1 else ''

            self.file_keys = self.s3_manager.list_files(bucket_name, prefix)

            if not self.file_keys:
                QMessageBox.warning(self, "No Files Found", "No log files found in the specified S3 path.")
                return

            if self.load_all_checkbox.isChecked():
                self.load_selected_files(self.file_keys)
            else:
                self.file_list.clear()
                self.file_list.addItems([key.split('/')[-1] for key in self.file_keys])
                self.file_list.setVisible(True)
                self.log_events.setVisible(False)

        except ProfileNotFound:
            QMessageBox.critical(self, "Profile Error", f"AWS profile '{profile}' not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load logs: {str(e)}")

    def on_file_selection_changed(self):
        """
        Quando o usuário seleciona um ou mais arquivos na lista, carrega apenas aqueles.
        """
        selected_items = self.file_list.selectedItems()
        if selected_items:
            selected_names = [item.text() for item in selected_items]
            selected_keys = [
                k for k in self.file_keys 
                if k.split('/')[-1] in selected_names
            ]
            self.load_selected_files(selected_keys)

    def load_selected_files(self, file_keys):
        """
        Faz o download e parse dos arquivos selecionados.
        """
        self.log_data.clear()
        progress = QProgressDialog("Loading log files...", "Cancel", 0, len(file_keys), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        for i, key in enumerate(file_keys):
            self.load_single_log(key)
            progress.setValue(i)
            if progress.wasCanceled():
                break

        progress.setValue(len(file_keys))
        self.populate_log_events()
        self.file_list.setVisible(False)
        self.log_events.setVisible(True)

        total_entries = sum(len(logs) for logs in self.log_data.values())
        QMessageBox.information(self, "Logs Loaded", f"Successfully loaded {total_entries} log entries.")

    def load_single_log(self, file_key):
        """
        Download e parse de um único arquivo de log.
        """
        content = self.s3_manager.download_and_decompress(file_key)
        if content:
            self.log_data[file_key] = LogParser.parse_log_content(content)

    def populate_log_events(self):
        """
        Popula o QTreeWidget com as entradas de log (timestamp, level, etc.).
        """
        self.log_events.clear()
        for file_key, logs in self.log_data.items():
            for entry in logs:
                item = QTreeWidgetItem([
                    entry['timestamp'],
                    entry['level'],
                    entry['worker'],
                    entry.get('task', ''),
                    entry.get('message', '')
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, entry)
                self.set_item_color(item, entry['level'])
                self.log_events.addTopLevelItem(item)

    def set_item_color(self, item, level):
        color = QColor(Qt.GlobalColor.black)
        if level == "ERROR":
            color = QColor(Qt.GlobalColor.red)
        elif level == "WARN":
            color = QColor(Qt.GlobalColor.darkYellow)
        item.setForeground(1, color)

    def on_event_clicked(self, item):
        """
        Exibe detalhes no QTextBrowser quando o usuário clica em uma linha do log.
        """
        entry = item.data(0, Qt.ItemDataRole.UserRole)
        if entry:
            self.log_details.setVisible(True)
            self.log_details.setHtml(f"""
                <pre style="font-family: Courier; white-space: pre-wrap; word-wrap: break-word;">
                <b>Timestamp:</b> {entry['timestamp']}
                <b>Level:</b> {entry['level']}
                <b>Worker:</b> {entry['worker']}
                <b>Task:</b> {entry.get('task', 'N/A')}

                <b>Full Message:</b>
                {entry['full_message']}
                </pre>
            """)

    def apply_filter(self):
        """
        Filtra os itens no QTreeWidget pelo texto digitado.
        """
        filter_text = self.filter_input.text().lower()
        for i in range(self.log_events.topLevelItemCount()):
            item = self.log_events.topLevelItem(i)
            entry = item.data(0, Qt.ItemDataRole.UserRole)
            if entry:
                if (filter_text in entry['full_message'].lower() or 
                    filter_text in entry['level'].lower() or 
                    filter_text in entry['worker'].lower() or 
                    (entry.get('task') and filter_text in entry['task'].lower())):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def export_logs(self):
        """
        Exporta os logs visíveis (não-hidden) para um arquivo .txt ou .csv.
        """
        options = (
            QFileDialog.Option.DontUseNativeDialog 
            | QFileDialog.Option.DontConfirmOverwrite
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            "",
            "Text Files (*.txt);;CSV Files (*.csv)",
            options=options
        )
        if file_path:
            with open(file_path, 'w') as file:
                for i in range(self.log_events.topLevelItemCount()):
                    item = self.log_events.topLevelItem(i)
                    if not item.isHidden():
                        entry = item.data(0, Qt.ItemDataRole.UserRole)
                        file.write(f"{entry['timestamp']},{entry['level']},{entry['worker']},{entry.get('task', '')},{entry.get('message', '')}\n")

            QMessageBox.information(self, "Export Complete", "Logs have been exported successfully.")

    def resizeEvent(self, event):
        """
        Ajusta a largura da coluna "Message" quando a janela é redimensionada.
        """
        super().resizeEvent(event)
        self.log_events.setColumnWidth(4, self.log_events.width() - 610)