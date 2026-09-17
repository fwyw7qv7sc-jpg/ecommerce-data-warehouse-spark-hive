
# E-commerce Data Warehouse with Spark, Hive, and Sqoop

Design and implementation of a data warehouse for a mini e-commerce application using Hive, Spark, Sqoop, and HDFS. The project includes data ingestion, ETL processes, and Hive analytics on sales and customer data.

## E-commerce Data Warehouse Design and Analytics

This project is a practice exercise to work with Sqoop, Hadoop, and Hive. It focuses on designing and implementing a data warehouse for an e-commerce application to perform analytics on sales and customer data. The data warehouse is built using big data tools such as Hive, Spark, Sqoop, and HDFS. The project involves data ingestion, ETL (Extract, Transform, Load) processes, and performing Hive analytics to generate insights that can help in decision-making for the business. An EC2 container is used for the project.

## Objectives

- **Data Ingestion**: Use Sqoop to import data from various transactional databases (e.g., MySQL, PostgreSQL) into HDFS.
- **Data Transformation and ETL**: Utilize Apache Spark for cleaning, transforming, and loading data from HDFS into Hive tables.
- **Data Warehouse Design**: Implement a star schema design in Hive to model sales and customer demographics data, enabling efficient querying and analysis.
- **Analytics**: Write and execute HiveQL queries to analyze sales trends, customer behaviors, and other business metrics.
- **Documentation**: Provide comprehensive documentation for setting up the environment, data ingestion, transformation processes, Hive schema design, and analytics.

## Documentation

Below is the comprehensive documentation to help you set up the project, understand the data model, and run the ETL and analytics processes. The documentation is divided into sections:

### Setup Guide

Instructions for setting up a Hadoop cluster, installing Hive, Spark, and Sqoop, and configuring the environment. You need to setup 2 env files for hadoop & hadoop-hive with details.

1. **Create a t2.2xlarge EC2 Instance on AWS & SSH into it:**

    ```bash
    ssh -i "path_to_pem_file.pem" ec2-user@your-ec2-instance-ip
    ```

2. **Install and Setup Docker and Docker-compose:**

    ```bash
    sudo yum update -y
    sudo yum install docker
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo gpasswd -a $USER docker
    newgrp docker
    sudo pacman -S libxcrypt-compat  # Needed for older versions of docker-compose to run
    ```

    Start Docker:

    ```bash
    sudo systemctl start docker
    ```

3. **Make a Working Directory (Optional but Preferred):**

    ```bash
    mkdir ecommerce-data-warehouse
    cd ecommerce-data-warehouse
    ```

4. **Clone the Repository:**

    ```bash
    git clone https://github.com/your-repo/ecommerce-data-warehouse.git
    cd ecommerce-data-warehouse
    docker-compose up -d
    ```

5. **Check if Docker Containers are Up:**

    ```bash
    docker ps
    ```

6. **SSH Login from Local Machine with Port Forwarding:**

    Replace the server IP and PEM path based on your saved path and EC2 instance IP.

    ```bash
    ssh -i "path_to_pem_file.pem" ec2-user@your-ec2-instance-ip -L 10000:localhost:10000
    ```

7. **Access Bash Shell of Different Containers:**

    ```bash
    docker exec -i -t ra_mysql bash
    docker exec -i -t ra_sqoop bash
    docker exec -i -t ra_hive-server bash
    docker exec -i -t hdp_spark-master bash
    ```

8. **Hive and Spark Dependencies Configuration & Setup:**

    - **Add PostgreSQL JAR**: 

        Download the JAR file from the internet and copy it from the local machine to EC2:

        ```bash
        scp -r -i "path_to_pem_file.pem" postgresql-42.3.1.jar ec2-user@your-ec2-instance-ip:/home/ec2-user/
        ```

        Copy the file from EC2 into the Spark container:

        ```bash
        docker cp /home/ec2-user/postgresql-42.3.8.jar hdp_spark-master:/spark/jars
        ```

    - **Copy `hive-site.xml` from Hive to Spark Container:**

        ```bash
        docker cp ra_hive-server:/opt/hive/conf/hive-site.xml /home/ec2-user/
        docker cp hive-site.xml hdp_spark-master:/spark/conf/hive-site.xml
        ```

9. **MySQL Database Setup and Populate Database:**

    - Download the AdventureWorks dataset for MySQL:

        [Download Link](https://github.com/vishal180618/OLTP-AdventureWorks2019-MySQL)

    - Copy the SQL dump file into the EC2 container and then into the MySQL Docker container:

        ```bash
        docker cp AdventureWorks2019.sql ra_mysql:/
        ```

    - Access MySQL and create the database:

        ```bash
        docker exec -i -t ra_mysql bash
        mysql -u root -p
        CREATE DATABASE testdb;
        USE testdb;
        ```

    - Import the SQL dump file:

        ```bash
        mysql -u root -p testdb < AdventureWorks2019.sql
        ```

10. **Data Ingestion with Sqoop:**

    Import data from MySQL to HDFS using Sqoop commands. Login to the Sqoop container:

    ```bash
    docker exec -i -t ra_sqoop bash
    ```

    Run the following Sqoop commands to import data:

    ```bash
    sqoop import --connect jdbc:mysql://ra_mysql:3306/testdb --username root --target-dir /input/v_salesorderheader/ --query 'SELECT ... FROM v_salesorderheader_demo WHERE $CONDITIONS' --split-by SalesOrderID --password example
    ```

11. **Creating Hive Tables and Loading Imported Data:**

    Connect to the Hive Docker container:

    ```bash
    docker exec -i -t ra_hive-server bash
    hive
    ```

    Create tables and load data as described in the documentation.

12. **Analytics Queries:**

    Run HiveQL queries to analyze data. Example queries can be found in the `basic_analytics.sql` file.

13. **Cleanup Process:**

    - Stop Docker containers:

        ```bash
        docker-compose stop
        ```

    - To stop Docker service:

        ```bash
        sudo systemctl stop docker
        ```

    - Remove Docker containers fully:

        ```bash
        docker-compose down
        ```

## How to Use This Repository

1. **Clone the Repository**: Download or clone the repository to your local machine.
2. **Follow the Setup Guide**: Set up the environment and install the necessary tools.
3. **Ingest Data**: Use Sqoop commands provided in the documentation to import data into HDFS.
4. **Run ETL Processes**: Execute Spark jobs to transform data and load it into Hive tables.
5. **Perform Analytics**: Use Hive to run analytical queries and derive insights from the data.
