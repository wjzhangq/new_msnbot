#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os.path
import time
import select
import socket
import threading
import commands
import traceback
import signal
import ringQueue


def cur_file_dir():
	path = sys.path[0]
	if os.path.isdir(path):
		return path
	elif os.path.isfile(path):
		return os.path.dirname(path)


import msnlib
import msncb

def msnbot_cb_msg(md, type, tid, params, sbd):
	t = tid.split()
	email = t[0]
	
	if email == 'Hotmail':
		return
	
	lines = params.split('\n')
	headers = {}
	eoh = 1
	for i in lines:
		if i == '\r':
			break
		t, v = i.split(':', 1)
		headers[t] = v
		eoh += 1
	if headers.get('Content-Type', '') == 'text/x-msmsgscontrol':
		# typing ignore
		return
	
	md._botobj._handle_msg(email, headers, lines[eoh:])
	msncb.cb_msg(md, type, tid, params, sbd)
	
class msnbot:
	def __init__(self, email, passwd):
		self.email = email
		self.passwd = passwd
		self.msg_handlers = []
		self.inp, self.outp = os.pipe()
		self.inm, self.outm = os.pipe()
		self.recvRing = ringQueue.ringQueue(20)
	
	def _setup(self):
		self.m = msnlib.msnd()
		self.m.cb = msncb.cb()
		self.m.email = self.email
		self.m.pwd = self.passwd
		
		self.m._botobj = self
		
		self.m.cb.msg = msnbot_cb_msg
	
	def login(self, status = 'online'):
		self._setup()
		self.m.login()
		self.m.sync()
		
		#loop all entire list
		while self.m.lst_total != self.m.syn_total:
			infd, outfd = self.get_pollable_fds()
			fds = select.select(infd, outfd, [], None)
			for i in fds[0] + fds[1]:
				self.m.read(i)
		
		self.change_status(status)
		self._check_users()
	
	def close(self):
		self.m.disconnect()
	
	def reconnect(self):
		self._setup()
		self.login(self.status)
		
	def change_status(self, status):
		self.status = status
		self.m.change_status(status)
	
	def _check_users(self):
		return
		for email in self.userdict.keys():
			if email not in self.m.users:
				self.m.useradd(email, email)
	
	def get_pollable_fds(self):
		inf = self.m.pollable()
		inf[0].append(self.inp)
		return inf
	
	def loop(self):
		try:
			while True:
				infd, outfd = self.get_pollable_fds()
				fds = select.select(infd, outfd, [], 1)
				for i in fds[0] + fds[1]:
					try:
						if i == self.inp:
							msgStr =  os.read(self.inp, 10240)
							email, body = msgStr.split(':', 1)
							r = self.m.sendmsg(email, body)
							os.write(self.outm, '%s' % (r,))
						else:
							self.m.read(i)
					except (msnlib.SocketError, socket.error), err:
						import traceback
						exc_type, exc_value, exc_traceback = sys.exc_info()
						traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
						traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
						traceback.print_exc()
						if i != self.m:
							self.m.close(i)
						else:
							return
					except (Exception), err:
						print err
					except:
						print 'some erero raise'
						exc_type, exc_value, exc_traceback = sys.exc_info()
						traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
						traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
						traceback.print_exc()
		except (Exception), err:
			print err
		except:
			print 'end some erero raise'
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
			traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
			traceback.print_exc()
	
	def bgloop(self):
		'''backgroup loop'''
		threading.Thread(name="msn loop thread", target=self.loop).start()

	def register_msg_handler(self, f):
		"Registers a message handler"
		self.msg_handlers.append(f)

	def _handle_msg(self, email, header, msg):
		reply = []
		
		self.recvRing.put([email, header,msg])
		
		for f in self.msg_handlers:
			r = f(email, header, msg)
			if r:
				reply.append(r)

		if reply:
			self.m.sendmsg(email, '\r\n'.join(reply))
	
	def send_msg(self, email, msg):
		if email not in self.m.users:
			return	'%s is not your friend, please add it first' % email
		
		if self.m.users[email].status == 'FLN':
			return '%s is offline, please try later' % email
		
		os.write(self.outp, email + ':' + msg)
		r = os.read(self.inm, 1024)
		if r == '1':
			ret =  'ok Message for %s queued for delivery' % email
		elif r == '2':
			ret = 'ok Message for %s delivery' % email
		elif r == '-2':
			ret = 'Message too big'
		else:
			ret = 'Error %s sending message' % r
		
		return ret


#
# Message handlers
#
def msn_msg_handler(email, header, msg):
	return ''


def getWho():
	strwho =  commands.getoutput('who')
	rawList =  [i.split()[0] for i in strwho.split('\n')]
	return set(rawList)

def signal_handler(signum, frame):
	print 'signal', signum
	sys.exit()


def newConn(conn, addr, m):
	print 'new connect', addr
	lastEmail = ''
	while True:
		try:
			rs, ws, es  = select.select([conn], [conn], [], 10)
			for r in rs:
				data = r.recv(10240)
				if not data:
					print 'no data'
				else:
					print lastEmail, 'is need'
					if len(lastEmail) > 0:
						print m.send_msg(lastEmail, data)
					else:
						print 'data:', data

			for r in ws:
				msg = m.recvRing.get()
				if msg == None:
					m.recvRing.wait(1)
					r.send('None\n')
				else:
					lastEmail = msg[0]
					print lastEmail , 'set'
					r.send(str(msg[0]) + '\n' + str(msg[1]) + '\n' + str(msg[2]) + '\n')

			if not rs and not ws:
				print 'timeout'
		except (Exception), e:
			print e
			try:
				r.close()
			except (Exception), e1:
				print e1
			print 'close the conn!'
			break

	
def main():
	signal.signal(signal.SIGINT,signal_handler)
	signal.signal(signal.SIGTERM,signal_handler)
	signal.signal(3,signal_handler)
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('127.0.0.1', 9876))
	s.listen(10)
	

	# get the login email and password from the parameters
	try:
		email = 'test@zhangwenjin.com'
		passwd = '123456'

	except:
		print "Use: msnsbot email password"
		sys.exit(1)

	b = msnbot(email, passwd)
	
	
	
	b.register_msg_handler(msn_msg_handler)
	b.login()
	b.bgloop()
	

	
	while True:
		rs, ws, es  = select.select([s], [], [])
	
		for r in rs:
			conn, addr = s.accept()
			threading.Thread(target=newConn, args=(conn, addr, b)).start()

if __name__ == '__main__':
	main()
