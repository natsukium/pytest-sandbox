{
  description = "pytest-sandbox";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    treefmt-nix.url = "github:numtide/treefmt-nix";
    dream2nix.url = "github:nix-community/dream2nix";
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
          packages = {
            default = config.packages.pytest-sandbox;
            pytest-sandbox = inputs.dream2nix.lib.evalModules {
              packageSets.nixpkgs = pkgs;
              modules = [
                {

                  imports = [ inputs.dream2nix.modules.dream2nix.WIP-python-pdm ];

                  deps =
                    { nixpkgs, ... }:
                    {
                      python = nixpkgs.python3;
                    };

                  mkDerivation =
                    let
                      inherit (pkgs) lib;
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
                    };

                  pdm = {
                    lockfile = ./pdm.lock;
                    pyproject = ./pyproject.toml;
                  };

                  buildPythonPackage = {
                    pyproject = true;
                    format = null;
                    build-system = [ pkgs.python3Packages.pdm-backend ];
                    pythonImportsCheck = [ "pytest_sandbox" ];
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
            };
          };

          pre-commit = {
            check.enable = true;
            settings = {
              src = ./.;
              hooks = {
                ruff.enable = true;
                pyright = {
                  enable = true;
                  package = pkgs.basedpyright;
                  entry = "${pkgs.lib.getExe pkgs.basedpyright}";
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
              packages =
                [
                  config.pre-commit.settings.enabledPackages
                  config.pre-commit.settings.package
                  config.treefmt.build.wrapper
                  config.packages.default
                ]
                ++ map (x: (pkgs.lib.head (pkgs.lib.attrValues x)).public) (
                  pkgs.lib.attrValues config.packages.pytest-sandbox.config.groups.testing.packages
                );
              shellHook =
                config.pre-commit.installationScript
                + ''
                  export PYTHONPATH=./src:$PYTHONPATH
                '';
            };
          };
        };
    };
}
