from lib.Todo import Todo

with Todo("example.db", 'notes') as app:
    window = {'title': 'Todo App', 'height': 400, 'width': 800}
    app.launch(**window)
