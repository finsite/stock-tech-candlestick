name: Deploy with Helm

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy with Helm
        run: helm upgrade --install stock-tech-candlestick ./helm
