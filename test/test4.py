from multiprocessing import Process

class A(Process):
    def __init__(self, i):
        super().__init__()
        print(i)

if __name__ == '__main__':
    for i in range(4):
        crawl_proxy = A(i)
        crawl_proxy.start()