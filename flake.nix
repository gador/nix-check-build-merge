{
  description = "nix-check-merge flake";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: [
          ps.flask
        ]);
        devEnv = pkgs.mkShell {
          packages = [
            pythonEnv

            pkgs.black
          ];
          shellHook = "";
        };
      in rec {
        defaultPackage = devEnv;
        devShell = devEnv;
      });
}
