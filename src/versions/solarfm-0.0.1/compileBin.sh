#!/bin/bash

function main() {
    gcc -no-pie -s SolarFM_exec_bin.cpp -o solarfm
}
main;
