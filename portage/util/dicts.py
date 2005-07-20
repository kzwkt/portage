# Copyright: 2005 Gentoo Foundation
# Author(s): Brian Harring (ferringb@gentoo.org)
# License: GPL2
# $Header$

class IndexableSequence(object):
	def __init__(self, get_keys, get_values, recursive=False, returnEmpty=False, 
			returnIterFunc=None, modifiable=False, delfunc=None, updatefunc=None):
		self.__get_keys = get_keys
		self.__get_values = get_values
		self.__cache = {}
		self.__cache_complete = False
		self.__cache_can_be_complete = not recursive and not modifiable
		self.__return_empty = returnEmpty
		self.__returnFunc = returnIterFunc
		self._frozen = not modifiable
		if not self._frozen:
			self.__del_func = delfunc
			self.__update_func = updatefunc


	def __getitem__(self, key):
		if not (self.__cache_complete or self.__cache.has_key(key)):
			self.__cache[key] = self.__get_values(key)
		return self.__cache[key]


	def keys(self):
		return list(self.iterkeys())

	
	def __delitem__(self, key):
		if self._frozen:
			raise AttributeError
		if not key in self:
			raise KeyError(key)
		return self.__del_func(key)


	def __setitem__(self, key, value):
		if self._frozen:
			raise AttributeError
		if not key in self:
			raise KeyError(key)
		return self.__update_func(key, value)


	def __contains__(self, key):
		try:	
			self[key]
			return True
		except KeyError:
			return False


	def iterkeys(self):
		if self.__cache_complete:
			return self.__cache.keys()
		return self.__gen_keys()


	def __gen_keys(self):
		for key in self.__get_keys():
			if not self.__cache.has_key(key):
				self.__cache[key] = self.__get_values(key)
			yield key
		self.__cache_complete = self.__cache_can_be_complete
		return


	def __iter__(self):
		if self.__returnFunc:
			for key, value in self.iteritems():
				if len(value) == 0:
					if self.__return_empty:
						yield key
				else:
					for x in value:
						yield self.__returnFunc(key, x)
		else:
			for key, value in self.iteritems():
				if len(value) == 0:
					if self.__return_empty:
						yield key
				else:
					for x in value:
						yield key+'/'+x
		return


	def items(self):
		return list(self.iteritems())
	

	def iteritems(self):
		if self.__cache_complete:
			return self.__cache.items()
		return self.__gen_items()


	def __gen_items(self):
		for key in self.iterkeys():
			yield key, self[key]
		return


class LazyValDict(object):

	def __init__(self, get_keys_func, get_val_func):
		self.__val_func = get_val_func
		self.__keys_func = get_keys_func
		self.__vals = {}
		self.__keys = {}


	def __setitem__(self):
		raise AttributeError


	def __delitem__(self):
		raise AttributeError


	def __getitem__(self, key):
		if self.__keys_func != None:
			map(self.__keys.setdefault, self.__keys_func())
			self.__keys_func = None
		if key in self.__vals:
			return self.__vals[key]
		if key in self.__keys:
			v = self.__vals[key] = self.__val_func(key)
			del self.__keys[key]
			return v
		raise KeyError(key)


	def iterkeys(self):
		if self.__keys_func != None:
			map(self.__keys.setdefault, self.__keys_func())
			self.__keys_func = None
		for k in self.__keys.keys():
			yield k
		for k in self.__vals.keys():
			yield k


	def keys(self):
		return list(self.iterkeys())


	def __contains__(self, key):
		if self.__keys_func != None:
			map(self.__keys.setdefault, self.__keys_func())
			self.__keys_func = None
		return key in self.__keys or key in self.__vals

	__iter__ = iterkeys
	has_key 	= __contains__


	def iteritems(self):
		for k in self.iterkeys():
			yield k, self[k]


	def items(self):
		return list(self.iteritems())


class ProtectedDict(object):
	__slots__=("orig","new","blacklist")

	def __init__(self, orig):
		self.orig = orig
		self.new = {}
		self.blacklist = {}


	def __setitem__(self, key, val):
		self.new[key] = val
		if key in self.blacklist:
			del self.blacklist[key]


	def __getitem__(self, key):
		if key in self.new:
			return self.new[key]
		if key in self.blacklist:
			raise KeyError(key)
		return self.orig[key]


	def __delitem__(self, key):
		if key in self.new:
			del self.new[key]
		elif key in self.orig:
			if key not in self.blacklist:
				self.blacklist[key] = True
				return
		raise KeyError(key)
			

	def iterkeys(self):
		for k in self.new.iterkeys():
			yield k
		for k in self.orig.iterkeys():
			if k not in self.blacklist and k not in self.new:
				yield k


	def keys(self):
		return list(self.iterkeys())


	def __contains__(self, key):
		return key in self.new or (key not in self.blacklist and key in self.orig)

	__iter__ = iterkeys
	has_key = __contains__


	def iteritems(self):
		for k in self.iterkeys():
			yield k, self[k]


	def items(self):
		return list(self.iteritems())

