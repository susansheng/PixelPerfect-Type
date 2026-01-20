#!/bin/bash

# 在新的终端窗口中打开并运行
cd "$(dirname "$0")"

osascript <<EOF
tell application "Terminal"
    do script "cd '$PWD' && ./run.sh"
    activate
end tell
EOF
