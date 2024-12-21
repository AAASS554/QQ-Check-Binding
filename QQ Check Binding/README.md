# PyQt5 Card Key Authentication System
[nglish](#english) | [中文](#中文)
# English
A card key authentication system framework based on PyQt5, providing complete card key management and verification functions.
## Features
- 🔐 Complete Card Key Management
 - Card key generation
 - Status management
 - Validity period control
 - Machine code binding
- 🛡️ Security Features
 - Machine code binding
 - Real-time status check
 - Anti-multiple instance protection
 - Database encryption
- 💻 Admin Panel
 - Batch card key generation
 - Status view/modification
 - Unbind/reset functions
 - Data export
## Requirements
- Python 3.7+
 MySQL 5.7+
 Windows OS
## Installation
bash
pip install -r requirements.txt
## Quick Start

1. Create database tables:

```sql
CREATE TABLE card_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_key VARCHAR(32) NOT NULL,
    valid_days INT NOT NULL,
    create_time DATETIME NOT NULL,
    status TINYINT NOT NULL DEFAULT 0,
    use_time DATETIME NULL,
    device_id VARCHAR(64) NULL,
    bind_time DATETIME NULL
);

CREATE TABLE card_status_change (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_key VARCHAR(32) NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    change_time DATETIME NOT NULL
);
```

2. Configure database:

```python
DB_CONFIG = {
    'host': 'your_host',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database',
    'port': 3306,
    'charset': 'utf8mb4',
}
```

3. Run admin panel:

```bash
python src/admin.py
```

4. Develop your application by inheriting the framework:

```python
from maina import MainWindow

class MyApp(MainWindow):
    def init_function_ui(self, layout):
        # Add your function UI
        pass
        
    def on_activation_status_changed(self, is_activated):
        # Handle activation status change
        if is_activated:
            # Enable features
            pass
        else:
            # Disable features
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

## Build

Use PyInstaller to build:

```bash
.\build.bat
```

## License

MIT License

## Contact

Author: JiDeWanAn  
WeChat: Hatebetray_

## Disclaimer

This project is for learning and communication purposes only, please do not use it for commercial purposes. All consequences arising from the use of this project shall be borne by the user.

# 中文

基于 PyQt5 的卡密验证系统框架，提供完整的卡密管理和验证功能。
## 功能特点
- 🔐 完整的卡密管理系统
 - 卡密生成
 - 状态管理
 - 有效期控制
 - 机器码绑定
- 🛡️ 安全特性
 - 机器码绑定
 - 状态实时检查
 - 防多开保护
 - 数据库加密
- 💻 管理后台
 - 卡密批量生成
 - 状态查看/修改
 - 解绑/重置功能
 - 数据导出
## 系统要求
- Python 3.7+
- MySQL 5.7+
- Windows 操作系统
## 安装依赖
```bash
pip install -r requirements.txt
```
## 快速开始

1. 创建数据库表：

```sql
CREATE TABLE card_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_key VARCHAR(32) NOT NULL,
    valid_days INT NOT NULL,
    create_time DATETIME NOT NULL,
    status TINYINT NOT NULL DEFAULT 0,
    use_time DATETIME NULL,
    device_id VARCHAR(64) NULL,
    bind_time DATETIME NULL
);

CREATE TABLE card_status_change (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_key VARCHAR(32) NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    change_time DATETIME NOT NULL
);
```

2. 修改数据库配置：

```python
DB_CONFIG = {
    'host': 'your_host',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database',
    'port': 3306,
    'charset': 'utf8mb4',
}
```

3. 运行管理后台：

```bash
python src/admin.py
```

4. 继承框架开发自己的应用：

```python
from maina import MainWindow

class MyApp(MainWindow):
    def init_function_ui(self, layout):
        # 添加你的功能UI
        pass
        
    def on_activation_status_changed(self, is_activated):
        # 处理激活状态改变
        if is_activated:
            # 启用功能
            pass
        else:
            # 禁用功能
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

## 打包发布

使用 PyInstaller 打包：

```bash
.\build.bat
```

## License

MIT License

## Contact

Author: JiDeWanAn  
WeChat: Hatebetray_

## Disclaimer

This project is for learning and communication purposes only, please do not use it for commercial purposes. All consequences arising from the use of this project shall be borne by the user.

本项目仅供学习交流使用，请勿用于商业用途。使用本项目所产生的一切后果由使用者自行承担。