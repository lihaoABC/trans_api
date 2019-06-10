# coding:utf-8

class COD:

    OK                  = "0"
    BEGIN               = "1"

    REDINFO             = "2"
    GETVINFO            = "3"
    GETNINFO            = "33"

    REDIMG              = "4"
    GETIMG              = "5"
    REDTHU              = "17"
    GETTHU              = "18"
    THUERR              = "19"
    THUNIL              = "20"

    REDVIDEO            = "6"
    GETVIDEO            = "7"
    REDUPLOAD           = "8"
    GETUPIMG            = "9"
    GETUPVIDEO          = "10"
    MAKEJSON            = "11"
    SAND                = "12"
    EXISTS              = "13"
    LIMIST              = "14"
    RESET               = "15"
    RESOK               = "16"



    NODATA              = "4003"
    IMGERR              = "4005"
    IMGNIL              = "4006"
    VIDEOERR            = "4007"
    UPLOADERR           = "4009"

    GENTHUERR           = "4010"

    URLEX               = "4011"
    URLES               = "4013"

    BIG                 = "4014"
    FORMAT              = "4015"



message_map = {
    COD.OK                      : r"发布成功",
    COD.BEGIN                   : r"开始爬取",

    COD.REDINFO                 : r"开始获取文章信息",
    COD.GETVINFO                 : r"获取视频信息成功",
    COD.GETNINFO                 : r"获取新闻信息成功",

    COD.REDTHU                  : r"开始下载缩略图",
    COD.GETTHU                  : r"获取缩略图成功",
    COD.REDIMG                  : r"开始下载图片",
    COD.GETIMG                  : r"获取图片成功",

    COD.REDVIDEO                : r"开始下载视频",
    COD.GETVIDEO                : r"下载视频成功",
    COD.REDUPLOAD               : r"开始上传文件",
    COD.GETUPIMG                : r"上传缩略图成功",
    COD.GETUPVIDEO              : r"上传视频成功",
    COD.MAKEJSON                : r"生成用来发布的json文件",
    COD.SAND                    : r"已发送",
    COD.EXISTS                  : r"标题重复，增加不成功",
    COD.LIMIST                  : r"没有增加信息的权限",


    COD.NODATA                  : r"获取信息失败",
    COD.THUERR                  : r"下载缩略图失败",
    COD.GENTHUERR               : r"生成缩略图失败",
    COD.THUNIL                  : r"缩略图地址为空",
    COD.IMGERR                  : r"下载图片失败",
    COD.IMGNIL                  : r"图片地址为空",
    COD.VIDEOERR                : r"下载视频失败",
    COD.UPLOADERR               : r"上传文件失败",
    COD.BIG                     : r"文件超过100M,下载失败",



    COD.URLEX                   : r"此url重复",
    COD.URLES                   : r"不支持此url",
    COD.FORMAT                  : r"url格式错误",

    COD.RESET                   : r"视频正在转码",
    COD.RESOK                   : r"视频转码成功",



}


if __name__ == '__main__':
    a = '4014'
    print(COD.BIG)
    for key, value in COD.__dict__.items():
        if value == a:
            message = message_map[COD.__dict__[key]]
            print(message)