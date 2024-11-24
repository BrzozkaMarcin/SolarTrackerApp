# -*- coding: utf-8 -*-

menuBarStyle = \
"""
    QMenuBar {
        background-color: #E0E0E0;
        border-bottom: 2px solid #C0C0C0;
        color: black;
    }
    QMenuBar::item {
        background-color: transparent;
        padding: 5px 10px;
        border-radius: 5px;
    }
    QMenuBar::item:selected {
        background-color: #A0A0A0;
    }
    QMenu {
        background-color: #E0E0E0;
        border: 2px solid #C0C0C0;
        padding: 5px;
        border-radius: 5px;
    }
    QMenu::item {
        background-color: transparent;
        padding: 5px 20px;
    }
    QMenu::item:selected {
        background-color: #A0A0A0;
    }
"""

selectPortFieldStyle = \
"""
    QComboBox {
        background-color: #FFFFFF;
        border: 2px solid #C0C0C0;
        border-radius: 5px;
        padding: 5px;
    }
    QComboBox:hover {
        border: 2px solid #808080;
    }
    QComboBox::drop-down {
        border-left: 1px solid #C0C0C0;
        background-color: #F0F0F0;
    }
    QComboBox::down-arrow {
        image: url(:/down_arrow_icon.png);
        width: 10px;
        height: 10px;
    }
    QComboBox QAbstractItemView {
        background-color: #FFFFFF;
        border: 1px solid #C0C0C0;
        selection-background-color: #C0C0C0;
        selection-color: #FFFFFF;
    }
"""

portButtonStyle = \
"""
            QPushButton {
                background-color: #404040; 
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
"""

messageBoxStyle = \
"""
    QTextEdit {
        background-color: #FFFFFF;
        border: 2px solid #C0C0C0;
        border-radius: 5px;
        padding: 5px;
    }
"""

positionFrameStyle = \
"""
    QFrame {
        border: 2px solid #C0C0C0;
        border-radius: 5px;
        padding: 5px;
        background-color: #F7F7F7;
    }
"""

