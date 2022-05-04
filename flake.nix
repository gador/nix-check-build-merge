{
  description = "nix-check-merge flake";

  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";

  inputs.flake-utils = {
    url = "github:numtide/flake-utils";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        venvDir = "./.venv";
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python3.withPackages (ps:
          with ps; [
            flask
            build
            click
            sphinx
            
            #test and formatting
            pytest
            pytest-cov
            pytest-mock
            vulture
            isort
            flake8
            mypy
            vulture
          ]);
        pre-commit = pkgs.writeScriptBin "pre-commit" ''
          #!${pkgs.runtimeShell}
          echo "Sorting imports"
          isort src/nix_cbm
          echo "Formatting"
          black src/nix_cbm/* -l 90
        '';
        devEnv = pkgs.mkShell {
          inherit venvDir;
          packages = [
            pythonEnv

            pkgs.black
            pkgs.mypy
            pkgs.git
            pkgs.ripgrep
            pre-commit
          ];
          shellHook = ''
            # make the locally developed package generally available
            export PYTHONPATH="${
              ./src
            }:$PYTHONPATH"

            # setup local venv dir for IDEs
            if [ -d "${venvDir}" ]; then
                echo "Skipping venv creation, '${venvDir}' already exists"
            else
                echo "Creating new venv environment in path: '${venvDir}'"
            python -m venv "${venvDir}"
            fi
            ln -sf ${pythonEnv}/lib/python3.9/site-packages/* ${venvDir}/lib/python3.9/site-packages
            source "${venvDir}/bin/activate"
          '';
        };
        package = pkgs.python3Packages.buildPythonApplication rec {
          pname = "nix-check-build-merge";
          version = "0.0.2";
          src = ./.;

          propagatedBuildInputs = with pkgs.python3Packages; [
            flask
            build
            click
            pkgs.git
          ];
          checkInputs = with pkgs.python3Packages; [ pytestCheckHook ];
        };
      in rec {
        packages.default = package;
        devShells.default = devEnv;
        checks = {
          format = pkgs.runCommand "format" {
            buildInputs = with pkgs; [
              black
              python3Packages.flake8
              python3Packages.vulture
            ];
          } ''
            mkdir $out
            black ${./src} --check --diff --color -l 90
            flake8 --config ${./setup.cfg} ${./src}
            vulture ${./src} 
          '';
          pytest = pkgs.runCommand "pytest" {
            buildInputs = with pkgs.python3Packages; [
              pytest
              pytest-mock
              pytest-cov
              pytest-xdist
              click
              flask
            ];
          } ''
            mkdir $out
            # this adds the package to sys.path of python
            # so pytest can find and import it
            export PYTHONPATH="${./src}:$PYTHONPATH"
            # don't use cache dir, since it is read only with nix
            python -m pytest ${
              ./.
            } -p no:cacheprovider -n auto --cov nix_cbm --cov-report term-missing
          '';
        };
      });
}
