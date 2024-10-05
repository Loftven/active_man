# Добро пожаловать в vulnerable active_man application

## Введение
Добро пожаловать в репозиторий проекта active_man! Этот проект направлен на оттачивание навыков пентестинга веб-приложений. Так же он может применяться при собеседовании на позицию junior-pentester для оценки навыков.

## Сюжет
Недавно УК City разработало приложение “Активный человек”, которое позволит властям и горожанам эффективнее контактировать друг с другом. Приложение позволяет гражданам выбирать инфраструктурные проекты для реализации в своем городе. Сегодня утром граждане увидели провокационные надписи в новом приложении, а в сети появились данные о продаже архива с данными жителей города. Глава УК City заявил прессе, что все данные были защищены с помощью шифрования, но граждане опасаются за свою конфиденциальность. Началось расследование.

## Уязвимости
В рамках нашего проекта были исследованы следующие уязвимости:

- **A03:2021 – Injection (SQL injection)**: Это тип атаки на базы данных, при котором злоумышленник вводит вредоносный SQL-код в поля ввода, чтобы манипулировать запросами к базе данных. Это может привести к несанкционированному доступу, утечке данных, изменению или удалению информации
- **A07:2021 – Identification and Authentication Failures (IDOR)**: Уязвимость, связанная с небезопасной ссылкой на объект
- **A03:2021 – Injection (RCE via PDF creation)**: Уязвимость, связанная с небезопасной генерацией pdf-документов
- **A02:2021 – Cryptographic Failures**: Уязвимость, связанная с ненадежным шифрованием zip архива

## Технологии
В приложении использовались следующие технологии:
- **Json Web Token** для авторизации
- **SQLite** для хранения информации
- **Flask** для создания веб-приложения
- **Docker** для контейнеризации приложения
- **LaTeX** для генерации документов

## Запуск
Для запуска используйте docker:
Скачайте проект, откройте терминал в корневой папке проекта и напишите команды "docker build -t <tag_name> . ", "docker run -d -p 5000:5000 -p 5022:22 --name <container_name> <tag_name>". Для взаимодействия с приложением перейдите по ссылке http://localhost:5000/

## Прохождение

<details>
  <summary>Нажмите, чтобы открыть меню:</summary>

  - Заходим на сайт и оцениваем функциональность.
  - Регистрируемся.
  - Видим, что можем поставить лайк и подтвердить аккаунт. На этом этапе эксплуатируем or-based SQL injection ![тык](https://book.hacktricks.xyz/pentesting-web/sql-injection) и ![тык](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://portswigger.net/web-security/sql-injection/cheat-sheet&ved=2ahUKEwjlq6yxgOmIAxVDFBAIHf9XFwgQFnoECBcQAQ&usg=AOvVaw1-chxB0XFPiDFl3H0x7eal).
  - После подтверждения аккаунта становится доступным вход по QR. Декодируем его и видим, что для входа используется токен и id пользователя. Меняем id на id админа.
  - Оцениваем функциональность, доступную админу. Видим, что можем закрыть проект, однако не хватает голосов граждан. Проведя фаззинг, обнаруживаем, что данный эндпоинт также поддерживает метод POST. Далее подбираем параметр (helper), который нужно передать, чтобы обойти проверку на голоса (True).
  - Закрываем проект и получаем сгенерированный PDF-документ. Используя `Exiftool`, определяем, что при генерации использовался пакет LaTeX ![клик](https://book.hacktricks.xyz/pentesting-web/formula-csv-doc-latex-ghostscript-injection#command-execution).
  - С помощью полезных нагрузок, приведённых в ссылке выше, проводим разведку сервера. В папке `/root/.ssh` находим приватный ключ `id_rsa`. Получаем его в PDF при помощи нагрузки:

{\scriptsize
\immediate\write18{cat /home/simple-user/.ssh/id_rsa | base64 > output}
\input{output}
}



  - Декодируем и сохраняем в файл `id_rsa` (команда: `cat id_in_base64 | base64 -d > id_rsa`). Видим, что это зашифрованный ключ.
  - Используя `ssh2john`, создаём хеш этого ключа: `ssh2john id_rsa > hash`. С помощью `John the Ripper` подбираем пароль: `john hash --wordlist=/path/to/rockyou`. Получаем пароль и входим на сервер (пароль: "droopy").
  - В соответствии с сюжетом необходимо получить доступ к конфиденциальным данным, поэтому проводим разведку в рабочей папке `/app/instance` и находим `archive.zip`, защищённый паролем. Однако в нём используется слабое шифрование ![тык](https://jizen0x01.github.io/Mess-Me-Writeup/#) и ![тык](https://github.com/kimci86/bkcrack/blob/master/example/tutorial.md).
  - Используя приведённые выше ссылки, получаем доступ к содержимому архива: создаём файл, используя команду:

    

bash
echo -n "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52" > plain.text



 <p>Проверяем содержимое архива</p>
  <div align="center"><img src="https://github.com/Loftven/standoff_app/blob/master/assets/1.png" alt="Проверяем содержимое архива" /></div>
  
  <p>Запускаем взлом</p>
  <div align="center"><img src="https://github.com/Loftven/standoff_app/blob/master/assets/2.png" alt="Запускаем взлом" /></div>

  <p>Дешифруем архив</p>
  <div align="center"><img src="https://github.com/Loftven/standoff_app/blob/master/assets/3.png" alt="Дешифруем архив" /></div>
  
- В базе данных находим конечный флаг: `{ThI5_IS_Your_Fl@6}`

</details>

## Заключение
Спасибо за интерес к проекту! Буду рад предложениям по созданию уязвимых сервисов, а также советам по улучшению существующих. Приятного хакинга !
