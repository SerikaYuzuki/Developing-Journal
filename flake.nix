{
  description = "Flake using official Quarto package";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-darwin" ] (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          name = "quarto-env";

          buildInputs = [
            pkgs.quarto
            pkgs.texliveFull
            pkgs.deno
            pkgs.pandoc
            pkgs.git
            pkgs.python312
            pkgs.python312Packages.numpy
            pkgs.python312Packages.pandas
            pkgs.python312Packages.matplotlib
            pkgs.python312Packages.jupyter
            pkgs.python312Packages.rdkit
            pkgs.python312Packages.scipy
            pkgs.python312Packages.plotly
          ];

          shellHook = ''
            echo "✅ Official Quarto package is ready!"
            echo "🔧 Version: $(quarto --version)"
          '';
        };
      });
}