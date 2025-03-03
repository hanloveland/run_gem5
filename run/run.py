import subprocess

GEM_PATH = '/var/share/gem5/gem5/build/X86/gem5.opt'
scipt_path = 'skylake-config/run-se.py'
binary_path = '/var/share/gem5/gem5/tests/test-progs/hello/bin/x86/linux/hello'
try:
    result = subprocess.run([GEM_PATH,scipt_path,'Tuned',binary_path],capture_output=True, text=True, check=True)
    print("Run Result")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("Error Run Scipt")
    print(e.stderr)