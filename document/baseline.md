# BaseLine 的训练步骤

- 预处理
- 表合并
- 特征工程
- 训练

## 预处理

BaseLine只清理了NaN值。

## 表合并

首先建立表之间的关系图，图中的节点代表一张表，边代表一个外键。

广搜确定深度，根据深度逐级合并

合并时如果表中有时间列会做特殊处理


    if config['time_col'] in u and config['time_col'] in v:
        log(f"join {u_name} <--{type_}--t {v_name}")
        u = temporal_join(u, v, v_name, key, config['time_col'])


## 特征工程

- 对单类别的列和多类别的列通过转为int类型办法进行hash


```
def transform_categorical_hash(df):
        for c in [c for c in df if c.startswith(CONSTANT.CATEGORY_PREFIX)]:
            df[c] = df[c].apply(lambda x: int(x))

        for c in [c for c in df if c.startswith(CONSTANT.MULTI_CAT_PREFIX)]:
            df[c] = df[c].apply(lambda x: int(x.split(',')[0]))
```

- 去掉时间列

```
def transform_datetime(df, config):
    for c in [c for c in df if c.startswith(CONSTANT.TIME_PREFIX)]:
        df.drop(c, axis=1, inplace=True)
```


## 训练

通过网格搜索寻找最佳的超参数

# DeepBlueAi 的训练步骤


## 预处理

- 要求训练集与测试集的总样本数不超过 400 万条数据。如训练集与测试集的总样本数过多，就对其进行采样。

- 会尝试从列中识别出用户(user_col)、会话(session_col)和二值的列(binary_col)。

- 会建立列之间的关系图，图中的节点代表一张表中的列，节点的名字如:**main_table:t_01**, **table_1:t_01**,这两个节点间会建立一条边。
- 对于分类的列，如果表1的c1和表2的c2其出现的值有许多重合，在这两个节点间也会建立一条边。

```
    if len(all_cat2set[name1] & all_cat2set[name2])/less_len > 0.1:
        mc_graph[name1][name2] = 1
        mc_graph[name2][name1] = 1
```

- 根据上面建立好的图，根据深度搜索的路径将所有的列划分为不同的block
```
def dfs(now,block_id):
    block2name[block_id].append(now)
    for nex in nodes:
        if mc_graph[now][nex] and ( not (nex in vis) ):
            vis[nex] = 1
            dfs(nex,block_id)

for now in nodes:
    if now in vis:
        continue
    vis[now] = 1
    block_id += 1
    block2name[block_id] = []
    dfs(now,block_id)
```

这些block会用于后续的特征工程当中。

- 对用不同的列，也会有不同的处理方式，各类处理方式具体见**preprocessor**部分，总体较为复杂。


## 表合并

总体上的流程类似，但是合并的时候会根据外键的类型(M2M、M2O、O2M、O2O)做不同处理，涉及到时间的也会特殊处理。详细代码见**feat/default_merge_feat**。

## 特征工程

复杂了很多，有许多自定义的特征，有自动的特征提取和组合。

- 基础特征部分，针对 user、key、session 的统计特征，有很好的效果
- 一阶组合特征部分，主表中较为重要的 user、key、session 与其余的 numerical 或 categorical 挑选出的数据进行组合
- 大量组合特征部分，使用时间桶对 categorical 和 numerical 数据进行组合， 以及categorical 或 numerical 数据两两组合形成新的特征
- 有监督学习的 CTR 和均值编码特征

## 训练


- 提前计算，记录到当前用时，通过训练模型几个轮次来计算出模型启动的时间以及模型训练每一轮数据所消耗的时间

- 预估模型训练时间设置合理的boost_round，详见automl/auto_lgb.py/param_compute

- 通过尝试性的训练试探得到最合适的学习速率，详见automl/auto_lgb.py/param_opt_new

- 使用 bagging 的方法模型融合。通过计算一个 demo 模拟真实数据集训练和预测来预估真实数据集所需要的时间，如时间不足则选择在训练时 early-stop，允许精度上的损失来保证代码能够在规定时间内运行完毕。如时间充裕，则通过当前剩余时间计算允许多少个模型进行融合

- 自动针对数据情况采取不同的采样方式和比例