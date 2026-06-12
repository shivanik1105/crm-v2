import subprocess
import time
import os
import sys

env = os.environ.copy()
env['PYTHONPATH'] = r'F:\shivani\VSCode\projects\crm\backend'

# Start the server in background
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=r'F:\shivani\VSCode\projects\crm',
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server
for i in range(15):
    time.sleep(1)
    try:
        import urllib.request
        urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)
        print('Server is running on port 8000')
        break
    except:
        pass
else:
    print('Server failed to start')
    proc.terminate()
    out, err = proc.communicate()
    print('STDERR:', err.decode())
