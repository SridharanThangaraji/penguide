import sys
from core.orchestrator import Orchestrator

def main():
    if len(sys.argv) < 2:
        return  # silent exit, Unix-style

    user_input = " ".join(sys.argv[1:])
    cogment = Orchestrator()
    output = cogment.step(user_input)

    if output:
        print(output)

if __name__ == "__main__":
    main()
