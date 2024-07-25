import aiosqlite, logging

class UsersDataBase:
    def __init__(self):
        self.name = 'database/users.db'
        
    async def create_table(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            create_users_table = '''
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                real_name TEXT,
                majnor INTEGER,
                language TEXT
                );
                '''
            await cursor.execute(create_users_table)
            await db.commit()

# ===================================================================================== #

    async def add_user(self, id: int, name: str, real_name: str, majnor: int, language: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "INSERT INTO users (id, name, real_name, majnor, language) VALUES (?, ?, ?, ?, ?)"
            if not name:
                name = 0 if not cursor.lastrowid else cursor.lastrowid
                await cursor.execute(query, (id, f"UnNamed_{name}", real_name, majnor, language))
            else:
                await cursor.execute(query, (id, name, real_name, majnor, language))
            await db.commit()
            
    async def get_user(self, id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "SELECT * FROM users WHERE id = ?"
            await cursor.execute(query, (id,))
            return await cursor.fetchone()
        
    async def get_all_users(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "SELECT * FROM users"
            await cursor.execute(query)
            return await cursor.fetchall()

# ===================================================================================== #
   
class HomeWorkBase:
    def __init__(self):
        self.name = 'database/homework.db'
        
    async def create_table(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            create_homework_table = '''
                CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY,
                subject TEXT,
                homework_text TEXT,
                data TEXT,
                user_add TEXT
                );
                '''
            await cursor.execute(create_homework_table)
            await db.commit()
            
# ===================================================================================== #

    async def add_work(self, subject: str, homework_text: str, data: str, user_add: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "INSERT INTO homework (id, subject, homework_text, data, user_add) VALUES (?, ?, ?, ?, ?)"
            
            try:
                id = cursor.lastrowid
            except TypeError:
                id = 0
            await cursor.execute(query, (id, subject, homework_text, data, user_add))
            await db.commit()
    
    async def dell_work(self, subject: str, data: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "DELETE FROM homework WHERE subject = ? AND data = ?"
            await cursor.execute(query, (subject, data))
            await db.commit()
            
    async def get_work(self, subject: str, data: str, user_add: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "SELECT * FROM homework WHERE subject = ? AND data = ? AND user_add = ?"
            await cursor.execute(query, (subject, data, user_add))
            return await cursor.fetchone()
            
    async def get_all_subs_by_name(self, subject: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "SELECT * FROM homework WHERE subject = ?"
            await cursor.execute(query, (subject,))
            return await cursor.fetchall()
        
    async def update_text(self, subject: str, homework_text: str, data: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "UPDATE homework SET homework_text = ? WHERE subject = ? AND data = ?"
            await cursor.execute(query, (homework_text, subject, data))
            await db.commit()
            
    async def get_all_works(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = "SELECT * FROM homework"
            await cursor.execute(query)
            return await cursor.fetchall()
            
