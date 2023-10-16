#!/bin/bash
 python3 analise.py -r ca44ff5eccbd5b05b6ade6314784595b -f ./valid_codes
 python3 analise.py -r ca44ff5eccbd5b05b6ade6314784595b -f ./invalid_codes
 python3 analise.py -a ./ref_code -f ./valid_codes
 python3 analise.py -a ./ref_code -f ./invalid_codes

 python3 analise.py -a ./ref_code -f ./valid_codes --hash=sha256
 python3 analise.py -a ./ref_code -f ./invalid_codes --hash=sha256