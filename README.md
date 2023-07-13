# SysPlant
#### "Your Syscall Factory" *(feat. Canterlot's Gate)*

![Canterlot's Gate](docs/assets/canterlot.jpeg)

SysPlant is a small implementation in NIM of the currently known syscall hooking methods. It currently supports following gates:
- [Hell's Gate](https://github.com/am0nsec/HellsGate) : Lookup syscall by first opcodes
- [Halos's Gate](https://blog.sektor7.net/#!res/2021/halosgate.md) : Lookup syscall by first opcodes and search nearby if first instruction is a JMP
- [Tartarus' Gate](https://github.com/trickster0/TartarusGate) : Lookup syscall by first opcodes and search nearby if first or third instruction is a JMP
- [FreshyCalls](https://github.com/crummie5/FreshyCalls) : Lookup syscall by name (start with Nt and not Ntdll), sort addresses to retrieve syscall number
- [SysWhispers2](https://github.com/jthuraisamy/SysWhispers2) : Lookup syscall by name (start with Zw), sort addresses to retrieve syscall number
- **Canterlot's Gate ! :unicorn: :rainbow:** *(from an initial idea of [MDSEC article](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/)) but who was missing a pony name* : Lookup syscall using Runtime Exception Table (sorted by syscall number) and detect padding to syscall instruction for random jumps.
- **Custom** Allows you to choose a generation method, a syscall resolver (basic / random) and a syscall stub (direct / indirect). **Careful: some combinations means nothing so it won't work (eg: freshy iterator + random resolver + indirect stub => as Freshy return back the syscall stub entry address, your syscall number will be rewrite by a random one)**  

*Note: You can also generate your own combinations using the proper options... But be careful some options might not work or even make sense*

> :warning: **DISCLAIMER**
> Please only use this tool on systems you have permission to access.
> Usage is restricted to Pentesting or Education only.
> All credits are based on my own research, please feel free to claim any method if I made mistakes...

## Introduction
This personal project aims to be a simple tool to better understand & generate different syscall retrieval methods, and being able to play with direct / indirect syscall stub. The first goal was to get my hands into NIM and then it overflow :wink: ...  
SysPlant has been developped for Linux users, some stuff might be broken within Windows or Mac. PR are welcome if you found anything that does not work as expected.

## Installation
This is a python project that will generate NIM source code (bit weird hu ?! :grin:). So you can use it inside your python project as an external module or directly on your device as a tool.

### As a Python module
If you are using standard pip3 package manager
```sh
pip3 install sysplant
```

If you are more inclined to use virtual environments *(you should!)* this project is based on [Poetry](https://python-poetry.org/) virtual env.
```sh
poetry add sysplant
```

### As a single tool
Install the project as you would do for any GitHub project
```sh
git clone https://github.com/x42en/sysplant && cd sysplant
poetry shell
poetry install
./main.py -h
```

## Help
This tool comes with various options that should be self-explanatory using the standard `-h` flag
```bash
$ ./main.py -h
usage: main.py [-h] [-x86 | -x64] [--debug | --verbose | --quiet] [-p {all,donut,common} | -f FUNCTIONS] [-x] -o OUTPUT {hell,halo,tartarus,freshy,syswhispers,canterlot,custom} ...

..:: SysPlant - Your Syscall Factory ::..

positional arguments:
  {hell,halo,tartarus,freshy,syswhispers,canterlot,custom}

optional arguments:
  -h, --help            show this help message and exit
  -x, --scramble        Randomize internal function names to evade static analysis
  -o OUTPUT, --output OUTPUT
                        Output path for NIM generated file

Output options:
  -x86                  Set mode to 32bits
  -x64                  Set mode to 64bits (Default True)

Output options:
  --debug               Display all DEBUG messages upon execution
  --verbose             Display all INFO messages upon execution
  --quiet               Remove all messages upon execution

Syscall options:
  -p {all,donut,common}, --preset {all,donut,common}
                        Preset functions to generate (Default: common)
  -f FUNCTIONS, --functions FUNCTIONS
                        Comma-separated functions
```

If you choose the `custom` generation some options apply
```bash
$ ./main.py custom -h
usage: main.py custom [-h] [-i {hell,halo,tartarus,freshy,syswhispers,canterlot}] [-r {basic,random}] [-s {direct,indirect}]

optional arguments:
  -h, --help            show this help message and exit
  -i {hell,halo,tartarus,freshy,syswhispers,canterlot}, --iterator {hell,halo,tartarus,freshy,syswhispers,canterlot}
                        Select syscall iterator (Default: canterlot)
  -r {basic,random}, --resolver {basic,random}
                        Select syscall resolver (Default: basic)
  -s {direct,indirect}, --stub {direct,indirect}
                        Select syscall stub (Default: indirect)
```

## Usage
Here are some usage examples that will generate common NtFunctions only. This tool is not restricted to them, please **[READ THE DOC](https://x42en.github.io/sysplant/)**

#### Hell's Gate generation
```bash
$ ./main.py -o syscall.nim hell
```

#### Halo's Gate generation
```bash
$ ./main.py -o syscall.nim halo
```

#### Tartarus's Gate generation
```bash
$ ./main.py -o syscall.nim tartarus
```

#### FreshyCall generation
```bash
$ ./main.py -o syscall.nim freshy
```

#### Syswhispers2 like generation
```bash
$ ./main.py -o syscall.nim syswhispers
```

#### Canterlot's Gate generation
```bash
$ ./main.py -o syscall.nim canterlot
```

#### Custom generation
```bash
$ ./main.py -o syscall.nim custom -i canterlot -r random -s indirect
```

## Example
A simple example (launching calc.exe) is accessible using `inject.nim`.  
1. Be sure to install [winim](https://github.com/khchen/winim) library first: `nimble install winim`
2. Generate the `syscall.nim` file with `./main.py -o example/syscall.nim canterlot`
3. Compile the injection template file with `nim c -d=release -d=danger -d=strip --opt=size -d=mingw --app=console --cpu=amd64 --out=app.exe example/inject.nim` on Linux (be sure to have mingw installed)
4. Copy the `app.exe` generated on your Windows device.

Happy Hacking :beach: !

## Credits
Massive shout-out to these useful projects that helps me during this journey, or individuals for their reviews
- [@alice blogpost about syscalls techniques](https://alice.climent-pommeret.red/posts/direct-syscalls-hells-halos-syswhispers2/)
- [@redops blogpost about direct vs indirect syscalls](https://redops.at/en/blog/direct-syscalls-a-journey-from-high-to-low)
- [@Jackson_T & @modexpblog for Syswhispers2](https://github.com/jthuraisamy/SysWhispers2)
- [@klezvirus for syswhispers3](https://github.com/klezVirus/SysWhispers3)

## :construction: TODO
This project is really in WIP state...  
Some PR & reviews are more than welcome :tada: !
- [x] Add internal names randomization
- [ ] Add x86 support
- [ ] Add WoW64 support
- [-] Add some tests
- [x] Setup documentation

## License
This project is licensed under the [MIT License](https://www.tldrlegal.com/license/mit-license), for individuals only. If you want to integrate this work in your commercial project please contact me through `0x42en[at]gmail.com`