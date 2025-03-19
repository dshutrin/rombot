import pymysql


class Base:
	def __init__(self):
		self.conn = pymysql.connect(
			host='localhost',
			user='root',
			password='Ltkmnf-02',
			database='romabot',
			cursorclass=pymysql.cursors.DictCursor
		)
		self.cur = self.conn.cursor()
		self.init_tables()

	def init_tables(self):
		cmds = (
			'create table if not exists users(id int primary key auto_increment, uid int not null, role bool default 0, mode varchar(30) default "start", saved_q text);',
			'create table if not exists tasks(id int primary key auto_increment, q text, a text);'
		)

		for cmd in cmds:
			self.cur.execute(cmd)

		self.conn.commit()

	def change_mode(self, uid, mode):
		self.cur.execute(f'update users set mode="{mode}" where uid={uid};')
		self.conn.commit()

	def get_mode(self, uid):
		try:
			self.cur.execute(f'select mode from users where uid={uid};')
		except:
			return None

		data = self.cur.fetchone()
		if data:
			return data['mode']
		return None

	def is_admin(self, uid):
		try:
			self.cur.execute(f'select role from users where uid={uid};')
		except:
			return False

		data = self.cur.fetchone()
		if data:
			return bool(data['role'])
		return False

	def get_query(self, uid):
		try:
			self.cur.execute(f'select saved_q from users where uid={uid};')
		except:
			return None

		data = self.cur.fetchone()
		if data:
			return data['saved_q']
		return None

	def set_phrase(self, uid, phrase):
		self.cur.execute(f'update users set saved_q="{phrase}" where uid={uid};')
		self.conn.commit()

	def add_task(self, query, answer):
		self.cur.execute(f'select * from tasks where q="{query}";')
		data = self.cur.fetchall()

		if len(data) > 0:
			return 'Такая фраза уже существует'
		else:
			self.cur.execute(f'insert into tasks(q, a) values("{query}", "{answer}");')
			self.conn.commit()

			return 'Успех'

	def get_answer(self, q):
		self.cur.execute(f'select a from tasks where q="{q}";')
		data = self.cur.fetchall()

		if len(data) > 0:
			return data[0]['a']
		else:
			return 'Такого кода не существует!'

	def rm_code(self, q):
		self.cur.execute(f'select * from tasks where q="{q}";')
		data = self.cur.fetchall()

		if len(data) > 0:
			id_ = data[0]['id']
			self.cur.execute(f'delete from tasks where id={id_};')
			self.conn.commit()
			return 'Успех'
		else:
			return 'Не найден'
