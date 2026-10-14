"""Read-only connection check. Does not submit a quantum workload."""
import json
from qchat.ibm import IBMRunner

def main():
    runner=IBMRunner()
    print(json.dumps(runner.info(),indent=2))
    print('Physical backend configured. No physical execution has been tested by this check.')
if __name__=='__main__':main()
