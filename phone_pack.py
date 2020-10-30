# -*- coding: utf-8 -*-
import argparse
import os
import struct
import codecs
import csv
import collections

from datetime import datetime

__author__ = 'brian'
__version__ = '1.0.0'


class DataConverter(object):
    table = collections.OrderedDict()
    tableData = collections.OrderedDict()

    def __init__(self, cvs_file=None, out_file=None, version=None):

        self.head_fmt = "<4si"
        self.phone_fmt = "<iiB"
        self.head_fmt_length = struct.calcsize(self.head_fmt)
        self.phone_fmt_length = struct.calcsize(self.phone_fmt)
        self.first_index_offset = 0
        self.phone_record_count = 0

        self.cvs_file = cvs_file
        self.out_file = out_file
        self.dat_version = str(version)

        self.carriers = {
            "移动": 1,
            "联通": 2,
            "电信": 3,
            "中国移动": 1,
            "中国联通": 2,
            "中国电信": 3,
            "电信虚拟运营商": 4,
            "联通虚拟运营商": 5,
            "移动虚拟运营商": 6,
            "未知运营商": 7,
        }

        if cvs_file is None:
            self.cvs_file = os.path.join(os.path.dirname(__file__), "mobile.1810.csv")

        # index offset
        index_offset = self.head_fmt_length

        with codecs.open(self.cvs_file, mode='r') as FILE:
            reader = csv.reader(FILE)
            for row in reader:
                self.phone_record_count = self.phone_record_count + 1
                # if self.phone_record_count >10:
                #     break

                # no    prefix      province    city     carrier   region      zipCode
                # 1     1300000	    山东         济南     中国联通    531         250000
                # 记录区 中每条记录的格式为"<省份>|<城市>|<邮编>|<长途区号>\0"。 每条记录以'\0'结束；
                # 索引区 中每条记录的格式为"<手机号前七位><记录区的偏移><卡类型>"，每个索引的长度为9个字节；
                no = int(row[1])

                carrier = self.carriers.get(row[4], 7)
                dat_str = "{}|{}|{}|{}\0".format(row[2], row[3], row[6], str(row[5]))
                idx_name = "{}.{}.{}".format(row[0], row[1], row[6])

                self.table[no] = {
                    "no": no,
                    "carrier": carrier,
                    "data": dat_str,
                }
                self.tableData[dat_str] = 0

    def pack(self):
        # ### 手机号归属地查询
        #     | 4 bytes |                     <- phone.dat 版本号（如：1701即17年1月份）
        #     ------------
        #     | 4 bytes |                     <-  第一个索引的偏移
        #     -----------------------
        #     |  offset - 8            |      <-  记录区
        #     -----------------------
        #     |  index                 |      <-  索引区
        #     -----------------------
        #
        # 1. 头部为8个字节，版本号为4个字节，第一个索引的偏移为4个字节；
        # 2. 记录区 中每条记录的格式为"<省份>|<城市>|<邮编>|<长途区号>\0"。 每条记录以'\0'结束；
        # 3. 索引区 中每条记录的格式为"<手机号前七位><记录区的偏移><卡类型>"，每个索引的长度为9个字节；

        with open(self.out_file, "wb") as FILE:
            # pack data
            # 记录数据多条重复, 合并记录区
            data_buffer = b''
            index_offset = self.head_fmt_length
            for key, value in self.tableData.items():
                # 计算索引offset
                self.tableData[key] = index_offset
                index_offset = index_offset + len(key)
                # 组合记录区数据
                data_buffer += struct.pack(str(len(key)) + "s", key)

            # 设置索引offset
            self.first_index_offset = index_offset

            # pack header
            header_buffer = struct.pack(self.head_fmt, self.dat_version.encode('utf-8'), self.first_index_offset)

            # write buffer
            FILE.write(header_buffer)
            FILE.write(data_buffer)

            # pack index
            for key, value in self.table.items():
                data_offset = self.tableData[value["data"]]
                index_buffer = struct.pack(self.phone_fmt, value["no"], data_offset, value["carrier"])
                FILE.write(index_buffer)

    def version(self):
        print("Version: {}".format(self.dat_version))
        print("File: {}".format(self.out_file))
        print("Size: {}".format(os.path.getsize(self.out_file)))
        print("Count: {}".format(self.phone_record_count))


def cmdline_parser():
    defaultVersion = datetime.now().strftime('%y%m')
    parser = argparse.ArgumentParser(description=u'PackMe: 生成phone.dat数据文件')
    parser.add_argument('-i', '--input', metavar=u'file', help=u'csv源文件路径', required=True)
    parser.add_argument('-o', '--output', metavar=u'file', help=u'生成phone.dat数据文件路径',
                        default="phone.{}.dat".format(defaultVersion), required=False)
    parser.add_argument('-v', '--version', metavar=u'2010', help=u'版本号', type=int,
                        default=defaultVersion, required=False)

    return parser


def main():
    parser = cmdline_parser()
    args = parser.parse_args()

    pp = DataConverter(args.input, args.output, args.version)

    pp.pack()
    pp.version()


if __name__ == '__main__':
    main()
