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
        pythonEnv = pkgs.python3.withPackages (ps:
          with ps; [
            flask
            pytest
            pytest-cov
            pytest-mock
            vulture
            isort
            flake8
          ]);
          pre-commit = pkgs.writeScriptBin "pre-commit"
          ''
          #!${pkgs.runtimeShell} 
          echo "Sorting imports"
          isort .
          echo "Formatting"
          black .
        '';
        devEnv = pkgs.mkShell {
          packages = [
            pythonEnv

            pkgs.black
            pkgs.mypy
            pre-commit
          ];
          shellHook = "";
        };
      in rec {
        packages.default = devEnv;
        devShells.default = devEnv;
        checks = {
          black =
            pkgs.runCommand "black" { buildInputs = with pkgs; [ black ]; } ''
              mkdir $out
              black . --check
            '';
        };
      });
}
