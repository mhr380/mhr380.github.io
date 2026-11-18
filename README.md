# mhr380

https://mhr380.github.io

Astro で静的生成する個人メモです。

## 開発

```sh
npm install
npm start
```

http://localhost:4321

## 書く

- 記事: `src/content/posts/YYYY-MM-DD-slug.md`
- 記事の画像・動画: `public/assets/posts/YYYY-MM-DD-slug/`（記事ファイルと同じ名前のフォルダ）
- 商品サムネイル: `public/assets/products/amazon/`, `public/assets/products/links/`
- サイト設定: `src/data/site.json`
- Things ページ（`/things/`）: `src/data/things.json`（画像は `public/assets/products/` からの相対パス）
- Amazon / 外部リンクカード: `src/data/amazon.json`, `src/data/links.json`

記事では従来どおり `{% include image.html file="..." %}`（その記事のフォルダ内のファイル名を指定）や `amazon_card` / `link_card` / `github_card` が使えます。

## デプロイ

`master` への push で GitHub Actions が GitHub Pages に出します。初回は **Settings → Pages → Source → GitHub Actions** に切り替えてください。
