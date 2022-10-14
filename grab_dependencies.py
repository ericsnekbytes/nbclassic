import re


def run():
    with open("nbclassic.egg-info/requires.txt", "r", encoding="utf8") as fhandle:
        text = fhandle.read()

    match = re.search(r'([^\[]+)(?:[^\[]+\[(?!t)[^\[]+)*\[test\]([^\[]+)', text)

    with open("test_requirements.txt", "w", encoding="utf8") as fhandle:
        fhandle.write(match.group(1).strip()+'\n')
        fhandle.write(match.group(2).strip())


if __name__ == '__main__':
    run()
