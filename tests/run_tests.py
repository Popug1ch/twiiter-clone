import subprocess
import sys
import os

def print_banner():
    print("=" * 70)
    print("🎯 ЗАПУСК ТЕСТОВ MICROBLOG API")
    print("=" * 70)

def run_all_tests():
    cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short", "--color=yes", "."]
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    return result.returncode

def main():
    print_banner()
    if len(sys.argv) < 2:
        print("python run_tests.py [all|health|users|tweets|medias|schemas|integration]")
        return 0
    command = sys.argv[1]
    if command == "all":
        return run_all_tests()
    cmd = [sys.executable, "-m", "pytest", "-v", command]
    return subprocess.run(cmd, cwd=os.path.dirname(__file__)).returncode

if __name__ == "__main__":
    sys.exit(main())
