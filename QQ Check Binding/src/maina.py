import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTextEdit, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from admin import CardAuth
import datetime
from utils.protection import AntiDebug
import hashlib
import wmi
import uuid

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.card_auth = CardAuth()
        self.is_activated = False
        self.expiry_time = None
        self.current_card_key = None
        self.device_id = self.get_machine_code()
        
        # 状态更新计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_display)
        self.timer.start(1000)  # 每秒更新显示
        
        # 卡密状态检查计时器
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_card_status)
        self.check_timer.start(10000)  # 每10秒检查一次
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("软件验证系统 - By 记得晚安")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f6f7f8;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        
        # 卡密验证部分
        auth_group = QGroupBox("卡密验证")
        auth_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e3e5e7;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #18191C;
                padding: 0 10px;
            }
        """)
        auth_layout = QHBoxLayout(auth_group)
        
        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText('请输入卡密...')
        self.card_input.setFixedWidth(200)
        self.card_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e3e5e7;
                border-radius: 4px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #FB7299;
            }
        """)
        
        auth_btn = QPushButton('验证卡密')
        auth_btn.clicked.connect(self.verify_card)
        auth_btn.setStyleSheet("""
            QPushButton {
                background-color: #FB7299;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fc8bab;
            }
            QPushButton:pressed {
                background-color: #e45c84;
            }
        """)
        
        auth_layout.addWidget(QLabel('卡密:'))
        auth_layout.addWidget(self.card_input)
        auth_layout.addWidget(auth_btn)
        auth_layout.addStretch()
        
        layout.addWidget(auth_group)
        
        # 有效期显示
        time_group = QGroupBox("使用状态")
        time_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e3e5e7;
                border-radius: 8px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #18191C;
                padding: 0 10px;
            }
        """)
        time_layout = QHBoxLayout(time_group)
        
        self.time_label = QLabel('未激活')
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 8px;
                border: 1px solid #e3e5e7;
                border-radius: 4px;
                background: #f6f7f8;
                min-width: 200px;
            }
        """)
        time_layout.addStretch()
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        
        layout.addWidget(time_group)
        
        # 功能区域 - 继承此类时重写此部分
        self.init_function_ui(layout)
        
        # 作者信息
        info_layout = QVBoxLayout()
        author_label = QLabel("作者：记得晚安")
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setStyleSheet("""
            QLabel {
                color: #FB7299;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        info_layout.addWidget(author_label)
        layout.addLayout(info_layout)

    def init_function_ui(self, layout):
        """初始化功能区��UI - 继承时重写此方法"""
        pass

    def update_time_display(self):
        """更新时间显示"""
        if not self.is_activated or not self.expiry_time:
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #666666;
                    font-size: 14px;
                    padding: 8px;
                    border: 1px solid #e3e5e7;
                    border-radius: 4px;
                    background: #f6f7f8;
                    min-width: 200px;
                }
            """)
            self.time_label.setText('未激活')
            return
            
        now = datetime.datetime.now()
        if now > self.expiry_time:
            self.is_activated = False
            self.expiry_time = None
            self.current_card_key = None
            self.on_activation_status_changed(False)
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #F56C6C;
                    font-size: 14px;
                    padding: 8px;
                    border: 1px solid #fde2e2;
                    border-radius: 4px;
                    background: #fef0f0;
                    min-width: 200px;
                    font-weight: bold;
                }
            """)
            self.time_label.setText('已过期')
            return
            
        remaining = self.expiry_time - now
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        seconds = remaining.seconds % 60
        
        self.time_label.setStyleSheet("""
            QLabel {
                color: #67C23A;
                font-size: 14px;
                padding: 8px;
                border: 1px solid #e1f3d8;
                border-radius: 4px;
                background: #f0f9eb;
                min-width: 200px;
                font-weight: bold;
            }
        """)
        self.time_label.setText(f'剩余有效期: {days}天 {hours:02d}:{minutes:02d}:{seconds:02d}')

    def check_card_status(self):
        """检查卡密状态"""
        if not self.is_activated or not self.current_card_key:
            return
        
        try:
            connection = self.card_auth.db.get_connection()
            with connection.cursor() as cursor:
                # 检查是否有状态变更
                cursor.execute("""
                    SELECT 1 FROM card_status_change 
                    WHERE card_key = %s AND change_type = 'reset'
                    AND change_time > DATE_SUB(NOW(), INTERVAL 10 SECOND)
                """, (self.current_card_key,))
                
                if cursor.fetchone():
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.on_activation_status_changed(False)
                    QMessageBox.warning(self, '警告', "卡密状态已被重置，请重新验证")
                    return
                
                # 检查卡密是否存在
                cursor.execute("SELECT 1 FROM card_keys WHERE card_key = %s", (self.current_card_key,))
                if not cursor.fetchone():
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.on_activation_status_changed(False)
                    QMessageBox.warning(self, '警告', "卡密已被删除，请重新购买")
                    return
                
                # 验证卡密状态
                success, message, expiry_time = self.card_auth.verify_card(self.current_card_key, self.device_id)
                
                if not success:
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.on_activation_status_changed(False)
                    QMessageBox.warning(self, '警告', f"卡密状态异常: {message}")
                    return
                
                # 检查是否过期
                if datetime.datetime.now() > expiry_time:
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.on_activation_status_changed(False)
                    QMessageBox.warning(self, '警告', "卡密已过期，请重新购买")
                    return
                
                # 更新过期时间
                self.expiry_time = expiry_time
                
        except Exception as e:
            print(f"检查卡密状态失败: {str(e)}")
            self.is_activated = False
            self.expiry_time = None
            self.current_card_key = None
            self.on_activation_status_changed(False)
        finally:
            if connection:
                connection.close()

    def verify_card(self):
        """验证卡密"""
        card_key = self.card_input.text().strip()
        if not card_key:
            QMessageBox.warning(self, '提示', '请输入卡密')
            return
        
        success, message, expiry_time = self.card_auth.verify_card(card_key, self.device_id)
        if success:
            self.is_activated = True
            self.expiry_time = expiry_time
            self.current_card_key = card_key
            self.on_activation_status_changed(True)
            QMessageBox.information(self, '成功', message)
        else:
            self.is_activated = False
            self.expiry_time = None
            self.current_card_key = None
            self.on_activation_status_changed(False)
            QMessageBox.warning(self, '错误', message)

    def on_activation_status_changed(self, is_activated):
        """激活状态改变时的回调 - 继承时重写此方法"""
        pass

    def get_machine_code(self):
        """获取稳定的机器码"""
        try:
            c = wmi.WMI()
            # 获取CPU序列号
            cpu = c.Win32_Processor()[0].ProcessorId.strip()
            # 获取主板序列号
            board = c.Win32_BaseBoard()[0].SerialNumber.strip()
            # 获取BIOS序列号
            bios = c.Win32_BIOS()[0].SerialNumber.strip()
            # 组合并加密
            machine_code = f"{cpu}-{board}-{bios}"
            return hashlib.md5(machine_code.encode()).hexdigest()
        except:
            # 如果获取失败，使用备用方案
            return hashlib.md5(str(uuid.getnode()).encode()).hexdigest()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 