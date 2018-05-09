import requests
from bs4 import BeautifulSoup
import os
import time
import re
import random

se = requests.session()
class Pixiv():
    def __init__(self):
        self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.target_url = 'https://www.pixiv.net/ranking.php?mode=daily&date='
        self.main_url = 'http://www.pixiv.net'
        self.headers = {
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        self.pixiv_id = '894703504@qq.com'
        self.password = 'zhengxin08261008'
        self.post_key = []
        self.return_to = 'http://www.pixiv.net/'
        self.load_path = 'E:\scrawler'
        self.ip_list = []
    def login(self):
        post_key_html = se.get(self.base_url,headers = self.headers).text
        post_key_soup = BeautifulSoup(post_key_html,'lxml')
        self.post_key = post_key_soup.find('input')['value']
        data = {
            'pixiv_id': self.pixiv_id,
            'password': self.password,
            'return_to': self.return_to,
            'post_key': self.post_key
        }
        se.post(self.login_url,data=data,headers=self.headers)
    def get_proxy(self):
        html = requests.get('http://haoip.cc/tiqu.htm')
        ip_list_temp = re.findall(r'r/>(.*?)<b', html.text, re.S)
        for ip in ip_list_temp:
            i = re.sub('\n', '', ip)
            self.ip_list.append(i.strip())
            print(i.strip())
    #获取指定天数的排行的图片
    #网页https://www.pixiv.net/ranking.php?mode=daily&date=20180505
    #重点在于data = 20180505
    #顺便一提，获取的是小图，可做桌面的大图隐藏在div class="_illust_modal ui-modal-close-box"里
    #这里获取的图片是div class="works_display"里的中图
    def get_img(self,html,date):
        img_soup = BeautifulSoup(html,'lxml')
        img_list = img_soup.find_all('div',attrs={'class','ranking-image-item'})
        for img in img_list:
            href = img.find('a')['href']#直接提取第一个href
            jump_to_url = self.main_url + href#跳转到目标url
            print(jump_to_url)
            jump_to_html = self.get_html(jump_to_url,3).text #获取图片的html
            
            img_soup_m = BeautifulSoup(jump_to_html,'lxml')
            img_info = img_soup_m.find('div',attrs={'class','works_display'}).find('div',attrs={'class','_layout-thumbnail ui-modal-trigger'})
            if img_info is None:
                continue
            self.download_img(img_info,jump_to_url,date)#下载这个图片
    #下载图片
    #def download_img(self,img_info,href,page_num):
     #   title = img_info.find('img')['alt']#提取标题
     #   src = img_info.find('img')['src']#提取图片位置
     #   src_headers = self.headers
     #   src_headers['Referer'] = href #增加一个referer,否则会403，referer一般是当前网址：https://www.pixiv.net/ranking.php?mode=daily&date=20180505
     #   try:
      #      html=requests.get(src,headers = src_headers)
     #       img = html.content
      #  except:#有时候会发生错误导致不能获取图片，跳过就好
     #       print('获取图片失败')
     #       return False
    
    
    #反爬的代理工作。。。
    def get_html(self, url, timeout, proxy=None, num_entries=5):
        if proxy is None:
            try:
                return se.get(url, headers=self.headers, timeout=timeout)
            except:
                if num_entries > 0:
                    print('获取网页出错,5秒后将会重新获取倒数第', num_entries, '次')
                    time.sleep(5)
                    return self.get_html(url, timeout, num_entries = num_entries - 1)
                else:
                    print('开始使用代理')
                    time.sleep(5)
                    ip = ''.join(str(random.choice(self.ip_list))).strip()
                    now_proxy = {'http': ip}
                    return self.get_html(url, timeout, proxy = now_proxy)
        else:
            try:
                return se.get(url, headers=self.headers, proxies=proxy, timeout=timeout)
            except:
                if num_entries > 0:
                    print('正在更换代理,5秒后将会重新获取第', num_entries, '次')
                    time.sleep(5)
                    ip = ''.join(str(random.choice(self.ip_list))).strip()
                    now_proxy = {'http': ip}
                    return self.get_html(url, timeout, proxy = now_proxy, num_entries = num_entries - 1)
                else:
                    print('使用代理失败,取消使用代理')
                    return self.get_html(url, timeout)
                
                
    def download_img(self, img_info, href, date):
        title = img_info.find('img')['alt']  # 提取标题
        src = img_info.find('img')['src']  # 提取图片位置
        src_headers = self.headers
        src_headers['Referer'] = href  # 增加一个referer,否则会403,referer就像上面登陆一样找
        try:
            html = requests.get(src, headers=src_headers)
            img = html.content
        except:  # 有时候会发生错误导致不能获取图片.直接跳过这张图吧
            print('获取该图片失败')
            return False

        title = title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_').replace('|', '_')\
            .replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()
        # 去掉那些不能在文件名里面的.记得加上strip()去掉换行
        title = title+"time="+date#加上排行榜时间
        print(self.load_path)
        if os.path.exists(os.path.join(self.load_path, str(date), title + '.jpg')):
            for i in range(1, 100):
                if not os.path.exists(os.path.join(self.load_path, str(date), title + str(i) + '.jpg')):
                    title = title + str(i)
                    break
        # 如果重名了,就加上一个数字
        print('正在保存名字为: ' + title + ' 的图片')
        with open(os.path.join(self.load_path, str(date), title + '.jpg'), 'ab') as f:  # 图片要用b
            f.write(img)
        print('保存该图片完毕')

        
    def mkdir(self,path):
        path = path.strip()
        is_exist = os.path.exists(os.path.join(self.load_path,path))
        if not is_exist:
            print('创建一个名字为'+path+'的文件夹')
            os.makedirs(os.path.join(self.load_path,path))
            return True
        else:
            print('名字为'+path+'的文件夹已经存在')
            os.chdir(os.path.join(self.load_path,path))
            return False
    def work(self):
        Ldate = [x for x in range(1,8)]
        def datelist(date):
            return '2018050'+str(date)
        self.login()
        for date in list(map(datelist,Ldate)):  
            path = str(date)  # 以天为单位
            self.mkdir(path)  # 创建文件夹
            # print(self.target_url + str(page_num))
            now_html = self.get_html(self.target_url + str(date),3)  # 获取页码
            self.get_img(now_html.text, date)  # 获取图片
            print('第 {date} 天保存完毕'.format(date=date))
            time.sleep(2)  # 防止太快被反
pixiv = Pixiv()
pixiv.work()