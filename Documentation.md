# Documentation

## General Commands

### +prefix
You can use this command to change the server's prefix for the bot. (Server's owner only)
**To get server's current prefix:**
```
+prefix
```
**To change server's current prefix:**
```
+prefix [prefix]

```
**For example:** `+prefix ++`

### +userinfo
Sends your user information in the channel.
**You can check other user's info by mentioning them:**
```
+userinfo [@user]
```
**For example:** `+userinfo @MuslimBot`

## Islamic Features

### Quran

#### +quran
allows you to quote verses from the Qur'an. You can optionally specify a translation (see **Valid Translations** below). If you do not, the bot will send the verses in English.

**To get a single verse:**
```
+quran [surah]:[verse] [translation]
```
For example:
```
+quran 1:1 french
```
**To get multiple verses:**
```
+quran [surah]:[firstVerse]-[lastVerse] [translation]
```
For example:
```
+quran 1:1-7 khattab 
```
The above command would quote Surah 1, Verses 1-7 (Surah al-Fatihah) using the translation of Dr Mustafa Khattab.

##### Valid translations
```
+translationlist
```


#### +aquran
functions exactly like  **+quran**, but sends the verses in Arabic.

For example, to quote the first verse of the Qur'an:
```
+aquran 1:1
```

#### +morphology
allows you to analyse the Arabic morphology of any word in the Qur'an.

```
+morphology [surah]:[verse]:[word number]
```

For example:
```
+morphology 1:2:4
```
The above would analyse the morphology of the 4th word of the 2nd verse of the 1st chapter of the Qur'an. The bot will also show the syntax of the verse the word is in, if the data is available.


#### +mushaf
sends the page containing a Qur'anic verse on a standard mushaf.
```
+mushaf [surah]:[verse]
```
For example:
```
+mushaf 1:2
```
The above would send an image of the page containing Qur'an 1:2 on a *Medina Mushaf*. 

If you want a page with color-coded *tajweed* rules, add 'tajweed' to the end of the command.

For example:
```
+mushaf 112:1 tajweed
```



### Tafsir (Commentaries on the Qur'an) 

#### +atafsir
allows you to quote from over 37 Arabic *tafaseer* (commentaries on the Qurʾān). A list of valid *tafaseer* is available [here](https://github.com/galacticwarrior9/islambot/blob/master/Tafsir.md).

```
+atafsir [surah]:[verse] [tafsir]
```

For example:

```
+atafsir 2:255 tabari
```

The above command would quote the tafsir of Ayatul Kursi from Tafsir al-Tabari.


#### +tafsir
allows you to quote the English tasfir (commentary) of verses from Tafsīr al-Jalālayn (`jalalayn`), Tafsīr Ibn Kathīr (`ibnkathir`), Tafsīr al-Tustarī (`tustari`), Rashīd al-Dīn Maybudī's Kashf al-Asrār (`kashf`), al-Qurayshi's Laṭāʾif al-Ishārāt (`qurayshi`), Tafsīr ʿAbd al-Razzāq al-Kāshānī (`kashani`) and al-Wahidi's Asbāb al-Nuzūl (`wahidi`). It works in the same manner as **+atafsir**.

```
+tafsir [surah]:[verse] [jalalayn/ibnkathir/kashf/tustari/qurayshi/kashani/wahidi]
```

For example:

```
+tafsir 1:1 ibnkathir
```
The above command would quote the tafsir of Surah al-Fatihah, verse 1 from Tafsir Ibn Kathir. 

### Dua 

#### +dualist
Sends the list of available dua topics for `+dua`. 


#### +dua
allows you to get duas from *Fortress of the Muslim* (Hisn al-Muslim). 

```
+dua [dua topic from -dualist]
```

For example, to get duas for breaking fasts:
```
+dua breaking fast
```


### Hadith 

#### +hadith
allows you to quote hadith from sunnah.com in English.

```
+hadith [hadith collection name] [book number]:[hadith number]
```

For example, to get the second hadith in Book 1 of Sahih Bukhari:
```
+hadith bukhari 1:2
```

The above would fetch the hadith from https://sunnah.com/bukhari/1/2

Alternatively, you can simply type the sunnah.com link in chat. The bot will then send it if it is able to. 


##### Hadith collection names 

| **Hadith Collection** | **Name for Bot** | **Supported Languages** |
|--|--|--|
| Musnad Ahmad ibn Hanbal | `ahmad` | English, Arabic | 
| Sahih al-Bukhari | `bukhari` | Urdu, English, Arabic
| Sahih Muslim | `muslim` | English, Arabic
|  Jami' at-Tirmidhi | `tirmidhi` | English, Arabic
| Sunan Abi Dawud | `abudawud` | Urdu, English, Arabic
| Sunan an-Nasa'i | `nasai` | English, Arabic
| Muwatta Malik | `malik` | English, Arabic
| Riyadh as-Saliheen | `riyadussaliheen ` | English, Arabic
| Al-Adab al-Mufrad | `adab ` | English, Arabic
| Bulugh al-Maram | `bulugh ` | English, Arabic
| 40 Hadith Qudsi | `qudsi ` | English, Arabic
| 40 Hadith Nawawi | `nawawi ` | English, Arabic

40 Hadith Qudsi and Nawawi are only forty hadith long and therefore only need a hadith number. For example: `-hadith qudsi 32`


#### +ahadith
is the same as **+hadith**, but sends the hadith in Arabic.

#### +uhadith
is the same as **+hadith**, but sends the hadith in Urdu. Only Sahih al-Bukhari and Sunan Abu Dawud are available in Urdu.


### Prayer (Salaah) Times

The bot can also fetch the prayer times for any location. More precise locations will yield more accurate prayer times. 

```
+prayertimes [location]
```

For example:
```
+prayertimes Burj Khalifa, Dubai
```

..would fetch prayer times in the general area of the Burj Khalifa in Dubai. 


### Hijri Calendar

#### +hijridate

This shows the current Hijri date (in the US).

#### +converttohijri
Converts a Gregorian date to its corresponding Hijri date.

```
+converttohijri DD-MM-YY 
```

For example:
```
+converttohijri 31-08-2017
```

#### +convertfromhijri
Converts a Hijri date to its corresponding Gregorian date.

For example, to convert 17 Muharram 1407:
```
+convertfromhijri 17-01-1407
```

### Random Generator

#### verse
```
+random verse
```
Gets a random verse from quran


## Quran Audio

### +play
instructs the bot to play a recitation of a surah, ayah or page from the Qur'an. 
#### Playing a surah
```
+play [surah number] [optional reciter]
```

**OR**
```
+play [surah name] [optional reciter]
```


If no reciter is specified, Mishary al-Afasy's recitation will be used. 
[Click here for the list of **surah** reciters](https://github.com/nullbyto/MuslimBot/blob/master/Reciters.md).

**Example 1**: `+play surah al-fatiha Shaik Abu Bakr Al Shatri`

This would play Abu Bakr al-Shatri's recitation of Surah al-Fatiha.

**Example 2**: `+play surah 112 Abdulrahman Alsudaes`

This would play Abdul Rahman al-Sudais' recitation of Surah al-Ikhlas. 

#### Playing a single ayah
```
+play ayah [surah]:[ayah] [optional reciter]
```
If no reciter is specified, Mishary al-Afasy's recitation will be used.

**Example**: `+play ayah 2:255 hatem farid`

This would play Hatem Farid's recitation of Surah al-Baqarah, ayah 255.

#### Playing a single page from the mushaf

```
-qplay page [page number] [optional reciter]
```
`[page]` must be between 1 and 604.
If no reciter is specified, Mishary al-Afasy's recitation will be used.

**Example**: `+play page 10 hani al-rifai`

This would play Hani al-Rifai's recitation of the 10th page of a standard *mushaf*.

### +reciters
Gets the lists of reciters for `+play`.

There are two lists. One is for surah recitations, and the other is for ayah/page recitations. [Click here for the list of **surah** reciters.](https://github.com/galacticwarrior9/QuranBot/blob/master/Reciters.md)
#### +search
Use 	`+search` to search the list of reciters for `+play`. For example, `+search dossary` would return Ibrahim al-Dossary and Yasser al-Dossary.

### +live
Plays a live audio stream.

 - Type `-qlive makkah` foMuslimBot is licensed under the [GNU GPL v3.0](https://github.com/nullbyto/MuslimBot/blob/master/LICENSE).
Conditions for using:
- Credits given
- Code made open-source Qur'an radio.

### +pause
Pauses the audio.

### +resume
Resumes the audio.

### +stop
Stops the audio.

### +leave
Disconnects the bot from voice chat.