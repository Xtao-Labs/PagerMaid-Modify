#!/bin/bash
if [[ $EUID -ne 0 ]]
then
    clear
    echo "错误：本脚本需要 root 权限执行。" 1>&2
    exit 1
fi

welcome() {
  echo ""
  echo "安装即将开始"
  echo "如果您想取消安装，"
  echo "请在 5 秒钟内按 Ctrl+C 终止此脚本。"
  echo ""
  sleep 5
}

docker_check() {
  echo "正在检查 Docker 安装情况 . . ."
  if command -v docker >> /dev/null 2>&1;
  then
    echo "Docker 似乎存在, 安装过程继续 . . ."
  else
    echo "Docker 未安装在此系统上"
    echo "请安装 Docker 并将自己添加到 Docker"
    echo "分组并重新运行此脚本。"
    exit 1
  fi
}

git_check() {
  echo "正在检查 Git 安装情况 . . ."
  if command -v git >> /dev/null 2>&1;
  then
    echo "Git 似乎存在, 安装过程继续 . . ."
  else
    echo "Git 未安装在此系统上！"
    echo "请安装 Git 并重新运行此脚本。"
    exit 1
  fi
}

access_check() {
  echo "测试 Docker 环境 . . ."
  if [ -w /var/run/docker.sock ]
  then
    echo "该用户可以使用 Docker , 安装过程继续 . . ."
  else
    echo "该用户无权访问 Docker，或者 Docker 没有运行。 请添加自己到 Docker 分组并重新运行此脚本。"
    exit 1
  fi
}

build_docker() {
  printf "请输入 PagerMaid 容器的名称："
  read -r container_name <&1
  echo "正在拉取 Docker 镜像 . . ."
  docker rm -f "$container_name" > /dev/null 2>&1
  docker pull mrwangzhe/pagermaid_modify
}

start_docker() {
  echo "正在启动 Docker 容器 . . ."
  echo "在登录后，请按 Ctrl + C 使容器在后台模式下重新启动。"
  sleep 3
  docker run -it --restart=always --name="$container_name" --hostname="$container_name" mrwangzhe/pagermaid_modify <&1
  echo ""
  echo "Docker 创建完毕。"
  echo ""
  shon_online
}

start_installation() {
  welcome
  docker_check
  git_check
  access_check
  build_docker
  start_docker
}

cleanup(){
  printf "请输入 PagerMaid 容器的名称："
  read -r container_name <&1
  echo "正在删除 Docker 镜像 . . ."
  docker rm -f "$container_name" > /dev/null 2>&1
  echo ""
  shon_online
}

stop_pager(){
  printf "请输入 PagerMaid 容器的名称："
  read -r container_name <&1
  echo "正在关闭 Docker 镜像 . . ."
  docker stop "$container_name" > /dev/null 2>&1
  echo ""
  shon_online
}

start_pager(){
  printf "请输入 PagerMaid 容器的名称："
  read -r container_name <&1
  echo "正在启动 Docker 容器 . . ."
  docker start $container_name > /dev/null 2>&1
  echo ""
  echo "Docker 启动完毕。"
  echo ""
  shon_online
}

restart_pager(){
  printf "请输入 PagerMaid 容器的名称："
  read -r container_name <&1
  echo "正在重新启动 Docker 容器 . . ."
  docker restart $container_name > /dev/null 2>&1
  echo ""
  echo "Docker 重新启动完毕。"
  echo ""
  shon_online
}

reinstall_pager(){
  build_docker
  start_docker
}

shon_online(){
echo ""
echo "欢迎使用 PagerMaid-Modify Docker 一键安装脚本。"
echo ""
echo "请选择您需要进行的操作:"
echo "  1) Docker 安装 PagerMaid"
echo "  2) Docker 卸载 PagerMaid"
echo "  3) 关闭 PagerMaid"
echo "  4) 启动 PagerMaid"
echo "  5) 重新启动 PagerMaid"
echo "  6) 重新安装 PagerMaid"
echo "  7) 退出脚本"
echo ""
echo "     Version：0.2.0"
echo ""
echo -n "请输入编号: "
read N
case $N in
  1)
  start_installation
  ;;
  2)
  cleanup
  ;;
  3)
  stop_pager
  ;;
  4)
  start_pager
  ;;
  5)
  restart_pager
  ;;
  6)
  reinstall_pager
  ;;
  7)
  exit
  ;;
  *)
  echo "Wrong input!"
  sleep 5s
  shon_online
  ;;
esac 
}

shon_online
