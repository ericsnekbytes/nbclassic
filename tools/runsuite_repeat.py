"""CI/CD debug script"""


import os
import subprocess
import time


def run():
    for stepnum in range(10):
        try:
            print(f'\n\n{os.listdir(".")}\n\n')
            proc = subprocess.run(['pytest', '-sv', 'nbclassic/tests/end_to_end'])
        except Exception:
            print(f'\n[RUNSUITE_REPEAT] Run {stepnum} -> Exception')
            continue
        print(f'\n[RUNSUITE_REPEAT] Run {stepnum} -> {"Success" if proc.returncode == 0 else proc.returncode}\n')


if __name__ == '__main__':
    run()
