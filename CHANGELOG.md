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

