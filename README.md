# E-commerce Data Warehouse with Spark, Hive, Sqoop
这是一个基于 Docker 搭建的本地电商数据仓库项目，用于学习和实践传统离线数据开发的完整数据链路。

项目模拟电商业务场景，以 MySQL 作为业务数据库，通过 Sqoop 将业务数据同步到 HDFS 的 ODS 层，再使用 Spark 完成数据清洗和转换，生成 DWD 层 Parquet 数据，最后通过 Hive 构建 DWS 和 ADS 层并进行业务分析。

整个项目覆盖 MySQL、HDFS、YARN、Sqoop、Spark、Hive、Parquet、SQL、Docker 和 Git 等数据开发常用技术。

## 1. 项目架构
```text
                          MySQL
                     业务数据库
                         │
                         │ Sqoop
                         ▼
                  ┌──────────────┐
                  │     HDFS     │
                  │     ODS      │
                  └──────────────┘
                         │
                         │ Spark ETL
                         ▼
                  ┌──────────────┐
                  │     DWD      │
                  │    Parquet   │
                  └──────────────┘
                         │
                         │ Hive SQL
                         ▼
                  ┌──────────────┐
                  │     DWS      │
                  │ 城市订单汇总   │
                  └──────────────┘
                         │
                         │ Window Function
                         ▼
                  ┌──────────────┐
                  │     ADS      │
                  │ 城市销售排名   │
                  └──────────────┘
```

## 2. 技术栈
| 技术 | 版本 | 作用 |
| :--- | :--- | :--- |
| Docker | - | 搭建本地大数据运行环境 |
| Docker Compose | - | 管理多个大数据服务 |
| MySQL | 5.7 | 模拟业务数据库 |
| Sqoop | 1.4.7 | MySQL → HDFS 数据同步 |
| Hadoop | 3.2.1 | HDFS 分布式存储和 YARN 资源管理 |
| Spark | 3.0.0 | ODS → DWD 数据清洗和转换 |
| Hive | 2.3.2 | 数据仓库建模和 SQL 分析 |
| PostgreSQL | - | Hive Metastore 后端数据库 |
| Python / Faker | - | 生成模拟业务数据 |
| Parquet | - | DWD、DWS、ADS 数据存储格式 |
| Git | - | 项目版本管理 |

## 3. 项目目录
```
ecommerce-data-warehouse-spark-hive-main/
├── docker-compose.yml
├── Dockerfile.sqoop
├── hadoop.env
├── hadoop-hive.env
├── generate_data.py
├── etl_spark.py
├── basic_analytics.sql
├── README.md
└── .gitignore
```

**主要文件说明：**
| 文件 | 作用 |
| :--- | :--- |
| docker-compose.yml | 定义 Hadoop、Spark、Hive、MySQL、Sqoop 等服务 |
| Dockerfile.sqoop | 构建与 Hadoop 3.2.1 兼容的 Sqoop 环境 |
| hadoop.env | Hadoop 环境配置 |
| hadoop-hive.env | Hadoop / Hive 环境配置 |
| generate_data.py | 生成 MySQL 测试数据 |
| etl_spark.py | Spark ODS → DWD ETL 程序 |
| basic_analytics.sql | Hive 分析 SQL |
| README.md | 项目说明文档 |

## 4. 数据模型
### 4.1 users
用户表，共生成 20000 条数据。
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_id | INT | 用户 ID |
| name | VARCHAR | 用户姓名 |
| city | VARCHAR | 用户所在城市 |
| reg_date | DATETIME | 注册时间 |

### 4.2 orders
订单表，共生成 100000 条数据。
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| order_id | INT | 订单 ID |
| user_id | INT | 用户 ID |
| product_category | VARCHAR | 商品类别 |
| amount | DECIMAL | 订单金额 |
| order_time | DATETIME | 下单时间 |

**数据关系：**
```
users
│
│ user_id
└──────────────< orders
```
一个用户可以对应多个订单。

## 5. 生成业务数据
项目使用 Python + Faker 生成模拟电商数据。

**运行：**
```bash
python3 generate_data.py
```

**生成：**
- `users`   → 20000 条
- `orders`  → 100000 条

**MySQL 配置：**
- Host: `127.0.0.1`
- Port: `3307`
- Database: `testdb`
- Username: `root`
- Password: `example`

如果本机还没有安装 Python 依赖：
```bash
pip3 install pymysql faker
```

> **注意**：`generate_data.py` 使用 `CREATE TABLE IF NOT EXISTS`，再次运行时会向现有表继续插入数据，而不是自动清空旧数据。

## 6. 启动 Docker 环境
启动项目：
```bash
docker compose up -d
```

查看服务状态：
```bash
docker compose ps
```

项目主要服务包括：
`namenode` `datanode` `resourcemanager` `nodemanager1` `historyserver` `spark-master` `spark-worker-1` `hive-server` `hive-metastore` `hive-metastore-postgresql` `mysql`

Sqoop 不需要长期运行，执行数据同步时通过：
```bash
docker compose run --rm sqoop ...
```
临时启动。

## 7. ODS 层：MySQL → HDFS
ODS（Operational Data Store）主要保存从业务数据库同步过来的原始数据。

### 7.1 导入 users
```bash
docker compose run --rm sqoop sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username root \
  --password example \
  --table users \
  --target-dir /user/root/ods/users \
  --num-mappers 1
```

导入成功后：
```
/user/root/ods/users/
├── _SUCCESS
└── part-m-00000
```

### 7.2 导入 orders
```bash
docker compose run --rm sqoop sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username root \
  --password example \
  --table orders \
  --target-dir /user/root/ods/orders \
  --num-mappers 1
```

导入成功后：
```
/user/root/ods/orders/
├── _SUCCESS
└── part-m-00000
```

可以通过 HDFS 查看：
```bash
docker exec -it ra_namenode hdfs dfs -ls -R /user/root/ods
```

当前 ODS 数据量：
- `users`  → 20000
- `orders` → 100000

## 8. DWD 层：Spark ETL
DWD（Data Warehouse Detail）保存经过清洗和转换后的明细数据。

Spark 程序：`etl_spark.py`

**主要处理：**
- 从 HDFS ODS 读取 CSV 数据
- 自动推断字段类型
- 转换时间字段
- 将订单金额转换为 Double
- 根据主键去重
- 将数据写入 Parquet

**执行：**
```bash
docker cp etl_spark.py hdp_spark-master:/tmp/etl_spark.py
```

然后：
```bash
docker exec -it hdp_spark-master \
/spark/bin/spark-submit \
--master spark://spark-master:7077 \
/tmp/etl_spark.py
```

**DWD 输出路径：**
- `/user/root/dwd/users`
- `/user/root/dwd/orders`

**数据格式：** `Parquet`

**DWD 数据粒度：**
- `dwd_users` → 一行代表一个用户
- `dwd_orders` → 一行代表一个订单

## 9. Hive 建立 DWD 外部表
Hive 通过外部表读取 HDFS 上 Spark 生成的 Parquet 数据。

进入 Hive：
```bash
docker exec -it ra_hive-server \
beeline -u jdbc:hive2://localhost:10000
```

创建数据库：
```sql
CREATE DATABASE IF NOT EXISTS ecommerce_dw;
USE ecommerce_dw;
```

创建用户明细表：
```sql
CREATE EXTERNAL TABLE dwd_users (
    user_id INT,
    name STRING,
    city STRING,
    reg_date TIMESTAMP
) STORED AS PARQUET
LOCATION '/user/root/dwd/users';
```

创建订单明细表：
```sql
CREATE EXTERNAL TABLE dwd_orders (
    order_id INT,
    user_id INT,
    product_category STRING,
    amount DOUBLE,
    order_time TIMESTAMP
) STORED AS PARQUET
LOCATION '/user/root/dwd/orders';
```

验证：
```sql
SELECT COUNT(*) FROM dwd_users;
SELECT COUNT(*) FROM dwd_orders;
```

当前结果：
- `dwd_users`  → 20000
- `dwd_orders` → 100000

## 10. DWS 层：城市订单汇总
DWS（Data Warehouse Summary）主要保存面向分析场景的汇总数据。

本项目按照城市统计：
- 订单数量
- 销售总额
- 平均订单金额

SQL：
```sql
CREATE TABLE ecommerce_dw.dws_city_order_stats STORED AS PARQUET
AS SELECT
    u.city,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.amount), 2) AS total_amount,
    ROUND(AVG(o.amount), 2) AS avg_amount
FROM ecommerce_dw.dwd_orders o
JOIN ecommerce_dw.dwd_users u
    ON o.user_id = u.user_id
GROUP BY u.city;
```

查询：
```sql
SELECT * FROM ecommerce_dw.dws_city_order_stats ORDER BY total_amount DESC LIMIT 10;
```

当前数据：
```
100,000 条订单
        ↓ 按照城市 GROUP BY
        ↓ 67 个城市汇总结果
```

**DWS 数据粒度：** 一行代表一个城市

## 11. ADS 层：城市销售排名
ADS（Application Data Store）主要面向最终业务分析和报表使用。

本项目根据城市销售总额进行排名，使用 Hive 窗口函数：
```sql
CREATE TABLE ecommerce_dw.ads_city_sales_rank STORED AS PARQUET
AS SELECT
    city,
    order_count,
    total_amount,
    avg_amount,
    RANK() OVER (
        ORDER BY total_amount DESC
    ) AS sales_rank
FROM ecommerce_dw.dws_city_order_stats;
```

查询 Top 10：
```sql
SELECT * FROM ecommerce_dw.ads_city_sales_rank ORDER BY sales_rank LIMIT 10;
```

**ADS 数据粒度：** 一行代表一个城市

相比 DWS，ADS 增加了 `sales_rank` 字段，用于直接支持城市销售排名类报表。

## 12. 数据仓库分层
本项目使用经典的离线数仓分层：
`ODS  →  DWD  →  DWS  →  ADS`

**ODS**
保存从业务系统同步过来的原始数据。
本项目链路：`MySQL → Sqoop → HDFS / ODS`

**DWD**
对 ODS 数据进行清洗、转换、去重，形成明细层数据。
本项目链路：`ODS → Spark → DWD`

**DWS**
对 DWD 明细数据进行主题汇总。
本项目链路：`DWD → Hive SQL → 城市订单汇总`

**ADS**
面向最终业务分析和报表。
本项目链路：`DWS → 窗口函数 → 城市销售排名`

## 13. 项目中实践的核心知识点
### Hadoop / HDFS
- 理解 NameNode、DataNode 以及 HDFS 文件和目录管理
- 常用命令：
  ```bash
  hdfs dfs -ls
  hdfs dfs -mkdir
  hdfs dfs -put
  hdfs dfs -cat
  hdfs dfs -du
  ```

### YARN
- 理解 Hadoop 的资源管理和任务调度
- 核心组件：ResourceManager、NodeManager
- 本项目中 Sqoop 导入产生的 MapReduce 任务由 YARN 进行资源调度
- Spark ETL 使用 Spark Standalone 集群运行

### Sqoop
- 理解关系型数据库和 Hadoop 之间的数据同步
- 本项目链路：`MySQL → Sqoop → HDFS`
- 重点参数：`--connect` `--username` `--password` `--table` `--target-dir` `--num-mappers`

### Spark
- 理解 Spark 的 DataFrame、Transformation、Action 和 ETL 流程
- 本项目处理流程：
  ```
  读取 ODS
      ↓ 类型转换
      ↓ 数据清洗
      ↓ 去重
      ↓ 写入 Parquet
  ```

### Hive
- 理解 Hive 如何通过 SQL 查询 HDFS 上的数据
- 本项目链路：
  ```
  Hive
      ↓ DWD 外部表
      ↓ DWS 汇总
      ↓ ADS 应用数据
  ```

### SQL
重点实践语法：
`JOIN` `GROUP BY` `COUNT` `SUM` `AVG` `ROUND` `ORDER BY` `RANK() OVER()`

## 14. 常用端口
| 服务 | 端口 | 用途 |
| :--- | :--- | :--- |
| NameNode | 9870 | HDFS Web UI |
| NameNode | 9010 → 9000 | HDFS RPC（Host → Container） |
| Spark Master | 8080 | Spark Web UI |
| Spark Master | 7077 | Spark Master 通信端口 |
| Spark Worker | 8081 | Spark Worker Web UI |
| HiveServer2 | 10000 | Hive JDBC / Beeline |
| Hive Metastore | 9083 | Hive Metastore |
| MySQL | 3307 | MySQL 对外映射端口 |
| Hue | 1088 | HDFS 文件浏览 |
| Presto | 8089 | Presto 查询引擎 |

## 15. 常见问题
### 15.1 Apple Silicon 平台警告
在 Apple Silicon Mac 上运行部分 amd64 镜像时可能出现：
> The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)

这是 Docker 的架构兼容提示。本项目中的 MySQL 服务显式指定 `platform: linux/amd64`，在 Docker Desktop 的兼容机制下可以运行。

### 15.2 Hive 中文显示为 ???
如果 Hive Server 的 Java 默认编码不是 UTF-8，中文可能显示异常。
项目在 `docker-compose.yml` 中设置：
```yaml
LANG: C.UTF-8
LC_ALL: C.UTF-8
```
使 Hive Server 使用 UTF-8 编码。

### 15.3 Sqoop 与 Hadoop 版本兼容
原始 Sqoop 镜像使用 Hadoop 2.7.4，而本项目 Hadoop 使用 3.2.1，可能出现：
> Could not find or load main class org.apache.hadoop.mapreduce.v2.app.MRAppMaster

项目通过 `Dockerfile.sqoop` 将 Hadoop 3.2.1 环境加入 Sqoop 容器，并设置 MapReduce 环境变量解决该问题。

### 15.4 MySQL 中文显示为 ???
如果 MySQL 客户端默认使用 latin1，查询中文时可能显示为 `??`，这不一定代表数据库中的数据损坏。

可以使用 UTF-8 客户端连接：
```bash
docker exec -it ra_mysql \
mysql --default-character-set=utf8mb4 \
-uroot -pexample \
-e "SELECT user_id, name, city FROM testdb.users LIMIT 5;"
```

## 16. 项目目标
这个项目主要用于理解传统离线数据开发中的完整数据链路：
```
业务数据库
    ↓ 数据同步
    ↓ ODS
    ↓ 数据清洗
    ↓ DWD
    ↓ 数据汇总
    ↓ DWS
    ↓ 业务数据集市
    ↓ ADS
```

重点学习技术栈：
`Linux / Docker` `MySQL` `HDFS` `YARN` `Sqoop` `Spark` `Hive` `SQL` `数据仓库分层` `Parquet` `ETL` `窗口函数` `Git / GitHub`

## 17. 后续可以扩展
后续可以继续增加：
- 按日期构建分区表
- 商品类别维度分析
- 用户消费等级
- 日 / 月销售趋势
- Top N 商品
- 用户复购率
- Spark SQL
- Hive 分区与分桶
- 数据质量检查
- Airflow 调度

> 本项目仅用于学习和实践数据开发技术。
