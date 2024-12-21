import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTextEdit, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from admin import CardAuth
import datetime
from utils.protection import AntiDebug
import ctypes
import platform
import hashlib
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.card_auth = CardAuth()
        self.is_activated = False
        self.expiry_time = None
        self.current_card_key = None  # 保存当前使用的卡密
        self.device_id = self.get_machine_code()  # 获取稳定的机器码
        
        # 状态更新计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_display)
        self.timer.start(1000)  # 每秒更新显示
        
        # 卡密状态检查计时器
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_card_status)
        self.check_timer.start(10000)  # 每30秒检查一次
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QQ信息查询系统 - By 记得晚安")
        self.setGeometry(100, 100, 600, 500)  # 调整窗口大小
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f6f7f8;
            }
        """)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)  # 增加组件间距
        
        # 标题部分
        title_label = QLabel("QQ信息查询系统")
        title_label.setStyleSheet("""
            QLabel {
                color: #FB7299;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
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
        self.card_input.setFixedWidth(250)
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
        
        # QQ查询部分
        query_group = QGroupBox("QQ查询")
        query_group.setStyleSheet("""
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
        query_layout = QHBoxLayout(query_group)
        
        self.qq_input = QLineEdit()
        self.qq_input.setPlaceholderText('请输入QQ号...')
        self.qq_input.setFixedWidth(250)
        self.qq_input.setEnabled(False)
        self.qq_input.setStyleSheet("""
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
            QLineEdit:disabled {
                background: #f6f7f8;
            }
        """)
        
        query_btn = QPushButton('查询')
        query_btn.clicked.connect(self.query_qq)
        query_btn.setEnabled(False)
        query_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #ebedf0;
                color: #999;
            }
        """)
        self.query_btn = query_btn
        
        query_layout.addWidget(QLabel('QQ号:'))
        query_layout.addWidget(self.qq_input)
        query_layout.addWidget(query_btn)
        query_layout.addStretch()
        
        layout.addWidget(query_group)
        
        # 结果显示区域
        result_group = QGroupBox("查询结果")
        result_group.setStyleSheet("""
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
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText('查询结果将在这里显示...')
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e3e5e7;
                border-radius: 4px;
                padding: 10px;
                background: #f6f7f8;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        # 作者信息和免责声明
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
        
        contact_label = QLabel("卡密购买加V：Hatebetray_")
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setStyleSheet("""
            QLabel {
                color: #23ADE5;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        info_layout.addWidget(contact_label)
        
        disclaimer_label = QLabel("软件仅供学习交流使用")
        disclaimer_label.setAlignment(Qt.AlignCenter)
        disclaimer_label.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 12px;
                font-style: italic;
                padding: 5px;
            }
        """)
        info_layout.addWidget(disclaimer_label)
        
        layout.addLayout(info_layout)

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
            self.qq_input.setEnabled(False)
            self.query_btn.setEnabled(False)
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
                    self.qq_input.setEnabled(False)
                    self.query_btn.setEnabled(False)
                    self.result_text.setText("卡密状态已被重置，请重新验证")
                    QMessageBox.warning(self, '警告', "卡密状态已被重置，请重新验证")
                    return
                
                # 首先检查卡密是否存在
                cursor.execute("SELECT 1 FROM card_keys WHERE card_key = %s", (self.current_card_key,))
                if not cursor.fetchone():
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.qq_input.setEnabled(False)
                    self.query_btn.setEnabled(False)
                    self.result_text.setText("卡密已被删除，请重新购买")
                    QMessageBox.warning(self, '警告', "卡密已被删除，请重新购买")
                    return
                
                # 验证卡密状态
                success, message, expiry_time = self.card_auth.verify_card(self.current_card_key, self.device_id)
                
                if not success:
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.qq_input.setEnabled(False)
                    self.query_btn.setEnabled(False)
                    self.result_text.setText(f"卡密状态异常: {message}\n请重新验证卡密")
                    QMessageBox.warning(self, '警告', f"卡密状态异常: {message}")
                    return
                
                # 检查是否过期
                if datetime.datetime.now() > expiry_time:
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.qq_input.setEnabled(False)
                    self.query_btn.setEnabled(False)
                    self.result_text.setText("卡密已过期，请重新购买")
                    QMessageBox.warning(self, '警告', "卡密已过期，请重新购买")
                    return
                
                # 更新过期时间
                self.expiry_time = expiry_time
                
        except Exception as e:
            print(f"检查卡密状态失败: {str(e)}")
            self.is_activated = False
            self.expiry_time = None
            self.current_card_key = None
            self.qq_input.setEnabled(False)
            self.query_btn.setEnabled(False)
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
            self.current_card_key = card_key  # 保存当前卡密
            self.qq_input.setEnabled(True)
            self.query_btn.setEnabled(True)
            QMessageBox.information(self, '成功', message)
        else:
            self.is_activated = False
            self.expiry_time = None
            self.current_card_key = None
            self.qq_input.setEnabled(False)
            self.query_btn.setEnabled(False)
            QMessageBox.warning(self, '错误', message)

    def query_qq(self):
        """查询QQ信息"""
        if not self.is_activated:
            QMessageBox.warning(self, '提示', '请先验证卡密')
            return
            
        # 再次检查卡密状态
        try:
            # 先检查卡密是否存在
            connection = self.card_auth.db.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM card_keys WHERE card_key = %s", (self.current_card_key,))
                if not cursor.fetchone():
                    self.is_activated = False
                    self.expiry_time = None
                    self.current_card_key = None
                    self.qq_input.setEnabled(False)
                    self.query_btn.setEnabled(False)
                    self.result_text.setText("卡密已被删除，请重新购买")
                    QMessageBox.warning(self, '警告', "卡密已被删除，请重新购买")
                    return
        except Exception as e:
            print(f"检查卡密存在性失败: {str(e)}")
        finally:
            if connection:
                connection.close()
        
        self.check_card_status()
        if not self.is_activated:
            return
            
        qq = self.qq_input.text().strip()
        if not qq:
            QMessageBox.warning(self, '提示', '请输入QQ号')
            return
            
        try:
            response = requests.get(f'https://zy.xywlapi.cc/qqapi?qq={qq}')
            data = response.json()
            
            if data['status'] == 200:
                result = (
                    f"查询状态: {data['message']}\n"
                    f"QQ号: {data['qq']}\n"
                    f"手机号: {data['phone']}\n"
                    f"归属地: {data['phonediqu']}"
                )
            else:
                result = f"查询失败: {data['message']}"
                
            self.result_text.setText(result)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')
            self.result_text.setText(f'查询出错: {str(e)}')

    def get_machine_code(self):
        """获取稳定的机器码"""
        try:
            import wmi
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
            import uuid
            return hashlib.md5(str(uuid.getnode()).encode()).hexdigest()

def check_integrity():
    """检查程序完整性"""
    try:
        # 计算主程序文件的哈希
        with open(sys.argv[0], 'rb') as f:
            content = f.read()
        current_hash = hashlib.sha256(content).hexdigest()
        
        # 开发阶段暂时返回True
        return True
    except:
        return True

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行程序"""
    try:
        if not is_admin():
            # 准备命令行参数
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            
            # 使用 ShellExecuteW 重新启动程序
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas",
                sys.executable,
                f'"{script}" {params}',
                None, 
                1  # SW_SHOWNORMAL
            )
            
            # 如果返回值大于32，说明启动成功
            if ret > 32:
                sys.exit(0)
            else:
                QMessageBox.critical(
                    None, 
                    '错误', 
                    '程序需要管理员权限才能运行！\n请右键选择"以管理员身份运行"。'
                )
                sys.exit(1)
    except Exception as e:
        QMessageBox.critical(
            None, 
            '错误', 
            f'启动失败: {str(e)}\n请右键选择"以管理员身份运行"。'
        )
        sys.exit(1)

def main():
    # 启动保护
    if not check_integrity():
        QMessageBox.critical(None, '错误', '程序完整性验证失败')
        sys.exit(1)
        
    AntiDebug.start_protection()
    
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, '错误', f'程序启动失败: {str(e)}')
        sys.exit(1)

if __name__ == "__main__":
    main() 