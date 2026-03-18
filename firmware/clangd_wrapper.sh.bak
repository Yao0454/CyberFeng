#!/bin/bash

# 这是真正的 ESP32 编译器路径
COMPILER="/Users/feng/.platformio/packages/toolchain-xtensa-esp32/bin/xtensa-esp32-elf-g++"

declare -a NEW_ARGS
skip_next=0

# 过滤掉 clangd 传过来的 --target 参数，防止 GCC 报错
for arg in "$@"; do
    if [ $skip_next -eq 1 ]; then
        skip_next=0
        continue
    fi

    if [[ "$arg" == "--target="* ]]; then
        continue
    elif [[ "$arg" == "-target" ]]; then
        skip_next=1
        continue
    else
        NEW_ARGS+=("$arg")
    fi
done

# 执行真正的编译器
exec "$COMPILER" "${NEW_ARGS[@]}"
