@echo off
cd /d "%~dp0"
set "PATH=C:\Ruby33-x64\bin;%PATH%"
bundle exec jekyll serve --host 127.0.0.1 --port 4000
