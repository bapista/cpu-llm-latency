# HotMobile 2027 version

ACM `sigconf` port of the paper for **HotMobile 2027** (28th Workshop on Mobile
Computing Systems & Applications). Body content is identical to the canonical
arXiv `article` version (`../main.tex`) — only the format and the abstract/intro
framing (nudged toward on-device/mobile/edge) differ.

- **Deadline:** Friday **9 October 2026, 11:59pm AoE**
- **Submit:** https://hotmobile27.hotcrp.com/
- **Format (confirmed from the CFP):** ACM `sigconf`, **10pt body**, **≤6 pages
  including references**, double column, not anonymous (arXiv preprint is fine),
  no simultaneous submission to another venue.
- **Current status:** compiles to **6 pages** with tectonic (`tectonic main.tex`);
  fits the limit with slack on the last page.

## Camera-ready checklist (do at submission / on acceptance)

1. **Use HotMobile's exact 10pt-amended `acmart` template** if they provide one.
   This port approximates 10pt via `\documentclass[sigconf,nonacm,10pt]{acmart}`;
   swap in the official template file if the layout must match precisely.
2. **Add CCS concepts** (`\begin{CCSXML}…\ccsdesc`) — optional for submission,
   required for camera-ready. There is room on page 6.
3. **Add the real ACM conference metadata** (`\acmConference`, `\acmYear`, DOI,
   copyright) once accepted — currently suppressed via `nonacm` + `printacmref=false`.
4. Verify the HotCRP-generated PDF matches this one (6 pages, Figure 1 + Algorithm 1).

## Note on strategy

HotMobile has **no simultaneous submission** — submit here OR to EuroMLSys, not
both at once. This is the archival, gate-clearing target with the soonest
confirmed deadline; EuroMLSys 2027 (~Feb 2027) is the fallback if this misses.
