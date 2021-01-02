from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from Layouts.details_ui import Ui_details
from Threads.threads import PrintCustomer, Save
import pandas as pd
from .loading_dialog import Loading


class DetailsDialog(QDialog, Ui_details):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('Assets\\icon.ico'))
        self.btnEdit.clicked.connect(lambda: self.setup_edit_view_mode(e_mode=True))

        self.comSalesYarn.setEnabled(self.cbYarn.isChecked())
        self.comSalesOmega.setEnabled(self.cbOmega.isChecked())
        self.comSalesCloth.setEnabled(self.cbCloth.isChecked())

        self.comYarn.setEnabled(self.cbYarn.isChecked())
        self.comOmega.setEnabled(self.cbOmega.isChecked())
        self.comCloth.setEnabled(self.cbCloth.isChecked())

        self.cbYarn.stateChanged.connect(lambda: self.state_changed('yarn'))
        self.cbOmega.stateChanged.connect(lambda: self.state_changed('omega'))
        self.cbCloth.stateChanged.connect(lambda: self.state_changed('cloth'))

        self.btnYarn.clicked.connect(lambda: self.add_cate(self.comYarn, 'yarn', self.twYarn))
        self.btnOmega.clicked.connect(lambda: self.add_cate(self.comOmega, 'omega', self.twOmega))
        self.btnCloth.clicked.connect(lambda: self.add_cate(self.comCloth, 'cloth', self.twCloth))

        self.twYarn.itemDoubleClicked.connect(lambda: self.del_cate(self.twYarn, 'yarn'))
        self.twOmega.itemDoubleClicked.connect(lambda: self.del_cate(self.twOmega, 'omega'))
        self.twCloth.itemDoubleClicked.connect(lambda: self.del_cate(self.twCloth, 'cloth'))
        self.btnSave.clicked.connect(self.save_)

        self.btnPrint.clicked.connect(self.print_customer)
        self.btnPrev.clicked.connect(self.prev_customer)

        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.loading = Loading()

        self.mode = 'v'
        self.customer = None
        self.sheet_row_index = None
        self.len_data = None
        self.categories = None
        self.sheet_customers = None
        self.sheet_requests = None
        self.sales_p = None
        self.customer_ = None
        self.old_edit = None
        self.auth = None

        self.auth_type = 'admin'

        self.cate_yarn = []
        self.cate_omega = []
        self.cate_cloth = []

        self.cates = {'yarn': self.cate_yarn,
                      'omega': self.cate_omega,
                      'cloth': self.cate_cloth
                      }

        self.row_yarn = 0
        self.row_omega = 0
        self.row_cloth = 0

        self.rows = {'yarn': self.row_yarn,
                     'omega': self.row_omega,
                     'cloth': self.row_cloth
                     }

    def set_data(self):
        self.setWindowTitle(f"Details - {self.customer['name'].values[-1]}")

        self.lblName.setText(self.customer['name'].values[-1])

        self.txtSlaesYarn.setText(self.customer['sales_yarn'].values[-1])
        self.txtSlaesOmega.setText(self.customer['sales_omega'].values[-1])
        self.txtSlaesCloth.setText(self.customer['sales_cloth'].values[-1])

        self.comSalesYarn.setCurrentText(self.customer['sales_yarn'].values[-1])
        self.comSalesOmega.setCurrentText(self.customer['sales_omega'].values[-1])
        self.comSalesCloth.setCurrentText(self.customer['sales_cloth'].values[-1])

        self.txtBranch.setText(self.customer['branch'].values[-1])
        self.comBranch.setCurrentText(self.customer['branch'].values[-1])

        self.txtArea.setText(self.customer['area'].values[-1])

        self.txtContactPerson.setText(self.customer['contact_p'].values[-1])
        self.txtAdrress.setText(self.customer['address'].values[-1])
        self.txtMail.setText(self.customer['e_mail'].values[-1])
        self.txtPhone1.setText(
            f"{self.customer['phone1'].values[-1]}" if self.customer['phone1'].values[-1] != '' else '')
        self.txtPhone2.setText(
            f"{self.customer['phone2'].values[-1]}" if self.customer['phone2'].values[-1] != '' else '')
        self.txtPhone3.setText(
            f"{self.customer['phone3'].values[-1]}" if self.customer['phone3'].values[-1] != '' else '')
        self.txtPhone4.setText(
            f"{self.customer['phone4'].values[-1]}" if self.customer['phone4'].values[-1] != '' else '')

        self.txtCustType.setText(self.customer['cust_type'].values[-1])
        self.comCustType.setCurrentText(self.customer['cust_type'].values[-1])

        self.txtSize.setText(self.customer['size'].values[-1])
        self.comSize.setCurrentText(self.customer['size'].values[-1])

        self.cbYarn.setChecked(True if self.customer['yarn'].values[-1] == 1 else False)
        self.cbOmega.setChecked(True if self.customer['omega'].values[-1] == 1 else False)
        self.cbCloth.setChecked(True if self.customer['factory'].values[-1] == 1 else False)

        self.fill_table(data=self.customer['yarn_cate_name'].values[-1], obj=self.twYarn,
                        len_rows=len(self.customer['yarn_cate_name'].values[-1]), cate_name='yarn')
        self.fill_table(data=self.customer['omega_cate_name'].values[-1], obj=self.twOmega,
                        len_rows=len(self.customer['omega_cate_name'].values[-1]), cate_name='omega')
        self.fill_table(data=self.customer['factory_cate_name'].values[-1], obj=self.twCloth,
                        len_rows=len(self.customer['factory_cate_name'].values[-1]), cate_name='cloth')

        print(self.auth)

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

    def state_changed(self, company):
        sales = {
            'yarn': self.comSalesYarn,
            'omega': self.comSalesOmega,
            'cloth': self.comSalesCloth
        }

        cb = {
            'yarn': self.cbYarn,
            'omega': self.cbOmega,
            'cloth': self.cbCloth
        }

        categories = {
            'yarn': self.twYarn,
            'omega': self.twOmega,
            'cloth': self.twCloth
        }

        category_com = {
            'yarn': self.comYarn,
            'omega': self.comOmega,
            'cloth': self.comCloth
        }

        sales[company].setEnabled(cb[company].isChecked())
        if cb[company].isChecked():
            category_com[company].setEnabled(True)
        else:
            self.cates[company] = []
            self.rows[company] = 0
            category_com[company].setEnabled(False)
            category_com[company].setCurrentText('')
            sales[company].setCurrentText('')

            self.fill_table(data=self.cates[company], obj=categories[company], len_rows=self.rows[company],
                            cate_name=company)

    def setup_edit_view_mode(self, e_mode=True):

        self.lblName.setReadOnly(not e_mode)
        self.txtContactPerson.setReadOnly(not e_mode)
        self.txtAdrress.setReadOnly(not e_mode)
        self.txtMail.setReadOnly(not e_mode)
        self.txtPhone1.setReadOnly(not e_mode)
        self.txtPhone2.setReadOnly(not e_mode)
        self.txtPhone3.setReadOnly(not e_mode)
        self.txtPhone4.setReadOnly(not e_mode)
        self.txtCustType.setReadOnly(not e_mode)
        self.txtSize.setReadOnly(not e_mode)
        self.txtArea.setReadOnly(not e_mode)

        self.fYarn.setVisible(e_mode)
        self.fOmega.setVisible(e_mode)
        self.fCloth.setVisible(e_mode)

        self.btnSave.setVisible(e_mode)
        self.btnCancle.setVisible(e_mode)

        self.btnPrint.setVisible(not e_mode)
        self.btnPrev.setVisible(not e_mode)

        self.cbYarn.setEnabled(e_mode)
        self.cbOmega.setEnabled(e_mode)
        self.cbCloth.setEnabled(e_mode)

        self.comSalesYarn.setVisible(e_mode)
        self.comSalesOmega.setVisible(e_mode)
        self.comSalesCloth.setVisible(e_mode)
        self.comCustType.setVisible(e_mode)
        self.comSize.setVisible(e_mode)
        self.comBranch.setVisible(e_mode)

        self.txtSlaesYarn.setVisible(not e_mode)
        self.txtSlaesOmega.setVisible(not e_mode)
        self.txtSlaesCloth.setVisible(not e_mode)
        self.txtCustType.setVisible(not e_mode)
        self.txtSize.setVisible(not e_mode)
        self.txtBranch.setVisible(not e_mode)

        self.fill_combos()

        if self.mode == 'v':
            self.btnCancle.clicked.connect(self.cancel_editing)
        else:
            self.btnEdit.setVisible(False)
            self.btnCancle.clicked.connect(lambda: self.close())

    def cancel_editing(self):
        self.setup_edit_view_mode(e_mode=False)
        self.set_data()

    def thread_error(self, error):
        QMessageBox.warning(self, 'ERROR!', error)

    def thread_save_error(self, error):
        if self.mode == 'v':
            self.customer = self.old_edit
            self.cancel_editing()
        self.loading.stop_dialog()
        QMessageBox.warning(self, 'ERROR!', error)

    def fill_table(self, data=None, obj=None, len_rows=0, cate_name=''):
        self.rows[cate_name] = len_rows
        self.cates[cate_name] = []
        # Create table
        len_columns = 1
        obj.setColumnCount(len_columns)
        if data is not None:
            obj.setRowCount(len_rows)
        obj.setHorizontalHeaderLabels(['الاصناف'])
        header = obj.horizontalHeader()
        header.setStretchLastSection(True)

        if data is not None:
            if len(data) > 0:
                for row in range(len_rows):
                    item = QTableWidgetItem(str(data[row]))
                    item.setTextAlignment(Qt.AlignHCenter)
                    obj.setItem(row, 0, item)
                    self.cates[cate_name].append(
                        f"{self.categories[self.categories[cate_name] == str(data[row])].index[-1]},")

    @staticmethod
    def fill_table_new(data=None, obj=None, len_rows=0):
        # Create table
        len_columns = 1
        obj.setColumnCount(len_columns)
        if data is not None:
            obj.setRowCount(len_rows)
        obj.setHorizontalHeaderLabels(['الاصناف'])
        header = obj.horizontalHeader()
        header.setStretchLastSection(True)

        if data is not None:
            if len(data) > 0:
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignHCenter)
                obj.setItem(len_rows - 1, 0, item)

    def fill_combos(self):
        if self.categories is not None:
            self.comYarn.clear()
            self.comYarn.addItem('')
            self.comYarn.addItems(self.categories['yarn'].values)

            self.comOmega.clear()
            self.comOmega.addItem('')
            self.comOmega.addItems(self.categories['omega'].values)

            self.comCloth.clear()
            self.comCloth.addItem('')
            self.comCloth.addItems(self.categories['cloth'].values)

            current_sales_yarn = self.comSalesYarn.currentText()
            self.comSalesYarn.clear()
            self.comSalesYarn.addItem('')
            self.comSalesYarn.addItems(self.sales_p['name'].values)
            self.comSalesYarn.setCurrentText(current_sales_yarn)

            current_sales_omega = self.comSalesOmega.currentText()
            self.comSalesOmega.clear()
            self.comSalesOmega.addItem('')
            self.comSalesOmega.addItems(self.sales_p['name'].values)
            self.comSalesOmega.setCurrentText(current_sales_omega)

            current_sales_cloth = self.comSalesCloth.currentText()
            self.comSalesCloth.clear()
            self.comSalesCloth.addItem('')
            self.comSalesCloth.addItems(self.sales_p['name'].values)
            self.comSalesCloth.setCurrentText(current_sales_cloth)

            current_cust_type = self.comCustType.currentText()
            self.comCustType.clear()
            self.comCustType.addItems(['تاجر', 'مصنع', 'تاجر قماش'])
            self.comCustType.setCurrentText(current_cust_type)

            current_branch = self.comBranch.currentText()
            self.comBranch.clear()
            self.comBranch.addItems(['القاهره', 'المحله'])
            self.comBranch.setCurrentText(current_branch)

            current_size = self.comSize.currentText()
            self.comSize.clear()
            self.comSize.addItems(['صغير', 'متوسط', 'كبير'])
            self.comSize.setCurrentText(current_size)

    def add_cate(self, com_obj, cate_name, tw_obj):
        cate = com_obj.currentText()
        if cate != '':
            if len(self.cates[cate_name]) > 0 and self.categories[self.categories[cate_name] == cate].index[-1] == 0:
                self.rows[cate_name] = 0
                self.cates[cate_name] = []

            if f"{self.categories[self.categories[cate_name] == cate].index[-1]}," not in self.cates[
                cate_name] \
                    and f'0,' not in self.cates[cate_name]:

                self.rows[cate_name] += 1
                self.fill_table_new(data=cate, obj=tw_obj, len_rows=self.rows[cate_name])
                self.cates[cate_name].append(
                    f"{self.categories[self.categories[cate_name] == cate].index[-1]},")
                com_obj.setCurrentIndex(0)
            else:
                com_obj.setCurrentIndex(0)

    def del_cate(self, tw_obj, cte_name):
        if self.comOmega.isVisible():
            index = tw_obj.currentRow()
            self.rows[cte_name] -= 1
            self.cates[cte_name].pop(index)
            tw_obj.removeRow(index)

    def save_(self):
        self.customer_ = {
            'i': self.customer['i'].values[-1] if self.mode == 'v' else self.sheet_row_index + 1,
            'name': self.lblName.text(),
            'sales_yarn': self.comSalesYarn.currentText(),
            'sales_omega': self.comSalesOmega.currentText(),
            'sales_cloth': self.comSalesCloth.currentText(),
            'contact_p': self.txtContactPerson.text(),
            'branch': self.comBranch.currentText(),
            'area': self.txtArea.text(),
            'address': self.txtAdrress.text(),
            'e_mail': self.txtMail.text(),
            'phone1': self.txtPhone1.text(),
            'phone2': self.txtPhone2.text(),
            'phone3': self.txtPhone3.text(),
            'phone4': self.txtPhone4.text(),
            'cust_type': self.comCustType.currentText(),
            'size': self.comSize.currentText(),
            'yarn': 1 if self.cbYarn.isChecked() else '',
            'omega': 1 if self.cbOmega.isChecked() else '',
            'factory': 1 if self.cbCloth.isChecked() else '',
            'yarn_cate': ''.join(self.cates['yarn'])[:-1] if len(self.cates['yarn']) > 0 else '',
            'omega_cate': ''.join(self.cates['omega'])[:-1] if len(self.cates['omega']) > 0 else '',
            'factory_cate': ''.join(self.cates['cloth'])[:-1] if len(self.cates['cloth']) > 0 else '',
            'by': self.auth
        }
        old_customer = []
        if self.mode == 'v':
            old_customer = {
                'i': self.customer['i'].values[-1],
                'name': self.customer['name'].values[-1],
                'sales_yarn': self.customer['sales_yarn'].values[-1],
                'sales_omega': self.customer['sales_omega'].values[-1],
                'sales_cloth': self.customer['sales_cloth'].values[-1],
                'contact_p': self.customer['contact_p'].values[-1],
                'branch': self.customer['branch'].values[-1],
                'area': self.customer['area'].values[-1],
                'address': self.customer['address'].values[-1],
                'e_mail': self.customer['e_mail'].values[-1],
                'phone1': self.customer['phone1'].values[-1],
                'phone2': self.customer['phone2'].values[-1],
                'phone3': self.customer['phone3'].values[-1],
                'phone4': self.customer['phone4'].values[-1],
                'cust_type': self.customer['cust_type'].values[-1],
                'size': self.customer['size'].values[-1],
                'yarn': self.customer['yarn'].values[-1],
                'omega': self.customer['omega'].values[-1],
                'factory': self.customer['factory'].values[-1],
                'yarn_cate': self.customer['yarn_cate'].values[-1],
                'omega_cate': self.customer['omega_cate'].values[-1],
                'factory_cate': self.customer['factory_cate'].values[-1],
                'by': self.auth
            }

        edited = True
        if self.mode == 'v':
            edited = False
            for key in self.customer_.keys():
                print('here', key)
                if self.customer_[key] != self.customer[key].values[-1]:
                    edited = True
                    try:
                        if int(self.customer_[key]) == int(self.customer[key].values[-1]):
                            edited = False
                    except:
                        pass
                    break

        if edited:
            if self.customer_['name'] != 'Name' and \
                    self.customer_['name'] != '' and \
                    (self.customer_['sales_yarn'] != '' or self.customer_['sales_omega'] != '' or
                     self.customer_['sales_omega'] != '') and \
                    self.customer_['contact_p'] != '' \
                    and self.customer_['cust_type'] != '' and \
                    (self.cbYarn.isChecked() + self.cbOmega.isChecked() + self.cbCloth.isChecked()) > 0:

                if self.sheet_customers is not None:
                    thread = Save(self)
                    thread.customer = self.customer_
                    thread.sheet = self.sheet_customers
                    thread.sheet_requests = self.sheet_requests
                    thread.mode = self.mode
                    thread.len_data = self.len_data
                    thread.sheet_row_index = self.sheet_row_index
                    thread.old_customer = old_customer
                    thread.auth_type = 'editor'
                    thread.done.connect(self.has_been_saved)
                    thread.error.connect(self.thread_save_error)
                    thread.start()

                    self.create_obj()
                    self.cancel_editing()
                    self.loading.start_dialog()
                else:
                    self.thread_error('تحقق من الاتصال بالانترنت ...')
            else:
                self.thread_error('برجاء ادخال جميع البيانات المطلوبه (*) اولا ...')
        else:
            self.thread_error('لم تتم اي تغيرات ...')

    def has_been_saved(self, head, msg):
        QMessageBox.information(self, head, msg)
        self.loading.stop_dialog()

    def create_obj(self):
        if self.mode == 'v':
            self.old_edit = self.customer

        self.customer = pd.DataFrame(data=[self.customer_.values()], columns=self.customer_.keys())

        self.customer['yarn_cate_name'] = self.customer['yarn_cate'].apply(lambda x: self.categories['yarn'].loc[
            list(map(int, x.split(','))) if not isinstance(x, int) and x != '' else [] if x == '' else [
                x]].values)

        self.customer['omega_cate_name'] = self.customer['omega_cate'].apply(
            lambda x: self.categories['omega'].loc[
                list(map(int, x.split(','))) if not isinstance(x, int) and x != '' else [] if x == '' else [
                    x]].values)

        self.customer['factory_cate_name'] = self.customer['factory_cate'].apply(
            lambda x: self.categories['cloth'].loc[
                list(map(int, x.split(','))) if not isinstance(x, int) and x != '' else [] if x == '' else [
                    x]].values)
