# GitHub launch and hosting

The project repository is [mcfruitpunch/omniroot-apparel-network](https://github.com/mcfruitpunch/omniroot-apparel-network).

## Preview the static prototype

Open `index.html` locally, or publish it through GitHub Pages:

1. Open the repository **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Choose **main** and **/(root)**, then **Save**.
4. Once the initial deployment finishes, the expected URL is:
   https://mcfruitpunch.github.io/omniroot-apparel-network/

The project is a static browser simulation, not a live clothing marketplace.
No account registration, real payments, actual production routing, file storage, or secure fit-profile infrastructure exist yet. Browser session state resets when the page is reloaded. Do not enter sensitive measurements in the demo.

## Running tests

From the repository root, install Playwright with Python and a Chromium browser, then run:

```sh
python -m pip install playwright
python -m playwright install chromium
python test_prototype.py
```

The included browser regression script checks the fit-profile gate, order submission, maker steps, design review, and mobile overflow. It does not validate clothing patterns or physical fit.

## Development priorities

Read `BLUEPRINT.md` for the architectural model, privacy boundaries and product lifecycle; use `BUILD_BACKLOG.md` to sequence work. The illustrative `fit-passport.schema.json` and `production-packet.schema.json` are **not ready for processing real users' personal data**.

## Licensing

The repository is public, but no open-source software license or external-design licensing framework has been selected. Establish rights for the code and any submitted designs before inviting general reuse or contributions.
