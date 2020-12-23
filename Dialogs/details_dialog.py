from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from Layouts.details_ui import Ui_details
from Threads.threads import PrintCustomer


class DetailsDialog(QDialog, Ui_details):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('Assets\\icon.ico'))
        self.btnPrint.clicked.connect(self.print_customer)
        self.btnPrev.clicked.connect(self.prev_customer)

        self.customer = None

    def set_data(self):
        # print(self.customer['name'].values[-1])
        self.setWindowTitle(f"Details - {self.customer['name'].values[-1]}")

        self.lblName.setText(self.customer['name'].values[-1])
        self.txtSlaesP.setText(self.customer['sales_p'].values[-1])
        self.txtAdmin.setText(self.customer['admin'].values[-1])
        self.txtAdrress.setText(self.customer['address'].values[-1])
        self.txtMail.setText(self.customer['e_mail'].values[-1])
        self.txtPhone1.setText(
            f"0{self.customer['phone1'].values[-1]}" if self.customer['phone1'].values[-1] != '' else '')
        self.txtPhone2.setText(
            f"0{self.customer['phone2'].values[-1]}" if self.customer['phone2'].values[-1] != '' else '')
        self.txtPhone3.setText(
            f"0{self.customer['phone3'].values[-1]}" if self.customer['phone3'].values[-1] != '' else '')
        self.txtPhone4.setText(
            f"0{self.customer['phone4'].values[-1]}" if self.customer['phone4'].values[-1] != '' else '')

        self.txtCustType.setText(self.customer['cust_type'].values[-1])
        self.txtSize.setText(self.customer['size'].values[-1])

        self.cbYarn.setChecked(True if self.customer['yarn'].values[-1] == 1 else False)
        self.cbOmega.setChecked(True if self.customer['omega'].values[-1] == 1 else False)
        self.cbCloth.setChecked(True if self.customer['factory'].values[-1] == 1 else False)

        self.fill_table(data=self.customer['yarn_cate'].values[-1], obj=self.twYarn)
        self.fill_table(data=self.customer['omega_cate'].values[-1], obj=self.twOmega)
        self.fill_table(data=self.customer['factory_cate'].values[-1], obj=self.twCloth)

    def print_customer(self):
        thread = PrintCustomer(self)
        thread.customer = self.customer
        thread.prev_mode = False
        thread.error.connect(self.thread_error)
        thread.start()

    def prev_customer(self):
        thread = PrintCustomer(self)
        thread.customer = self.customer
        thread.error.connect(self.thread_error)
        thread.start()

    def thread_error(self, error):
        QMessageBox.warning(self, 'ERROR!', error)

    @staticmethod
    def fill_table(data=None, obj=None):
        # Create table
        len_columns = 1
        obj.setColumnCount(len_columns)
        if data is not None:
            obj.setRowCount(len(data))
        obj.setHorizontalHeaderLabels(['الاصناف'])
        obj.resizeColumnsToContents()
        obj.resizeRowsToContents()
        header = obj.horizontalHeader()
        header.setStretchLastSection(True)

        if data is not None:
            if len(data) > 0:
                for row in range(len(data)):
                    item = QTableWidgetItem(str(data[row]))
                    item.setTextAlignment(Qt.AlignHCenter)
                    obj.setItem(row, 0, item)
