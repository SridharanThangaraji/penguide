import sys
from core.orchestrator import Orchestrator

def main():
    cogment = Orchestrator()

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        output = cogment.step(user_input)
        if output:
            print(output)
        return

    # Interactive loop
    print("Penguide - Your Linux & Kernel Guide (Type 'exit' to quit)")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue
            
            output = cogment.step(user_input)
            if output:
                print(output)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
