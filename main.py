import sys
from PyQt5 import QtWidgets
from form_main import ClassMain


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ClassMain()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложениеы


if __name__ == '__main__':
    main()