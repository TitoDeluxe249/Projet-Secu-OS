import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


import click
from src.core.monitor import start_monitoring
from src.security.permissions import show_permissions, modify_permissions

@click.group()
def cli():
    """📁 FileSystem Monitoring Tool - CLI"""
    pass

@cli.command()
@click.argument("path", type=click.Path(exists=True))
def monitor(path):
    """Surveille un répertoire ou fichier"""
    start_monitoring(path)

@cli.command()
@click.argument("file", type=click.Path(exists=True))
def perms(file):
    """Affiche les droits d'accès à un fichier"""
    show_permissions(file)

@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.argument("mode", type=str)
def chmod(file, mode):
    """Modifie les permissions (ex: 755, 644)"""
    modify_permissions(file, mode)

if __name__ == "__main__":
    cli()
