{ maintainer }:
# taken from nixpkgs maintainer/scripts
with (import <nixpkgs> {});
let
  maintainer_ = pkgs.lib.maintainers.${maintainer};
  packagesWith = cond: return: prefix: set:
    (pkgs.lib.flatten
      (pkgs.lib.mapAttrsToList
        (name: pkg:
          let
            result = builtins.tryEval
              (
                if pkgs.lib.isDerivation pkg && cond name pkg then
                # Skip packages whose closure fails on evaluation.
                # This happens for pkgs like `python27Packages.djangoql`
                # that have disabled Python pkgs as dependencies.
                  builtins.seq pkg.outPath
                    [ (return "${prefix}${name}") ]
                else if pkg.recurseForDerivations or false || pkg.recurseForRelease or false
                # then packagesWith cond return pkg
                then packagesWith cond return "${name}." pkg
                else [ ]
              );
          in
          if result.success then result.value
          else [ ]
        )
        set
      )
    );

  packages = packagesWith
    (name: pkg:
      (
        if builtins.hasAttr "meta" pkg && builtins.hasAttr "maintainers" pkg.meta
        then
          (
            if builtins.isList pkg.meta.maintainers
            then builtins.elem maintainer_ pkg.meta.maintainers
            else maintainer_ == pkg.meta.maintainers
          )
        else false
      )
    )
    (name: name)
    ("")
    pkgs;

in
pkgs.stdenv.mkDerivation {
  name = "nixpkgs-update-script";
  buildInputs = [ pkgs.hydra-check ];
  buildCommand = ''
    exit 1 # don't use as build command
  '';
  shellHook = ''
    unset shellHook # do not contaminate nested shells
    echo "${builtins.concatStringsSep "," packages}"
    exit $?
  '';
}
