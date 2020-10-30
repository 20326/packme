
PackMe
----------------------------
手机归属地数据打包(中国)

### 快速使用

```shell script

python phone_pack.py -i mobile.1810.csv -o phone.1810.dat -v 1810
Version: 1810
File: phone.1810.dat
Size: 3747097
Count: 415284

```

    注意: mobile.1810.csv版本格式要求

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

* 1 移动
* 2 联通
* 3 电信
* 4 电信虚拟运营商
* 5 联通虚拟运营商
* 6 移动虚拟运营商
* 7 未知运营商


## License

Copyright (c) 2020 (brian)

Licensed under the [MIT license](https://opensource.org/licenses/MIT) ([`LICENSE`](LICENSE)).
