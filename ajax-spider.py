#!/usr/bin/python3
# _*_ coding:utf-8_*_

'''
spider-ajax
1.获取博客上的ajax加载的网页内容
2.今日头条,模拟ajax请求方法爬取今日头条的街拍图
'''

import re
# 导入相应库
from multiprocessing.pool import Pool
from requests import codes
import requests, os
from urllib.parse import urlencode
# MD5消息算法,作用:去重重复标题
from hashlib import md5
# 启用进程池下载图片
from multiprocessing import pool

# 构造请求方式
headers = {
    'User-agent': 'Mozilla/5.0 (Macintosh;Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/52.0.2743.116 Safari/537.36'}


# 获取页面
def get_page(offset):
    # 构建词典,用ajax传值的方法构造请求
    params = {
        # 此处的字典根据网页参数进行字典模拟
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': 20,
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis'
    }
    # 构造请求的URL
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(params)
    # 加入异常判断
    try:
        # request方法进行请求
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # 以json格式返回
            return response.json()
    except requests.ConnectionError as e:
        return None


# 提取信息
def get_images(json):
    # 获取到data,如果data存在
    if json.get('data'):
        # 遍历出data下的内容
        for item in json.get('data'):
            # 获取title
            title = item.get('title')
            # 获取连接
            images = item.get('image_list')
            # 遍历每一个链接
            for image in images:
                # 返回生成器
                yield {
                    # 获取每一个下的url
                    'image': image.get('url'),
                    'title': title
                }


# 保存信息
def save_images(item):
    # 以图片为标题的问价是否存在
    if not os.path.exists(item.get('title')):
        # 如果存在则创建以图片为标题的文件夹
        os.mkdir(item.get('title'))
    # 存储图片
    try:
        # 获得的每一张图片链接进行请求,每一个image下的东西都是链接
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            # 使用format高阶函数以片链接,md5,16进制的格式为文件名,图片格式为jpg
            file_path = '{0}/{1}{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
            # 如果此路径不存在,则写入此路径
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    # 写入响应回的内容
                    f.write(response.content)
    except requests.ConnectionError as e:
        print('false to save')


# 主函数,传值
def main(offset):
    info = get_page(offset)
    # 返回值遍历,用get_images()处理信息方法
    for image in get_images(info):
        print(image)
        save_images(image)


# 构造起始页数,此处应为全局变量
group_start = 1
group_end = 20

if __name__ == "__main__":
    # 创建线程对象
    pool = Pool()
    # 用列表推导式创建组,从起始页到结束页
    groups = ([x * 20 for x in range(group_start, group_end + 1)])
    # 创建进程池,main函数,groups为迭代器
    pool.map(main, groups)
    # 关闭进程池
    pool.close()
    # 这里的pool.join()是说：主进程阻塞后，让子进程继续运行完成，子进程运行完后，再把主进程全部关掉
    pool.join()
