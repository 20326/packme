# -*- coding: utf-8 -*-
import argparse
import collections
import os
import struct
from datetime import datetime

import pandas as pd

__author__ = 'brian'
__version__ = '1.1.0'


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
            "中国移动": 1,
            "中国联通": 2,
            "中国电信": 3,
            "中国电信/虚拟运营商": 4,
            "中国联通/虚拟运营商": 5,
            "联通/虚拟": 5,
            "中国移动/虚拟运营商": 6,
            "中国广电": 7,
            "中国广电/虚拟运营商": 8,
            "中国电信/物联网卡": 20,
            "中国联通/物联网卡": 21,
            "联通/物联网": 21,
            "中国移动/物联网卡": 22,
            "中国电信/数据上网卡": 23,
            "中国电信/数据上网卡/物联网卡": 23,
            "中国联通/数据上网卡": 24,
            "中国移动/数据上网卡": 25,
            "中国电信/卫星电话卡": 26,
            "中国联通/卫星电话卡": 27,
            "中国移动/卫星电话卡": 28,
            "应急通信/卫星电话卡": 29,
            "工信/卫星电话卡": 30,
            "未知运营商": 99
        }

        if cvs_file is None:
            self.cvs_file = os.path.join(os.path.dirname(__file__), "phone.2503.csv")

        # "id", "pref", "phone", "province", "city", "isp", "isp_type", "post_code", "city_code", "area_code", "create_time"
        # "1", "130", "1300000", "山东", "济南", "中国联通", "2", "250000", "0531", "370100", "2025/3/4 14:50:26"
        # 记录区 中每条记录的格式为"<省份>|<城市>|<邮编>|<长途区号>\0"。 每条记录以'\0'结束；
        # 索引区 中每条记录的格式为"<手机号前七位><记录区的偏移><卡类型>"，每个索引的长度为9个字节；

        df = pd.read_csv(self.cvs_file, dtype={'city_code': str, 'post_code': str}, encoding='utf-8', low_memory=False)
        for index, row in df.iterrows():
            self.phone_record_count = self.phone_record_count + 1

            no = int(row["phone"])

            carrier = self.carriers.get(row["isp"], 99)
            dat_str = "{}|{}|{}|{}\0".format(row["province"], row["city"], row["post_code"], str(row["city_code"]))

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
            # Prepare to pack data
            data_buffer = b''  # Buffer for the record data
            index_offset = self.head_fmt_length  # Start index offset after the header
            for key, value in self.tableData.items():
                # Calculate the index offset for each record
                self.tableData[key] = index_offset
                # Encode as utf-8
                key = key.encode('utf-8')
                index_offset = index_offset + len(key)
                # Append the record data to the buffer
                data_buffer += struct.pack(str(len(key)) + "s", key)

            # set the first index offset
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
