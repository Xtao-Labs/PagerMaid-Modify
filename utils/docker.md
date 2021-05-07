## 一、一键脚本

```
wget https://raw.githubusercontent.com/Xtao-Labs/PagerMaid-Modify/master/utils/docker.sh
bash docker.sh
```

*注：一键脚本安装的Docker将以root权限运行，在使用pagermaid时最方便。*

## docker-compose 安装

1. 准备脚本

```
git clone https://github.com/Xtao-Labs/PagerMaid-Modify pagermaid
cd pagermaid
cp config.gen.yml config.yml
cp docker-compose.gen.yml docker-compose.yml
```

2. 编辑刚刚复制的`docker-compose.yml`为你自己的信息，如不想解决权限问题，建议`RUN_AS_ROOT=true`。

3. 如果会配置，就自己编辑刚刚复制的`config.yml`。如果不会就直接下一步。

4. 启动容器`docker-compose up -d`。

5. 如第3步未配置`config.yml`，则运行`docker exec -it <容器名> bash utils/docker-config.sh`进行配置。

