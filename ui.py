from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QTableWidget, QTableWidgetItem, QFrame, QLineEdit, QPushButton, QHeaderView, QMessageBox
)
from PyQt6.QtCore import QTimer
import pyqtgraph as pg
import psutil

class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.updateStats()

    def initUI(self):
        self.setWindowTitle("System Monitor")
        self.setGeometry(100, 100, 1300, 750)

        main_layout = QVBoxLayout()
        usage_layout = self.create_usage_section()
        middle_layout = self.create_middle_section()

        main_layout.addLayout(usage_layout)
        main_layout.addLayout(middle_layout)
        self.setLayout(main_layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStats)
        self.timer.start(2000)

    def create_usage_section(self):
        layout = QHBoxLayout()
        self.cpu_label, self.cpu_bar = QLabel("CPU: 0%"), QProgressBar()
        self.memory_label, self.memory_bar = QLabel("Memory: 0%"), QProgressBar()
        self.disk_label, self.disk_bar = QLabel("Disk: 0%"), QProgressBar()

        for label, bar in [(self.cpu_label, self.cpu_bar), 
                            (self.memory_label, self.memory_bar), 
                            (self.disk_label, self.disk_bar)]:
            vbox = QVBoxLayout()
            vbox.addWidget(label)
            vbox.addWidget(bar)
            layout.addLayout(vbox)
        
        return layout

    def create_middle_section(self):
        layout = QHBoxLayout()
        graph_layout = self.create_graph_section()
        process_layout = self.create_process_section()

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        
        layout.addLayout(graph_layout)
        layout.addWidget(separator)
        layout.addLayout(process_layout)
        return layout

    def create_graph_section(self):
        layout = QVBoxLayout()
        self.cpu_plot, self.memory_plot, self.disk_plot = pg.PlotWidget(title="CPU Usage"), pg.PlotWidget(title="Memory Usage"), pg.PlotWidget(title="Disk Usage")
        self.cpu_data, self.memory_data, self.disk_data = [0] * 30, [0] * 30, [0] * 30
        self.time_data = list(range(30))
        self.cpu_curve, self.memory_curve, self.disk_curve = self.cpu_plot.plot(self.time_data, self.cpu_data, pen='r'), self.memory_plot.plot(self.time_data, self.memory_data, pen='g'), self.disk_plot.plot(self.time_data, self.disk_data, pen='b')

        for plot in [self.cpu_plot, self.memory_plot, self.disk_plot]:
            plot.showGrid(x=True, y=True)
            plot.setBackground("black")
            layout.addWidget(plot)
        
        return layout

    def create_process_section(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Processes"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.updateProcesses)
        layout.addWidget(self.search_input)

        self.process_table = QTableWidget()
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Memory %"])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.process_table)

        self.kill_button = QPushButton("Kill Process")
        self.kill_button.clicked.connect(self.killProcess)
        layout.addWidget(self.kill_button)

        return layout

    def updateStats(self):
        from system_info import get_system_stats
        cpu_usage, memory_usage, disk_usage = get_system_stats()

        self.cpu_label.setText(f"CPU: {cpu_usage}%")
        self.cpu_bar.setValue(int(cpu_usage))
        self.memory_label.setText(f"Memory: {memory_usage}%")
        self.memory_bar.setValue(int(memory_usage))
        self.disk_label.setText(f"Disk: {disk_usage}%")
        self.disk_bar.setValue(int(disk_usage))

        self.cpu_data.append(cpu_usage)
        self.memory_data.append(memory_usage)
        self.disk_data.append(disk_usage)

        for data_list in [self.cpu_data, self.memory_data, self.disk_data]:
            if len(data_list) > 30:
                data_list.pop(0)

        self.cpu_curve.setData(self.time_data, self.cpu_data)
        self.memory_curve.setData(self.time_data, self.memory_data)
        self.disk_curve.setData(self.time_data, self.disk_data)
        self.updateProcesses()

    def updateProcesses(self):
        from system_info import get_process_list
        search_text = self.search_input.text().lower()
        processes = get_process_list(search_text)

        self.process_table.setRowCount(len(processes))
        for row, process in enumerate(processes):
            for col, value in enumerate(process):
                self.process_table.setItem(row, col, QTableWidgetItem(str(value)))

    def killProcess(self):
        from system_info import terminate_process
        selected = self.process_table.currentRow()
        if selected >= 0:
            pid = int(self.process_table.item(selected, 0).text())
            success, message = terminate_process(pid)
            QMessageBox.information(self, "Result", message)
            self.updateProcesses()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a process to kill.")
