# KeysNumStd

```
for col in todo_cols:
    cur_num_cols = X.get_groupby_cols(by=col,cols=num_cols)
    cur_num_cols = cur_num_cols[:self.config.keys_order2_num_std]
    for num_col in cur_num_cols:
        new_col = '{}_{}_std'.format(col, num_col)
        new_col = FeatContext.gen_feat_name(namespace,self.__class__.__name__,new_col,CONSTANT.NUMERICAL_TYPE)
        col2type[new_col] = CONSTANT.NUMERICAL_TYPE
        col2groupby[new_col] = col
        exec_cols.append((col, num_col))
        new_cols.append(new_col)
```

- **todo_cols** 用以分组的类别

    ```todo_cols = X.user_cols+X.key_cols+X.session_cols```

- **num_cols** 分组中聚合的维度
    ```num_cols = X.combine_num_cols```

- **combine_num_cols**

    之前进行的特征工程得到的列，其类型为数值类型的

- **col2groupby**

    col2group 
    a : col -> b : tuple of col

    记录了新生成的列由哪些列生成，例如 *n_BinsCatCntOrder2DIYNew:KeyTimeBin_Minute_c_3_cnt:default* 查询得到('KeyTimeBin_Minute', 'c_3')

- **get_groupby_cols**

    get_groupby_cols

    a: col b: list of cols -> c: list of cols

    通过上面的字典递归查询，从b中筛选出通过a聚类生成的列


示意

原数据

index | A |  B  
-|-|-
0 | 0 | 0 |
1 | 0 | 1 |
2 | 1 | 0 |

生成新数据后

index | A |  B | New
-|-|-|-
0 | 0 | 0 | 0.707
1 | 0 | 1 | 0.707
2 | 1 | 0 | NaN


# KeysCatCntOrder2New


找到需要处理的列

```
for col in todo_cols:
    work_cols = X.get_groupby_cols(by=col,cols=cat_cols)
    work_cols = work_cols[:self.config.keys_order2_cat_max]
    for cat_col in work_cols:
        new_col = '{}_{}_cnt'.format(col, cat_col)
        new_col = FeatContext.gen_feat_name(namespace,self.__class__.__name__,new_col,CONSTANT.NUMERICAL_TYPE)
        
        col2type[new_col] = CONSTANT.NUMERICAL_TYPE
        col2groupby[new_col] = (col,cat_col)
        exec_cols.append((col, cat_col))
        new_cols.append(new_col)
```

- **todo_cols** 用以分组的类别

    ```todo_cols = X.user_cols+X.key_cols+X.session_cols```

- **cat_cols** 分组中聚合的维度
    ```cat_cols = X.combine_cat_cols```

- **combine_cat_cols**

    之前进行的特征工程得到的列，其值代表类型的


- **get_groupby_cols**

    get_groupby_cols

    a: col b: list of cols -> c: list of cols

    通过上面的字典递归查询，从b中筛选出通过a聚类生成的列

具体的处理措施

```
def func(df):
    cats = gen_combine_cats(df, df.columns)
    cnt = cats.value_counts()
    ss = cats.map(cnt)
    return downcast(ss)

res = Parallel(n_jobs=CONSTANT.JOBS, require='sharedmem')(delayed(func)(df[[col1, col2]]) for col1, col2 in exec_cols)
```

- **gen_combine_cats**

    ```
    category = df[cols[0]].astype('float64')
    for col in cols[1:]:
        mx = df[col].max()
        category *= mx
        category += df[col]
    return category
    ```
   具体而言，对于两列a, b进行如下映射得到新的一列：c = aB + b
   在已知B时，可以从c恢复出a、b


示意

原数据

index | A |  B  
-|-|-
0 | 0 | 0 |
1 | 0 | 1 |
2 | 1 | 0 |

生成新数据后

index | A |  B | New_cat | New
-|-|-|-|-
0 | 0 | 0 | 0 | 1
1 | 0 | 1 | 1 | 2
2 | 1 | 0 | 1 | 2


# BinsCatCntOrder2DIYNew


找到需要处理的列

```
for col in todo_cols:
    work_cols = X.get_groupby_cols(by=col,cols=cat_cols)
    work_cols = work_cols[:self.config.keys_order2_bin_cat_max]
    for cat_col in work_cols:
        new_col = '{}_{}_cnt'.format(col, cat_col)
        new_col = FeatContext.gen_feat_name(namespace,self.__class__.__name__,new_col,CONSTANT.NUMERICAL_TYPE)
        col2type[new_col] = CONSTANT.NUMERICAL_TYPE
        col2groupby[new_col] = (col,cat_col)
        exec_cols.append((col, cat_col))
        new_cols.append(new_col)
```

- **todo_cols** 用以分组的类别

    ```todo_cols = X.bin_cols```

- **bin_cols** 之前的特征工程中，分为区间统计得到的一些特征


- **get_groupby_cols**

    get_groupby_cols

    a: col b: list of cols -> c: list of cols

    通过上面的字典递归查询，从b中筛选出通过a聚类生成的列


具体的处理措施

```
def func(df):
    cats = gen_combine_cats(df, df.columns)
    cnt = cats.value_counts()
    ss = cats.map(cnt)
    return downcast(ss)

res = Parallel(n_jobs=CONSTANT.JOBS, require='sharedmem')(delayed(func)(df[[col1, col2]]) for col1, col2 in exec_cols)
```

- **gen_combine_cats**

    ```
    category = df[cols[0]].astype('float64')
    for col in cols[1:]:
        mx = df[col].max()
        category *= mx
        category += df[col]
    return category
    ```
   具体而言，对于两列a, b进行如下映射得到新的一列：c = aB + b
   在已知B时，可以从c恢复出a、b


# BinsNumMeanOrder2DIYNew


找到需要处理的列

```
for col in todo_cols:
    cur_num_cols = X.get_groupby_cols(by=col,cols=num_cols)
    cur_num_cols = cur_num_cols[:self.config.keys_order2_bin_num_max]
    for num_col in cur_num_cols:
        new_col = '{}_{}_mean'.format(col, num_col)
        new_col = FeatContext.gen_feat_name(namespace,self.__class__.__name__,new_col,CONSTANT.NUMERICAL_TYPE)
        col2type[new_col] = CONSTANT.NUMERICAL_TYPE
        col2groupby[new_col] = col
        exec_cols.append((col, num_col))
        new_cols.append(new_col)
```

- **todo_cols** 用以分组的类别

    ```todo_cols = X.bin_cols```

- **bin_cols** 之前的特征工程中，分为区间统计得到的一些特征


- **num_cols** 分组中聚合的维度
    ```um_cols = X.combine_num_cols```

- **get_groupby_cols**

    get_groupby_cols

    a: col b: list of cols -> c: list of cols

    通过上面的字典递归查询，从b中筛选出通过a聚类生成的列


具体的处理措施

```
def func(df):
    col = df.columns[0]
    num_col = df.columns[1]
    
    df[num_col] = df[num_col].astype('float32')
    
    means = df.groupby(col,sort=False)[num_col].mean()
    ss = df[col].map(means)
    return downcast(ss)

res = Parallel(n_jobs=CONSTANT.JOBS, require='sharedmem')(delayed(func)(df[[col1, col2]]) for col1, col2 in exec_cols)
```

示意

原数据

index | A |  B  
-|-|-
0 | 0 | 0 |
1 | 0 | 1 |
2 | 1 | 0 |

生成新数据后

index | A |  B | New
-|-|-|-
0 | 0 | 0 | 0.5 
1 | 0 | 1 | 0.5 
2 | 1 | 0 | 0.0


# CatNumMeanOrder2DIYNew


找到需要处理的列

```
size = len(todo_cols)
for i in range(size):
    col1 = todo_cols[i]
    cur_todo_cols = X.get_groupby_cols(by=col1,cols=todo_cols)
    cur_todo_cols = set(cur_todo_cols)
    for j in range(i+1, size):
        col2 = todo_cols[j]
        if col2 not in cur_todo_cols:
            continue
        new_col = '{}_{}_cnt'.format(col1, col2)
        new_col = FeatContext.gen_feat_name(namespace,self.__class__.__name__,new_col,CONSTANT.NUMERICAL_TYPE)
        col2type[new_col] = CONSTANT.NUMERICAL_TYPE
        col2groupby[new_col] = (col1,col2)
        exec_cols.append((col1, col2))
        new_cols.append(new_col)
```

这是类别列之间的组合，对于每一列，它与那些不由它生成的列进行组合

- **todo_cols** 有待组合的列

    ```todo_cols = X.combine_cat_cols[:self.config.all_order2_cat_max]```


- **get_groupby_cols**

    get_groupby_cols

    a: col b: list of cols -> c: list of cols

    通过上面的字典递归查询，从b中筛选出通过a聚类生成的列


具体的处理措施

```
def func(df):
    cats = gen_combine_cats(df, df.columns)
    cnt = cats.value_counts()
    ss = cats.map(cnt)

    return downcast(ss)
res = Parallel(n_jobs=CONSTANT.JOBS, require='sharedmem')(delayed(func)(df[[col1, col2]]) for col1, col2 in exec_cols)
```


# PreMcToNumpy

```
for col in multi_cols:
    vals = df[col].values
    datas,datalen = ac.get_need_data(vals)

    col2muldatas[col] = np.array(datas,dtype='int64').astype(np.int32)
    col2muldatalens[col] = np.array(datalen,dtype='int32')

X.col2muldatas = col2muldatas
X.col2muldatalens = col2muldatalens
```

- **multi_cols** 具有多个类别的列

    ```multi_cols = X.multi_cat_cols```

- **get_need_data**
```
def get_need_data(  vals ):
    cdef:
        int idx,N = vals.shape[0]
        list datas = []
        list datalen = []
        
    for idx in range(N):
        i = vals[idx]
        if type(i) == float:
            datalen.append( 0 )
        else:
            datas.extend( i )
            datalen.append( len(i) )
        
    return datas,datalen
```

示意

原数据

index | A   
-|-
0 | (0,1) |
1 | (1) |
2 | (2) |

生成数据

datas: 0,1,1,2
datalen: 2, 1, 1

这一特征的目的如下：

> 考虑我们在生成特征的过程中，主要是对 multi-category 类型做遍历操作，所以可以使用一个数组去存储 multi-category 的每个数据项。并且用额外一个数组去保存每个 multi-category 的数据项集的长度。这样根据其长度数组和数据数组，我们就能做一个高效的遍历。<br>
链接：https://zhuanlan.zhihu.com/p/77469019


# McCatRank

找到需要处理的列

```
max_count = 300
for col1 in X.multi_cat_cols:
    if (col1 in X.col2block):
        block_id1 = X.col2block[col1]
        
        for col2 in (X.cat_cols+X.user_cols+X.key_cols+X.session_cols):
            if (col2 in X.col2block):
                block_id2 = X.col2block[col2]
                
                if block_id1 == block_id2:
                    exec_cols.append( (col1,col2) )
                    new_col =  col1+'_'+col2
                    new_col = FeatContext.gen_feat_name(namespace,self.__class__.__name__,new_col,CONSTANT.NUMERICAL_TYPE)
                    col2type[new_col] = CONSTANT.NUMERICAL_TYPE
                    new_cols.append(new_col)
                    if len(new_cols)>=max_count:
                        break
    
    if len(new_cols)>=max_count:
        break
```

简单而言，对于一个属于multi_cat_cols的列a,如果一个列b属于cat_cols+X.user_cols+X.key_cols+X.session_cols，并且这两列
属于同一个block，就将二者进行组合


具体的处理措施

```
cat_cols = []
for (col1,col2) in exec_cols:
    cat_cols.append(col2)

cat_cols = sorted(list(set(cat_cols)))

col2muldatas = X.col2muldatas
col2muldatalens = X.col2muldatalens

col2catdatas = {}

for col in cat_cols:
    catdata = df[col].fillna(-1).astype('int32').values
    col2catdatas[col] = catdata
```

没有特殊意义，只是为了加速处理，将col2中的列的numpy数组提前保存到了col2catdatas中


```
res = Parallel(n_jobs=CONSTANT.JOBS,require='sharedmem')(delayed(ac.cat_rank_multi)(col2muldatas[col1],col2muldatalens[col1],col2catdatas[col2]) for (col1,col2) in exec_cols)
```

```
def cat_rank_multi(  int[:] muldata, int[:] muldatalens, int[:] catdata ):
    cdef:
        int index = 0
        int i,j,N = muldatalens.shape[0]
        int les
        int cat
        int flag
        
    ans = np.zeros( N ,dtype=np.int16 )
        
    for i in range(N):
        les = muldatalens[i]
        flag = 0
        cat = catdata[ i ]
        for j in range(index,index+les):
            if muldata[j] == cat:
                flag = j-index+1
                break
        ans[i] = flag     
        index += les
    return ans
```

示意

原数据

index | A | B  
-|-|-
0 | (0,1) | 0
1 | (1,3,4) | 4
2 | (2) | 5

生成数据

datas: 0,1,1,3,4,2
datalen: 2, 3, 1

以第二行为例，b = 4，对应的a = (1,3,4)，结果为3
处理的结果为b在a中的位置

# LGBFeatureSelection

用于低阶特征提取后的筛选

## 训练并保留重要性大于5的特征
```
threshold = 5
df_imp = lgb_train(X,y)
log(f'importances sum {df_imp["importances"].sum()}')
if df_imp["importances"].sum() != 6200:
    keep_feats = list(df_imp.loc[df_imp['importances'] >= threshold,'features'])
    if len(keep_feats) < 150:
        useful_feats = list(df_imp.loc[df_imp['importances'] > 0,'features'])
        if len(useful_feats) <= 150:
            keep_feats = useful_feats
        else:
            df_imp_sorted = df_imp.sort_values(by='importances',ascending=False)
            keep_feats = list(df_imp_sorted['features'].iloc[:150])
else:
    keep_feats = list(df_imp.loc[df_imp['importances'] >= threshold,'features'])
```

## 对保留特征进行进一步处理

将之前提取的特征分类型记录，即前述combine_num_cols等的来源

```
keep_cats = []

keep_cats_set = set()
cat_set = set(X.cat_cols)

for feat in keep_feats:

    if X.col2type[feat] == CONSTANT.CATEGORY_TYPE:
        if feat in cat_set:
            if feat not in keep_cats_set:
                keep_cats_set.add(feat)
                keep_cats.append(feat)

    elif feat in X.col2source_cat:
        keep_feat = X.col2source_cat[feat]
        if keep_feat in cat_set:
            if keep_feat not in keep_cats_set:
                keep_cats_set.add(keep_feat)
                keep_cats.append(keep_feat)

```
```
keep_nums = []
for feat in keep_feats:
    if X.col2type[feat] ==  CONSTANT.NUMERICAL_TYPE:
        keep_nums.append(feat)

keep_binaries = []
for feat in keep_feats:
    if X.col2type[feat] ==  CONSTANT.BINARY_TYPE:
        keep_binaries.append(feat)

X.reset_combine_cols(keep_cats,keep_nums,keep_binaries)
```

# LGBFeatureSelection

用于一些组合特征的筛选，相比**LGBFeatureSelection**，主要加入了以下部分

## 根据正负样本比例保留生成特征，比例越大，保留越多

## 根据处理速度选择保留阈值，越快则阈值越小，保留特征越多

# LGBFeatureSelection

用于一些大量组合的特征，在特征工程生成的一些特征会记录为**wait_selection_cols**,比起**LGBFeatureSelection**，
这部分的特征也可能被剔除

```
for cols in X.wait_selection_cols:
    drops = df_imp.loc[cols].sort_values(by='importances',ascending=False).index[self.config.wait_feat_selection_num:]
    drops = set(drops)
    drop_feats = drop_feats | drops
```