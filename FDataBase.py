import sqlite3

class FDataBase:
    def __init__(self, db) -> None:
        self.__db = db
        self.__cur = db.cursor()

    def add_time(self, user_id, time, milliseconds):
        try:
            self.__cur.execute('insert into Times values(null, ?, ?, ?)', (user_id, time, milliseconds))
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        
        return True
    
    def add_user(self, name):
        try:
            self.__cur.execute('insert into Users values(null, ?)', (name, ))
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        
        return True

    
    def get_time(self):
        try:
            self.__cur.execute(f'select * from Times')
            res = self.__cur.fetchall()
            if res:
                return res

        except sqlite3.Error as e:
            print(e)

        return []
    
    def is_name_in_db(self, name):
        try:
            self.__cur.execute(f'select count() as count from Users where username like "{name}"')
            res = self.__cur.fetchone()
            if res['count'] > 0:
                return True
            
        except sqlite3.Error as e:
            print(e)
            return False
        
        return False
    
    def get_data_by_nick(self, nick):
        try:
            self.__cur.execute(f'''select Times.time_each_assembly as "time", Times.milliseconds as "milli", Users.username from Times
                                    inner join Users on Users.user_id = Times.user_id
                                    where Users.username like "{nick}"
                                ''')
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print(e)
            return []
        
        return []
    
    def get_id_by_nick(self, nick):
        try:
            self.__cur.execute(f'''select user_id from Users
                                    where Users.username like "{nick}"
                                ''')
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print(e)
            return ''
        
        return ''
    
    import sqlite3

    def delete_last_n_entries_by_nick(self, id, n):
        try:
            self.__cur.execute(f'''DELETE FROM Times WHERE rowid IN (
                                        SELECT rowid FROM Times WHERE user_id == {int(id)}
                                        ORDER BY time_id DESC
                                        LIMIT {n}
                                    )''')
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False

        return True
