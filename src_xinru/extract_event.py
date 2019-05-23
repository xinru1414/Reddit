import os,sys
import subprocess


def main():
    directory = sys.argv[1]
    for file in os.listdir(directory):
        try:
            print(file)
            output = subprocess.run(['./runevents.sh', '-model', 'src/main/resources/models', os.path.join(directory,file), 'raw'], capture_output=True)
            output.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error processing '{file}': {e}")


if __name__ == '__main__':
    main()