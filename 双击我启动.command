#!/bin/bash

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 启动服务并在新终端窗口中显示
osascript <<EOF
tell application "Terminal"
    do script "cd '$DIR' && ./run.sh; exec bash"
    activate
end tell
EOF

# 等待3秒让服务启动
sleep 3

# 自动打开浏览器
open "http://localhost:9090"
