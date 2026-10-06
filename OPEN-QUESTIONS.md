# Open questions for the customer

Items found during the agrammon.ch → Hugo content reconciliation that need a
decision or confirmation from the customer before they can be finalised.

| # | Page | Question | Status |
|---|------|----------|--------|
| 1 | Dokumentation → Grundlagen (DE/EN/FR) | **MISSING LINK.** On live, the "UNECE (…)" reference is hyperlinked to `http://www.unece.org/env/documents/2007/eb/wg5/WGSR40/ece.eb.air.wg.5.2007.13.e.pdf`. That URL returns **HTTP 403** to scripted requests -- but so does the unece.org homepage (bot protection), so the link may still work in a browser. Kept as plain text for now. → Confirm the correct/current target, or drop the link. | ⏳ open |
| 2 | Dokumentation → Modellparameter → Emissionsfaktoren (DE/EN/FR) | **DIFFERING TERMINOLOGY across languages.** DE "Emissionsfaktoren", EN "Emission factors", FR "Taux d'émission" (= emission *rates*). This already matches the live site and may be intentional. → Customer to decide whether FR should be unified. | ⏳ open |
| 3 | Downloads → Modell Agrammon (DE/EN/FR) | **MISSING / WRONG DOWNLOAD.** The entry "Änderungen der Version 7.0.0 gegenüber Version 6.5.2 (2026-05-29)" has no file on the live site (DE/FR: link text only; EN: links the version-5.0 document). → Customer to supply the correct 7.0.0 PDF. | ✅ resolved 2026-10-06: live site now links the 7.0.0 PDFs (DE/FR); added here. |

<!--
Add new rows as they come up. Keep the visible `{{< todo >}}` marker in the
relevant content files in sync with the row here so they can be found by grep:
    grep -rn "{{< todo" content/
-->
