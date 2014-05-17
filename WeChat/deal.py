# -*- coding: utf-8 -*-
__author__ = 'syb'
"""主要是处理用户发送的消息"""
import time
import urllib
import urllib2
import xml.etree.ElementTree as XMLTree

YouDaoData = {}
YouDaoData['key'] = "987935518"
YouDaoData['keyfrom'] = "sybwechat"
YouDaoData['doctype'] = "xml"
YouDaoData['version'] = '1.1'
YouDaoData['type'] = 'data'
YouDaoBasicUrl = 'http://fanyi.youdao.com/openapi.do?'


def YouDaoURL(search):
    """获取需要查询xml的url地址"""
    YouDaoData['q'] = search
    url = YouDaoBasicUrl + urllib.urlencode(YouDaoData)
    return url


def YouDaoDataDeal(url):
    request = urllib2.Request(url)
    xmlData = urllib2.urlopen(request).read()
    return YouDaoXmlDataDeal(xmlData)


def YouDaoXmlDataDeal(content):
    content = XMLTree.fromstring(content)
    replayContent = ''
    if content.tag == 'youdao-fanyi':
        for child in content:
            if child.tag == 'errorCode':
                """错误码，正常的应该返回0"""
                if child.text == '20':
                    return u'抱歉，您输入的过长，无法翻译'
                elif child.text == '30':
                    return u'抱歉，无法有效的翻译'
                elif child.text == '40':
                    return u'无法翻译该语言'
                elif child.text == '50':
                    return u'抱歉，系统出错，请重试'

            elif child.tag == 'query':
                """查询的具体单词"""
                replayContent = '%s%s\n' % (replayContent,  child.text)

            elif child.tag == 'basic':
                """基本释义"""
                replayContent = '%s%s\n' % (replayContent, u'【基本释义】')
                for grands in child:
                    if grands.tag == 'phonetic':
                        replayContent = '%s%s%s\n' % (replayContent, u'【音标】：', grands.text)
                    elif grands.tag == 'explains':
                        for ex in grands.findall('ex'):
                            replayContent = '%s%s\n' % (replayContent, ex.text)
            elif child.tag == 'web':
                """网络释义"""
                replayContent = '%s%s\n' % (replayContent, u'【网络释义】')
                for explain in child.findall('explain'):
                    for key in explain.findall('key'):
                        replayContent = '%s%s\t' % (replayContent, key.text)
                    for value in explain.findall('value'):
                        for ex in value.findall('ex'):
                            replayContent = '%s%s\t' % (replayContent, ex.text)
                    replayContent = '%s\n' % replayContent
    return replayContent


def dealText(Content):
    describe = Content.decode('utf-8')[:2].encode('utf-8')
    if describe == '翻译':
        text = Content.decode('utf-8')[2:].encode('utf-8')
        url = YouDaoURL(text)    #获取对应的url
        # return url
        XMLData = YouDaoDataDeal(url)    #得到url中的xml数据
        return XMLData
    else:
        return '暂时功能还在开发中。。。'
        # text = Content[2:]


def replyTextXml(msg, Content):
    xml = " <xml>\
            <ToUserName><![CDATA[%s]]></ToUserName>\
            <FromUserName><![CDATA[%s]]></FromUserName> \
            <CreateTime>%s</CreateTime>\
            <MsgType><![CDATA[%s]]></MsgType>\
            <Content><![CDATA[%s]]></Content>\
            <FuncFlag>0</FuncFlag>\
            </xml>"
    xml = xml % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'text',  Content)
    return xml


