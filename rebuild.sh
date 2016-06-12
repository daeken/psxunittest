#!/bin/sh

python beetlegen.py
cp cputest.cpp ../beetle-psx-libretro/mednafen/psx/cputest.cpp
cp cputest.cpp ../interp/beetle-psx-libretro/mednafen/psx/cputest.cpp

echo
echo

CUR=`pwd`
cd ../beetle-psx-libretro/
rm mednafen/psx/cpu-interpreter.o mednafen/psx/cpu-recompiler.o
RUN_TESTS=1 make >/dev/null
perl -pi -e 's/dynarec/interpreter/g' ~/Library/Application\ Support/RetroArch/config/retroarch-core-options.cfg
cp ~/Library/Application\ Support/RetroArch/config/retroarch-core-options.cfg test1.txt
echo 'Testing new interpreter'
./run ~/roms/sotn.cue 2>/dev/null
echo

perl -pi -e 's/interpreter/dynarec/g' ~/Library/Application\ Support/RetroArch/config/retroarch-core-options.cfg
cp ~/Library/Application\ Support/RetroArch/config/retroarch-core-options.cfg test2.txt
echo 'Testing dynarec'
./run ~/roms/sotn.cue 2>/dev/null
echo
cd $CUR

echo 'Testing original interpreter:'
CUR=`pwd`
cd ../interp/beetle-psx-libretro/
rm mednafen/psx/cpu.o
RUN_TESTS=1 make >/dev/null
./run ~/roms/sotn.cue 2>/dev/null
cd $CUR
