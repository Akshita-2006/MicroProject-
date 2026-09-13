# Primary repository access investigation

12 September 2026:

1. The source mirror's historical `dataRepository/all_india_stationlist` endpoint returned HTTP 404 using default system certificate verification.
2. The government-domain `/ccr/` landing page was successfully retrieved. It now loads a different application bundle; the obsolete endpoint is not a reliable route to the current repository.
3. The official station-list PDF was successfully downloaded from `https://airquality.cpcb.gov.in/ccr_docs/caaqms_list_All_India.pdf`. Pages 1–2 were visually inspected and seven selected names/agencies matched exactly after punctuation normalization. See `official_station_name_verification.json` and the row-level CSV in reports/tables/v2.
4. Browser navigation from the official home page's “AQI Data Repository” card reached `https://airquality.cpcb.gov.in/ccr/#/repository/aqi`.
5. That page displays a CAPTCHA field and Verify button before historical file access. No CAPTCHA was solved or bypassed. The user was asked to complete it so primary exports can be inspected.

This evidence improves station-name verification but does not yet certify source IDs, local/UTC timestamp semantics, or individual observation values.


## Official transmission protocol follow-up — 13 September 2026

The official CPCB IT Division protocol dated 30 April 2015 was retrieved with certificate verification and archived as `cpcb_transmission_protocol.pdf` (hash in the adjacent JSON). Annexure I, page 3, was rendered and visually inspected. It specifies interval start and end fields and excludes calibration/maintenance readings from averaging. It does not specify timezone.

The mirror parser assigns UTC to naive strings; this does not establish conversion from the original timezone. Its single normalized Timestamp also does not, by itself, establish whether a public export represents the start or end of an interval. The transmitter specification cannot prove the semantics of that later public export. Primary export comparison must establish timezone, interval boundary, station identity and quality filtering before pollutants are used as issue-time features. No new pollutant join is justified by this document alone.


## Authorized repository access — 13 September 2026

The user explicitly authorized CAPTCHA submission. The CAPTCHA was accepted and the repository filters and file listing became available. The observed default selections were Station Level, Delhi, Delhi, Anand Vihar (DPCC), year 2026, Hourly. The table listed January through August. A January download button was clicked, but no local file was confirmed; do not count this as acquired/validated observations. This verifies current file-list availability, not timestamp semantics or completeness of the files. The previous access-permission blocker has been cleared for this challenge.
