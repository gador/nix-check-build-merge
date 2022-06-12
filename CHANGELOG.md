#### [Version 0.3.1](https://gador/nix-check-build-merge/releases/tag/0.3.1) 
### Other Changes 
- minor cleanup, add frontend choice for architecture [#60](https://gador/nix-check-build-merge/issues/#60) ([@gador](https://github.com/@gador))
- add functionality to arch select in frontend [#61](https://gador/nix-check-build-merge/issues/#61) ([@gador](https://github.com/@gador))
- improve frontend navigation [#62](https://gador/nix-check-build-merge/issues/#62) ([@gador](https://github.com/@gador))
- refactor preflight and init_app [#63](https://gador/nix-check-build-merge/issues/#63) ([@gador](https://github.com/@gador))
- update flake.lock [#64](https://gador/nix-check-build-merge/issues/#64) ([@gador](https://github.com/@gador))
- single source for VERSION tag [#65](https://gador/nix-check-build-merge/issues/#65) ([@gador](https://github.com/@gador))
 
 #### [Version 0.3.0](https://gador/nix-check-build-merge/releases/tag/0.3.0) 
### Implemented Enhancements 
- Add asynchronous  frontend [#56](https://gador/nix-check-build-merge/issues/#56) ([@gador](https://github.com/@gador))
### Other Changes 
- improve nixpkgs test routine [#53](https://gador/nix-check-build-merge/issues/#53) ([@gador](https://github.com/@gador))
- add a second preflight test [#54](https://gador/nix-check-build-merge/issues/#54) ([@gador](https://github.com/@gador))
- [supervisord] run nixcbm from dev directory when developing [#55](https://gador/nix-check-build-merge/issues/#55) ([@gador](https://github.com/@gador))
- Version bump to Release 0.3 [#57](https://gador/nix-check-build-merge/issues/#57) ([@gador](https://github.com/@gador))
- put build CI workflow in a sperate file [#58](https://gador/nix-check-build-merge/issues/#58) ([@gador](https://github.com/@gador))
 
 #### [Version 0.2.1](https://gador/nix-check-build-merge/releases/tag/0.2.1) 
### Fixed Bugs 
- load settings from db [#39](https://gador/nix-check-build-merge/issues/#39) ([@gador](https://github.com/@gador))
- clean Package list after change of maintainer [#40](https://gador/nix-check-build-merge/issues/#40) ([@gador](https://github.com/@gador))
- check for current database before calling it [#44](https://gador/nix-check-build-merge/issues/#44) ([@gador](https://github.com/@gador))
- bugfix: save nixpkgs to db [#45](https://gador/nix-check-build-merge/issues/#45) ([@gador](https://github.com/@gador))
- normalize path before returning path [#46](https://gador/nix-check-build-merge/issues/#46) ([@gador](https://github.com/@gador))
- ensure nixpkgs path is local to the user [#50](https://gador/nix-check-build-merge/issues/#50) ([@gador](https://github.com/@gador))
### Other Changes 
- fix small errors in README [#36](https://gador/nix-check-build-merge/issues/#36) ([@gador](https://github.com/@gador))
- save persistent config in sqlite database [#37](https://gador/nix-check-build-merge/issues/#37) ([@gador](https://github.com/@gador))
- Add settings page to frontend [#38](https://gador/nix-check-build-merge/issues/#38) ([@gador](https://github.com/@gador))
- Add coveralls and readme badge [#41](https://gador/nix-check-build-merge/issues/#41) ([@gador](https://github.com/@gador))
- unify nix store path in flake.nix [#42](https://gador/nix-check-build-merge/issues/#42) ([@gador](https://github.com/@gador))
- change src path for dev environment [#43](https://gador/nix-check-build-merge/issues/#43) ([@gador](https://github.com/@gador))
- ci(Mergify): configuration update [#47](https://gador/nix-check-build-merge/issues/#47) ([@gador](https://github.com/@gador))
- check path first before commiting [#48](https://gador/nix-check-build-merge/issues/#48) ([@gador](https://github.com/@gador))
- update path testing [#49](https://gador/nix-check-build-merge/issues/#49) ([@gador](https://github.com/@gador))
- use fullpath [#51](https://gador/nix-check-build-merge/issues/#51) ([@gador](https://github.com/@gador))
 
 #### [Version 0.2.0](https://gador/nix-check-build-merge/releases/tag/0.2.0) 
### Implemented Enhancements 
- Add option to check different architectures [#34](https://gador/nix-check-build-merge/issues/#34) ([@gador](https://github.com/@gador))
### Fixed Bugs 
- bugfix: move to batch mode for sqlite [#31](https://gador/nix-check-build-merge/issues/#31) ([@gador](https://github.com/@gador))
- upgrade db model to include arch and allow same package names  [#32](https://gador/nix-check-build-merge/issues/#32) ([@gador](https://github.com/@gador))
### Other Changes 
- add Config variables for architecture to check [#33](https://gador/nix-check-build-merge/issues/#33) ([@gador](https://github.com/@gador))
 
 #### [Version 0.1.1](https://gador/nix-check-build-merge/releases/tag/0.1.1) 
### Fixed Bugs 
- Add frontend tests and prepare listing for different architectures [#29](https://gador/nix-check-build-merge/issues/#29) ([@gador](https://github.com/@gador))
 
 #### [Version 0.1.0](https://gador/nix-check-build-merge/releases/tag/0.1.0) 
### Implemented Enhancements 
- Add second page to selectively display failed builds [#27](https://gador/nix-check-build-merge/issues/#27) ([@gador](https://github.com/@gador))
 
 # Changelog

## 0.0.5
- add redis
- add hypothesis testing

## 0.0.4
- flake.lock update
- added supervisor config
- added gunicorn
- added start script  (runs supervisor and gunicorn)

## 0.0.3
- added a lot more unittests
- added static type check with mypy
- added initial sphinx documentation
- added app output to flake
- reworked .venv development environment
- made table prettier
- reworked git logic (use worktree now)
- updated to Python3.10
- save package list to database
- seperate hydra-check and package by maintainer listing

## 0.0.2 
- list packages maintained by maintainer
- first CLI options

## 0.0.1
- initial version without any functionality
- python and nix skeletal project system

