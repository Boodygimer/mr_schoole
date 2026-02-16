{ pkgs, ... }: {
  channel = "stable-24.05";
  packages = [
    pkgs.python3
    pkgs.python3Packages.flask
    pkgs.python3Packages.flask-sqlalchemy
    pkgs.python3Packages.flask-login
    pkgs.python3Packages.flask-mail
  ];
  idx.previews = {
    enable = true;
    previews = {
      web = {
        command = [ "python3" "app.py" "--port" "$PORT" "--host" "0.0.0.0" ];
        manager = "web";
      };
    };
  };
}