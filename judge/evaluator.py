import subprocess
import tempfile
import os
import time
import sys

def run_python_code(code, input_str, time_limit):
    python_executable = sys.executable
    """Ejecuta código Python y retorna (output, error, status)"""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(code.encode('utf-8'))
        tmp_path = tmp.name

    start_time = time.time()
    try:
        proc = subprocess.run(
            [python_executable, tmp_path],
            input=input_str,
            capture_output=True,
            text=True,
            timeout=time_limit
        )
        duration = time.time() - start_time
        if proc.stderr:
            return proc.stdout.strip(), proc.stderr.strip(), duration, "RE"
        
        return proc.stdout.strip(), proc.stderr.strip(), duration, "SUCCESS"
    
    except subprocess.TimeoutExpired:
        return "", "Time Limit Exceeded", time_limit, "TLE"
    
    except Exception as e:
        return "", str(e), 0, "RE"
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
   