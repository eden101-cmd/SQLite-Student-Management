from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit,QPushButton, QMainWindow,QTableWidget,QTableWidgetItem,QDialog,\
    QComboBox, QToolBar,QStatusBar,QMessageBox
from PyQt6.QtGui import QAction,QIcon
import sys
import sqlite3
from PyQt6.QtCore import Qt

# here we will use the QMainWindow because we can add
# to this one a menu bar and more bars that we cant add with the Qwidget
#and division between sections in the app

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800,600) #nicer to enter the application like this

        file_menu_item = self.menuBar().addMenu("&File")  #adding the buttons at the top of the app
        help_menu_item = self.menuBar().addMenu("&Help")  #adding the buttons at the top of the app
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"),"Add Student",self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About",self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)


        search_action = QAction(QIcon("icons/search.png"),"Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id","Name","Course","Mobile"))
        self.table.verticalHeader().setVisible(False) # will take off the outside column with the indexes of the table
        self.setCentralWidget(self.table) #showing the table in the app

        #create tool bar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar) # added the toolbar to the window instance
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # create status bad and add status bar elements:
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        #Setect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)
        #before we add buttons to the status bar, we need to clear any other buttons!
        #it will clear all the buttons every time at the end we will only have one button
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("select * from students")
        #print(list(result)) # a list of tupels, every tuple is a row in the table!
        self.table.setRowCount(0) # It clears the existing rows in the table widget by calling self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            #print(enumerate(result)) -> take every tuple from the list
            #print(row_number) #index starting from zero
            #print(row_data) #row_data is every row
            self.table.insertRow(row_number)
            for column_number,data in enumerate(row_data): # for every line it will take the column number from 0 -3
                #and will enter every time one piece of the data by the number of the column 0 will mean the first column and etc...
                #print(column_number)
                #print(data)
                # converts the data to a string and creates a QTableWidgetItem to display it in the table.
                self.table.setItem(row_number,column_number,QTableWidgetItem(str(data)))
        connection.close()

    # the insert dialog is where the user will enter the name course phone and submit in order to add to the table
    def insert(self):
        dialog = InsertDialog() #pop up window
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during a course I took on Udemy
        feel free to modify and reuse this app
        """
        self.setText(content)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # get student name from selected row:
        index = main_window.table.currentRow() #integer
        student_name = main_window.table.item(index,1).text() # meaning the column - name

        #get id for selected row:
        self.student_id = main_window.table.item(index,0).text()


        # add student name widget:
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # add combo box of courses
        course_name = main_window.table.item(index,2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # add mobile widget:
        mobile = main_window.table.item(index,3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)



        # add a submit button:
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("update students set name = ?, course = ?, mobile = ? where id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        #refresh the table!
        main_window.load_data()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete ?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation,0,0,1,2)
        layout.addWidget(yes,1,0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # get index and student_id for selected row:
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("delete from students where id = ?",(student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success!")
        confirmation_widget.setText("The record was deleted successfully")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #add student name widget:
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology","Math","Astronomy","Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # add mobile widget:
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # add a submit button:
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(
            self.course_name.currentIndex())  # this will give us the choice in the text from the combo box
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("insert into students (name,course,mobile) values (?,?,?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # add student name widget:
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text() #the user entering in the name box
        connection = sqlite3.connect("database.db") #connecting to the database
        cursor = connection.cursor() #creating the cursor
        # this query will give us all the names that equal to the name we enter
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        row = list(result)[0] #converting to a list from and taking the 1st tuple        print(row)
        # the main window is an instance of the MainWindow,this class has
        # table attribute -> then we can access the table -> then the table
        #has a Qwidget attribute -> this class has a finditems attribute ->
        #which allows us to use the findItems method which allows us to
        #to match the name we entered to what we have in the table
        #with this method Qt.MatchFlag.MatchFixedString
        print(row)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            #each item is a Qwidget object
            print(item)
            #item is a method of table -> this method will get 2 arguments
            # item.row() = index of the row, and 1 is the index of
            # the column = name and the set selected will
            #represent us the matching selected rows with our
            #name
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()



app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())