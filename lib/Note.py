from lib.Database import Database
class Note(object):
    columns = ['title', 'content', 'priority', 'due_in', 'completed', 'id']
    def __init__(self, *values):
        if values:
            if isinstance(values[0], list):
                values = values[0]
        i = 0
        for column in Note.columns:
            try:
                value = values[i]
            except IndexError:
                value = None
            finally:
                setattr(self, column, value)
                i += 1

    def save(self):
        #update or insert
        values = []
        c_marks = []
        insert_columns_not_null = []
        insert_columns = Note.insert_columns()
        for col in insert_columns:
            val = getattr(self, col)
            if val:
                values.append(val)
                c_marks.append('?')
                insert_columns_not_null.append(col)
        if self.id is None:
            columns = ','.join(insert_columns_not_null)
            c_marks = ','.join(c_marks)
            Database.cursor.execute('INSERT INTO {0} ({1}) VALUES ({2})'.format(Database.table, columns, c_marks), values)
        else:
            values.append(self.id)
            update_syntax = ''
            for col in insert_columns_not_null[:-1]:
                update_syntax += '{} = ?, '.format(col)
            update_syntax += '{} = ?'.format(insert_columns_not_null[len(insert_columns_not_null)-1])
            Database.cursor.execute('UPDATE {0} SET {1} WHERE id = ?'.format(Database.table, update_syntax), values)
        
        self.commit()
        self.id = Database.cursor.lastrowid

    def commit(self):
        Database.db.commit()

    def setCompleted(self, v):
        if v < 1 or v > 2:
            v = 2
        self.completed = v
        self.save()

    def delete(self):
        Database.cursor.execute('DELETE FROM {} WHERE id = ?'.format(Database.table), (self.id,)) # requires us to provide a tuple or an array..
        self.commit()

    @staticmethod
    def insert_columns():
        #without the id column
        return Note.columns[:len(Note.columns)-1]

    @staticmethod
    def find(note_id, select = '*'): # get a specific note
        found = Database.cursor.execute('SELECT {0} FROM {1} WHERE id = ?'.format(select, Database.table), (note_id,)).fetchone()
        note_info = list(found)
        # now we want to move the first element (ID) to the end of the list
        note_info.append(note_info.pop(0))
        return Note(note_info)

    @staticmethod
    def multi_where(rows, **where):
        where_syntax = ''
        args = []
        try:
            if where:
                where_syntax = 'WHERE {}'.format(where['syntax'])
                args = where['args']
        except KeyError:
            pass
        finally:
            return Database.cursor.execute('SELECT {0} FROM {1} {2}'.format(rows, Database.table, where_syntax), args).fetchall()
 
    @staticmethod
    def get_notes_by(column, queries):
        notes = []
        i = 0
        due_args = []
        where_syntax = ''
        for date_tuple in queries:
            if i:
                where_syntax += ' AND '
            try:
                q_mark = ' ?'
                due_args.append(date_tuple[1])
            except IndexError:
                q_mark = ''
            finally: 
                where_syntax += '{column} {cond}{q_mark}'.format(column=column, cond=date_tuple[0], q_mark=q_mark)
            i += 1

        return Note.multi_where('*', syntax=where_syntax, args=due_args)
