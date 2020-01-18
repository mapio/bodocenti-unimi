# B. O. Docenti @ Unimi

Questo repository contiene il codice di `bodocenti´ uno script per scaricare l'elenco degli iscritti agli esami dal [backoffice docenti](https://work.unimi.it/boDocenti/) del [La Statale](https://www.unimi.it/) di Milano.

[![asciicast](https://asciinema.org/a/5KcjQNAFEZrdEzjGtSxFUSVg7.png)](https://asciinema.org/a/5KcjQNAFEZrdEzjGtSxFUSVg7?speed=2)

Usando [Selenium](https://selenium.dev/) e [Firefox](https://www.mozilla.org/en-US/firefox/new/) in modalità *headless* con [gekodriver](https://github.com/mozilla/geckodriver), lo script accede al backoffice usando le *credenziali d'Ateneo* (che devono essere memorizzate in variabili d'ambiente, o immesse all'invocazione) e scarica in formato [tab-separated-values](https://en.wikipedia.org/wiki/Tab-separated_values) gli elenchi degli iscritti a tutti gli esami (permettendo di scegliere tra gli appelli *aperti*, oppure *in via di verbalizzazione* o *chiusi*).

## Installazione

Per prima cosa è necessario avere installato [Firefox](https://www.mozilla.org/en-US/firefox/new/) e [gekodriver](https://github.com/mozilla/geckodriver), nel caso di Mac OS X, ad esempio, driver può essere installato come

    brew install geckodriver

quindi è sufficiente installare il binario dell'ultima [release](https://github.com/mapio/bodocenti-unimi/releases), tale binario è stato prodotto con [Pyinstaller](https://www.pyinstaller.org/) e dovrebbe risultare autocontenuto.

## Uso

Per scaricare gli elenchi degli iscritti di tutti gli appelli a cui si ha accesso dal backoffice docenti è sufficiente usare il comando

    ./bodocenti

Esiste un minimo `help` per conoscere le opzioni

    usage: bodocenti [-h] [-u USER] [-d DIR] [-n [NOME]] [-i] [-c]

    Scarica gli elenchi di iscritti da BODocenti @ UniMI.

    optional arguments:
      -h, --help            show this help message and exit
      -u USER, --user USER  nome utente del backoffice
      -d DIR, --dir DIR     directory dove salvare gli elenchi (se assente, verrà
                            usata la directory corrente)
      -n [NOME], --nome [NOME]
                            insegnamento da considerare (se asssente, saranno
                            considerati tutti gli insegnamenti)
      -i, --inserimento     se presente, considera anche gli appelli in fase di
                            inserimento esiti
      -c, --chiusi          se presente, considera anche gli appelli chiusi

### Autenticazione e sicurezza

Il backoffice docenti può essere acceduto solo usando le credenziali di Ateneo. Lo script *non conserva* le credenziali in alcun modo (come è possibile verificare dal codice sorgente). Onde evitare di digitare il proprio username si può usare l'opzione `--user` ma per ovvi motivi di sicurezza non ne esiste una per specificare la passwrd. Una ragionevole alternativa può essere quella di memorizzare le proprie credenziali nelle variabili d'ambiente `BODOCENTI_USER` e `BODOCENTI_PADSSOWRD`.