#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import xcsc_tushare as xc
from datetime import datetime

xc.set_token('a974d1ebb145840ead809fbf098db57a31d4d51ec4dda6beaadefd5f')
pro = xc.pro_api(env='prd')


def preN_indx(n, trade_date, FirstDeclareDate_ls):
    '''
    n: 前n个交易日
    trade_date: 交易日历的列表
    FirstDeclareDate_ls: 首次并购日的列表
    '''
    # 获取FirstDeclareDate_ls中每个元素在trade_date中的索引
    indx = []
    for date in FirstDeclareDate_ls:
        try:
            indx.append(trade_date.index(date))
        # 如果日期不在交易日历内
        except:
            indx.append(sum(dd < date for dd in trade_date))
            
    return indx


def add_stkCode(stkCode):
    '''
    stkCode: list格式，存储着未加后缀的证券代码
    '''
    stkCode_new = []
    for cd in stkCode:
        if cd[:2] == '00' or cd[:2] == '30':
            stkCode_new.append(cd + '.SZ')
        elif cd[:2] == '60':
            stkCode_new.append(cd + '.SH')
        else:
            # 暂不考虑科创板股票
            print('Error in: ',cd)
            
    return stkCode_new
            
# 主函数
def main(n):
    '''
    n: 前n个交易日
    '''
    # 获取2005-2020年A股交易日历
    trade_date = pro.trade_cal(exchange='SSE', start_date='20050101', end_date='20201231')['trade_date'].values
    trade_date = [datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d') for date in trade_date]
    
    # 读取数据文件
    df = pd.read_excel("targetcc_CAR.xlsx",converters={'Stkcd': str,'FirstDeclareDate': str})

    # 将FirstDeclareDate列转换为字符格式
    FirstDeclareDate_ls = df['FirstDeclareDate'].values.tolist()
    FirstDeclareDate_ls = [date[:10] for date in FirstDeclareDate_ls]
    
    # 股票代码后缀的添加
    stkCode = df['Stkcd'].values.tolist()
    stkCode = add_stkCode(stkCode)
    
    # 获取前n期在交易日历列表中的索引
    indx = preN_indx(n, trade_date, FirstDeclareDate_ls)
    
    
    close_ls = []
    for i in range(len(df)):
        try:
            close_ls.append(pro.daily(ts_code=stkCode[i], trade_date=trade_date[indx[i]].replace('-',''))['close'].values[0])
        except:
            print(stkCode[i],"--",trade_date[indx[i]])
    
    return close_ls


if __name__ == '__main__':
    close_ls = main(5)

