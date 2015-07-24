#!/usr/bin/env python
# coding = utf-8
import uuid
import hashlib

# hash + salt encrypt
def encrypt(plain_text_pwd):
	salt = uuid.uuid4().hex
	print salt
	return hashlib.sha512(plain_text_pwd + salt).hexdigest() + salt

# check password
# matched, return True, or False
def checkpwd(plain_text_pwd, hash_pwd):
	salt = hash_pwd[len(hash_pwd) - 32 : len(hash_pwd)]
	return hashlib.sha512(plain_text_pwd + salt).hexdigest() + salt == hash_pwd
