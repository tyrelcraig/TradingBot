#!/usr/bin/env python3

"""
AES Cipher
https://www.pycryptodome.org/en/latest/src/cipher/aes.html
 - Make sure PyCryptoDome is installed (pip install pycryptodome) 
"""

from Crypto.Cipher import AES
from Crypto import Random
import getpass
import ast

from FileHelpers import write_json_to_file

IV = Random.new().read(AES.block_size)
MODE = AES.MODE_CFB

export_filename = "../database/secrets.json"

class AESCipher(object):

	def encrypt(api_key, api_secret, export=True, export_file=export_filename):
		cipher = AES.new(getpass.getpass("Input encryption password (string will not show)"), MODE, IV)
		api_key_n = cipher.encrypt(api_key)
		api_secret_n = cipher.encrypt(api_secret)
		api_pair = {"key": str(api_key_n), "secret": str(api_secret_n)}
		if export:
			write_json_to_file(export_file, api_pair)
		return api_pair

	def decrypt(self):
		if encrypted:
			cipher = AES.new(getpass.getpass("Input decryption password (string will not show)"), MODE, IV)
			self.api_key = cipher.decrypt(self.api_key).decode()
			self.api_secret = cipher.decrypt(self.api_secret).decode()
		else:
			raise ImportError("`pycrypto` module has to be installed")