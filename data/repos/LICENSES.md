# Licences of the subject repositories

Each of the 32 subject repositories was identified by reading its licence file(s) out of the local
clone at the SHA pinned in `manifest.csv` (`git -C <clone_dir> show <sha>:<path>`), not from the
GitHub API `license` field, which reports `NOASSERTION` for five of them; the identification was
done on 2026-09-18. The same values are carried in `manifest.csv` as `license_spdx`,
`license_file` and `license_note`. Every file listed below was read at the pinned commit; no row
needed a fall-back to the working tree. `license_file` names the governing file(s) at the root of
the repository; sub-directory and vendored licences are described in the note.

| Repo | Pinned SHA | SPDX id | Licence file | Note |
| --- | --- | --- | --- | --- |
| `TheAlgorithms/Python` | `78d335823dd8aa854faae6b6558e5f3ebcbd9630` | `MIT` | `LICENSE.md` | Permissive; single MIT licence at the repository root. |
| `yt-dlp/yt-dlp` | `c7fb478d21e9e59524befbe23f7801bb267fb880` | `Unlicense` | `LICENSE` | Public-domain dedication; no redistribution or commercial restriction. |
| `AUTOMATIC1111/stable-diffusion-webui` | `82a973c04367123ae98bd9abdf80d9eda9b910e2` | `AGPL-3.0-only` | `LICENSE.txt` | Strong network copyleft: redistributing or hosting a modified version obliges source release under the same terms. No 'or later' election in the repo, so recorded as -only. |
| `open-webui/open-webui` | `0a7c15832fb30b1903753e83f81dc7d27e5b0944` | `LicenseRef-OpenWebUI` | `LICENSE` | Bespoke source-available licence (not OSI-approved): BSD-3-Clause text plus clause 4 forbidding removal or alteration of 'Open WebUI' branding in any deployment above 50 end users per rolling 30 days without written or enterprise permission. Restricts redistribution and commercial rebranding. |
| `langchain-ai/langchain` | `5c1f28271295bb13034f4cf8964f74c117357d40` | `MIT` | `LICENSE` | MIT at the root and in all 21 per-package libs/*/LICENSE files; identical terms. |
| `ytdl-org/youtube-dl` | `956b8c585591b401a543e409accb163eeaaa1193` | `Unlicense` | `LICENSE` | Public-domain dedication; no redistribution or commercial restriction. |
| `Shubhamsaboo/awesome-llm-apps` | `f163bb5a92111cee4610ac98e5dce4c6a2a09c26` | `Apache-2.0` | `LICENSE` | Root Apache-2.0. Eight bundled sub-projects under generative_ui_agents/ carry their own MIT or Apache-2.0 LICENSE files; all permissive. |
| `github/spec-kit` | `d743a695e46d6decfeb48fb2a641913ff5ab9ac5` | `MIT` | `LICENSE` | Root MIT; extensions/template/LICENSE is an MIT placeholder shipped with the extension scaffold. |
| `krahets/hello-algo` | `28c1e74c1d3594fca7cc41b78a6bd18b700c5ce9` | `CC-BY-NC-SA-4.0` | `LICENSE` | Creative Commons Attribution-NonCommercial-ShareAlike 4.0: COMMERCIAL USE IS PROHIBITED and derivatives must be shared alike. Not a software licence. overrides/partials/LICENSE is the MIT licence of mkdocs-material. |
| `iluwatar/java-design-patterns` | `4cabb204f240240bea319605a5ffa46ded728001` | `MIT` | `LICENSE.md` | MIT. The licence file adds a note that the model-view-viewmodel module uses the ZK framework under LGPL; lgpl-3.0.txt ships at the root. The trailing note is why the GitHub API reports NOASSERTION. |
| `macrozheng/mall` | `dcaa93b3150352e5044708d7211b5bed0af4509f` | `Apache-2.0` | `LICENSE` | Permissive; single Apache-2.0 licence at the root. |
| `TheAlgorithms/Java` | `b6fb8ad0fac794f16e8de4f8bb4a37360034606a` | `MIT` | `LICENSE` | Permissive; single MIT licence at the repository root. |
| `termux/termux-app` | `084d709fbf23ea83b5cb85fd3d795c775be06676` | `GPL-3.0-only` | `LICENSE.md` | Explicitly 'GPLv3 only'. Documented exceptions: terminal-view and terminal-emulator are Apache-2.0; termux-shared is MIT except com/termux/shared/termux/* (GPL-3.0-only) and file/filesystem/* (GPL-2.0-with-classpath-exception). Copyleft restricts relicensing of derivatives. |
| `skylot/jadx` | `2fb1b16386941660fda07e9017285aec40fcb37f` | `Apache-2.0` | `LICENSE` | Permissive; NOTICE lists third-party components bundled with jadx. |
| `ReactiveX/RxJava` | `ec327a2fef842e80bfdefb42de81a08a14027b6a` | `Apache-2.0` | `LICENSE` | Permissive; COPYRIGHT restates the Apache-2.0 grant. |
| `lysine-dev/retrofit` | `e27d855b7b029e7f907dfc52205fdb3e9c603c16` | `Apache-2.0` | `LICENSE.txt` | Permissive; single Apache-2.0 licence at the root. |
| `freeCodeCamp/freeCodeCamp` | `ad0bd29beb67863afd6cba2f38e98ec786a40f84` | `BSD-3-Clause` | `LICENSE.md` | Permissive; standard three-clause BSD, no commercial restriction. |
| `firecrawl/firecrawl` | `c563a66ff9b00c7c138be34d22c3d8d04dfbd0c5` | `AGPL-3.0-only` | `LICENSE` | Network copyleft for the application. The SDKs and ingestion UI (apps/js-sdk, apps/js-sdk/firecrawl, apps/python-sdk, apps/ruby-sdk, apps/elixir-sdk, apps/ui/ingestion-ui) ship their own MIT LICENSE files. No 'or later' election, so recorded as -only. |
| `yangshun/tech-interview-handbook` | `e1d28e8886c0b6ff3e50da991ce0e895134ddc59` | `MIT` | `LICENSE` | Permissive; single MIT licence at the repository root. |
| `garrytan/gstack` | `a6b3a57512ca6d5c6aa5b68f74f736195021f96e` | `MIT` | `LICENSE` | MIT. NOTICE.md lists files derived from Apache-2.0 upstreams and licenses/Apache-2.0.txt ships the corresponding text; attribution obligations only. |
| `excalidraw/excalidraw` | `c0ad61c6743aef7623e641cd1460d757cc6cacf3` | `MIT` | `LICENSE` | MIT at the root; packages/laser-pointer/LICENSE is the same MIT licence. |
| `immich-app/immich` | `efbbd32e55067eb02a51030c5c948ae617484f8b` | `AGPL-3.0-only` | `LICENSE` | Strong network copyleft: self-hosting a modified version for others obliges source release. packages/cli/LICENSE is the same AGPL-3.0 text. No 'or later' election, so recorded as -only. |
| `earendil-works/pi` | `e4c75a73222ae2c72abb5f5314fa35ee8effc508` | `MIT` | `LICENSE` | Permissive; single MIT licence at the repository root. |
| `ant-design/ant-design` | `745b6d11a132573a5127eaf19860b8a5f2f6d263` | `MIT` | `LICENSE` | Permissive; single MIT licence at the repository root. |
| `ollama/ollama` | `6b8bef2caa5bd46b50e13a9dd893fcedc9f3aaea` | `MIT` | `LICENSE` | MIT at the root; app/dialog/LICENSE is a vendored ISC-licensed component. |
| `fatedier/frp` | `d20a232996007dfe6ab425abc0a39a3ae9a0889b` | `Apache-2.0` | `LICENSE` | Permissive; single Apache-2.0 licence at the root. |
| `JuliusBrussee/caveman` | `c2906c626be1d703b04e203d9f804a263e87f4ef` | `MIT AND BUSL-1.1` | `LICENSE`, `LICENSE.BSL` | Split licence documented in LICENSING.md. Adoption surfaces (packages/*, skills/, extension shell, mem/js, mem/py, shared/provider-catalog) are MIT; the engine-linked directories (engine/, proxy/, rewriter/, browse/, mcp/, shrink/, mem/, shared/platform/) are Business Source License 1.1, which is NOT open source: offering the licensed work to third parties as a hosted, managed or embedded service requires a commercial licence until the change date 2030-06-21, after which Apache-2.0 applies. |
| `gohugoio/hugo` | `ec57bb7d348989513b919c7ea9ff08fed0bec327` | `Apache-2.0` | `LICENSE` | Hugo's code is Apache-2.0 and docs/content is Apache-2.0 (docs/content/LICENSE.md), but docs/LICENSE.md states the documentation theme (layouts, CSS, JavaScript) has no open-source licence and is not meant for reuse; that subtree is not redistributable. |
| `gin-gonic/gin` | `5c6a15f8f9566612076bd209e623861bf92a6283` | `MIT` | `LICENSE` | Permissive; single MIT licence at the repository root. |
| `syncthing/syncthing` | `bb19c017ae672b766338e21ab8c4d8ef6024fae3` | `MPL-2.0` | `LICENSE` | File-level copyleft: modified MPL files must stay MPL, larger works may be combined. cmd/strelaysrv and cmd/infra/strelaypoolsrv are MIT; gui/default/vendor/* are third-party bundles. |
| `junegunn/fzf` | `b1be3a8be1b833ce5b92fbbac11637643d60a046` | `MIT` | `LICENSE` | MIT at the root; src/LICENSE is the same MIT licence. |
| `jesseduffield/lazygit` | `71d3e7dfa5f9278172013bfa1bb83d60d155436a` | `MIT` | `LICENSE` | MIT at the root; pkg/gocui/LICENSE is BSD-3-Clause and vendor/* holds third-party Go module licences. |

## Non-permissive and non-OSI licences

* `open-webui/open-webui` — `LicenseRef-OpenWebUI`, a bespoke source-available licence (BSD-3-Clause
  plus a branding clause). Not OSI-approved.
* `JuliusBrussee/caveman` — `MIT AND BUSL-1.1`. The Business Source License 1.1 part is not open
  source and requires a commercial licence for third-party hosted, managed or embedded service use
  until the change date 2030-06-21.
* `krahets/hello-algo` — `CC-BY-NC-SA-4.0`. Commercial use is prohibited.
* `AUTOMATIC1111/stable-diffusion-webui`, `firecrawl/firecrawl`, `immich-app/immich` — AGPL-3.0,
  network copyleft.
* `termux/termux-app` — GPL-3.0-only, copyleft.
* `syncthing/syncthing` — MPL-2.0, file-level copyleft.
* `gohugoio/hugo` — Apache-2.0 code, but the documentation theme under `docs/` carries no
  open-source licence and is not redistributable.

All other repositories are under permissive terms (MIT, Apache-2.0, BSD-3-Clause) or are dedicated
to the public domain (Unlicense).

## Caveat

`scripts/select_repos.py` rewrites this manifest on a re-selection; since 2026-09-18 its writer keeps every column already present in the file, so these three licence columns survive a re-run (verified by reading the writer's field list).
does not include the three licence columns. Re-running it would drop them; they must be re-applied,
or that field list extended, after any re-selection.
