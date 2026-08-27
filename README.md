# ahigardiner.dk

Statisk website for AHI Gardiner. Bygges af `build.py` og deployes til Simply.

## Sådan hænger det sammen

- `build.py` genererer alle 16 HTML-sider, `robots.txt` og `sitemap.xml` ind i `site/`
- `assets/css/style.css` og `assets/js/main.js` er kildefiler og kopieres ind ved build
- GitHub Actions bygger ved hvert push og committer `deploy.zip` i repo-roden
- Simply henter `deploy.zip` via **File Manager → Upload → Upload fra URL** med
  destinationsmappe `/ahigardiner.dk` og flueben i "Forsøg at udpakke .zip-fil"

Rå-adresse til Simply:

```
https://raw.githubusercontent.com/Necipdg/ahigardiner-dk/main/deploy.zip
```

## Billeder

Billederne ligger **ikke** i dette repo. De er uploadet én gang til
`/ahigardiner.dk/assets/img/` på webhotellet og ændrer sig sjældent. `deploy.zip`
inderholder derfor kun HTML, CSS, JS, robots.txt og sitemap.xml — en udpakning
rører ikke billederne.

## Hosting

`ahigardiner.dk` er et domænealias på `skrotauto.dk`. Indholdet serveres fra mappen
`/ahigardiner.dk` på skrotauto-webhotellet. PHP 8.2. HTTPS via Let's Encrypt med
"Tving HTTPS" slået til i Simplys kontrolpanel.
