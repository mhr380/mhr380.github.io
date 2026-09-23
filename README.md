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

- 記事: `_posts/YYYY-MM-DD-slug.md`
- 画像・動画: `public/assets/static/`
- サイト設定: `src/data/site.json`
- Amazon / 外部リンクカード: `src/data/amazon.json`, `src/data/links.json`

記事では従来どおり `{% include image.html %}` や `amazon_card` / `link_card` / `github_card` が使えます。

## デプロイ

`main` への push で GitHub Actions が GitHub Pages に出します。初回は **Settings → Pages → Source → GitHub Actions** に切り替えてください。
