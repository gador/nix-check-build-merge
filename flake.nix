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
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [ flask build ]);
        pythonCheckEnv = pkgs.python3.withPackages (ps:
          with ps; [
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
          isort .
          echo "Formatting"
          black .
        '';
        devEnv = pkgs.mkShell {
          packages = [
            pythonEnv
            pythonCheckEnv

            pkgs.black
            pkgs.mypy
            pre-commit
          ];
          shellHook = "";
        };
        package = pkgs.python3Packages.buildPythonApplication rec {
          pname = "nix-check-build-merge";
          version = "0.0.1";
          src = ./.;

          propagatedBuildInputs = with pkgs.python3Packages; [ flask build ];

          checkInputs = with pkgs.python3Packages; [ pytestCheckHook ];
        };
      in rec {
        packages.default = package;
        devShells.default = devEnv;
        checks = {
          format = pkgs.runCommand "name" {
            buildInputs = with pkgs; [
              black
              python3Packages.flake8
              python3Packages.vulture
            ];
          } ''
            mkdir $out
            black . --check
            flake8
            vulture .
          '';
          pytest = pkgs.runCommand "name" {
            buildInputs = with pkgs.python3Packages; [ pytest pytest-mock ];
          } ''
            mkdir $out
            # add later
            # pytest
          '';
        };
      });
}
