import re
import Crypto.Hash.MD5 as MD5
import base64
q = ""
md5 = MD5.new(q.encode("utf-8")).digest()
base = base64.b64encode(md5).decode()
print(base)

