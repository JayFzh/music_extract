# coding=utf-8

import os

import pymysql

import process


class memory():
    def __init__(self, host, port, user, passwd, db):
        '''
        初始化存储类
        :param host:主机位置
        :param port:端口
        :param user:用户名
        :param passwd:密码
        :param db:数据库名
        '''
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db

    def addsong(self, path):
        '''
        添加歌曲方法，将指定路径的歌曲提取指纹后放到数据库
        :param path:路径
        :return:
        '''
        if type(path) != str:
            print('path need string')
            return None
        basename = os.path.basename(path)
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
                                   charset='utf8')
            # 创建与数据库的连接
        except:
            print('DataBase error')
            return None
        cur = conn.cursor()
        namecount = cur.execute("select * from fingerprint.music_data WHERE song_name = '%s'" % basename)
        # 查询新添加的歌曲是否已经在曲库中了
        if namecount > 0:
            print('the song has been record!')
            return None
        v = process.voice()
        v.loaddata(path)
        v.fft()
        print(v.high_point.__str__())
        cur.execute("insert into fingerprint.music_data VALUES('%s','%s')" % (basename, v.high_point.__str__()))
        # 将新歌曲的名字和指纹存到数据库中
        conn.commit()
        cur.close()
        conn.close()

    def fp_compare(self, search_fp, match_fp):
        '''
        指纹比对方法。
        :param search_fp: 查询指纹
        :param match_fp: 库中指纹
        :return:最大相似值 float
        '''
        if len(search_fp) > len(match_fp):
            return 0
        max_similar = 0
        search_fp_len = len(search_fp)
        match_fp_len = len(match_fp)
        for i in range(match_fp_len - search_fp_len):
            temp = 0
            for j in range(search_fp_len):
                if match_fp[i + j] == search_fp[j]:
                    temp += 1
            if temp > max_similar:
                max_similar = temp
        return max_similar

    def search(self, path):
        '''
        从数据库检索出
        :param path: 需要检索的音频的路径
        :return:返回列表，元素是二元组，第一项是匹配的相似值，第二项是歌曲名
        '''
        v = process.voice()
        v.loaddata(path)
        v.fft()
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
                                   charset='utf8')
        except:
            print
            'DataBase error'
            return None
        cur = conn.cursor()
        cur.execute("SELECT * FROM fingerprint.music_data")
        result = cur.fetchall()
        compare_res = []
        for i in result:
            compare_res.append((self.fp_compare(v.high_point[:-1], eval(i[1])), i[0]))
        compare_res.sort(reverse=True)
        cur.close()
        conn.close()
        print(compare_res)
        return compare_res

    def search_and_play(self, path):
        '''
        跟上个方法一样，不过增加了将搜索出的最优结果直接播放的功能
        :param path: 带检索歌曲路径
        :return:
        '''
        v = process.voice()
        v.loaddata(path)
        v.fft()
        # print v.high_point
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
                                   charset='utf8')
        except:
            print('DataBase error')
            return None
        cur = conn.cursor()
        cur.execute("SELECT * FROM fingerprint.music_data")
        result = cur.fetchall()
        compare_res = []
        for i in result:
            compare_res.append((self.fp_compare(v.high_point[:-1], eval(i[1])), i[0]))
        compare_res.sort(reverse=True)
        cur.close()
        conn.close()
        print(compare_res)
        v.play(compare_res[0][1])
        return compare_res


if __name__ == '__main__':
    sss = memory('localhost', 3306, 'root', 'fzh201226', 'fingerprint')
    # sss.addsong('C:/Users/37301/Desktop/music/huainian.wav')
    # sss.addsong('C:/Users/37301/Desktop/music/happier.wav')
    # sss.addsong('C:/Users/37301/Desktop/music/kaitian.wav')
    # sss.addsong('C:/Users/37301/Desktop/music/mojito.wav')
    # sss.addsong('C:/Users/37301/Desktop/music/moviepeople.wav')
    # sss.addsong('C:/Users/37301/Desktop/music/lover.wav')
    sss.search_and_play('C:/Users/37301/Desktop/music/huainian_test.wav')
