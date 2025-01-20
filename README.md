# Intro
This script parses QR data from some electronic suppliers and saves data into a CSV via shell. It is useful to check received components and store them in a CSV ready for input in other software.

# API
This script uses Mouser API. You need to get an API key from Mouser and save into api_key.json in the same directory as the script. The file should look like this:
```json
{
  "api_key":"xxxxxxxx-yyyy-zzzz-kkkk-wwwwwwwwwwww"
}
```
# Supported suppliers
## LCSC
```json
{
  "pbn": "PICK2412170040",
  "on": "GB2412170353",
  "pc": "C28260",
  "pm": "CL21C222JBFNNNE",
  "qty": 60,
  "mc": "",
  "cc": 1,
  "pdi": 139269778,
  "hp": null,
  "wc": "ZH"
}
```

# TME

```text
QTY:5 PN:CD40106BE PO:31727961/3 CPO:ordinerip1 MFR:TEXASINSTRUMENTS MPN:CD40106BE RoHS https://www.tme.eu/details/CD40106BE
```


