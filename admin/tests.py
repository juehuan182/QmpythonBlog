from django.test import TestCase

# Create your tests here.


import subprocess


file = '/root/src/www/shell_script/backup/test.sh'
# output = subprocess.Popen(file, shell=True)
# print(output)

output = subprocess.Popen(file, shell=True)

print(type(output), str(output))
