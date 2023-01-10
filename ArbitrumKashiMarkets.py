import requests
import pandas as pd

url = 'https://api.thegraph.com/subgraphs/name/sushi-labs/kashi-arbitrum'
url2='https://api.thegraph.com/subgraphs/name/sushiswap/arbitrum-exchange'

def kashi1(url1):
    query = '''{
        kashiPairs(first:1000, orderBy:totalCollateralShare, orderDirection:desc) {
            id
            name
            asset {
                id
                name
                decimals
            }
            totalAsset {
                id
                base
            }
            totalBorrow {
                elastic
            }
            totalCollateralShare
            collateral {
                name
                id
                decimals
            }
        }
    }'''
    page = requests.post(url1, json={'query': query})
    data = page.json()
    ldata = data['data']['kashiPairs']
    rows = []
    for i in ldata:
        rows.append({
            'pair': i['name'],
            'addr': i['id'],
            'assetname': i['asset']['name'],
            'assetid': i['asset']['id'],
            'totalAsset': float(i['totalAsset']['base']),
            'assetdec': float(i['asset']['decimals']),
            'assetam': float(i['totalAsset']['base']) /10**( float(i['asset']['decimals'])),
            'totalBorrow': float(i['totalBorrow']['elastic']),
            'totalBorrowAm': float(i['totalBorrow']['elastic']) / 10**(float(i['asset']['decimals'])),
            'collateralname': i['collateral']['name'],
            'collateralid': i['collateral']['id'],
            'totalCollateral': float(i['totalCollateralShare']),
            'collateraldec': float(i['collateral']['decimals']),
            'collateralam': float(i['totalCollateralShare']) / 10**(float(i['collateral']['decimals']))
        })
    return pd.DataFrame(rows)

df = kashi1(url)
df1 = df.loc[df.totalBorrowAm > 1]
#df1.to_csv('kashirekted.csv')
idda=df1.assetid.tolist()
iddc=df1.collateralid.tolist()
idd=idda+iddc
iddtr=list(dict.fromkeys(idd))

valueth=[]
def valeth():
    for i in iddtr:
       query='''{
  tokens(where:{id:"''' + f'{i}' + '''"}){
    derivedETH
    name
    id
  }
}'''
       page=requests.post(url2, json={'query': query})
       data=page.json()
       ldata=data['data']['tokens']
       for i in ldata:
           valueth.append(i['derivedETH'])
valeth()

df2=pd.DataFrame(iddtr, columns=['id'])
df2['ethvalue']=(valueth)

assetval=[]
collval=[]
for i in idda:
    assetval.append(df2.loc[df2['id']==i, 'ethvalue'].item())

    
for i in iddc:
    collval.append(df2.loc[df2['id']==i, 'ethvalue'].item())

page1=requests.get('https://api.ethplorer.io/getTokenInfo/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2?apiKey=freekey')
data1=page1.json()
ldata1=float(data1['price']['rate'])

df1.reset_index(drop=True, inplace=True)
df3=pd.DataFrame(assetval, columns=['assetprice'])
df3['collateralprice']=(collval)

df4=pd.concat([df1, df3], axis=1, join='inner')
df4['borrowedValueUsd']=df4['totalBorrowAm']*df4['assetprice'].astype(float)*ldata1
df4['collValueUsd']=df4['collateralam']*df4['collateralprice'].astype(float)*ldata1
df4['diffrence']=df4['collValueUsd']-df4['borrowedValueUsd']
df4['diffrence2']=df4['collValueUsd']-(df4['assetam']*df4['assetprice'].astype(float))*ldata1
df4['diff']=df4[['diffrence', 'diffrence2']].max(axis=1)
df5=df4[df4.diffrence < 0]
df5.reset_index(drop=True, inplace=True)
df5.to_csv('ArbMarkets.csv')

