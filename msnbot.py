#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os.path
import time
import select
import socket
import thread
import commands

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
		return self.m.pollable()
	
	def loop(self):
		while True:
			infd, outfd = self.get_pollable_fds()
			infd.append(self.inp)
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
					traceback.print_last()
					if i != self.m:
						self.m.close(i)
					else:
						return
	
	def bgloop(self):
		'''backgroup loop'''
		thread.start_new_thread(self.loop, ())
		

	def register_msg_handler(self, f):
		"Registers a message handler"
		self.msg_handlers.append(f)

	def _handle_msg(self, email, header, msg):
		reply = []

		for f in self.msg_handlers:
			r = f(email, '', header, msg)
			if r:
				reply.append(r)

		if reply:
			self.m.sendmsg(email, '\r\n'.join(reply))
	
	def send_msg(self, email, msg):
		os.write(self.outp, email + ':' + msg)
		r = os.read(self.inm, 1024)
		if r == '1':
			ret =  'Message for %s queued for delivery' % email
		elif r == '2':
			ret = 'Message for %s delivery' % email
		elif r == '-2':
			ret = 'Message too big'
		else:
			ret = 'Error %s sending message' % r
		
		return ret


#
# Message handlers
#

def sample_msg_handler(email, info, header, msg):
	return "Echo!\n" + '\n'.join(msg)
	
# gtalkbot-compatible message handler
class gtalkbot_msg_handler:
	def __init__(self, path):
		self.plugins = []
		sys.path.insert(0, path)
		for f in os.listdir(path):
			if f.endswith('.py'):
				root, ext = os.path.splitext(f)
				self.plugins.append(__import__(root))
		sys.path.pop(0)
		self.verbs = {}

		for p in self.plugins:
			for v in p.Verbs():
				if v not in self.verbs:
					self.verbs[v] = []
				self.verbs[v].append(p)
		print self.verbs
		self.authenticated_users = []

	def handle_msg(self, email, info, header, msg):
		# XXX: this only handles the first line
		vl = msg[0].split(None, 1)
		if not vl:
			return
		if len(vl) < 2:
			verb, line = vl[0], ''
		else:
			verb, line = vl

		if email not in self.authenticated_users and verb != 'auth':
			return 'You need to authenticate\n' \
				+ 'Use: auth <password>'

		if verb == 'auth':
			if line != info:
				return 'Wrong password, try again'
			self.authenticated_users.append(email)
			return 'Welcome!'

		elif verb == 'help':
			if not line:
				return 'Use: help <verb>'

			reply = []
			for p in self.plugins:
				if 'Help' not in dir(p):
					continue
				r = p.Help(line)
				if r:
					reply.append(r)
			if reply:
				return '\r\n'.join(reply)
			else:
				return 'Sorry, no help for ' + line

		elif verb in self.verbs:
			reply = []
			for p in self.verbs[verb]:
				r = p.Command(verb, line)
				if r:
					reply.append(r)
			if reply:
				return '\r\n'.join(reply)
			else:
				return 'Unknown verb'

		else:
			return 'Unknown verb'


	def __call__(self, email, info, header, msg):
		return self.handle_msg(email, info, header, msg)

def getWho():
	strwho =  commands.getoutput('who')
	rawList =  [i.split()[0] for i in strwho.split('\n')]
	return set(rawList)
	
def main():

	# get the login email and password from the parameters
	try:
		email = 'test@zhangwenjin.com'
		passwd = '123456'

	except:
		print "Use: msnsbot email password userlist pluginspath"
		sys.exit(1)

	b = msnbot(email, passwd)
	b.register_msg_handler(sample_msg_handler)
	b.login()
	b.register_msg_handler(gtalkbot_msg_handler(os.getcwd() + os.sep + 'plugins'))
	b.bgloop()
	
	preWho = getWho()
	while True:
		time.sleep(10)
		curWho = getWho()
		if len(curWho) != len(preWho):
			if len(curWho) > len(preWho):
				b.send_msg('msn@zhangwenjin.com', ','.join(curWho - preWho) + ' has login')
			else:
				b.send_msg('msn@zhangwenjin.com', ','.join(preWho - curWho) + ' has logout')

			preWho = curWho

if __name__ == '__main__':
	main()
