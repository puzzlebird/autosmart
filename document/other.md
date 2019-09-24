# col2block


列之间建立边有如下两种方式：
```
if col2 == col1: 
    name2 = t_name_2+':'+col2
    mc_graph[name1][name2] = 1
    mc_graph[name2][name1] = 1
    log(f'init: {name1}, {name2}')  
```

```
if len(all_cat2set[name1] & all_cat2set[name2])/less_len > 0.1:
    mc_graph[name1][name2] = 1
    mc_graph[name2][name1] = 1
    log(f'same: {name1}, {name2}') 
```

以demo数据为例，得到的block如下：

- ['main:c_02', 'table_1:c_01', 'main:c_01', 'table_1:m_1', 'table_1:m_2', 'table_1:m_4', 'table_1:m_5', 'table_1:m_6', 'table_2:c_02', 'table_3:c_02']

- ['table_1:c_2', 'table_1:m_3', 'table_2:c_3']

<details>

<summary>Log</summary>
------------init: main:c_02, main:c_02

------------init: main:c_02, table_2:c_02

------------init: main:c_02, table_3:c_02

------------init: main:c_01, main:c_01

------------init: main:c_01, table_1:c_01

------------init: table_1:c_01, main:c_01

------------init: table_1:c_01, table_1:c_01

------------init: table_2:c_02, main:c_02

------------init: table_2:c_02, table_2:c_02

------------init: table_2:c_02, table_3:c_02

------------init: table_3:c_02, main:c_02

------------init: table_3:c_02, table_2:c_02

------------init: table_3:c_02, table_3:c_02

------------init mcgraph

------------same: main:c_02, table_1:c_01

------------same: main:c_02, table_1:m_1

------------same: main:c_02, table_1:m_2

------------same: main:c_02, table_1:m_4

------------same: main:c_02, table_1:m_5

------------same: main:c_02, table_1:m_6

------------same: main:c_01, table_1:m_1

------------same: table_1:c_01, table_1:m_1

------------same: table_1:c_01, table_2:c_02

------------same: table_1:c_01, table_3:c_02

------------same: table_1:c_2, table_1:m_3

------------same: table_1:m_1, table_1:m_2

------------same: table_1:m_1, table_1:m_4

------------same: table_1:m_1, table_1:m_5

------------same: table_1:m_1, table_1:m_6

------------same: table_1:m_1, table_2:c_02

------------same: table_1:m_1, table_3:c_02

------------same: table_1:m_2, table_1:m_4

------------same: table_1:m_2, table_1:m_5

------------same: table_1:m_2, table_1:m_6

------------same: table_1:m_2, table_2:c_02

------------same: table_1:m_2, table_3:c_02

------------same: table_1:m_3, table_2:c_3

------------same: table_1:m_4, table_1:m_5

------------same: table_1:m_4, table_1:m_6

------------same: table_1:m_4, table_2:c_02

------------same: table_1:m_4, table_3:c_02

------------same: table_1:m_5, table_1:m_6

------------same: table_1:m_5, table_2:c_02

------------same: table_1:m_5, table_3:c_02

------------same: table_1:m_6, table_2:c_02

------------same: table_1:m_6, table_3:c_02

</details>


# category hash

这里与block有关，同一个block中的列会被一起处理

- cats 
    ```
    vals = ss.values
    ss = pd.Series( list(ac.mscat_fit(vals)) )
    cats = ss.dropna().drop_duplicates().values

    if len(self.cats) == 0:
        self.cats = sorted(list(cats))
    else:
        added_cats = sorted(set(cats) - set(self.cats))
        self.cats.extend(added_cats)
    ```


找出所有不同的值

```
def mscat_fit(vals ):
    cdef:
        set ans = set()
        int idx,N = vals.shape[0]
        
    for idx in range(N):
        val = vals[idx]
        if type(val) == float:
            continue
        ans.update( val.split(',') )
        
    return ans
```



## Category

```
codes = pd.Categorical(ss,categories=self.cats).codes + CONSTANT.CAT_SHIFT
codes = codes.astype('float')
codes[codes==(CONSTANT.CAT_SHIFT-1)] = np.nan # equals to codes[codes==-1] = np.nan

codes = downcast(codes,accuracy_loss=False)
```

## Multi Category

```
codes = pd.Series( ac.mscat_trans(ss.values,self.cats) , index = ss.index )
return codes
```

举例来说，首先有以下数据

[(a), (b, a)] 

cats = [ a, b]

cat2index = {
    'a': 1,
    'b': 2
}

ans = [ (1), (2,1) ]

为了加速使用了CPython

```
def mscat_trans(vals,cats):
    cdef:
        dict cat2index = {index: i + 1 for i,index in enumerate(cats)}
        list ans = []
        int idx,N = vals.shape[0]
        list tmp = []
    
    
    for idx in range(N):
        val = vals[idx]
        if type(val) == float:
            ans.append( tuple() )
        else:
            tmp = []
            x = val.split(',')
            for i in x:
                tmp.append( cat2index[i] )
                
            ans.append( tuple( tmp ) )
         
    return ans
```

# M2O join



# M2M join


