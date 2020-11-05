"""
Copyright 2020 Black Foundry.

This file is part of Robo-CJK.

Robo-CJK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robo-CJK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import base64

U,V,W=2-2,-3+4,8-11
yy=enumerate
x=base64.b64decode

def i__r(w):
	return chr(ord(w[V]) - W - w[U])

def d__r(v):
	return chr(-v[U] + ord(v[V]) + W)

def t__t(i):
	return (i+4)%2 

def varichari(s):
	u = s
	return str("".join(map(lambda x: d__r(x) if t__t(x[U]) % 2 else i__r(x), yy(u))))

def d(s):
	return x(s)[::-1]

def test_all():
	"""
	"""
	ex = b'dHNldA=='
	x = "qirz"
	print(tuple(enumerate(x)))
	print(i__r((0,'w')))
	print(d__r((3,'t')))
	print(t__t(5))
	print(varichari(x))
	print(d(ex).decode())


if __name__ == "__main__":
	"""
	"""
	test_all()