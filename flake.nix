{
  description = "nix-check-merge flake";

  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";

  inputs.flake-utils = {
    url = "github:numtide/flake-utils";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils }:
    # cannot use eachDefaultSystem due to pyopenssl being broken
    # on darwin and aarch64. see https://github.com/pyca/pyopenssl/issues/873
    flake-utils.lib.eachSystem [ flake-utils.lib.system.x86_64-linux ] (system:
      let
        venvDir = "./.venv";
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python310.withPackages (ps:
          with ps; [
            supervisor
            gunicorn
            flask
            flask_sqlalchemy
            flask_migrate
            build
            click
            sphinx
            rq
            redis
            pathvalidate

            #test and formatting
            pytest
            pytest-cov
            pytest-mock
            vulture
            isort
            flake8
            mypy
            vulture
            hypothesis
            fakeredis
          ]);
        pre-commit = pkgs.writeScriptBin "pre-commit" ''
          #!${pkgs.runtimeShell}
          echo "Sorting imports"
          isort src/nix_cbm
          isort tests
          echo "Formatting"
          black src/nix_cbm/* -l 90
          black tests/* -l 90
        '';
        devEnv = pkgs.mkShell {
          inherit venvDir;
          packages = [
            pythonEnv

            pkgs.sqlite-utils
            pkgs.black
            pkgs.mypy
            pkgs.git
            pkgs.ripgrep
            pkgs.hydra-check
            pkgs.redis
            pre-commit
          ];
          shellHook = ''
            # make the locally developed package generally available
            export PYTHONPATH="./src:$PYTHONPATH"

            # setup local venv dir for IDEs
            if [ -d "${venvDir}" ]; then
                echo "Skipping venv creation, '${venvDir}' already exists"
            else
                echo "Creating new venv environment in path: '${venvDir}'"
            python -m venv "${venvDir}"
            fi
            ln -sf ${pythonEnv}/lib/python3.10/site-packages/* ${venvDir}/lib/python3.10/site-packages
            source "${venvDir}/bin/activate"
          '';
        };
        package = pkgs.python310Packages.buildPythonApplication rec {
          pname = "nix-check-build-merge";
          version = "0.3.1";
          src = ./.;

          propagatedBuildInputs = with pkgs.python310Packages; [
            supervisor
            gunicorn
            flask
            flask_sqlalchemy
            flask_migrate
            build
            click
            rq
            redis
            pkgs.git
            pkgs.hydra-check
            pkgs.redis
            pathvalidate

            # support programs
            pkgs.git
            pkgs.ripgrep
            pkgs.hydra-check

          ];
          patches = [
            (pkgs.substituteAll {
              src = ./supervisord.patch;
              gunicorn = "${pkgs.python310Packages.gunicorn}/bin/gunicorn";
              redis = "${pkgs.redis}/bin/redis-server";
            })
            (pkgs.substituteAll {
              src = ./nixcbm_start.patch;
              bash = "${pkgs.bash}";
              supervisord = "${pkgs.python310Packages.supervisor}/bin/supervisord";
            })
          ];
          preCheck = ''
            export HOME=$TMPDIR
            # make sure the version is correct (important when building from source and not from package)
            [ $(cat VERSION) = ${version} ]  || exit 1
          '';
          checkInputs = with pkgs.python310Packages; [
            pytestCheckHook
            hypothesis
            fakeredis

            # we test for these tools, so they need to be present
            pkgs.ripgrep
            pkgs.git
            pkgs.hydra-check
            pkgs.nix
          ];
          postInstall = ''
            substituteInPlace supervisord.conf --replace "nixcbm worker" "$out/bin/nixcbm worker"
            install -Dm 0644 supervisord.conf $out/etc/supervisord.conf
            substituteInPlace nixcbm_start.sh --replace "supervisord.conf" "$out/etc/supervisord.conf"
            install -Dm 0755 nixcbm_start.sh $out/bin/nixxcbm_start 
          '';

          meta = with pkgs.lib; {
            description = "Allows you to check for build failures all the nixpkgs you maintain";
            homepage = "https://github.com/gador/nix-check-build-merge";
            license = licenses.mit;
            maintainers = with maintainers; [ gador ];
            mainProgram = "nixcbm_start";
          };
        };
      in
      rec {
        packages.default = package;
        apps.default = {
          type = "app";
          program = "${package}/bin/nixcbm_start";
        };
        devShells.default = devEnv;
        # use nix flake check -L to print more test info
        checks = {
          format = pkgs.runCommand "format"
            {
              buildInputs = with pkgs; [
                black
                python310Packages.flake8
                python310Packages.vulture
              ];
            } ''
            mkdir $out
            black ${./.}/src --check --diff --color -l 90
            flake8 --config ${./.}/setup.cfg ${./.}/src
            # need to exclude automatic generated files
            vulture --min-confidence 70 --ignore-names "revision" ${./.}/src
          '';
          pytest = pkgs.runCommand "pytest"
            {
              buildInputs = with pkgs.python310Packages; [
                pytest
                pytest-mock
                pytest-cov
                pytest-xdist
                click
                flask
                flask_sqlalchemy
                flask_migrate
                hypothesis
                redis
                rq
                coveralls
                pathvalidate
                fakeredis

                # we test for these tools, so they need to be present
                pkgs.ripgrep
                pkgs.git
                pkgs.hydra-check
                pkgs.nix
              ];
            } ''
            mkdir $out
            # this adds the package to sys.path of python
            # so pytest can find and import it
            export PYTHONPATH="${./.}/src:$PYTHONPATH"
            # need a home for db file
            export HOME=$TMPDIR
            # don't use cache dir, since it is read only with nix
            python -m pytest ${./.} -p no:cacheprovider --cov nix_cbm --cov-report term-missing --cov-config=${./.}/.coveragerc
            cp -v .coverage $out/.coverage
            echo ${./.}/src > $out/srcpath
          '';
          mypy = pkgs.runCommand "mypy"
            {
              buildInputs = with pkgs.python310Packages; [
                mypy
                flask
                click
                flask_sqlalchemy
                flask_migrate
              ];
            } ''
            mkdir $out
            mypy --config-file ${./.}/setup.cfg ${./.}/src
          '';
        };
      });
}
