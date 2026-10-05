---
id: CR-1
type: change-request
title: "Personas koda pārbaude iesniegumā"
status: READY
priority: high
reporter: "Reģistrācijas nodaļa (izdomāts)"
owner: "@<github-lietotājvārds>"
contract: "docs/openapi.yaml · POST /submissions · personalCode"
depends_on: []
exported: "2026-09-30 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu"
---

# CR-1 · Personas koda pārbaude iesniegumā

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Iesniegumos bieži ir nepareizi personas kodi. Sistēmai jāpārbauda personas koda formāts un nederīgi iesniegumi jānoraida.

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade `personalCode` | Sagaidāmais rezultāts |
|---|---|---|
| 1 | `32000000001` | `201`, saglabāts `32000000001` |
| 2 | `320000-00001` | `201`, saglabāts `32000000001` (bez defises) |
| 3 | `" 32000000001 "` | `201`, saglabāts `32000000001` (atstarpes sākumā un beigās noņemtas) |
| 4 | `3200000000` (10 cipari) | `400 VALIDATION_ERROR`, `personalCode` · `INVALID_FORMAT` |
| 5 | `320000000011` (12 cipari) | `400 VALIDATION_ERROR`, `personalCode` · `INVALID_FORMAT` |
| 6 | `3200000000O` (burts O nulles vietā) | `400 VALIDATION_ERROR`, `personalCode` · `INVALID_FORMAT` |
| 7 | Lauka `personalCode` nav | `400 VALIDATION_ERROR`, `personalCode` · `REQUIRED` |
| 8 | `010190-00000` (vecā formāta sintētisks kods) | `201`, saglabāts `01019000000` |
| 9 | `3200-0000001` (defise nepareizā vietā) | `400 VALIDATION_ERROR`, `personalCode` · `INVALID_FORMAT` |
| 10 | `""` vai `"   "` | `400 VALIDATION_ERROR`, `personalCode` · `REQUIRED` |
| 11 | `320000--00001` vai `32000000001-` | `400 VALIDATION_ERROR`, `personalCode` · `INVALID_FORMAT` |
| 12 | `320000 00001` (atstarpe vidū) | `400 VALIDATION_ERROR`, `personalCode` · `INVALID_FORMAT` |
| 13 | Nederīgs `personalCode` ievadīts UI formā | Iesniegums netiek nosūtīts, un kļūda tiek parādīta pie `personalCode` lauka |

Visos `400` gadījumos iesniegums netiek saglabāts.

## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| Kādi formāti derīgi? | Tieši 11 cipari; papildus drīkst būt viena defise tieši pēc 6. cipara. Pirms saglabāšanas defise tiek noņemta. | Reģistrācijas nodaļa, 2026-09-30 |
| Vai atšķirīgi validē jaunā un vecā formāta personas kodus? | Nē. CR-1 ietvaros abiem piemēro vienādus vienkāršotos formāta noteikumus. | Reģistrācijas nodaļa, 2026-09-30 |
| Vai pārbauda kontrolciparu vai dzimšanas datumu? | Nē. Tiek pārbaudīts tikai CR-1 noteiktais formāts. | Reģistrācijas nodaļa, 2026-09-30 |
| Kā apstrādā atstarpes? | Atstarpes ievades sākumā un beigās tiek noņemtas. Atstarpes personas koda iekšienē nav atļautas. | Reģistrācijas nodaļa, 2026-09-30 |
| Tukša vērtība vai tikai atstarpes? | Tāpat kā trūkstošs lauks: `REQUIRED`. | Reģistrācijas nodaļa, 2026-09-30 |
| Vai pārbaude ir arī UI formā? | Jā. Nederīga personas koda gadījumā iesniegums netiek nosūtīts un kļūda tiek parādīta pie lauka. | Reģistrācijas nodaļa, 2026-09-30 |

## Ārpus tvēruma (out of scope)

- Kontrolcipara pārbaude
- Dzimšanas datuma korektuma pārbaude
- Pārbaude pret Iedzīvotāju reģistru
- Jau saglabāto iesniegumu labošana (12 iesniegumi no 2026-09-27)

## Komentāri (comments)

- 2026-09-28 · Reģistrācijas nodaļa: "Vakar 12 iesniegumi ar nepareizu kodu. Visi jālabo ar roku."