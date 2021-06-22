#!/usr/bin/env bash
set -ex
mkdir -p out
cd out

BASE=/home/boristeo/fun/fpga

XRAY_UTILS_DIR=$BASE/prjxray/utils
XRAY_TOOLS_DIR=$BASE/prjxray/build/tools
XRAY_DATABASE_DIR=$BASE/prjxray/database

$BASE/yosys/yosys -p "synth_xilinx -flatten -nowidelut -abc9 -arch xc7 -top top; write_json attosoc.json" ../verilog/top.v
$BASE/nextpnr-xilinx/nextpnr-xilinx --chipdb $BASE/nextpnr-xilinx/xilinx/xc7z010.bin --xdc ../xdc/zybo.xdc --json attosoc.json --write attosoc_routed.json --fasm attosoc.fasm
${XRAY_UTILS_DIR}/fasm2frames.py --db-root ${XRAY_DATABASE_DIR}/zynq7 --part xc7z010clg400-1 attosoc.fasm > attosoc.frames
${XRAY_TOOLS_DIR}/xc7frames2bit --part_file ${XRAY_DATABASE_DIR}/zynq7/xc7z010clg400-1/part.yaml --part_name xc7z010clg400-1 --frm_file attosoc.frames --output_file attosoc.bit

