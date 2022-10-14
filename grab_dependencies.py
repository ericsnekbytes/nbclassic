import re


def run():
    with open("nbclassic.egg-info/requires.txt", "r", encoding="utf8") as fhandle:
        text = fhandle.read()

    match = re.search(
        ("""([^\[]+)              # Grab everything before first bracket
         (?:[^\[]+\[(?!t)[^\[]+)* # Match and Ignore non [test] sections
         \[test\]                 # Match and ignore the test header
         ([^\[]+)                 # Match everythin inside the test section"""),
        text,
        flags=re.VERBOSE
    )

    with open("test_requirements.txt", "w", encoding="utf8") as fhandle:
        fhandle.write(match.group(1).strip()+'\n')
        fhandle.write(match.group(2).strip())


if __name__ == '__main__':
    run()
