import requests
import pandas as pd

url = 'https://api.thegraph.com/subgraphs/name/sushi-labs/kashi-ethereum'

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

addresses_string = ','.join(iddtr)
page = requests.get('https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses=' + addresses_string + '&vs_currencies=usd')
data = page.json()
lldata=[]
for i in data:
    lldata.append(i)
ldata=list(data.values())
priceusd=[i['usd'] for i in ldata]

df2=pd.DataFrame(lldata, columns=['id'])
df2['usdvalue']=(priceusd)

assetval=[]
collval=[]
for i in idda:
    assetval.append(df2.loc[df2['id']==i, 'usdvalue'].item())

    
for i in iddc:
    collval.append(df2.loc[df2['id']==i, 'usdvalue'].item())

df1.reset_index(drop=True, inplace=True)
df3=pd.DataFrame(assetval, columns=['assetprice'])
df3['collateralprice']=(collval)

df4=pd.concat([df1, df3], axis=1, join='inner')
df4['borrowedValueUsd']=df4['totalBorrowAm']*df4['assetprice'].astype(float)
df4['collValueUsd']=df4['collateralam']*df4['collateralprice'].astype(float)
df4['diffrence']=df4['collValueUsd']-df4['borrowedValueUsd']
df4['diffrence2']=df4['collValueUsd']-(df4['assetam']*df4['assetprice'].astype(float))
df4['diff']=df4[['diffrence', 'diffrence2']].max(axis=1)
df5=df4[df4.diffrence < 0]
df5.reset_index(drop=True, inplace=True)
df5.to_csv('AIlamer1.4.csv')

