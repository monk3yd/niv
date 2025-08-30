{
  inputs = {
    # nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    devenv.url = "github:cachix/devenv";
  };

  outputs =
    {
      self,
      nixpkgs,
      devenv,
      ...
    }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
        };
        overlays = [ ];
      };

      # Define you Python application as a Nix package
      niv-package = pkgs.python312.pkgs.buildPythonApplication {
        pname = "niv";
        version = "0.1.0";

        # The source code for the package is the current directory
        src = self;

        # Add the build too
        nativeBuildInputs = with pkgs.python312.pkgs; [
          # hatch-vcs
          build
          hatchling
        ];

        # Tell Nix which Python dependencies are required to run the application
        propagatedBuildInputs = with pkgs.python312.pkgs; [
          typer
          pandas
          polars
          openpyxl
          xlsxwriter
        ];

        # Explicitly build the wheel into a 'dist' directory.
        buildPhase = ''
          runHook preBuild
          python -m build --no-isolation --wheel --outdir dist .
          runHook postBuild
        '';

        # Specify the build format (pyproject.toml is standard)
        format = "pyproject";

        # This ensures that tests are not run during the Nix build,
        # which is often desirable for simplicity.
        doCheck = false;

      };
    in
    {
      # Expose the package to other flakes
      # Another flake can now depend on this and access 'niv.packages.x86_64-linux.default'
      packages.${system}.default = niv-package;

      # nix build .#container
      # ls -lah result
      # docker load < $result
      # docker run container-image
      # packages.${system}.container = pkgs.dockerTools.buildLayeredImage {
      #   name = "container-image";
      #   tag = "latest";
      #   contents = [ pkgs.hello ];
      #   config.Cmd = [ "hello" ];
      # };

      devShell.x86_64-linux = devenv.lib.mkShell {
        inherit inputs pkgs;

        modules = [
          (
            { pkgs, lib, ... }:
            {
              # NOTE: devenv configuration goes here

              # https://devenv.sh/supported-languages/nix/
              languages.nix.enable = true;
              languages.nix.lsp.package = pkgs.nil;

              # https://devenv.sh/supported-languages/python/
              languages.python = {
                enable = true;
                package = pkgs.python312;
                manylinux.enable = true;
                uv = {
                  enable = true;
                  package = pkgs.uv;
                  sync.enable = true;
                };
              };

              # https://devenv.sh/supported-languages/terraform/#languagesterraformenable
              # languages.terraform.enable = true;

              packages = with pkgs; [
                python312Packages.isort
                python312Packages.black
                python312Packages.ruff
                python312Packages.reuse
                niv-package
              ];

              # env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
              #   pkgs.stdenv.cc.cc
              #   pkgs.zlib
              #   pkgs.glib
              #   pkgs.libuv
              #   pkgs.xorg.libX11
              #   pkgs.xorg.libXcomposite
              #   pkgs.xorg.libXdamage
              #   pkgs.xorg.libXext
              #   pkgs.xorg.libXfixes
              #   pkgs.xorg.libXrandr
              #   pkgs.alsa-lib
              #   pkgs.nspr
              #   pkgs.nss
              #   pkgs.cups
              #   pkgs.dbus
              #   pkgs.expat
              #   pkgs.atk
              #   pkgs.at-spi2-atk
              #   pkgs.cairo
              #   pkgs.pango
              #   pkgs.gtk3
              # ];

              enterShell = ''
                # unset PYTHONPATH

                export UV_LINK_MODE=copy
                export UV_NO_SYNC=1
                export UV_PYTHON_DOWNLOADS=never
                export UV_PYTHON_PREFERENCE=system
                export REPO_ROOT=$(git rev-parse --show-toplevel)

                . .devenv/state/venv/bin/activate
              '';

            }
          )
        ];
      };
    };
}
