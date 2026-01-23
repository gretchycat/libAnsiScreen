#!/bin/bash
PWD=$(pwd)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
for t in test_*.py; do
	python3 "$t" thetis.ans
	if [ $? = 0 ];then
		echo -e "\033[1;32m=== ${t} passed\033[0m"
	else
		echo -e "\033[1;31m=== ${t} failed\033[0m"
	fi
done

cd ${PWD}
