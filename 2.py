import subprocess
from pexpect import popen_spawn
import pexpect

cmd = "cd /Users/zhongfener/Desktop/python/github"
returned_value = subprocess.call(cmd, shell=True)

cmd = 'git init'
subprocess.call(cmd, shell=True)

cmd = "git add ."
subprocess.call(cmd, shell=True)

cmd = 'git commit -m "just test！！！"'
subprocess.call(cmd, shell=True)

cmd = 'git remote remove origin'
subprocess.call(cmd, shell=True)

cmd = "git remote add origin https://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@github.com/huojiayang/test123.git"
subprocess.call(cmd, shell=True)

cmd = "git push -u origin master"
subprocess.call(cmd, shell=True)

print(cmd, 66666)