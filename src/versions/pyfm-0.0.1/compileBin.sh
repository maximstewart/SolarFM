#!/bin/bash

function main() {
    gcc -no-pie -s PyFM_exec_bin.cpp -o pyfm
}
main;
