
PackMe
----------------------------
手机归属地数据库打包(中国)

### 快速使用

```shell script

python phone_pack.py -i phone.2503.csv -o phone.2503.dat -v 2503
Version: 2503
File: phone.2503.dat
Size: 4652693
Count: 515858


```

    注意: phone.2503.csv 版本格式要求

### 数据来源
* [dannyhu926/phone_location](https://github.com/dannyhu926/phone_location/blob/master/mysql/phone_location.sql)

### 兼容版本

* [go解析]https://github.com/20326/finder

-----
* [python解析]https://github.com/lovedboy/phone
* [go解析]https://github.com/xluohome/phonedata
* 其它不一一列举


#### phone.dat文件格式

```

        | 4 bytes |                     <- phone.dat 版本号
        ------------
        | 4 bytes |                     <-  第一个索引的偏移
        -----------------------
        |  offset - 8            |      <-  记录区
        -----------------------
        |  index                 |      <-  索引区
        -----------------------

```

* `头部` 头部为8个字节，版本号为4个字节，第一个索引的偏移为4个字节(<4si)。      
* `记录区` 中每条记录的格式为"\<省份\>|\<城市\>|\<邮编\>|\<长途区号\>\0"。 每条记录以'\0'结束。  
* `索引区` 中每条记录的格式为"<手机号前七位><记录区的偏移><卡类型>"，每个索引的长度为9个字节(`<iiB`)。

解析步骤:

 * 解析头部8个字节，得到索引区的第一条索引的偏移。
 * 在索引区用二分查找得出手机号在记录区的记录偏移。
 * 在记录区从上一步得到的记录偏移处取数据，直到遇到'\0'。
 
定义的卡类型为:

* 1 中国移动
* 2 中国联通
* 3 中国电信
* 4 中国电信/虚拟运营商
* 5 中国联通/虚拟运营商
* 6 中国移动/虚拟运营商
* 7 中国广电
* 8 中国广电/虚拟运营商

新增定义!
* 20 中国电信/物联网卡
* 21 中国联通/物联网卡
* 22 中国移动/物联网卡
* 23 中国电信/数据上网卡
* 24 中国联通/数据上网卡
* 25 中国移动/数据上网卡
* 26 中国电信/卫星电话卡
* 27 中国联通/卫星电话卡
* 28 中国移动/卫星电话卡
* 29 应急通信/卫星电话卡
* 30 工信/卫星电话卡
* 99 未知运营商

## License

Copyright (c) 2020 (brian)

Licensed under the [MIT license](https://opensource.org/licenses/MIT) ([`LICENSE`](LICENSE)).
