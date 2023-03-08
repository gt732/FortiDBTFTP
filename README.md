# FortiDBTFTP
Quick project that uses a modified version of py3tftp library to write to a postgres db instead of creating a file locally. The fortigate firewall is configured for scheduled backups and uploads the configuration via tftp to a postgres db.

Original library https://github.com/sirMackk/py3tftp

## Postgres Table
```
id PRIMARY KEY,
hostname TEXT,
config TEXT,
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
```
## Run Docker Compose
```
version: '3'
services:
  py3tftpsql:
    image: gt732/py3tftpsql
    depends_on:
      - postgres
    environment:
      - DATABASE_HOSTNAME=postgres
      - DATABASE_PORT=5432
      - DATABASE_NAME=py3tftpsql
      - DATABASE_PASSWORD=your_pw
      - DATABASE_USERNAME=your_username
    ports:
      - "69:69/udp"
  postgres:
    image: postgres
    environment:
      - POSTGRES_DB=py3tftpsql
      - POSTGRES_USER=your_username
      - POSTGRES_PASSWORD=your_pw
    volumes:
      - postgres-db:/var/lib/postgresql/data
    ports:
      - "55362:5432/tcp"
volumes:
  postgres-db:
```
```
docker compose up
```
![alt text](https://i.imgur.com/YQ8p2lv.png)
## Create a backup schedule on the fortigate using automation stitch

![alt text](https://i.imgur.com/d0yL4qB.png)
![alt text](https://i.imgur.com/PlvdBrH.png)

## Once the stitch triggers you should see the configs upload to the database - For my demo I have 3 fortigates scheduled
![alt text](https://i.imgur.com/yOfEqI2.png)

## Example script to check for configuratrion differences between two dates using the database

```
python check_config_diff.py --help
usage: check_config_diff.py [-h] --hostname HOSTNAME --date1 DATE1 --date2 DATE2

options:
  -h, --help           show this help message and exit
  --hostname HOSTNAME  firewall hostname
  --date1 DATE1        first backup date (YYYY-MM-DD)
  --date2 DATE2        second backup date (YYYY-MM-DD)
```

## Here I check for any configuration changes for firewall NJ-FGT and provide two dates --date1 2023-03-06 --date2 2023-03-07

```
$ python check_config_diff.py --hostname NJ-FGT --date1 2023-03-06 --date2 2023-03-07

 *** No Configuration Difference Found ! *** 

$ 
```

## I added a new policy and checked the configuration difference for --date1 2023-03-07 --date2 2023-03-08

![alt text](https://i.imgur.com/Y2EaRmT.png)
