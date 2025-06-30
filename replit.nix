{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.python311Packages.discordpy
    pkgs.python311Packages.flask
    pkgs.python311Packages.openai
    pkgs.ffmpeg
  ];
}