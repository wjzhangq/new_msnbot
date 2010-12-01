import threading

class ringQueue():
	def __init__(self, ringMax):
		if ringMax < 3:
			raise 'ringMax must lagest 3'
		self.ringMax = ringMax
		self.startPos = 0
		self.endPos = 0
		self.ring = [0 for i in xrange(ringMax)]
		self.ringEvent = threading.Event()
	
	def put(self, val):
		tmp = self.endPos + 1
		if tmp >= self.ringMax:
			tmp = tmp - self.ringMax
		
		if tmp == self.startPos:
			tmp1 = self.startPos + 1
			if tmp1 >= self.ringMax:
				tmp1 = tmp1 - self.ringMax
			self.startPos = tmp1
		
		self.endPos = tmp
		self.ring[tmp] = val
		self.ringEvent.set()
		
		
	
	def get(self):
		if self.startPos == self.endPos:
			self.ringEvent.clear()
			return None
		else:
			tmp = self.startPos + 1
			if tmp >= self.ringMax:
				tmp = tmp - self.ringMax
			ret = self.ring[tmp]
			self.startPos = tmp
			
			return ret
	
	def clear(self):
		self.startPos = 0
		self.endPos = 0
		self.ringEvent.clear()
	
	def getLen(self):
		if self.startPos == self.endPos:
			return 0
		elif self.startPos > self.endPos:
			return self.ringMax + self.endPos - self.startPos
		else:
			return self.endPos - self.startPos
			
	def wait(self, timeout=None):
		self.ringEvent.wait(timeout)

		
if __name__ == '__main__':
	import random
	
	q = ringQueue(5)
	for i in xrange(10):
		put = random.randrange(1, 10)
		get = random.randrange(1, 10)
		for j in xrange(put):
			q.put(j)
			print 'put %d and length %d' % (j, q.getLen())
		for j in xrange(get):
			t = q.get()
			print 'get %s and length %d' % (t, q.getLen())
		
		
