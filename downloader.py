from concurrent.futures import *
import requests
import time
import os


class Downloader:
    def __init__(self, url, nThread, proxies):
        self.session = requests.Session()
        head = self.session.head(url, proxies=proxies).headers
        self.size = int(head['Content-Length'])
        print('文件大小：{}'.format(self.size))
        self.name = url[url.rfind('/') + 1:]
        ind = self.name.find('?')
        if ind != -1:
            self.name = self.name[0:ind]
        print('文件名：{}'.format(self.name))
        self.url = url
        self.nThread = nThread
        self.proxies = proxies
        self.pool = ThreadPoolExecutor(max_workers=self.nThread)
        self.curThreads = 0

    def testAndSplit(self, begin, end):
        if self.curThreads < self.nThread:
            self.pool.submit(self.downloadSub, begin, (begin + end) // 2)
            self.pool.submit(self.downloadSub, (begin + end) // 2 + 1, end)
            return True
        return False

    # 下载子任务
    def downloadSub(self, begin, end):
        self.curThreads += 1
        if self.testAndSplit(begin, end):
            return
        sumBytes = 0
        headers = {'Range': "bytes={}-{}".format(begin, end)}
        with self.session.get(self.url, headers=headers, proxies=self.proxies, stream=True) as resp, \
                open("download/{}".format(self.name), 'rb+') as f:
            f.seek(begin)
            for chunk in resp.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
                    sumBytes += len(chunk)
                if self.testAndSplit(begin + sumBytes, end):
                    break
        self.curThreads -= 1

    # # 统计当前下载进度
    # def statistics(self):
    #     while True:
    #         s = 0
    #         for i in range(self.nThread):
    #             file = 'download/{}.{}'.format(self.name, i)
    #             if os.path.exists(file):
    #                 s += os.path.getsize(file)
    #         r = s / self.size * 100
    #         print("\r当前进度：{}/{} {:.2f}%".format(s, self.size, r), end='')
    #         if r == 100:
    #             break
    #         time.sleep(1)

    # 下载
    def download(self):
        tBegin = time.time()
        f = open('download/{}'.format(self.name), 'wb')
        f.close()
        self.pool.submit(self.downloadSub, 0, self.size - 1)
        time.sleep(1000)
        # self.statistics()
        # print('\n花费时间：{:.2f}s'.format(time.time() - tBegin))


if __name__ == '__main__':
    url = input("请输入url：").rstrip()
    nThread = 8
    proxies = {'http': 'http://localhost:1081', 'https': 'http://localhost:1081'}
    downloader = Downloader(url, nThread, proxies)
    downloader.download()
