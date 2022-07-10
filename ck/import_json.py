# todo
# find all poet.*.json
# read json file one by one
# read json to SQLite db


import json
from nis import cat
import re
import sqlite3

import os
from abc import ABC


def import_single_file(file_path, cls, category=''):
    print('loading: ', file_path)
    p = cls(file_path, category)
    p.save_to_sqlite3()


class Json2SQLite3(ABC):
    text_columns = []
    table_name = ''
    default_category = ''

    def __init__(self, path, category='') -> None:
        self.path = path
        self.category = category or self.default_category
        self.traffic = self.load_json(path)

    def load_json(self, path):
        return json.load(open(path))

    def save_to_sqlite3(self):
        connection = sqlite3.connect('db.sqlite')
        cursor = connection.cursor()
        value_string = ', '.join([f'{c} Text' for c in self.text_columns])
        cursor.execute(
            f'Create Table if not exists {self.table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, category Text, {value_string})')

        def insert_db(row):
            keys = {c: row[c] for c in self.text_columns}
            for k in keys:
                if not isinstance(keys[k], str):
                    keys[k] = json.dumps(keys[k], ensure_ascii=False)
            fields = [keys[c] for c in self.text_columns]
            fields.insert(0, self.category)

            q = ['?']
            qs = q*len(fields)
            cursor.execute(
                f"insert into {self.table_name} ('category', {','.join(self.text_columns)}) values({','.join(qs)})", fields)

        if isinstance(self.traffic, list):
            for row in self.traffic:
                insert_db(row)
        else:
            insert_db(self.traffic)

        connection.commit()
        connection.close()
        print(f'{self.path} data inserted Succefully')


class PoetJson(Json2SQLite3):
    text_columns = ['author', 'paragraphs', 'title']
    table_name = 'poet'

    def __init__(self, path, category='') -> None:
        self.path = path
        self.category = category or path.split('.')[3]
        self.traffic = json.load(open(path))


class CiJson(Json2SQLite3):
    text_columns = ['author', 'paragraphs', 'rhythmic']
    table_name = 'ci'


class WudaiJson(Json2SQLite3):
    text_columns = ['title', 'author', 'paragraphs', 'rhythmic', 'notes']
    table_name = 'wudai'
    default_category = 'huajianji'


class LunyuJson(Json2SQLite3):
    text_columns = ['chapter', 'paragraphs']
    table_name = 'lunyu'


class ShijingJson(Json2SQLite3):
    text_columns = ['title', 'chapter', 'section', 'content']
    table_name = 'shijing'


class YoumengyingJson(Json2SQLite3):
    text_columns = ['content', 'comment']
    table_name = 'youmengying'


class SishuwujingJson(Json2SQLite3):
    text_columns = ['chapter', 'paragraphs']
    table_name = 'sishuwujing'


class DiziguiJson(Json2SQLite3):
    text_columns = ['chapter', 'paragraphs']
    table_name = 'dizigui'

    def load_json(self, path):
        temp = super().load_json(path)
        return temp['content']


# 千家诗
class QianjiashiJson(Json2SQLite3):
    text_columns = ['type', 'chapter', 'author', 'paragraphs']
    table_name = 'qianjiashi'

    def load_json(self, path):
        temp = super().load_json(path)
        result = []
        for i in temp['content']:
            type = i['type']
            for j in i['content']:
                j['type'] = type
                result.append(j)

        return result


# 唐宋诗
def import_poet():
    files = os.listdir("../json")
    l = list(map(lambda x: "../json/"+x, files))

    for file_path in l:
        if 'poet' in file_path:
            print('loading Poet')
            p = PoetJson(file_path)
            p.save_to_sqlite3()

        elif '唐诗三百首' in file_path:
            print('唐诗三百首')
            p = PoetJson(file_path, '唐诗三百首')
            p.save_to_sqlite3()

        else:
            continue


# 词
def import_ci():
    files = os.listdir("../ci")
    l = list(map(lambda x: "../ci/"+x, files))

    for file_path in l:
        if 'ci.song' in file_path:
            p = CiJson(file_path, category='song')
            p.save_to_sqlite3()

        else:
            continue


# 五代
def import_wudai():
    files = os.listdir("../wudai/huajianji")
    l = list(map(lambda x: "../wudai/huajianji/"+x, files))

    for file_path in l:
        if file_path.endswith('juan.json'):
            print('loading: ', file_path)
            p = WudaiJson(file_path, category='huajianji')
            p.save_to_sqlite3()

        else:
            continue


# 南唐二主词
def import_wudai_rz():
    import_single_file('../wudai/nantang/poetrys.json',
                       WudaiJson, category='nantang')


# 论语
def import_lunyu():
    import_single_file('../lunyu/lunyu.json', LunyuJson)


# 诗经
def import_shijing():
    import_single_file('../shijing/shijing.json', ShijingJson)


# 幽梦影
def import_youmengying():
    import_single_file('../youmengying/youmengying.json', YoumengyingJson)


# 四书五经
def import_sishuwujing():
    import_single_file('../sishuwujing/daxue.json',
                       SishuwujingJson, category='daxue')
    import_single_file('../sishuwujing/mengzi.json',
                       SishuwujingJson, category='mengzi')
    import_single_file('../sishuwujing/zhongyong.json',
                       SishuwujingJson, category='zhongyong')


# 蒙学
def import_mengxue():
    import_single_file('../mengxue/dizigui.json',
                       DiziguiJson, category='mengxue')
    import_single_file('../mengxue/qianjiashi.json',
                       QianjiashiJson, category='mengxue')


def main():
    import_poet()
    import_ci()
    import_wudai()
    import_wudai_rz()
    import_lunyu()
    import_shijing()
    import_youmengying()
    import_sishuwujing()
    import_mengxue()


if __name__ == "__main__":
    main()
