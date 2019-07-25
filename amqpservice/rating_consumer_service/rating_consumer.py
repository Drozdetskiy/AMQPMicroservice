from time import sleep


def run_consumer():
    while True:
        print("test consumer")
        sleep(1)


if __name__ == '__main__':
    run_consumer()
