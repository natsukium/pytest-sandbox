{
  description = "pytest-sandbox";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    dream2nix = {
      url = "github:nix-community/dream2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-parts.url = "github:hercules-ci/flake-parts";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.nixpkgs-stable.follows = "nixpkgs";
    };
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.git-hooks.flakeModule
        inputs.treefmt-nix.flakeModule
      ];

      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem =
        { config, pkgs, ... }:
        {
          packages =
            let
              pytest-sandbox-with = pkgs.lib.makeOverridable (
                {
                  python ? "python311",
                  doCheck ? false,
                }:
                inputs.dream2nix.lib.evalModules {
                  packageSets.nixpkgs = pkgs;
                  modules = [
                    {

                      imports = [ inputs.dream2nix.modules.dream2nix.WIP-python-pdm ];

                      deps =
                        { nixpkgs, ... }:
                        {
                          python = nixpkgs."${python}";
                        };

                      mkDerivation =
                        let
                          inherit (pkgs) lib;
                          inherit (config.packages.pytest-sandbox.config.deps) python;
                        in
                        {
                          src = lib.cleanSourceWith {
                            src = lib.cleanSource ./.;
                            filter =
                              name: type:
                              !(builtins.any (x: x) [
                                (lib.hasSuffix ".nix" name)
                                (lib.hasPrefix "." (builtins.baseNameOf name))
                                (lib.hasSuffix "flake.lock" name)
                              ]);
                          };
                          inherit doCheck;
                          nativeCheckInputs =
                            [ python.pkgs.pytestCheckHook ]
                            ++ map (x: (pkgs.lib.head (pkgs.lib.attrValues x)).public) (
                              pkgs.lib.attrValues config.packages.pytest-sandbox.config.groups.testing.packages
                            );
                        };

                      pdm = {
                        lockfile = ./pdm.lock;
                        pyproject = ./pyproject.toml;
                      };

                      buildPythonPackage =
                        let
                          inherit (config.packages.pytest-sandbox.config.deps) python;
                        in
                        {
                          pyproject = true;
                          format = null;
                          build-system = [ python.pkgs.pdm-backend ];
                          pythonImportsCheck = [ "pytest_sandbox" ];
                          pytestFlagsArray = [ "-m 'not network'" ];
                        };
                    }
                    {
                      paths = {
                        projectRoot = ./.;
                        projectRootFile = "flake.nix";
                        package = ./.;
                      };
                    }
                  ];
                }
              );
            in
            {
              default = config.packages.pytest-sandbox;
              pytest-sandbox = pytest-sandbox-with { };
              pytest-sandbox-39 = pytest-sandbox-with { python = "python39"; };
              pytest-sandbox-310 = pytest-sandbox-with { python = "python310"; };
              pytest-sandbox-311 = pytest-sandbox-with { python = "python311"; };
              pytest-sandbox-312 = pytest-sandbox-with { python = "python312"; };
            };

          checks = {
            python39 = config.packages.pytest-sandbox-39.override { doCheck = true; };
            python310 = config.packages.pytest-sandbox-310.override { doCheck = true; };
            python311 = config.packages.pytest-sandbox-311.override { doCheck = true; };
            python312 = config.packages.pytest-sandbox-312.override { doCheck = true; };
          };

          pre-commit = {
            check.enable = true;
            settings = {
              src = ./.;
              hooks = {
                ruff.enable = true;
                pyright =
                  let
                    pyEnv = pkgs.python3.withPackages (
                      _:
                      map (x: (pkgs.lib.head (pkgs.lib.attrValues x)).public) (
                        pkgs.lib.attrValues config.packages.pytest-sandbox.config.groups.default.packages
                      )
                      ++ map (x: (pkgs.lib.head (pkgs.lib.attrValues x)).public) (
                        pkgs.lib.attrValues config.packages.pytest-sandbox.config.groups.testing.packages
                      )
                    );
                    wrapped-pyright = pkgs.runCommand "pyright" { nativeBuildInputs = [ pkgs.makeWrapper ]; } ''
                      makeWrapper ${pkgs.lib.getExe pkgs.basedpyright} $out/bin/pyright \
                        --set PYTHONPATH ${pyEnv}/${pyEnv.sitePackages}
                    '';
                  in
                  {
                    enable = true;
                    package = wrapped-pyright;
                  };

                typos.enable = true;

                markdownlint.enable = true;

                actionlint.enable = true;

                treefmt.enable = true;
              };
            };
          };

          treefmt = {
            projectRootFile = "pyproject.toml";
            programs = {
              ruff.format = true;
              nixfmt-rfc-style.enable = true;
              taplo.enable = true;
              yamlfmt.enable = true;
            };
          };

          devShells = {
            default = pkgs.mkShell {
              inputsFrom = [ config.packages.pytest-sandbox.devShell ];
              packages = [
                config.pre-commit.settings.enabledPackages
                config.pre-commit.settings.package
                config.treefmt.build.wrapper
                config.packages.pytest-sandbox
                pkgs.python311Packages.editables
                pkgs.commitizen
              ];
              shellHook = config.pre-commit.installationScript;
            };
          };
        };
    };
}
