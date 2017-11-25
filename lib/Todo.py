from lib.Database import Database
from lib.Note import Note
import dateparser
import datetime
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TabbedApp(QTabWidget):
    def __init__(self, parent = None):
        super(TabbedApp, self).__init__(parent)
        TasksList.due_lists = {
            'today': [('>', dateparser.parse('yesterday at 23:59')),
                        ('<', dateparser.parse('tomorrow at 00:01'))],
            'overdue': [('<', dateparser.parse('today at 00:01'))],
            'tomorrow': [('>', dateparser.parse('today at 23:59')),
                            ('<', dateparser.parse('in 2 days at 00:01'))],
            'upcoming': [('>', dateparser.parse('tomorrow at 23:59'))],
            'sometime': [('IS null', )]
        }
        for date in TasksList.due_lists.keys():
            setattr(self, date, TasksList(date))
            self.addTab(getattr(self, date), date.capitalize())
    

class TasksList(QTreeView):
    due_lists = {}
    def __init__(self, date):
        super(TasksList, self).__init__()
         
        # Create an empty model for the list's data
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['ID', 'Title', 'Content', 'Priority', 'Due_in', 'Delete'])
         
        all_notes = Note.get_notes_by('due_in', TasksList.due_lists[date])
        for note in all_notes:
            TasksList.createRow(note, self.model)

        self.model.itemChanged.connect(self.on_change)

        # Apply the model to the list view
        self.setModel(self.model)

    # define what to do when an item is changed
    def on_change(self, item):
        note_id = item.model().item(item.row(), 0).text()
        # edit title
        # mark completed
        try:
            note = Note.find(note_id)
        except TypeError:
            pass
        else:
            col = item.column()
            # if column 0, it's the checkbox
            if col == 0:
                f = item.font()
                if item.checkState() == 2: #checked
                    note.setCompleted(2)
                    f.setStrikeOut(True)
                elif item.checkState() == 0: #unchecked
                    note.setCompleted(1)
                    f.setStrikeOut(False)
                item.setFont(f)
            elif col == 5: # delete
                note.delete()
                item.model().removeRow(item.row())
            else: #all else
                sql_column = self.model.horizontalHeaderItem(col).text().lower()
                setattr(note, sql_column, item.text())
                note.save()

    @staticmethod
    def createRow(task, model):
        # create an item with a caption
        col1 = QStandardItem(str(task[0]))
        if task[5] == 2: # if completed
            f = col1.font()
            f.setStrikeOut(True)
            col1.setFont(f)
            col1.setCheckState(2)
        col2 = QStandardItem(task[1])
        col3 = QStandardItem(task[2])
        col4 = QStandardItem(task[3])
        col5 = QStandardItem(dateparser.parse(task[4]).strftime("%c"))
        col6 = QStandardItem()
        col6.setCheckable(True)
     
        # add a checkbox to it
        col1.setCheckable(True)
     
        # Add the item to the model
        model.appendRow([col1, col2, col3, col4, col5, col6])

class AddTaskForm(QDialog):
    def __init__(self, list_view):
        super(AddTaskForm, self).__init__()
        self.list_view = list_view
        mainLayout = QFormLayout()
        self.title_input = QLineEdit(self)
        self.content_input = QLineEdit(self)
        self.priority_input = QLineEdit(self)
        self.date_input = QLineEdit(self)
        mainLayout.addRow(QLabel('Title:'), self.title_input)
        mainLayout.addRow(QLabel('Content:'), self.content_input)
        mainLayout.addRow(QLabel('Priority:'), self.priority_input)
        mainLayout.addRow(QLabel('Due in:'), self.date_input)
        add_task_button = QPushButton('Add Task')
        add_task_button.clicked.connect(self.add)
        mainLayout.addWidget(add_task_button) 
        self.setLayout(mainLayout)
        self.setWindowTitle('Add Task')

    def add(self):
        note = Note()
        note.title = self.title_input.text()
        note.content = self.content_input.text()
        note.priority = self.priority_input.text()
        # take care of due dates
        note.due_in = self._manage_dates(self.date_input.text())
        note.save()
        task = (note.id, note.title, note.content, note.priority, note.due_in, 1)
        TasksList.createRow(task, self.list_view.model)
        self.hide() # close the 'add task' window

    def _manage_dates(self, date):
        # today/tomorrow at X
        # in 2 days at X
        # 20/10 at X
        return dateparser.parse(date)
 
class Todo(object):
    def __init__(self, db, table_name):
        super().__init__()
        Database.connect_to_db(db)
        Database.init_db(table_name)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        Database.db.close()

    def launch(self, **window_args):
        wargs = {'title': '', 'width': 800, 'height': 600}
        wargs.update(window_args)
        a = QApplication(sys.argv)
        window = QWidget()
        window.setWindowTitle(wargs['title'])
        window.setMinimumSize(wargs['width'], wargs['height'])
        layout = QGridLayout()
        add_task_button = QPushButton('Add Task')
        add_task_button.clicked.connect(self.add)
        layout.addWidget(add_task_button)
        self.tabbedApp = TabbedApp()
        layout.addWidget(self.tabbedApp)
        window.setLayout(layout)
        # Show the window and run the app
        window.show()
        sys.exit(a.exec_())

    def add(self):
        self.task_form = AddTaskForm(self.tabbedApp.currentWidget())
        self.task_form.show()
